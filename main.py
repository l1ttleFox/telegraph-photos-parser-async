import asyncio
from os import path, mkdir, getcwd

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from aiohttp import ClientSession, TCPConnector
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


def create_dirs(name, month, day, offset):
    if not path.isdir(f"{getcwd()}\\images"):
        mkdir(f"{getcwd()}\\images")
    if not path.isdir(f"{getcwd()}\\images\\{name}"):
        mkdir(f"{getcwd()}\\images\\{name}")
    if not path.isdir(f"{getcwd()}\\images\\{name}\\{month}_{day}_{offset[1:]}"):
        mkdir(f"{getcwd()}\\images\\{name}\\{month}_{day}_{offset[1:]}")


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

        return photos


async def parse(session: ClientSession, name, day, month, offset):
    HEADERS = {
        'User-Agent': User_Agent
    }
    url = f"https://telegra.ph/{name}-{month}-{day}{offset}"
    photo_links = await search_page(session, url, HEADERS, day, month)
    if len(photo_links) > photos_required:
        create_dirs(name, month, day, offset)
        tasks = list()
        for i, i_link in enumerate(photo_links):
            i_download_path = f"images/{name}/{month}_{day}_{offset[1:]}/{month}_{day}_{offset[1:]}_{i}.jpg"
            tasks.append(download_photo(session, i_link, HEADERS, i_download_path))
        await asyncio.gather(*tasks)


async def main():
    conn = TCPConnector(limit_per_host=10)
    async with ClientSession(trust_env=True, connector=conn) as session:
        for _month in range(1, 13):
            for _day in range(1, 32):
                for _offset in range(1, offset + 1):
                    if _offset == 1:
                        await parse(session, name, f"{_day:02}", f"{_month:02}", "")
                    else:
                        await parse(session, name, f"{_day:02}", f"{_month:02}", f"-{_offset}")


if __name__ == "__main__":
    name = input(f"{cs.INFO}Name: ")
    offset = input("Offset (enter=1): ")
    offset = int(offset) if offset != '' else 1
    photos_required = input("Minimum photos to save (enter=1): ")
    photos_required = int(photos_required) if photos_required != '' else 0
    print(cs.END)

    User_Agent = UserAgent().random

    asyncio.run(main())
