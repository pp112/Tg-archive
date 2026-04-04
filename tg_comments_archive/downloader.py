import os
import asyncio

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatType
from rich.progress import Progress, TaskID
from dotenv import load_dotenv

from tg_comments_archive.utils import (
    get_progress, 
    complete_msg, 
    safe_path_text, 
    get_media_filename, 
    is_media_file, 
    console
)

load_dotenv()

class Downloader:
    def __init__(self):
        self.api_id = os.getenv("API_ID")
        self.api_hash = os.getenv("API_HASH")

        use_proxy = os.getenv("USE_PROXY").lower() == "true"
        
        if use_proxy:
            self.proxy = {
                "scheme": os.getenv("PROXY_SCHEME"),
                "hostname": os.getenv("PROXY_HOST"),
                "port": int(os.getenv("PROXY_PORT")),
                "username": os.getenv("PROXY_USER") or None,
                "password": os.getenv("PROXY_PASS") or None,
            }
        else:
            self.proxy = None

        self.dialog_target = os.getenv("DIALOG_TARGET")

        self.app = Client("account", api_id=self.api_id, api_hash=self.api_hash, proxy=self.proxy)

        self.sem = asyncio.Semaphore(5)

    async def get_chat_id(self):
        """Поиск чата"""
        async for dialog in self.app.get_dialogs():
            name = dialog.chat.first_name or dialog.chat.title
            if name == self.dialog_target:
                if dialog.chat.type == ChatType.PRIVATE:
                    raise ValueError(f"Чат {name} — личный, комментарии недоступны")
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

    async def download_media_list(
        self,
        messages: list[Message],
        folder: str,
        progress: Progress,
        task: TaskID
    ):
        """Скачивает медиафайлы из списка сообщений"""
        tasks = []

        for i, message in enumerate(messages, 1):
            file_name = get_media_filename(message, i)
            path = f"./downloads/{folder}/{file_name}"
            if os.path.isfile(path):
                progress.update(task, advance=1)
                continue

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

                progress.update(task_main, advance=1, description=msg.text[:50])

                text = safe_path_text(msg.text)
                date = msg.date.strftime("%d.%m.%y")
                folder = f"{text}_{date}"
                
                media_messages = []
                
                # Собираем медифайлы из поста
                async for reply in self.app.get_discussion_replies(chat_id, msg_id):
                    if is_media_file(reply):
                        media_messages.append(reply)

                total_files = len(media_messages)

                # Скачиваем медиафайлы
                if total_files > 0:
                    task_files = progress.add_task("Скачиваем медиафайлы", total=total_files)
                    
                    await self.download_media_list(media_messages, folder, progress, task_files)

                    progress.remove_task(task_files)

    async def run(self):
        """Запуск"""
        async with self.app:
            with console.status(f'[green]Ищем чат:[/green] [cyan]{self.dialog_target}[/cyan]'):
                chat_id = await self.get_chat_id()

            complete_msg("Чат найден")

            await self.download_media_comments(chat_id)

        print()
        complete_msg("Все медиафайлы успешно скачаны!")

        await asyncio.to_thread(input, "\nНажмите Enter для выхода...")
