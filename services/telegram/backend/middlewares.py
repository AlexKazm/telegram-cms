from typing import Callable

from services.feed.plugins.rss import rss_feed
from services.feed.backend.listeners import DefaultRSSListener
from services.feed.backend.parsers import DefaultRSSParser
from services.core.backend.transport import RPCAPITransport
from services.scheduler.backend.senders import DefaultSchedulerSender


class DefaultTelegramMiddleware:
    def __init__(
            self,
            listener=DefaultRSSListener,
            sender=DefaultSchedulerSender,
            parser=DefaultRSSParser,
            controller=rss_feed,
            transport=RPCAPITransport,
    ):
        self.listener = listener()
        self.sender = sender()
        self.parser = parser()
        self.controller = controller
        self.transport = transport()


DefaultTelegramMiddleware = DefaultTelegramMiddleware()
