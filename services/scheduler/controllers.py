import asyncio
from datetime import datetime

from services.core.utils import generator, get_event_loop
from services.scheduler.models import TelegramSubscription
from services.telegram.utils import telegram_logger


class DefaultScheduler:
    GLOBAL_SAFE_SLEEP_TIME = 5

    def __init__(self, publication_interval: int, autopilot: bool):
        self.started = False
        self.publication_interval = publication_interval
        self.loop = asyncio.get_running_loop()
        self.worker = None
        if autopilot:
            self.start_worker()

    def start_worker(self):
        self.worker = self.loop.create_task(self.work())

    async def work(self):
        self.started = True
        await telegram_logger(f"{self.__repr__()} started. Waiting for events.")

        while self.started:
            # subscriptions = await TelegramSubscription.filter(deferred=True, published=False)
            # async for subscription in generator(subscriptions):
            #       if await subscription.is_ready_to_publish():
            #               await subscription.spawn_deferred()
            #               await asyncio.sleep(0.1)
            await asyncio.sleep(0.1)

        else:
            await telegram_logger(f"{self.__repr__()} stoped gracefully.")

    # FIXME
    @staticmethod
    async def schedule_publication_date(data: dict, date_time: datetime = None):
        if not date_time:
            # await subscription.push_to_queue(self.publication_interval, data)
            return await asyncio.sleep(0.1)

        else:
            # await subscription.deferred_at(date_time, data)
            return await asyncio.sleep(0.1)

    @staticmethod
    async def spawn(data: dict):
        """

        :param data: dict
        :return:
        """
        subscriptions = await TelegramSubscription.filter(source=data['data']['feed_url']['url'])
        async for subscription in generator(subscriptions):
            await subscription.spawn(data)
            await asyncio.sleep(0.1)
