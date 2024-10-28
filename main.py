import asyncio
import shutil
from datetime import datetime, timedelta
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


class GetUserResponse:
    def __init__(self):
        super().__init__()
        self.is_waiting = False

    @property
    def file_naming_data(self):
        now = datetime.now()
        path = YANDEX_DISK_FOLDER_NAME

        if not yandex_disk_client.exists(path):
            yandex_disk_client.mkdir(path)

        file_name = f"File(date={now.day}_{now.month}_{now.year}, time={now.hour}_{now.minute}_{now.second}).jpeg"
        return file_name, path

    async def save_f_and_upload_to_ya_cloud(self, request: Message):
        file_name, path = self.file_naming_data
        await request.download(file_name=file_name)
        yandex_disk_client.upload(f"downloads/{file_name}", f"{path}/{file_name}")
        SavedFileNames.create(file_name=file_name)  # create log about saved file

        try:
            shutil.rmtree("downloads")
        except Exception as e:
            print(f"cannot delete folder 'downloads'\nError type: {type(e)}\nError text: {str(e)}")

    async def save_user_photo(self, _: Client, request: Message):
        print(Fore.LIGHTGREEN_EX + "[#] получено фото от пользователя! Сохранение...")

        await self.save_f_and_upload_to_ya_cloud(request=request)
        await request.reply_text(text="Сохранение произведено успешно!")
        print(Fore.LIGHTGREEN_EX + "[#] Ответ от пользователя сохранен!")

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
        return MessageHandler(self.save_user_photo, filters=filters.photo)


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
