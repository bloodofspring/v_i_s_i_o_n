import os
import shutil
from datetime import datetime

from colorama import Fore
from pyrogram import filters
from pyrogram.types import Message

from config import YANDEX_DISK_FOLDER_NAME
from database.models import SavedFileNames
from instances import yandex_disk_client


class FileDownloader:
    extension: str = ""

    def __init__(self, pyrogram_request: Message):
        self.pyrogram_request: Message = pyrogram_request

    @property
    async def file(self) -> tuple[str, str, str, int]:
        raise NotImplementedError

    @property
    def file_naming_data(self):
        now = datetime.now()
        path = YANDEX_DISK_FOLDER_NAME

        if not yandex_disk_client.exists(path):
            yandex_disk_client.mkdir(path)

        file_name = f"File(date={now.day}_{now.month}_{now.year}, time={now.hour}_{now.minute}_{now.second})"

        return file_name, path

    @staticmethod
    def rm_downloads_dir():
        try:
            shutil.rmtree("downloads")
        except:
            pass

    async def upload_to_ya_cloud(self):
        name, full_way, save_path, f_size = self.file
        yandex_disk_client.upload(full_way, save_path)
        SavedFileNames.create(file_name=name)  # create log about saved file

        self.rm_downloads_dir()

        return name, f_size

    async def save_message(self, _, request: Message):
        print((
                Fore.LIGHTYELLOW_EX + f"[{datetime.now()}][#]>>-||--> " +
                Fore.LIGHTGREEN_EX + f"Получен файл от пользователя! [type={request.chat.type}] -- Сохранение..."
        ))

        _, f_size = self.upload_to_ya_cloud()

        if await filters.private_filter(None, None, m=request):
            await request.reply_text(text="Сохранение произведено успешно!")

        print((
                Fore.LIGHTYELLOW_EX + f"[{datetime.now()}][#]>>-||--> " +
                Fore.LIGHTGREEN_EX + f"Файл от пользователя сохранен! [size={f_size}B, type={self.extension}]"
        ))


class TxtDownloader(FileDownloader):
    extension = ".txt"

    @property
    async def file(self) -> tuple[str, str, str, int]:
        file_name, path = self.file_naming_data

        if not os.path.exists("downloads"):
            os.mkdir("downloads")

        with open(f"downloads/{file_name}.txt", "w") as f:
            f.write(self.pyrogram_request.text)

        file_size = os.stat(f"downloads/{file_name}.txt").st_size

        return file_name, f"downloads/{file_name}.txt", path, file_size


class PicDownloader(FileDownloader):
    extension = ".jpeg"

    @property
    async def file(self) -> tuple[str, str, str, int]:
        file_name, path = self.file_naming_data

        await self.pyrogram_request.download(file_name=file_name)
        file_size = os.stat(f"downloads/{file_name}.jpeg").st_size

        return file_name, f"downloads/{file_name}.jpeg", path, file_size
