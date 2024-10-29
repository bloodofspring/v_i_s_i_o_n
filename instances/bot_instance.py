"""Инициализация бота"""
from os import environ
from typing import Final

from dotenv import load_dotenv
from pyrogram import Client
from telebot import TeleBot

load_dotenv()

pyrogram_client: Final[Client] = Client(
    environ['name'],
    api_id=environ["api_id"], api_hash=environ['api_hash'],
    bot_token=environ['bot_token']
)

# telebot_client: Final[TeleBot] = TeleBot(token=environ['bot_token'])
