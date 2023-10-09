import pydantic
import requests
import tldextract
from urllib.parse import urljoin
from .helpers import detect_image_format
import aiohttp
import asyncio
import lxml.html
import timeout_decorator

timeout = 2

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

# Asynchronous version of get_favicon_from_sources
async def async_get_favicon_from_sources(session, url):
    favicon_links = []
    try:
        used_url = f"http://{tldextract.extract(url).fqdn}/"
        async with session.get(used_url, headers=headers, timeout=timeout) as res:
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
                                favicon_links.append({"url": urljoin(url, href), "format": format.lower()})
                            else:
                                return
                    else:
                        return

            sources = ['//link[@rel="icon" or @rel="shortcut icon"]', '//meta[@name="msapplication-TileImage"]', '//link[@rel="apple-touch-icon"]']
            for source in sources:
                await find_in_html_and_make_request(source)
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the page: {e}")
    return favicon_links

# Synchronous version of get_favicon_from_sources
def sync_get_favicon_from_sources(url):
    favicon_links = []
    try:
        used_url = f"http://{tldextract.extract(url).fqdn}/"
        response = requests.get(used_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        content = response.text
        html = lxml.html.fromstring(content)

        def find_in_html_and_make_request(path):
            links = html.xpath(path)
            for link in links:
                href = link.get('href')
                if href:
                    response = requests.get(f"{urljoin(url, href)}", headers=headers, timeout=timeout)
                    format = detect_image_format(response.content)
                    if format:
                        favicon_links.append({"url": urljoin(url, href), "format": format.lower()})
                    else:
                        return
                else:
                    return

        sources = ['//link[@rel="icon" or @rel="shortcut icon"]', '//meta[@name="msapplication-TileImage"]', '//link[@rel="apple-touch-icon"]']
        for source in sources:
            find_in_html_and_make_request(source)
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the page: {e}")
    return favicon_links

async def scan_async(domain_url: pydantic.HttpUrl, timeout = 2):
    @timeout_decorator.timeout(timeout)
    async def inner_timeout():
        async with aiohttp.ClientSession() as session:
            domain = tldextract.extract(domain_url)
            used_url = f"http://{domain.fqdn}/"
            links = await async_get_favicon_from_sources(session, used_url)
            return links
    try:
        return await inner_timeout()
    except:
        return None

def scan(domain_url: pydantic.HttpUrl, timeout = 2):
    @timeout_decorator.timeout(timeout)
    def inner_timeout():
        domain = tldextract.extract(domain_url)
        used_url = f"http://{domain.fqdn}/"
        links = sync_get_favicon_from_sources(used_url)
        return links
    try:
        return inner_timeout()
    except:
        return None