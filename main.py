from colorama import init
from pyrogram import Client
from pyrogram.types import Message

from database.create import create_tables
from file_downloader.FileDownloader import TxtDownloader, PicDownloader
from filters import save_message_filter
from instances import pyrogram_client


@pyrogram_client.on_message(filters=save_message_filter)
async def save_message(_: Client, request: Message):
    if request.photo is not None:
        await PicDownloader(pyrogram_request=request).save_message()
    elif request.text:
        await TxtDownloader(pyrogram_request=request).save_message()


def run_bot() -> None:
    init(autoreset=True)
    create_tables()
    pyrogram_client.run()


if __name__ == "__main__":
    run_bot()
