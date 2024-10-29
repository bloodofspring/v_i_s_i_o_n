import asyncio
import os.path
import shutil
from datetime import datetime, timedelta
from os import stat
from random import randint

from colorama import Fore, init
from pyrogram import filters, Client
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from config import OWNER_ID, YANDEX_DISK_FOLDER_NAME
from database.create import create_tables
from database.models import SavedFileNames
from instances import yandex_disk_client, pyrogram_client, telebot_client

PROGRAM_STARTED: datetime = datetime.now()


def is_owner(_, __, request: Message):
    return request and request.from_user and request.from_user.id == OWNER_ID


is_owner_filter = filters.create(is_owner)


class GetUserResponse:
    def __init__(self):
        super().__init__()
        self.is_waiting = False

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
        print(Fore.LIGHTYELLOW_EX + "[#] " + Fore.LIGHTGREEN_EX + "Получен файл от пользователя! Сохранение...")

        _, extension, size = await self.save_f_and_upload_to_ya_cloud(
            request=request, extension=".jpeg" if request.photo else ".txt"
        )
        await request.reply_text(text="Сохранение произведено успешно!")
        print(Fore.LIGHTYELLOW_EX + "[#] " + Fore.LIGHTGREEN_EX +
              f"Файл от пользователя сохранен! size={size} B, type={extension}"
              )

        if not self.is_waiting:
            await self.reschedule_notification_sending_time()

    @property
    def new_awake_time(self) -> int:
        start_time = 4 * 60 + 44  # 4:44
        add_time = 18 * 60  # +18 hrs

        now = datetime.now()
        until_ = (1440 + start_time) - (now.minute + now.hour * 60)

        return randint(until_, until_ + add_time) * 60

    async def reschedule_notification_sending_time(self):
        self.is_waiting = True
        awake_t = self.new_awake_time
        print(
            Fore.LIGHTWHITE_EX + "[!] " +
            Fore.LIGHTGREEN_EX + "Назначено новое время отправки сообщения!"
                                 "\nВремя ожидания ответа: {}"
                                 "\nСледующее сообщение: {}".format(
                datetime.now() - PROGRAM_STARTED, datetime.now() + timedelta(seconds=awake_t)
            )
        )
        await asyncio.sleep(awake_t)
        send_notification_to_mazutta()

    @property
    def de_pyrogram_handler(self):
        return MessageHandler(
            self.save_message,
            filters=(filters.photo | filters.text | filters.media_group) & (filters.private | filters.channel) & is_owner_filter
        )


def send_notification_to_mazutta() -> None:
    telebot_client.send_message(chat_id=OWNER_ID, text="Take a photo!")
    print(Fore.LIGHTWHITE_EX + "[!] " + Fore.LIGHTGREEN_EX + "Сообщение пользователю отправлено!")


def add_handlers() -> None:
    for handler in [GetUserResponse]:
        pyrogram_client.add_handler(handler().de_pyrogram_handler)


def run_bot() -> None:
    init(autoreset=True)
    send_notification_to_mazutta()

    add_handlers()
    create_tables()

    try:
        pyrogram_client.run()
    except Exception as e:
        print(f"Невозможно запустить клиента! {e}")


if __name__ == "__main__":
    run_bot()
