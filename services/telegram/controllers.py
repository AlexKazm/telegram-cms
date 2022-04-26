import asyncio
import random
from typing import List

from pyrogram import Client, Filters
from pyrogram.errors.exceptions.forbidden_403 import Forbidden
from pyrogram.errors.exceptions.bad_request_400 import BadRequest, PeerFlood
from pyrogram.errors.exceptions.flood_420 import FloodWait

from services.telegram.utils import MessageParser
from services.core.utils import get_event_loop, generator
from services.telegram.api.models import Message
from services.telegram.exceptions import ExceptionStatement
from services.telegram.enums import CallbackResult
from services.telegram.plugins import chat

from services.telegram.models import TelegramMessage, TelegramUser, TelegramInvitedUser


class TelegramController:
    chats = ['Python', 'pythonofftopic', 'ru_python', 'pydjango']

    def __init__(self, session: Client):
        self.loop: asyncio.get_event_loop = None
        self.session: Client = session

    @staticmethod
    async def callback(controller, result: CallbackResult, message, exception=None) -> None:
        controller: TelegramController

        result = CallbackResult(result)

        if message.service:
            try:
                await controller.session.delete_messages(
                    chat_id=message.chat['username'], message_ids=message.message_id)
            except Exception as e:
                statement = ExceptionStatement(result, message, e)
                await controller.session.send_message("me", ExceptionStatement.__dict__)
                del statement

        if result is CallbackResult.SUCCESS:
            message: Message = message
            message_model = await TelegramMessage.create(**message.dict())

            print(f"Created message model: {message_model}")

            try:
                if message.from_user['username'] and message.from_user['is_bot'] is False:
                    telegram_user = await TelegramUser.create(
                        user_id=message.from_user['id'], data=dict(message.from_user))

                    await telegram_user.save()
                    print(f"Created user model: {telegram_user}")
            except KeyError:
                pass

        elif result is CallbackResult.FAILED:
            statement = ExceptionStatement(result, message, exception)
            await controller.session.send_message("me", ExceptionStatement.__dict__)
            del statement

    async def invite_all_parsed_members_to_channel(self, chat_id: str, delay: int = 0, *args, **kwargs):
        if not self.session.is_connected:
            await self.session.start()

        flood_count = 0
        result = None

        q_result: List[TelegramUser] = await TelegramUser.all()
        async for member in generator(random.sample(q_result, len(q_result))):
            member: TelegramUser

            if not await TelegramInvitedUser.exists(user_id=member.user_id, chat_username=chat_id):
                print(self.session.session_name, member.user_id, chat_id, f"flood: {flood_count}")

                try:
                    result = await self.session.add_chat_members(
                        chat_id=chat_id, user_ids=str(member.data['username']), forward_limit=2)
                    await TelegramInvitedUser.try_create(
                        user_id=member.user_id, chat_username=chat_id
                    )
                    flood_count = 0

                except Forbidden as e:
                    result = str(e)
                    await TelegramInvitedUser.try_create(
                        user_id=member.user_id, chat_username=chat_id,
                        with_error=True, success=False, error=str(e))

                    flood_count = 0

                except FloodWait as e:
                    result = str(e)

                    flood_count += 1
                    if flood_count > 4:
                        print(f'waiting {e.x} seconds...')
                        await TelegramInvitedUser.try_create(
                            user_id=member.user_id, chat_username=chat_id,
                            with_error=True, success=False, error=str(e))

                        await asyncio.sleep(int(e.x))

                except PeerFlood as e:
                    result = str(e)

                    flood_count += 1
                    if flood_count > 4:
                        print(f'waiting {delay * 300} seconds...')
                        await TelegramInvitedUser.try_create(
                            user_id=member.user_id, chat_username=chat_id,
                            with_error=True, success=False, error=str(e))

                        await asyncio.sleep(delay * 300)

                except BadRequest as e:
                    result = str(e)
                    await TelegramInvitedUser.try_create(
                        user_id=member.user_id, chat_username=chat_id,
                        with_error=True, success=False, error=str(e))
                    flood_count = 0

                try:
                    await self.session.send_message("me", str(result))
                except FloodWait as e:
                    print(e.MESSAGE)

                await asyncio.sleep(int(delay))

    async def join_chat(self, chat_id: str):
        if not self.session.is_connected:
            await self.session.start()

        await self.session.join_chat(chat_id=chat_id)
        await asyncio.sleep(1)

    async def parse_chat_members(self, chat_id: str, offset: int = 0, delay: int = 0):

        if not self.session.is_connected:
            await self.session.start()

        await chat.parse_chat_members(session=self.session, chat_id=chat_id, delay=delay)

    async def init(self) -> None:
        self.loop = await get_event_loop()

        controller = self

        await self.session.start()

        @self.session.on_callback_query()
        async def callback_query_handler(filters: Filters, group: int = None) -> None:
            print("callback_query_handler:", group)

        @self.session.on_inline_query()
        async def inline_query_handler(filters: Filters, group: int = None) -> None:
            print("inline_query_handler:", group)

        #
        # @self.session.on_chosen_inline_result()
        # async def chosen_inline_result_handler(filters: Filters, group: int = None) -> None:
        #     print("chosen_inline_result_handler:", filters, group)
        #
        # @self.session.on_deleted_messages()
        # async def deleted_message_handler(filters: Filters, group: int = None) -> None:
        #     print("deleted_message_handler:", filters, group)
        #
        # @self.session.on_user_status()
        # async def on_user_status_handler(filters: Filters, group: int = None) -> None:
        #     print("on_user_status_handler:", filters, group)
        #
        # @self.session.on_poll()
        # async def on_poll_handler(filters: Filters, group: int = None) -> None:
        #     print("on_poll_handler:", filters, group)

        @self.session.on_message()
        async def message_handler(self, message) -> None:
            await MessageParser.parse(
                message, client_session=self, controller=controller)

            # old version of handling tasks. but you can use it if you want

            # task = controller.loop.create_task(
            #     MessageParser.parse(message, client_session=self)
            # )
            # task.add_done_callback(controller.message_callback)

        @self.session.on_disconnect()
        async def disconnect_handler(message=None) -> None:
            print(message)
