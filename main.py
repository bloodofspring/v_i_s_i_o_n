import os.path
import shutil
from datetime import datetime
from os import stat

from colorama import Fore, init
from pyrogram import filters, Client
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from config import YANDEX_DISK_FOLDER_NAME
from database.create import create_tables
from database.models import SavedFileNames
from filters import is_owner_filter, is_allowed_channel_filter
from instances import yandex_disk_client, pyrogram_client


class GetUserResponse:
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_file_naming_data(extension: str):
        now = datetime.now()
        path = YANDEX_DISK_FOLDER_NAME

        if not yandex_disk_client.exists(path):
            yandex_disk_client.mkdir(path)

        file_name = f"File(date={now.day}_{now.month}_{now.year}, time={now.hour}_{now.minute}_{now.second})" + extension
        return file_name, path

    async def save_f_and_upload_to_ya_cloud(self, request: Message, extension: str):
        file_name, path = self.get_file_naming_data(extension=extension)

        if request.photo is not None:
            await request.download(file_name=file_name)
        else:  # text case
            if not os.path.exists("downloads"): os.mkdir("downloads")
            with open(f"downloads/{file_name}", "w") as f:
                f.write(request.text)

        yandex_disk_client.upload(f"downloads/{file_name}", f"{path}/{file_name}")
        SavedFileNames.create(file_name=file_name)  # create log about saved file

        file_size = stat(f"downloads/{file_name}")

        try:
            shutil.rmtree("downloads")
        except:
            pass

        return file_name, extension, file_size.st_size

    async def save_message(self, _: Client, request: Message):
        print(Fore.LIGHTYELLOW_EX + f"[{datetime.now()}][#]>>-||--> " + Fore.LIGHTGREEN_EX + f"Получен файл от пользователя! [type={request.chat.type}] -- Сохранение...")

        _, extension, size = await self.save_f_and_upload_to_ya_cloud(
            request=request, extension=".jpeg" if request.photo else ".txt"
        )
        if await filters.private_filter(None, None, m=request):
            await request.reply_text(text="Сохранение произведено успешно!")
        print(Fore.LIGHTYELLOW_EX + f"[{datetime.now()}][#]>>-||--> " + Fore.LIGHTGREEN_EX +
              f"Файл от пользователя сохранен! [size={size}B, type={extension}]"
              )

    @property
    def de_pyrogram_handler(self):
        return MessageHandler(
            self.save_message,
            filters=(
                filters.photo | filters.text | filters.media_group
            ) & (
                filters.private & is_owner_filter | filters.channel & is_allowed_channel_filter
            )
        )


def add_handlers() -> None:
    for handler in [GetUserResponse]:
        pyrogram_client.add_handler(handler().de_pyrogram_handler)


def run_bot() -> None:
    init(autoreset=True)
    add_handlers()
    create_tables()

    try:
        pyrogram_client.run()
    except Exception as e:
        print(f"Невозможно запустить клиента! {e}")


if __name__ == "__main__":
    run_bot()
