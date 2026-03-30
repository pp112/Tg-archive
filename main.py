import asyncio
from tg_archive.downloader import start_downloader

def main():
    asyncio.run(start_downloader())

if __name__ == "__main__":
    main()