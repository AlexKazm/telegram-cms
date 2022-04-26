import time
from typing import List

import aiocache
from fastapi import Request, WebSocket, BackgroundTasks

from services.telegram.models import TelegramMessage, TelegramApplication, TelegramUser
from services.telegram.api.models import Application
from services.telegram.controllers import TelegramController
from services.telegram.connectors import TelegramConnector
from services.core.settings import cache
from services.core.utils import generator
from services.core.backend.transport import TransportMessage, TransportResponse, RPCRequest
from services.core.backend.events import DefaultTransportMessageEvent, TransportMessageEventType

from services.feed.models import RSS


class TelegramAPIController:

    def __init__(self, application, telegram):
        self.application = application
        self.telegram: TelegramConnector = telegram
        self.cache: aiocache.RedisCache = cache

        @self.application.put('/application/disable/')
        async def disable_application(app_id: int):
            return await self.telegram.disable_application(app_id)

        @self.application.put('/application/enable/')
        async def enable_application(app_id: int):
            return await self.telegram.enable_application(app_id)

        @self.application.post('/transport/message', response_model=TransportResponse)
        async def create_transport_message(message: TransportMessage):
            """
            :param message: TransportMessage
            :return: TransportResponse
            """
            function = getattr(self.telegram, message.request.function)
            response = await self.cache.get(key=message.key, namespace=message.namespace)
            data: TransportMessage = TransportMessage(
                key=response['key'],
                namespace=response['namespace'],
                request=RPCRequest(
                    function=response['request']['function'],
                    event=DefaultTransportMessageEvent(
                        type=TransportMessageEventType(response['request']['event']['type']['value']),
                        args=response['request']['event']['args']
                    )
                )
            )
            await function(**data.request.event.args)
            return TransportResponse(response="OK")

        @self.application.get('/application/list/')
        async def get_application_list():
            applications: List[TelegramApplication] = []
            async for application in generator(await TelegramApplication.all()):
                application: TelegramApplication
                await application.save()
                applications.append(application)

            return applications

        @self.application.post('/application/create')
        async def create_application(app: Application):
            return await TelegramApplication.create(config=app.dict())

        @self.application.delete('/application/delete/all')
        async def delete_all_applications():
            async for model in generator(await TelegramApplication.all()):
                await model.delete()

            return True

        @self.application.get('/message/list/')
        async def get_message_list():
            return await TelegramMessage.all()

        @self.application.get('/user/list/')
        async def get_user_list():
            return await TelegramUser.all()

        @self.application.post('/chat/members/parse_all')
        async def parse_chat_members(session_name: str, chat_id: str, background_tasks: BackgroundTasks):
            controller: TelegramController = await self.telegram.get_controller(session_name=session_name)
            background_tasks.add_task(controller.parse_chat_members, chat_id=chat_id, delay=0.1)
            return True

        @self.application.post('/action/invite_all_parsed_members_to_channel')
        async def invite_all_parsed_members_to_channel(session_name: str, chat_id: str,
                                                       background_tasks: BackgroundTasks):
            controller = await self.telegram.get_controller(session_name=session_name)
            background_tasks.add_task(controller.invite_all_parsed_members_to_channel, chat_id)

            return True

        @self.application.post('/separated/chat/join')
        async def separate_join_chat(chat_id: str, background_tasks: BackgroundTasks):
            """
            python_id -1001050982793
            """
            background_tasks.add_task(self.telegram.separate_job_for_sessions,
                                      job="join_chat",
                                      args={"chat_id": chat_id})
            return True

        # @self.application.post('/separated/chat/members/parse_all')
        # async def separate_parse_chat_members(chat_id: str, background_tasks: BackgroundTasks):
        #     """
        #     python_id -1001050982793
        #     """
        #     background_tasks.add_task(self.telegram.separate_job_for_sessions,
        #                               job="parse_chat_members",
        #                               args={"chat_id": chat_id})
        #     return True

        @self.application.post('/separated/invite_all_parsed_members_to_channel')
        async def separate_invite_all_parsed_members_to_channel(
                chat_id: str, background_tasks: BackgroundTasks):

            background_tasks.add_task(self.telegram.separate_job_for_sessions,
                                      job="invite_all_parsed_members_to_channel",
                                      args={"chat_id": chat_id})
            return True

        # socket connection handler
        @self.application.websocket('/ws')
        async def messages_updates(websocket: WebSocket):
            await websocket.accept()
            # await admin_consumer.update_socket(websocket)

            while True:
                # command, result = await admin_consumer.get_result()
                await websocket.send_text(f"[{time.ctime()}]: Hello from websockets")
