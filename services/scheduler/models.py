import hashlib
from typing import Optional, List

from tortoise import fields
from pydantic import BaseModel

from services.core.backend.events import DefaultTransportMessageEvent
from services.core.backend.transport import RPCAPITransport, RPCRequest
from services.core.utils import generator

from services.core.enums import Database
from services.core.models import TimestampedMixin, AbstractBaseModel


class Subscriber(AbstractBaseModel, TimestampedMixin):
    data = fields.JSONField(
        default=None,
        null=True,
        blank=True
    )

    hashes = fields.JSONField(
        default=None,
        null=True,
        blank=True
    )

    class Meta:
        table = 'Subscriber'
        default_connection = Database.telegramcms.name


class Subscription(AbstractBaseModel, TimestampedMixin):
    """

    Пример использования проверит данные для каждого подписчика

    usage:
        data: dict

        subscriptions = await Subscription.filter(source='https://medium.com/feed/free-code-camp')
        async for subscription in generator(subscriptions):
            await subscription.spawn(data)

    """

    source = fields.CharField(
        defaut=None, null=True, unique=False, max_length=1024
    )

    subscribers = fields.JSONField(
        default=None,
        null=True
    )

    class Meta:
        table = 'Subscription'
        default_connection = Database.telegramcms.name


class TelegramSubscriber(Subscriber):
    application: fields.ForeignKeyRelation = fields.ForeignKeyField(
        model_name="telegramcms.TelegramApplication",
        related_name='telegram_subscriber',
        on_delete=fields.SET_NULL,
        null=True
    )

    class Meta:
        table = 'TelegramSubscriber'
        default_connection = Database.telegramcms.name

    class Serializer(BaseModel):
        id: Optional[int]
        data: Optional[dict]
        hashes: Optional[dict]
        application: Optional[dict]

    serializer = Serializer

    async def push(self, data: dict, data_hash: str = None) -> None:
        """
        :param data: dict
        :param data_hash: str
        :return: None

        требуется отправить данные подписчику используя данные источника из data

        """
        if data_hash:
            if not self.hashes:
                self.hashes = []

            self.hashes.append(data_hash)
            await self.save()

        application = await self.application
        request = RPCRequest(
            function='send_message',
            event=DefaultTransportMessageEvent(
                args={
                    "application": application.__dict__,
                    "data": data,
                    "rpc_data": self.data
                }
            )
        )
        async with RPCAPITransport() as rpc:
            await rpc.send(service_url=rpc.telegram, request=request)


class TelegramSubscription(Subscription):
    class Meta:
        table = 'TelegramSubscription'
        default_connection = Database.telegramcms.name

    class APISerializer(BaseModel):
        id: Optional[int]
        source: Optional[str]
        subscribers: List[TelegramSubscriber.serializer]

    serializer = APISerializer

    async def spawn(self, data: dict) -> None:
        """
        :param data:
        :return: None

        нужно сделать хэш от data и сравнить со списком отправленных хешей.
        если среди отправленных такого нет, значит отправтить подписчику

        """

        data_hash = hashlib.md5(f"{data}".encode()).hexdigest()

        async for subscriber in generator(list(self.subscribers)):
            subscriber = await TelegramSubscriber.get(id=subscriber['id'])
            subscriber_hashes: dict or bool = subscriber.hashes

            # if not subscriber_hashes or data_hash not in list(subscriber_hashes):
            await subscriber.push(data, data_hash)
