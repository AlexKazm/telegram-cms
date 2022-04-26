"""This is an improved version of get_chat_members.py
Since Telegram will return at most 10.000 members for a single query, this script
repeats the search using numbers ("0" to "9") and all the available ascii letters ("a" to "z").
This can be further improved by also searching for non-ascii characters (e.g.: Japanese script),
as some user names may not contain ascii letters at all.
"""

import time
import json
import random
import asyncio
from string import ascii_lowercase

from pyrogram import Client, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from pyrogram import Client, Filters, Message as PMessage, User as PUser

from services.core.utils import generator
from services.telegram.models import TelegramUser


#
#
async def parse_chat_members(session: Client, chat_id: str, delay: int):
    queries = [""] + [str(i) for i in range(10)] + list(ascii_lowercase)
    limit = 200
    members = {}

    for q in queries:
        print('Searching for "{}"'.format(q))
        offset = 0  # For each query, offset restarts from 0

        while True:
            print(f"offset: {offset}")
            try:
                chunk = await session.get_chat_members(chat_id, offset, query=q)
                await asyncio.sleep(delay)

            except FloodWait as e:  # Very large chats could trigger FloodWait
                print("Flood wait: {} seconds".format(e.x))
                await asyncio.sleep(e.x)  # When it happens, wait X seconds and try again
                continue

            if not chunk:
                print('Done searching for "{}"'.format(q))
                print()
                break  # No more members left

            async for member in generator(random.sample(chunk, len(chunk))):
                user: PUser = member['user']
                json_data: dict = json.loads(str(user))

                if user['username'] and user['is_bot'] is False:
                    telegram_user = await TelegramUser.create(
                        user_id=user['id'], data=dict(json_data)
                    )

                    print(f"[{time.ctime()}]: Created user model {telegram_user}")

            members.update({i.user.id: i for i in chunk})
            offset += len(chunk)

            print("Total members: {}".format(len(members)))

    print("Grand total: {}".format(len(members)))
    del members

# Now the "members" list contains all the members of the target chat

# +44 7308 370209
# client = Client(
#     session_name='DanWashington', api_id=1548046, api_hash="86fd19337fbdafe5d375d66830cd5953", workdir="sessions",
#     app_version='Telegram macOS 7.0 (204345) STABLE', device_model='MacBook Pro, macOS 10.12.6',
#     system_version='Darwin 16.7.0',lang_code='en'
#     )

# +44 7366 202498 # App title= OSXDefaultNode4
# client = Client(
#     session_name='Scorp', api_id=1699233, api_hash="6142bd9b9695935143386e14b771aed8", workdir="sessions",
#     app_version='Telegram macOS 7.0 (204345) STABLE', device_model='MacBook Pro, macOS 10.12.6',
#     system_version='Darwin 16.7.0',lang_code='en'
#     )

# +44 7723 486513 # App title= OSXDefaultNode4
# client = Client(
#     session_name='Crystopher',
#     api_id=1608399,
#     api_hash="93aedb282ae2b7c009aab039560f906d",
#     workdir="sessions",
#     app_version='Telegram macOS 7.0 (204345) STABLE',
#     device_model='MacBook Pro, macOS 10.12.6',
#     system_version='Darwin 16.7.0',
#     lang_code='en'
#     )

# +44 7735 608996 # App title= OSXDefaultNode4
# client = Client(
#     session_name='JohnBelsh',
#     api_id=1557702,
#     api_hash="37a06f9cda1531032f0278bdc7a15457",
#     workdir="sessions",
#     app_version='Telegram macOS 7.0 (204345) STABLE',
#     device_model='MacBook Pro, macOS 10.12.6',
#     system_version='Darwin 16.7.0',
#     lang_code='en'
#     )

# +44 7735 608996 # App title= OSXDefaultNode4
