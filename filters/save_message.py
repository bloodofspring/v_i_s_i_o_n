from pyrogram import filters

from filters import is_owner_filter, is_allowed_channel_filter

save_message_filter = ((filters.photo | filters.text | filters.media_group) &
                       (filters.private & is_owner_filter | filters.channel & is_allowed_channel_filter))
