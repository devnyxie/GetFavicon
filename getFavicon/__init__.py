import pydantic
import requests
import tldextract
from urllib.parse import urljoin
from .helpers import detect_image_format_and_size, prepare_response
import aiohttp
import asyncio
import lxml.html
import timeout_decorator
import requests


from lxml import html


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

#################
####  ASYNC  ####
#################

async def async_get_favicon_from_sources(session, url):
    favicon_links = []
    tasks = []
    try:
        async with session.get(url) as res:
            content = await res.text()
            html = lxml.html.fromstring(content)
            async def find_in_html_and_make_request(path):
                links = html.xpath(path)
                if links:
                    for link in links:
                        # href = link.get('href')
                        href = link
                        if href:
                            task = async_get_favicon_from_url(session, url, href)
                            tasks.append(task)
            sources = [
                #     '//link[@rel="icon" or @rel="shortcut icon"]',
                #     '//meta[@name="msapplication-TileImage"]',
                #     '//link[@rel="apple-touch-icon"]',
                #     '//link[@rel="mask-icon"]'
                '//link[@rel="icon" or @rel="shortcut icon"]/@href',
                '//meta[@name="msapplication-TileImage"]/@content',
                '//link[@rel="apple-touch-icon"]/@href',
                '//link[@rel="mask-icon"]/@href'
            ]
            for source in sources:
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

async def scan_async(domain_url: pydantic.HttpUrl, timeout=4, size = None, all='true'):
    try:
        # async with aiohttp.ClientSession(headers=headers) as session:
        async with aiohttp.ClientSession() as session:
            domain = tldextract.extract(domain_url)
            protocol = 'https://' if domain_url.startswith('https://') else 'http://'
            used_url = f"{protocol}{domain.fqdn}/"
            async_get_favicon_task = async_get_favicon_from_sources(session, used_url)
            result = await asyncio.wait_for(async_get_favicon_task, timeout=timeout)
            return_data = prepare_response(result, size, all)
            return return_data
    except asyncio.TimeoutError:
        return {"response": "The designated time limit was exceeded.", "status": 500}
    except Exception as e:
        return {"response": f"Error in scan_async: {e}", "status": 500}


################
####  SYNC  ####
################

def sync_get_favicon_from_sources(url):
    favicon_links = []
    try:
        response = requests.get(url, headers=headers)
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
        sources = [
            '//link[@rel="icon" or @rel="shortcut icon"]',
            '//meta[@name="msapplication-TileImage"]',
            '//link[@rel="apple-touch-icon"]',
            '//link[@rel="mask-icon"]'
        ]
        for source in sources:
            find_in_html_and_make_request(source)
        response = requests.get(urljoin(url, 'favicon.ico'))
        format, width, height = detect_image_format_and_size(response.content)
        if format:
            favicon_links.append({"format": format.lower(), "width": width, "height": height, "url": urljoin(url, 'favicon.ico')})
        return favicon_links
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the page: {e}")
        return favicon_links

def scan(domain_url: pydantic.HttpUrl, timeout=4, size = None, all='true'):
    #By default, timeout-decorator uses signals to limit the execution time of the given function. This appoach does not work if your function is executed not in a main thread (for example if it’s a worker thread of the web application).
    @timeout_decorator.timeout(timeout, use_signals=False)
    def inner_timeout():
            domain = tldextract.extract(domain_url)
            protocol = 'https://' if domain_url.startswith('https://') else 'http://'
            used_url = f"{protocol}{domain.fqdn}/"
            result = sync_get_favicon_from_sources(used_url)
            return_data = prepare_response(result, size, all)
            return return_data
    try:
        return inner_timeout()
    except Exception as e:
        return {"response": f"Error in scan: {e}", "status": 500}