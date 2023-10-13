import pydantic
import requests
import tldextract
from urllib.parse import urljoin
from .helpers import detect_image_format_and_size
import aiohttp
import asyncio
import lxml.html
import timeout_decorator
import requests
headers = requests.utils.default_headers()
headers.update(
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        "Accept-Language": "en",
        "Referer": "https://www.google.com",
        "DNT": "1",
        "Cache-Control": "max-age=0"
    }
)

async def async_get_favicon_from_sources(session, url, timeout, first_only):
    favicon_links = []
    tasks = []

    try:
        async with session.get(url, timeout=timeout) as res:
            content = await res.text()
            html = lxml.html.fromstring(content)

            async def find_in_html_and_make_request(path):
                links = html.xpath(path)
                for link in links:
                    href = link.get('href')
                    if href:
                        task = async_get_favicon_from_url(session, url, href)
                        tasks.append(task)

            sources = [
                '//link[@rel="icon" or @rel="shortcut icon"]',
                '//meta[@name="msapplication-TileImage"]',
                '//link[@rel="apple-touch-icon"]',
                '//link[@rel="mask-icon"]'
            ]

            for source in sources:
                if first_only and favicon_links:
                    return favicon_links
                await find_in_html_and_make_request(source)

            tasks.append(check_favicon_ico(session, url))

            if tasks:
                    results = await asyncio.gather(*tasks)
                    favicon_links.extend([result for result in results if result is not None])
            return favicon_links
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the page: {e}")
        return favicon_links

async def check_favicon_ico(session, url):
    async with session.get(urljoin(url, 'favicon.ico'), headers=headers) as res:
        format, width, height = detect_image_format_and_size(await res.read())
        if format:
            return {"format": format.lower(), "width": width, "height": height, "url": urljoin(url, 'favicon.ico')}



async def async_get_favicon_from_url(session, base_url, href):
    try:
        async with session.get(urljoin(base_url, href)) as res:
            format, width, height = detect_image_format_and_size(await res.read())
            if format:
                return {"format": format.lower(), "width": width, "height": height, "url": urljoin(base_url, href) }
            else:
                return None
    except Exception as e:
        print(f"Error while fetching favicon from URL: {e}")
        return None

async def scan_async(domain_url: pydantic.HttpUrl, timeout=2, first_only = False):
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            domain = tldextract.extract(domain_url)
            protocol = 'https://' if domain_url.startswith('https://') else 'http://'
            used_url = f"{protocol}{domain.fqdn}/"
            async_get_favicon_task = async_get_favicon_from_sources(session, used_url, timeout, first_only)
            result = await asyncio.wait_for(async_get_favicon_task, timeout=timeout)
            return result
    except asyncio.TimeoutError:
        print("Timeout occurred in scan_async")
        return None
    except Exception as e:
        print(f"Error in scan_async: {e}")
        return None



def sync_get_favicon_from_sources(url, timeout, first_only):
    favicon_links = []
    try:
        # used_url = f"http://{tldextract.extract(url).fqdn}/"
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        content = response.text
        html = lxml.html.fromstring(content)

        def find_in_html_and_make_request(path):
            links = html.xpath(path)
            for link in links:
                href = link.get('href')
                if href:
                    response = requests.get(urljoin(url, href))
                    format, width, height = detect_image_format_and_size(response.content)
                    if format:
                        favicon_links.append({"format": format.lower(), "width": width, "height": height, "url": urljoin(url, href)})
                        if first_only:
                            return favicon_links
                else:
                    if first_only:
                        return favicon_links
            response = requests.get(urljoin(url, 'favicon.ico'))
            format, width, height = detect_image_format_and_size(response.content)
            if format:
                favicon_links.append({"format": format.lower(), "width": width, "height": height, "url": urljoin(url, 'favicon.ico')})
            return favicon_links
        sources = [
            '//link[@rel="icon" or @rel="shortcut icon"]',
            '//meta[@name="msapplication-TileImage"]',
            '//link[@rel="apple-touch-icon"]'
            '//link[@rel="mask-icon"]'
        ]
        for source in sources:
            if first_only and favicon_links:
                return favicon_links
            find_in_html_and_make_request(source)
        return favicon_links
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the page: {e}")
        return favicon_links

def scan(domain_url: pydantic.HttpUrl, timeout = 2, first_only = False):
    @timeout_decorator.timeout(timeout)
    def inner_timeout():
        try:
            domain = tldextract.extract(domain_url)
            protocol = 'https://' if domain_url.startswith('https://') else 'http://'
            used_url = f"{protocol}{domain.fqdn}/"
            links = sync_get_favicon_from_sources(used_url, timeout, first_only)
            return links
        except Exception as e:
            print(f"Error in scan: {e}")
            return None

    try:
        return inner_timeout()
    except Exception as e:
        print(f"Error in scan outer: {e}")
        return None