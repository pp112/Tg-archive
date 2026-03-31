import os
import asyncio

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from rich.progress import Progress, TaskID
from dotenv import load_dotenv

from tg_archive.utils import console
from tg_archive.utils import get_progress, complete_msg, safe_path_text, get_media_filename

load_dotenv()

class Downloader:
    def __init__(self):
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")

        self.proxy = {
            "scheme": os.getenv("PROXY_SCHEME"),
            "hostname": os.getenv("PROXY_HOST"),
            "port": int(os.getenv("PROXY_PORT")),
            "username": os.getenv("PROXY_USER") or None,
            "password": os.getenv("PROXY_PASS") or None,
        }

        self.dialog_target = os.getenv("DIALOG_TARGET")
        self.from_comments = os.getenv("FROM_COMMENTS").lower() == "true"

        self.app = Client("account", api_id=self.api_id, api_hash=self.api_hash, proxy=self.proxy)

        self.sem = asyncio.Semaphore(5)

    async def get_chat_id(self):
        """Поиск чата"""
        async for dialog in self.app.get_dialogs():
            name = dialog.chat.first_name or dialog.chat.title
            if name == self.dialog_target:
                return dialog.chat.id
        raise ValueError("Чат не найден")

    async def safe_download(
        self, 
        message: Message, 
        path: str, 
        progress: Progress, 
        task: TaskID
    ):
        """Безопасная загрузка, с обработкой Floodwait"""
        async with self.sem:
            while True:
                try:
                    await self.app.download_media(message, file_name=path)

                    progress.update(task, advance=1)
                    return
                
                except FloodWait as e:
                    console.print(f"[yellow]FloodWait: ждём {e.value} сек[/yellow]")
                    await asyncio.sleep(e.value)

    async def download_media_chat(self, chat_id):
        """Скачивание медиафайлов из обычного чата"""
        chat = await self.app.get_chat(chat_id)
        chat_name = safe_path_text(chat.title)

        media_messages = []
        i = 0

        async for message in self.app.get_chat_history(chat_id):
            i += 1
            file_name = get_media_filename(message, i)
            if file_name:
                media_messages.append((message, file_name))

        total_files = len(media_messages)

        progress = get_progress()

        with progress:
            task = progress.add_task("Скачиваем медиафайлы", total=total_files)

            tasks = []

            for message, file_name in media_messages:
                path = f"./downloads/{chat_name}/{file_name}"

                tasks.append(self.safe_download(message, path, progress, task))

            await asyncio.gather(*tasks)

    async def download_media_comments(self, chat_id):
        """Скачивание медиафайлов из комментариев"""
        messages_id = [message.id async for message in self.app.get_chat_history(chat_id)]
        
        progress = get_progress()

        with progress:
            task_main = progress.add_task("", total=len(messages_id))

            # Проходим по постам
            for msg_id in messages_id:
                msg = await self.app.get_messages(chat_id, msg_id)

                progress.update(task_main, advance=1, description=msg.text)

                text = safe_path_text(msg.text)
                date = msg.date.strftime("%d.%m.%y")
                folder = f"{text}_{date}"
                
                media_messages = []
                i = 0
                
                # Собираем медифайлы из поста
                async for reply in self.app.get_discussion_replies(chat_id, msg_id):
                    i += 1

                    file_name = get_media_filename(reply, i)
                    if file_name:
                        path = f"./downloads/{folder}/{file_name}"
                        media_messages.append((reply, path))                    

                total_files = len(media_messages)

                # Скачиваем медиафайлы
                if total_files > 0:
                    task_files = progress.add_task("Скачиваем медиафайлы", total=total_files)
                    
                    tasks = [
                        self.safe_download(reply, path, progress, task_files)
                        for reply, path in media_messages
                    ]

                    await asyncio.gather(*tasks)

                    progress.remove_task(task_files)

    async def run(self):
        """Запуск"""
        async with self.app:
            with console.status(f'[green]Ищем чат:[/green] [cyan]{self.dialog_target}[/cyan]'):
                chat_id = await self.get_chat_id()

            complete_msg("Чат найден")

            if self.from_comments:
                await self.download_media_comments(chat_id)
            else:
                await self.download_media_chat(chat_id)

            print()
            complete_msg("Все медиафайлы успешно скачаны!")

            await asyncio.to_thread(input, "\nНажмите Enter для выхода...")
