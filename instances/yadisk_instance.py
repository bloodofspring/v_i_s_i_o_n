"""Инициализация яндекс диск API"""
from os import environ
from typing import Final
import yadisk

from dotenv import load_dotenv

load_dotenv()

yandex_disk_client: Final[yadisk.YaDisk] = yadisk.YaDisk(token=environ["yadisk_token"])

# get token ->
# https://oauth.yandex.ru/authorize?response_type=token&client_id=<app_id>
# print(YADISK.check_token())
