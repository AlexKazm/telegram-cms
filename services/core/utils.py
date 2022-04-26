import os
import ssl
import re
import time
import asyncio

import databases
import sqlalchemy
import certifi

from typing import Iterable, Callable, Generator

from aiohttp.client import ClientSession

from services.core.enums import Database

ssl_context = ssl.create_default_context(cafile=certifi.where())

DEBUG = os.environ.get("DEBUG", default=True)
DEFAULT_HOST = os.environ.get("DEFAULT_HOST", default="0.0.0.0:9000")
DATABASE_URL = os.environ.get("DB_HOST", default="sqlite:///services/core/main.db")
KAFKA_TRANSPORT = os.environ.get("KAFKA_BOOTSTRAP_SERVER")
MEMCACHED = os.environ.get("MEMCACHED")
REDIS = os.environ.get("REDIS")
DOCKER_ENVIRONMENT = os.environ.get("DOCKER_ENVIRONMENT")
VERSION = os.environ.get("VERSION")

models = [
    'services.telegram.models',
    'services.feed.models',
    'services.admin.models',
    'services.scheduler.models',
    'services.telegraph.models',
    'aerich.models'
]

database_config = {
    "connections": {
        Database.telegramcms.name: Database.telegramcms.value
    },
    "apps": {
        "telegramcms": {
            "models": models,
            "default_connection": Database.telegramcms.name
        },
    },
}


async def logger(request):
    print(f"[{time.ctime()}]: {request}")


async def generator(l: list):
    i = 0
    len_a = len(l)
    while i < len_a:
        yield l[i]
        i += 1


async def serialize_iterable(iterable: Iterable, generator: Generator, method: Callable):
    async for obj in generator(iterable):
        method(await obj.serialize())


async def html_text_regex_cleaner(html: str):
    regex = re.compile('(?:<).*?(?:>)')
    result = re.sub(regex, '', str(html))

    regex = re.compile('(?:r"\").*?(?:r"\")]')
    result = re.sub(regex, '', result).replace("&nbsp;", "")
    result = re.sub("\r", "", result)
    result = re.sub("\n", "", result)
    return result


async def get_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        return asyncio.get_running_loop()


def with_client_session(coro):
    async def wrapper(method: str, url: str, data: dict = None, headers: dict = None):
        session = ClientSession()
        result = None

        if method == 'GET':
            result = await coro(method=session.get, url=url, data=data, headers=headers)
        elif method == ' POST':
            result = await coro(method=session.post, url=url, data=data, headers=headers)
        elif method == 'PUT':
            result = await coro(method=session.put, url=url, data=data, headers=headers)
        elif method == 'DELETE':
            result = await coro(method=session.delete, url=url, data=data, headers=headers)
        elif method == 'PATCH':
            result = await coro(method=session.patch, url=url, data=data, headers=headers)

        await session.close()
        return result

    return wrapper


class Request:

    @staticmethod
    @with_client_session
    async def send(method, url: str, data: dict = None, headers: dict = None):
        response = await method(url=url, data=data, headers=headers, ssl=ssl_context)
        return await response.text()

    @staticmethod
    @with_client_session
    async def send_iterable_data(method, url: str, data: Iterable, headers: dict = None):
        response = await method(url=url, json=data, headers=headers, ssl=ssl_context)
        return await response.text()


origins = [
    "http://localhost",
    "http://localhost:9000",
    "https://localhost",
    "https://localhost:9000",
    "http://0.0.0.0",
    "http://0.0.0.0:9000",
    "https://0.0.0.0",
    "https://0.0.0.0:9000",
]

allow_methods = [
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

allow_headers = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    "Access-Control-Allow-Origin",
    "Access-Control-Allow-Methods",
    "Access-Control-Max-Age",
    "Access-Control-Allow-Headers",
]
