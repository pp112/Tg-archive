import re

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from pyrogram.enums import MessageMediaType

console = Console()

ALLOWED_MEDIA = {MessageMediaType.PHOTO, MessageMediaType.VIDEO}


def get_progress():
    return Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(complete_style="green", finished_style="bright_green"),
        TextColumn("[bright_green]{task.completed}[/bright_green]/[yellow]{task.total}[/yellow]"),
        TextColumn("[bright_green]{task.percentage:>3.0f}%[/bright_green]")
    )

def complete_msg(msg):
    console.print(f"[bold green]✔ {msg}[/bold green]")

def safe_path_text(text: str) -> str:
    """Убирает недопустимые символы для путей"""
    return re.sub(r'[^\w\-_\. ]', '_', text).strip("_")

def get_media_filename(message, name):
    if message.media not in ALLOWED_MEDIA:
        return None

    if message.media == MessageMediaType.PHOTO:
        ext = "jpg"
    elif message.media == MessageMediaType.VIDEO:
        ext = "mp4"

    return f"{name}.{ext}"