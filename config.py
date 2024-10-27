from os import environ
from typing import Final

from dotenv import load_dotenv

load_dotenv()

OWNER_ID: Final[int] = int(environ["owner_id"])
YANDEX_DISK_FOLDER_NAME: Final[str] = environ["yandex_disk_folder_name"]
