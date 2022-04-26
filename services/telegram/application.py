import os

from fastapi import FastAPI
from tortoise import Tortoise

from services.telegram.controllers import TelegramController
from services.telegram.connectors import TelegramConnector
from services.telegram.api.controllers import TelegramAPIController
from services.core.utils import database_config, DEBUG, DEFAULT_HOST, DOCKER_ENVIRONMENT, VERSION

application = FastAPI(title='Telegram Service API', version="1.0.0")
telegram = TelegramConnector()
telegram_api_controller = TelegramAPIController(application, telegram)

AUTOPILOT = True if os.environ.get("TELEGRAM_AUTOPILOT") == 'True' else False


@application.on_event("startup")
async def startup():
    await Tortoise.init(database_config)
    await Tortoise.generate_schemas()

    await telegram.init(autopilot=AUTOPILOT)


# on server shutdown event
@application.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()


if bool(DOCKER_ENVIRONMENT):
    print(f"--- Telegram service started ---")
    print()
