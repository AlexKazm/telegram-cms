import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from asgi_caches.middleware import CacheMiddleware
from fastapi_contrib.auth.middlewares import AuthenticationMiddleware
from fastapi_contrib.auth.backends import AuthBackend
from aiocache import Cache
from tortoise import Tortoise

# from services.common.stream import event_stream as kafka_stream

from services.core.utils import (
    allow_headers, allow_methods, database_config, DEBUG, REDIS, DEFAULT_HOST, DOCKER_ENVIRONMENT, MEMCACHED,
    VERSION, KAFKA_TRANSPORT
)
from services.core.middlewares import LoginRequired

loop = asyncio.get_event_loop()

application = FastAPI(
    title="Telegram CMS",
    version="1.0.0",
)

cache = Cache.from_url(REDIS)
cache_middleware = CacheMiddleware(application, cache=cache)

application.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=allow_methods,
    allow_headers=allow_headers
)
application.add_middleware(AuthenticationMiddleware, backend=AuthBackend())
# application.add_middleware(LoginRequired)

templates = Jinja2Templates(directory='templates')
application.mount("/static", StaticFiles(directory='frontend/dist/'), name="static")
application.mount("/plugins", StaticFiles(directory='frontend/plugins/'), name="plugins")

# application.stream = kafka_stream
application.cache = cache_middleware


# before server starts event
@application.on_event("startup")
async def startup():
    await Tortoise.init(database_config)
    await Tortoise.generate_schemas()


# on server shutdown event
@application.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()


if bool(DOCKER_ENVIRONMENT):
    print(f"--- Using Docker '{VERSION}' environment ---")
    print(f"--- Settigs:")
    print(f"----- DEBUG: {DEBUG}")
    print(f"----- DEFAULT_HOST: {DEFAULT_HOST}")
    print(f"----- KAFKA: {KAFKA_TRANSPORT}")
    print(f"----- REDIS: {REDIS}")
    print(f"----- MEMCACHED: {MEMCACHED}")
    print(f"----- CACHE CLIENT: {cache_middleware}")
    print()
