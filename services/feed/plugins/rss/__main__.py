import os
import asyncio
from typing import Callable, List

import feedparser
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from services.core.utils import generator, database_config
from services.feed.backend.listeners import DefaultRSSListener
from services.feed.backend.parsers import DefaultRSSParser
from services.feed.controllers import BaseFeedListener
from services.feed.enums import FeedType
from services.feed.models import FeedUrl, Feed
from services.scheduler.backend.senders import DefaultSchedulerSender
from services.telegram.utils import telegram_logger
from services.core.utils import Request as aiorequests

# setting up environment vars
AUTOPILOT = True if os.environ.get("FEED_AUTOPILOT") == 'True' else False
loop = asyncio.get_event_loop()
rss_feed_type = os.environ.setdefault("RSSFeedControllerType", "DefaultRSSFeedController")
rss_listener_type = os.environ.setdefault("RSSListenerType", "DefaultRSSParser")


class DefaultRSSFeedController(BaseFeedListener):
    def __init__(self, listener: Callable = DefaultRSSListener,
                 sender: Callable = DefaultSchedulerSender):
        self.urls: List[FeedUrl] = []
        self.listener = listener()
        self.sender = sender()

        super(DefaultRSSFeedController, self).__init__(self.listener, self.sender)

    async def start(self, interval: int):
        await Tortoise.init(database_config)
        await Tortoise.generate_schemas()

        await super(DefaultRSSFeedController, self).start(interval)

        while self.started:
            await self._check_updates(interval)
        else:
            await telegram_logger(f"{self.__repr__()} stoped gracefully.")

    async def _check_updates(self, interval):
        async for feed in generator(await Feed.filter(type=FeedType.RSS)):
            feed: Feed
            try:
                [
                    self.urls.append(url) if url not in self.urls and feed.is_active else None
                    async for url in generator(await feed.get_urls())
                ]
            except DoesNotExist:
                pass
        await asyncio.sleep(0.1)

        async for feed_url in generator(self.urls):
            feed_url: FeedUrl
            url = feed_url.url

            page = await aiorequests.send(method="GET", url=url)
            rss: feedparser.FeedParserDict = await DefaultRSSParser.parse_raw(page)
            rss.feed_url = feed_url

            await self.listener.catch_updates(updates=rss, sender=self.sender)
            await asyncio.sleep(0.1)

        await asyncio.sleep(interval)


rss_feed = DefaultRSSFeedController()

if AUTOPILOT:
    print(f"--- RSS Feed service started ---")
    print(f"--- RSSFeedController: {rss_feed} ---")
    print(f"--- RSSListenerType: {rss_listener_type} ---")
    print()

    loop.create_task(rss_feed.fetch(5))
