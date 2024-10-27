"""Инициализация яндекс диск API"""
from os import environ
from typing import Final
import yadisk

from dotenv import load_dotenv

load_dotenv()

YADISK: Final[yadisk.YaDisk] = yadisk.YaDisk(token=environ["yadisk_token"])

# print(YADISK.check_token())
