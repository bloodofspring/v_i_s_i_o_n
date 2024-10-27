import asyncio
import shutil
from datetime import datetime, timedelta
from random import randint

from colorama import Fore, init
from pyrogram import filters, Client
from pyrogram.handlers import MessageHandler
from pyrogram.handlers.handler import Handler
from pyrogram.types import Message, CallbackQuery

from config import OWNER_ID, YANDEX_DISK_FOLDER_NAME
from database.create import create_tables
from database.models import Photos
from instances import yandex_disk_client, pyrogram_client, telebot_client

PROGRAM_STARTED: datetime = datetime.now()


class BaseHandler:
    """Базовый обработчик-исполнитель"""
    __name__ = ""
    HANDLER: Handler = MessageHandler
    FILTER: filters.Filter | None = None

    def __init__(self):
        self.client: Client | None = None
        self.request: Message | CallbackQuery | None = None

    async def func(self, client_: Client, request: Message | CallbackQuery):
        raise NotImplementedError

    @property
    def de_pyrogram_handler(self):
        return self.HANDLER(self.func, self.FILTER)


class GetUserResponse(BaseHandler):
    def __init__(self):
        super().__init__()
        self.is_waiting = False

    FILTER = filters.photo

    async def func(self, _, request: Message):
        print(Fore.LIGHTYELLOW_EX + "[#] получено фото от пользователя! Сохранение...")

        now = datetime.now()
        username = request.from_user.username

        path = YANDEX_DISK_FOLDER_NAME
        if not yandex_disk_client.exists(path):
            yandex_disk_client.mkdir(path)

        file_name = f"@{username}(date={now.day}_{now.month}_{now.year}, time={now.hour}_{now.minute}_{now.second}).jpeg"
        await request.download(file_name=file_name)
        yandex_disk_client.upload(f"downloads/{file_name}", f"{path}/{file_name}")
        Photos.create(file_name=file_name)

        await request.reply_text(text="Сохранение произведено успешно!")
        print(Fore.LIGHTGREEN_EX + "[#] Ответ от пользователя сохранен!")

        try:
            shutil.rmtree("downloads")
        except Exception as e:
            print(f"cannot delete folder 'downloads'\nError type: {type(e)}\nError text: {str(e)}")

        if not self.is_waiting:
            await self.stop_client()

    @staticmethod
    def set_new_awake_time() -> int:
        now = datetime.now()
        until_4_44 = 1724 - (now.minute + now.hour * 60)

        return randint(until_4_44, until_4_44 + 1440) * 60

    async def stop_client(self):
        self.is_waiting = True
        awake_t = self.set_new_awake_time()
        print(
            Fore.LIGHTYELLOW_EX +
            "[#] Назначено новое время отправки сообщения!"
            "\nВремя ожидания ответа: {}"
            "\nСледующее сообщение: {}".format(
                datetime.now() - PROGRAM_STARTED, datetime.now() + timedelta(seconds=awake_t)
            )
        )
        await asyncio.sleep(awake_t)
        send_notification_to_mazutta()


def send_notification_to_mazutta() -> None:
    telebot_client.send_message(chat_id=OWNER_ID, text="Take a photo!")
    print(Fore.LIGHTYELLOW_EX + "[!] Сообщение пользователю отправлено!")


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
