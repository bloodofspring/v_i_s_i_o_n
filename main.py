import os
from datetime import datetime, timedelta
from random import randint

from colorama import Fore, init
from pyrogram import filters, Client
from pyrogram.handlers import MessageHandler
from pyrogram.handlers.handler import Handler
from pyrogram.types import Message, CallbackQuery

from bot_instance import pyrogram_client, telebot_client
from config import OWNER_ID
from database.create import create_tables
from database.models import Photos

PROGRAM_STARTED: datetime = datetime.now()


class LogCreator:
    bot_started: str = Fore.LIGHTYELLOW_EX + "[!] Клиент пробужден! Ожидание ответа от пользователя..."
    response_got: str= Fore.LIGHTYELLOW_EX + "[#] Ответ от пользователя получен! Сохранение..."
    file_saved: str = Fore.LIGHTYELLOW_EX + "[#] Ответ от пользователя сохранен! Выключение..."
    bot_stopped: str = Fore.LIGHTWHITE_EX + ("[!] Клиент отправлен в режим сна."
                                        "\nВремя исполнения программы: {}"
                                        "\nСледующее пробуждение: {}")

    def info(self, log_name_or_text: str, *args):
        if not hasattr(self, log_name_or_text):
            print(log_name_or_text.format(*args))
            return

        print(getattr(self, log_name_or_text).format(*args))


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
    FILTER = filters.photo

    async def func(self, _, request: Message):
        now = datetime.now()
        username = request.from_user.username

        LogCreator().info(LogCreator.response_got)

        if not os.path.exists(f"@{username}_photos"):
            os.mkdir(f"@{username}_photos")

        file_name = (f"@{username}/Photo("
                     f"date={now.day}_{now.month}_{now.year}, "
                     f"time={now.hour}_{now.minute}_{now.second}"
                     f")")
        await request.download(file_name=file_name)
        Photos.create(file_name=file_name)
        await request.reply_text(text="Сохранение произведено успешно!")

        LogCreator().info(LogCreator.file_saved)

        self.stop_client()

    @staticmethod
    def set_new_awake_time() -> datetime:
        now = datetime.now()
        until_4_44 = 1724 - (now.minute + now.hour * 60)
        send_time = now + timedelta(minutes=randint(until_4_44, until_4_44 + 1440))

        return send_time

    def stop_client(self):
        exit(LogCreator.bot_stopped.format(datetime.now() - PROGRAM_STARTED, self.set_new_awake_time()))


def send_notification_to_mazutta() -> None:
    telebot_client.send_message(chat_id=OWNER_ID, text="Take a photo!")


def add_handlers() -> None:
    for handler in [GetUserResponse]:
        pyrogram_client.add_handler(handler().de_pyrogram_handler)


def run_bot() -> None:
    init(autoreset=True)
    send_notification_to_mazutta()

    add_handlers()
    create_tables()

    try:
        LogCreator().info(LogCreator.bot_started)
        pyrogram_client.run()
    except Exception as e:
        print(f"Невозможно запустить клиента! {e}")


if __name__ == "__main__":
    run_bot()
