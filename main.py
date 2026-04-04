import asyncio
from tg_comments_archive.downloader import Downloader

def main():
    downloader = Downloader()
    asyncio.run(downloader.run())

if __name__ == "__main__":
    main()