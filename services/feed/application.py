import os
import asyncio

from fastapi import FastAPI
from tortoise import Tortoise

from services.feed.api.controllers import FeedAPIController
from services.core.utils import database_config, DEBUG, DEFAULT_HOST, DOCKER_ENVIRONMENT, VERSION

loop = asyncio.get_event_loop()

application = FastAPI(title='Feed API', version='1.0.0')
feed_api_controller = FeedAPIController(application)


@application.on_event("startup")
async def startup():
    await Tortoise.init(database_config)
    await Tortoise.generate_schemas()


# on server shutdown event
@application.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()
