import re

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from pyrogram.enums import MessageMediaType
from pyrogram.types import Message

console = Console()


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
    if message.media == MessageMediaType.PHOTO:
        return f"{name}.jpg"
    elif message.media == MessageMediaType.VIDEO:
        return f"{name}.mp4"
    else:
        return None
    