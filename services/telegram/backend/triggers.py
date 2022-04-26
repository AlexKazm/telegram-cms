from typing import List

from services.core.utils import generator
from services.feed.models import FeedUrl
from services.telegram.backend.senders import DefaultTelegramChannelSender
from services.telegram.models import DefaultDataSubscription
from services.telegram.enums import DataSubscriptionType


class DefaultRSSTrigger:
    def __init__(self, sender=DefaultTelegramChannelSender):
        self.sender = sender

    async def check_data(self, result: List[dict]):
        async for data in generator(result):
            feed_url: FeedUrl.serializer = data['feed_url']

            subscriptions: List[DefaultDataSubscription] = \
                await DefaultDataSubscription.filter_rss_subscriptions_by_url(data)

            # FIXME
            # await self.sender.send_iterable(result)

    def __str__(self):
        return str(self.__repr__())
