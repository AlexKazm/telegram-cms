import asyncio

from services.telegram.utils import telegram_logger


class BaseFeedListener:

    def __init__(self, listener, sender):
        self.parser = listener
        self.sender = sender
        self._loop = asyncio.get_event_loop()

        self.started = False

    async def fetch(self, interval: int):
        self._loop.create_task(self.start(interval))

    async def start(self, interval: int):
        self.started = True

        await telegram_logger(f"{self.__repr__()} started. Waiting for Feed instances.")

    def __str__(self):
        return f"{self.__repr__()}: {'started' if self.started else 'not started'}"

    class Meta:
        abstract = True
