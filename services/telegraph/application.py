import os

from fastapi import FastAPI
from tortoise import Tortoise

from services.core.utils import database_config, DEBUG, DEFAULT_HOST, DOCKER_ENVIRONMENT, VERSION
from services.telegraph.controller import TelegraphController

application = FastAPI(title='Telegraph Service API', version="1.0.0")
telegraph = TelegraphController()


@application.on_event("startup")
async def startup():
    await Tortoise.init(database_config)
    await Tortoise.generate_schemas()

    await telegraph.init()


# on server shutdown event
@application.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()


if bool(DOCKER_ENVIRONMENT):
    print(f"--- Telegram service started ---")
    print()
