import pydantic
import requests
import tldextract
from urllib.parse import urljoin
from .helpers import detect_image_format_and_size
import aiohttp
import asyncio
import lxml.html
import timeout_decorator

headers = requests.utils.default_headers()
headers.update(
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    }
)

async def async_get_favicon_from_sources(session, url, timeout, first_only):
    favicon_links = []
    try:
        used_url = f"http://{tldextract.extract(url).fqdn}/"
        async with session.get(used_url, headers=headers, timeout=timeout) as res:
            content = await res.text()
            html = lxml.html.fromstring(content)

            async def find_in_html_and_make_request(path):
                links = html.xpath(path)
                tasks = []

                for link in links:
                    href = link.get('href')
                    if href:
                        task = async_get_favicon_from_url(session, url, href, timeout, first_only)
                        tasks.append(task)
                if tasks:
                    results = await asyncio.gather(*tasks)
                    favicon_links.extend([result for result in results if result is not None])

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
            return favicon_links
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the page: {e}")
        return favicon_links

async def async_get_favicon_from_url(session, base_url, href, timeout, first_only):
    try:
        async with session.get(urljoin(base_url, href), headers=headers, timeout=timeout) as res:
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
        async with aiohttp.ClientSession() as session:
            domain = tldextract.extract(domain_url)
            used_url = f"http://{domain.fqdn}/"
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
                    format, width, height = detect_image_format_and_size(response.content)
                    if format:
                        favicon_links.append({"format": format.lower(), "width": width, "height": height, "url": urljoin(url, href)})
                        if first_only:
                            return favicon_links
                    else:
                        if first_only:
                            return favicon_links
                else:
                    if first_only:
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
            used_url = f"http://{domain.fqdn}/"
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