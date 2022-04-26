import json
from typing import List

import aiocache
from fastapi.responses import RedirectResponse
from tortoise.transactions import in_transaction

from services.core.backend.events import DefaultTransportMessageEvent, TransportMessageEventType
from services.core.backend.transport import TransportMessage, RPCRequest, TransportResponse
from services.telegram.connectors import TelegramConnector
from services.telegram.models import TelegramApplication
from services.core.settings import cache
from services.core.utils import generator
from services.scheduler.controllers import DefaultScheduler
from services.scheduler.models import TelegramSubscription, TelegramSubscriber


class SchedulerAPIController:
    def __init__(self, application, telegram, scheduler):
        self.application = application
        self.telegram: TelegramConnector = telegram
        self.scheduler: DefaultScheduler = scheduler
        self.cache: aiocache.RedisCache = cache

        @self.application.get('/')
        async def main():
            return RedirectResponse('/docs')

        @self.application.post('/transport/message', response_model=TransportResponse)
        async def create_transport_message(message: TransportMessage):
            """
            :param message: TransportMessage
            :return: TransportResponse
            """
            function = getattr(self.scheduler, message.request.function)
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
            await function(data=data.request.event.args)

            return TransportResponse(response="OK")

        @self.application.get('/subscription/list/', response_model=List[TelegramSubscription.serializer])
        async def get_subscriptions_list():
            response: List[TelegramSubscription.serializer] = []
            models = await TelegramSubscription.all()

            async for model in generator(models):
                model: TelegramSubscription

                api_model = TelegramSubscription.serializer(
                    id=model.id,
                    source=model.source,
                    subscribers=model.subscribers
                )
                response.append(api_model)

            return response

        @self.application.post('/subscription', response_model=TelegramSubscription.serializer)
        async def create_subscription(data: TelegramSubscription.serializer):
            """
            {
              "source": "https://medium.com/feed/free-code-camp",
              "subscribers": [
                {
                  "id": 1,
                  "data": {
                    "chat_username": "python_intermediate"
                  },
                  "application": {
                    "id": 1
                  }
                }
              ]
            }

            :param data:
            :return:
            """

            subscribers = []

            async for subscriber in generator(data.subscribers):
                subscriber: TelegramSubscriber.serializer
                if await TelegramSubscriber.exists(id=subscriber.id):
                    subscribers.append(subscriber.__dict__)

            model = await TelegramSubscription.create(
                source=data.source,
                subscribers=subscribers
            )
            api_model = TelegramSubscription.serializer(
                id=model.id,
                source=model.source,
                subscribers=model.subscribers
            )

            return api_model

        @self.application.get('/subscriber/list/')
        async def get_subscribers_list():
            # FIXME LIST SERIALIZER
            # response: List[TelegramSubscriber.serializer] = []
            # models = await TelegramSubscriber.all()
            # async for model in generator(models):
            #     model: TelegramSubscriber
            #
            #     api_model = TelegramSubscriber.serializer(
            #         **model.__dict__
            #     )
            #     application = await model.application
            #     api_model.application = TelegramApplication.serializer(
            #         **application.__dict__
            #     )
            #
            #     response.append(api_model)
            # return response
            return await TelegramSubscriber.all()

        @self.application.delete('/subscription', response_model=bool)
        async def delete_subscriber(subscription_id: int):
            try:
                model = await TelegramSubscription.get(id=subscription_id)
                await model.delete()
                return True
            except Exception:
                return False

        @self.application.delete('/subscriber', response_model=bool)
        async def delete_subscriber(subscriber_id: int):
            try:
                model = await TelegramSubscriber.get(id=subscriber_id)
                await model.delete()
                return True
            except Exception:
                return False

        @self.application.post('/subscriber', response_model=TelegramSubscriber.serializer)
        async def create_subscriber(data: TelegramSubscriber.serializer):
            """
            {
              "data": {
                "chat_username": "python_intermediate"
              },
              "application": {
                "id": 1,
                "config": {
                  "api_id": 897994,
                  "session_name": "telegram_parser",
                  "workdir": "services/telegram/sessions",
                  "workers": 1,
                  "api_hash": "0fa73f5d084cb1ec9df4d116d701d52c"
                }
              }
            }

            :param data: TelegramSubscriber.serializer
            :return:
            """
            model = await TelegramSubscriber.create(
                application=await TelegramApplication.get(
                    id=data.application['id']
                ),
                data=data.data,
                hashes=data.hashes,
            )
            api_model = TelegramSubscriber.serializer(
                **model.__dict__
            )
            application = await model.application
            api_model.application = TelegramApplication.serializer(
                **application.__dict__
            )
            return api_model
