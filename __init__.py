from fastapi import FastAPI
import pydantic
import requests
import tldextract
import requests_cache
from datetime import timedelta
from requests_cache import CachedSession
from urllib.parse import urljoin
from helpers import detect_image_format
import aiohttp
import asyncio
import lxml.html

app = FastAPI()

timeout = 2

session_sqlite = CachedSession(
    'cache',
    use_cache_dir=True,
    cache_control=True,
    expire_after=timedelta(days=7),
    allowable_methods=['GET', 'POST', 'HEAD'],
    allowable_codes=[200, 400, ],
    ignored_parameters=['api_key'],
    match_headers=True,
    stale_if_error=True,
)
requests_cache.install_cache('cache')

headers = requests.utils.default_headers()
headers.update(
    {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; G3121 Build/40.0.A.6.189) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.123 Mobile Safari/537.36',
    }
)

async def parse_html(session, url):
    sources = ['//link[@rel="icon" or @rel="shortcut icon"]', '//meta[@name="msapplication-TileImage"]', '//link[@rel="apple-touch-icon"]']
    return_data = []
    async with session.get(url, headers=headers, timeout=timeout) as res:
        return_data = []
        res.raise_for_status()
        content = await res.text()
        html = lxml.html.fromstring(content)
        async def find_in_html_and_make_request(path):
            links = html.xpath(path)
            for link in links:
                href = link.get('href')
                if href:
                    async with session.get(f"{urljoin(url, href)}", headers=headers, timeout=timeout) as res:
                        format = detect_image_format(await res.read())
                        if format:
                            return_data.append({"url": urljoin(url, href), "format": format.lower()})
                        else:
                            return 
                else:
                    return
        for source in sources:
            await find_in_html_and_make_request(source)
        return return_data


async def fav_ico_check(session,url):
    async with session.get(f"{url}/favicon.ico", headers=headers, timeout=timeout) as res:
        format = detect_image_format(await res.read())
        if format == 'ICO':
            return [{"url": urljoin(url, "/favicon.ico"), "format": format.lower()}]
        return []

async def get_favicon_from_sources(url):
    favicon_links = []
    try:
        async with aiohttp.ClientSession() as session:
            tasks = [
                parse_html(session, url),
                fav_ico_check(session, url),
            ]
            results = await asyncio.gather(*tasks)
            for result in results:
                favicon_links.extend(result)
        return favicon_links
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the page: {e}")

    return favicon_links

async def getFavicon(domain_url: pydantic.HttpUrl):
    domain = tldextract.extract(domain_url)
    used_url = f"http://{domain.fqdn}/"
    links = await get_favicon_from_sources(used_url)
    return links


@app.get("/")
def serve_main():
    return
