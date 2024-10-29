from pyrogram import filters
from pyrogram.types import Message

from config import OWNER_ID


def is_owner(_, __, request: Message):
    return request and request.from_user and request.from_user.id == OWNER_ID


is_owner_filter = filters.create(is_owner)
