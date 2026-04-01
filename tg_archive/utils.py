import re

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message

console = Console()

MEDIA_EXTENSIONS = {
    MessageMediaType.PHOTO: ".jpg",
    MessageMediaType.VIDEO: ".mp4",
}

def get_progress():
    return Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[bright_green]{task.completed}[/bright_green]/[yellow]{task.total}[/yellow]"),
        TextColumn("[bright_green]{task.percentage:>3.0f}%[/bright_green]")
    )

def complete_msg(msg: str):
    console.print(f"[bold green]✔ {msg}[/bold green]")

def safe_path_text(text: str) -> str:
    """Убирает недопустимые символы для путей"""
    return re.sub(r'[\\/:*?"<>|]', '_', text).strip()

def get_media_filename(message: Message, name):
    ext = MEDIA_EXTENSIONS.get(message.media)
    return f"{name}{ext}" if ext else None

def is_media_file(message: Message):
    return message.media in MEDIA_EXTENSIONS