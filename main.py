import asyncio
from os import path, mkdir, getcwd, listdir

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from aiohttp import ClientConnectorError, ClientSession, TCPConnector
import aiofiles


class cs:
    INFO = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[31m'
    END = '\033[0m'

    @staticmethod
    def add_tabs(text: str) -> str:
        return text.replace("|", "\t|\t")

    @staticmethod
    def info(text: str) -> None:
        print(cs.INFO + cs.add_tabs(text), cs.END)

    @staticmethod
    def success(text: str) -> None:
        print(cs.GREEN + cs.add_tabs(text), cs.END)

    @staticmethod
    def failure(text: str) -> None:
        print(cs.RED + cs.add_tabs(text), cs.END)


def create_dirs(name, url):
    name = name.lower()

    if not path.isdir(f"{getcwd()}\\images"):
        mkdir(f"{getcwd()}\\images")
    if not path.isdir(f"{getcwd()}\\images\\{name}"):
        mkdir(f"{getcwd()}\\images\\{name}")
    new_path = f"{getcwd()}\\images\\{name}\\{len(listdir(f"{getcwd()}\\images\\{name}\\")) + 1}"
    if not path.isdir(new_path):
        mkdir(new_path)
    with open(new_path + "\\article_url.txt", "w") as file:
        file.write(url)

    return new_path


async def download_photo(session: ClientSession, url: str, headers, download_path: str):
    cs.success(f"DOWNLOAD|Start|{url}")
    async with session.get(url, headers=headers) as response:
        async with aiofiles.open(download_path, "wb") as file:
            body = await response.read()
            await file.write(body)
    cs.success(f"DOWNLOAD|End|{url}")


async def search_page(session: ClientSession, url: str, headers, day, month) -> list[str]:
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            cs.failure(f"FAILURE|Status code: {response.status}")
            return []

        cs.info(f"SEARCH|Start|{day}.{month} ({offset})|{url}")

        body = await response.read()
        soup = BeautifulSoup(body, 'html.parser')
        items = soup.findAll('img')
        photos = []
        for item in items:
            src = item.get('src')
            if not "http" in src:
                photos.append(f"https://telegra.ph{src}")
            else:
                photos.append(src)

        return photos


async def parse_article(session: ClientSession, name, day, month, offset):
    global ALREADY_CHECKED_URLS

    url = f"https://telegra.ph/{name}-{month}-{day}{offset}"
    if url in ALREADY_CHECKED_URLS:
        return

    HEADERS = {
        'User-Agent': User_Agent
    }
    photo_links = await search_page(session, url, HEADERS, day, month)
    if len(photo_links) > photos_required:
        base_download_path = create_dirs(name, url)
        tasks = list()
        for i, i_link in enumerate(photo_links):
            i_download_path = base_download_path + f"\\{len(listdir(base_download_path)) + i + 1}.jpg"
            tasks.append(download_photo(session, i_link, HEADERS, i_download_path))
        await asyncio.gather(*tasks)


async def main():
    conn = TCPConnector(limit_per_host=50)
    async with ClientSession(trust_env=True, connector=conn) as session:
        for _month in range(1, 13):
            for _day in range(1, 32):
                for _offset in range(1, offset + 1):
                    try:
                        if _offset == 1:
                            await parse_article(session, name, f"{_day:02}", f"{_month:02}", "")
                        else:
                            await parse_article(session, name, f"{_day:02}", f"{_month:02}", f"-{_offset}")
                    except ClientConnectorError:
                        continue


if __name__ == "__main__":
    name = input(f"{cs.INFO}Name: ").lower()
    offset = input("Offset (enter=1): ")
    offset = int(offset) if offset != '' else 1
    photos_required = input("Minimum photos to save (enter=1): ")
    photos_required = int(photos_required) if photos_required != '' else 0
    print(cs.END)

    User_Agent = UserAgent().random

    ALREADY_CHECKED_URLS = set()
    asyncio.run(main())
