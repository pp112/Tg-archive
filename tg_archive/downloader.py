import os

from pyrogram import Client
from dotenv import load_dotenv

from tg_archive.utils import console
from tg_archive.utils import get_progress, complete_msg, safe_filename, get_media_filename

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

PROXY = {
    "scheme": os.getenv("PROXY_SCHEME"),
    "hostname": os.getenv("PROXY_HOST"),
    "port": int(os.getenv("PROXY_PORT")),
    "username": os.getenv("PROXY_USER") or None,
    "password": os.getenv("PROXY_PASS") or None,
}

DIALOG_TARGET = os.getenv("DIALOG_TARGET")
FROM_COMMENTS = os.getenv("FROM_COMMENTS").lower() == "true"


async def get_target_chat_id(app, dialog_name: str):
    async for dialog in app.get_dialogs():
        chat_name = dialog.chat.first_name or dialog.chat.title
        if chat_name == dialog_name:
            chat_id_target = dialog.chat.id
            return chat_id_target
    raise ValueError("Чат не найден")

async def download_media_chat(app, chat_id):
    chat_name = await app.get_chat(chat_id).title

    total = await app.get_chat_history_count(chat_id)
    progress = get_progress()

    with progress:
        task = progress.add_task("Скачиваем медиафайлы", total=total)

        i = 0
        async for message in app.get_chat_history(chat_id):
            i += 1
            file_name = get_media_filename(message, i)
            if file_name is None:
                continue

            await app.download_media(message, file_name=f"./downloads/{chat_name}/{i}.jpg")
            
            progress.advance(task)

async def download_media_comments(app, chat_id, messages_id: list):
    progress = get_progress()

    with progress:
        task1 = progress.add_task("", total=len(messages_id))
        task2 = progress.add_task("")
        total_replies = None

        for message_id in messages_id:
            msg = await app.get_messages(chat_id, message_id)
            date = msg.date.strftime("%d.%m.%y")
            message_text = safe_filename((await app.get_messages(chat_id, message_id)).text)
            folder_name = f"{message_text}_{date}"
            
            total_replies = await app.get_discussion_replies_count(chat_id, message_id)
            progress.update(task1, advance=1, description=message_text)
            
            i = 0
            async for reply in app.get_discussion_replies(chat_id, message_id):
                i += 1
                file_name = get_media_filename(reply, i)
                if file_name is None:
                    continue
                
                file_path = f"./downloads/{folder_name}/{file_name}"
            
                progress.update(task2, advance=1, description=file_name, total=total_replies)

                await app.download_media(reply, file_name=file_path)

            progress.reset(task2)

async def process_comments(app, chat_id):
    with console.status(f'[green]Собираем сообщения...[/green]'):
        messages_id = [message.id async for message in app.get_chat_history(chat_id)]
    
    complete_msg("Сообщения собраны")
    await download_media_comments(app, chat_id, messages_id)


async def start_downloader():
    app = Client("account", api_id=API_ID, api_hash=API_HASH, proxy=PROXY) 

    async with app:
        with console.status(f'[green]Ищем чат:[/green] [cyan]{DIALOG_TARGET}[/cyan]'):
            chat_id = await get_target_chat_id(app, DIALOG_TARGET)
        complete_msg("Чат найден")

        if FROM_COMMENTS:
            await process_comments(app, chat_id)
        else:
            await download_media_chat(app, chat_id)

        print()
        complete_msg("Все медиафайлы успешно скачаны!")

        input("\nНажмите Enter для выхода...")
