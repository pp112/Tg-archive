import os
import tgcrypto
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

app = Client("account", api_id=API_ID, api_hash=API_HASH, proxy=PROXY) 


def get_target_chat_id(dialog_name: str):
    for dialog in app.get_dialogs():
        chat_name = dialog.chat.first_name or dialog.chat.title
        if chat_name == dialog_name:
            chat_id_target = dialog.chat.id
            return chat_id_target
    else:
        raise ValueError("Чат не найден")

def download_media_chat(chat_id):
    chat_name = app.get_chat(chat_id).title

    messages = app.get_chat_history(chat_id)

    total = app.get_chat_history_count(chat_id)
    progress = get_progress()

    with progress:
        task = progress.add_task("Скачиваем медиафайлы", total=total)

        for i, message in enumerate(messages, start=1):
            file_name = get_media_filename(message, i)
            if file_name is None:
                continue

            app.download_media(message, file_name=f"./downloads/{chat_name}/{i}.jpg")
            
            progress.advance(task)

def download_media_comments(chat_id, messages_id: list):
    progress = get_progress()

    with progress:
        task1 = progress.add_task("", total=len(messages_id))
        task2 = progress.add_task("")
        total_replies = None

        for message_id in messages_id:
            message_text = safe_filename(app.get_messages(chat_id, message_id).text)
            date = app.get_messages(chat_id, message_id).date.strftime("%d.%m.%y")
            folder_name = f"{message_text}_{date}"
            
            replies = app.get_discussion_replies(chat_id, message_id)

            total_replies = app.get_discussion_replies_count(chat_id, message_id)
            progress.update(task1, advance=1, description=message_text)
            
            for i, reply in enumerate(replies, start=1):
                file_name = get_media_filename(reply, i)
                if file_name is None:
                    continue
                
                file_path = f"./downloads/{folder_name}/{file_name}"
            
                progress.update(task2, advance=1, description=file_name, total=total_replies)

                app.download_media(reply, file_name=file_path)
                
            progress.reset(task2)

def process_comments(chat_id):
    with console.status(f'[green]Собираем сообщения...[/green]'):
        messages_id = [message.id for message in app.get_chat_history(chat_id)]
    complete_msg("Сообщения собраны")
    download_media_comments(chat_id, messages_id)


def start_downloader():
    with app:
        with console.status(f'[green]Ищем чат:[/green] [cyan]{DIALOG_TARGET}[/cyan]'):
            chat_id = get_target_chat_id(DIALOG_TARGET)
        complete_msg("Чат найден")

        if FROM_COMMENTS:
            process_comments(chat_id)
        else:
            download_media_chat(chat_id)

        print()
        complete_msg("Все медиафайлы успешно скачаны!")

        input("\nНажмите Enter для выхода...")
