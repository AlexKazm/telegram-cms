import os

import asyncio
import random
from io import BytesIO
from typing import List

from pyrogram import Client, InlineKeyboardMarkup, InlineKeyboardButton

from services.core.utils import generator
from services.telegram.controllers import TelegramController
from services.telegram.models import TelegramApplication
from services.telegram.plugins import image_generator
from services.telegram.utils import telegram_logger
from services.telegraph.controller import TelegraphController


class TelegramConnector:

    def __init__(self):
        self.sessions = []
        self.controllers: List[TelegramController] = []

    async def init(self, autopilot: bool):
        configs = await TelegramApplication.filter(is_active=True)
        await self.load_sessions(configs)

        if autopilot:
            await self.start_sessions()

    async def get_controller(self, session_name: str):
        async for controller in generator(self.controllers):
            controller: TelegramController

            if str(controller.session.session_name) == str(session_name):
                return controller
        return None

    async def start_sessions(self):
        async for session in generator(self.sessions):
            controller: TelegramController = session['controller']
            application: TelegramApplication = session['application']

            application.is_online = True

            await application.save()
            await controller.init()

    async def load_sessions(self, sessions_configs: List[TelegramApplication]):
        async for application in generator(sessions_configs):
            client = Client(**application.config)
            controller = TelegramController(session=client)

            session = {
                "client": client,
                "application": application,
                "controller": controller,
            }
            if not session in self.sessions:
                self.sessions.append(session)
                self.controllers.append(controller)

    async def separate_job_for_sessions(self, job: str, args: dict) -> None:
        """
        :job: str = name of controller coroutine to fetching
        :args: dict = args for job

        :return: None
        """

        # if job == 'parse_chat_members':
        #     args.setdefault("offset", 0)
        #     args.setdefault("delay", random.choices([1, 2, 3, 4])[0])

        if job == 'invite_all_parsed_members_to_channel':
            args.setdefault("delay", random.choices([10, 11, 12, 13, 14, 15, 16])[0] + \
                            random.choices([1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])[0])

        tasks: List[asyncio.Future] = []
        async for controller in generator(self.controllers):
            coroutine = getattr(controller, job).__call__(**args)
            print(args)
            try:
                tasks.append(asyncio.ensure_future(coroutine))
            except Exception:
                pass

            # if job == 'parse_chat_members':
            #     args['offset'] += 10000
            #     args['delay'] = random.choices([1, 2, 3, 4])[0] + \
            #                     random.choices([1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])[0]

            if job == 'invite_all_parsed_members_to_channel':
                args['delay'] = random.choices([10, 11, 12, 13, 14, 15, 16])[0] \
                                + random.choices([1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8])[0]

        await asyncio.wait(tasks)

    async def disable_application(self, application_id: int):
        try:
            app = await TelegramApplication.get(id=application_id)
            app.is_active = False
            await app.save()
            return True
        except Exception:
            return False

    async def enable_application(self, application_id: int):
        try:
            app = await TelegramApplication.get(id=application_id)
            app.is_active = True
            await app.save()
            return True
        except Exception:
            return False

    async def send_message(self, application: dict, data: dict, rpc_data: dict, *args, **kwargs):
        title = data['data']['title']
        html_content = data['data']['content']
        clean_content = data['data']['clean_content']
        source_url = data['data']['url']
        img_url = data['data']['img_url']

        controller = await self.get_controller(session_name=application['config']['session_name'])

        page_url = await TelegraphController.create_page(title=title, html=html_content)

        image: BytesIO = image_generator.create_image(
            img_template_path=image_generator.get_random_template_image_path(),
            text=title
        )

        try:
            await controller.session.send_photo(
                chat_id=rpc_data['chat_username'],
                photo=image,
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    # [
                    #     InlineKeyboardButton(text='👍', callback_data="cool"),
                    #     InlineKeyboardButton(text='👎', callback_data="bad")
                    # ],
                    [
                        InlineKeyboardButton(text="Read More", url=page_url),
                    ]
                ])
            )
        except AttributeError as e:
            await telegram_logger(message=f"can't send photo. details: {e}")
