from pyrogram import filters
from pyrogram.types import Message

from config import ALLOWED_CHANS_ID


def is_allowed_channel(_, __, request: Message):
    return request and request.sender_chat and request.sender_chat.id in ALLOWED_CHANS_ID


is_allowed_channel_filter = filters.create(is_allowed_channel)
