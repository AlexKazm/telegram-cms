from typing import List, Callable, Optional
import os
import json
import uuid

import aiocache
from pydantic import BaseModel
from aiohttp.client import ClientSession

from services.core.utils import Request, generator
from services.feed.models import RSS
from services.core.settings import cache
from services.core.backend.events import DefaultTransportMessageEvent


class RPCRequest(BaseModel):
    function: str
    event: Optional[DefaultTransportMessageEvent]


class TransportMessage(BaseModel):
    key: str
    namespace: str
    request: Optional[RPCRequest]


class TransportResponse(BaseModel):
    response: str


class RPCAPITransport:

    def __init__(self):
        self.telegram = os.environ.get("TELEGRAM_API")
        self.admin = os.environ.get("ADMIN_API")
        self.feed = os.environ.get("FEED_API")
        self.scheduler = os.environ.get("SCHEDULER_API")

        self.cache: aiocache.RedisCache = cache

    async def __aenter__(self):
        return self

    async def __aexit__(self, exec_type, exec_value, traceback):
        if exec_type or exec_value:
            print(exec_type)
        else:
            return True

    async def send(self, service_url: str, request: RPCRequest) -> TransportResponse:
        """

        :param service_url: str of self.telegram | self.rss_feed | self.admin | self.scheduler ...
        :param request: RPCRequest
        :return: TransportResponse
        """

        url = f"{service_url}/transport/message"

        message = TransportMessage(key=str(uuid.uuid4()), namespace='transport', request=request)

        await self.cache.set(key=message.key, value=message.dict(), namespace=message.namespace, ttl=60)

        async with ClientSession() as session:
            response = await session.post(
                url=url, json={
                    "key": message.key,
                    "namespace": message.namespace,
                    "request": RPCRequest(function=request.function).dict()
                })
            await session.close()

        return TransportResponse(response=await response.text())

