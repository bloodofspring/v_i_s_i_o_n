import os
import shutil
from datetime import datetime, timedelta

from colorama import Fore
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

        file_name = f"File(date={now.day}_{now.month}_{now.year}, time={now.hour}_{now.minute}_{now.second}_{now.microsecond})"

        return file_name, path

    @staticmethod
    def rm_downloads_dir():
        try:
            shutil.rmtree("downloads")
        except (Exception,):
            pass

    @staticmethod
    async def update_uploaded_file(full_way, filename_instance: SavedFileNames):
        name_on_yadisk = YANDEX_DISK_FOLDER_NAME + "/" + filename_instance.file_name
        try:
            yandex_disk_client.download(
                name_on_yadisk,
                f"downloads/{filename_instance.file_name}"
            )
        except (Exception,) as e:
            print(e, name_on_yadisk)
            return None

        f_size = str(os.path.getsize(f"downloads/{filename_instance.file_name}"))

        with open(f"downloads/{filename_instance.file_name}", "a") as af:
            af.write("\n")

            with open(full_way, "r") as rf:
                af.writelines(rf.readlines())

        yandex_disk_client.remove(name_on_yadisk)
        yandex_disk_client.upload(f"downloads/{filename_instance.file_name}", name_on_yadisk)

        f_size += f"+{str(os.path.getsize(full_way))}"

        return f_size

    async def upload_to_ya_cloud(self):
        name, full_way, save_path, f_size = await self.file
        recent_messages = SavedFileNames.select().where(SavedFileNames.created_at > (datetime.now() - timedelta(seconds=5))).order_by(SavedFileNames.created_at.desc()).execute()

        if recent_messages:
            f_size = await self.update_uploaded_file(
                full_way=full_way,
                filename_instance=recent_messages[0]
            )

            if f_size:
                return name, f_size

        yandex_disk_client.upload(full_way, save_path)
        SavedFileNames.create(file_name=name)

        self.rm_downloads_dir()

        return name, f_size

    async def save_message(self):
        print((
                Fore.YELLOW + f"[{datetime.now()}][#]>>-||--> " +
                Fore.GREEN + f"Получен файл от пользователя! [type={self.pyrogram_request.chat.type}] -- Сохранение..."
        ))

        _, f_size = await self.upload_to_ya_cloud()
        # if self.pyrogram_request.chat.type.PRIVATE:
        #     await self.pyrogram_request.delete()

        print((
                Fore.YELLOW + f"[{datetime.now()}][#]>>-||--> " +
                Fore.GREEN + f"Файл от пользователя сохранен! [size={f_size}B, type={self.extension}]"
        ))


class TxtDownloader(FileDownloader):
    extension = ".txt"

    @property
    async def file(self) -> tuple[str, str, str, int]:
        file_name, path = self.file_naming_data
        file_name += self.extension

        if not os.path.exists("downloads"):
            os.mkdir("downloads")

        with open(f"downloads/{file_name}", "w") as f:
            f.write(self.pyrogram_request.text)

        file_size = os.stat(f"downloads/{file_name}").st_size

        return file_name, f"downloads/{file_name}", f"{path}/{file_name}", file_size


class PicDownloader(FileDownloader):
    extension = ".jpeg"

    @property
    async def file(self) -> tuple[str, str, str, int]:
        file_name, path = self.file_naming_data
        file_name += self.extension

        await self.pyrogram_request.download(file_name=file_name)
        file_size = os.stat(f"downloads/{file_name}").st_size

        return file_name, f"downloads/{file_name}", f"{path}/{file_name}", file_size
