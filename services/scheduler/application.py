import os

from fastapi import FastAPI
from tortoise import Tortoise

from services.core.utils import database_config, DOCKER_ENVIRONMENT
from services.telegram.application import telegram
from services.scheduler.api.controllers import SchedulerAPIController
from services.scheduler.controllers import DefaultScheduler

application = FastAPI(title='Scheduler Service API', version="1.0.0")

AUTOPILOT = True if os.environ.get("SCHEDULER_AUTOPILOT") == 'True' else False

scheduler = DefaultScheduler(publication_interval=600, autopilot=AUTOPILOT)
scheduler_api_controller = SchedulerAPIController(application, telegram, scheduler)


@application.on_event("startup")
async def startup():
    await Tortoise.init(database_config)
    await Tortoise.generate_schemas()


# on server shutdown event
@application.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()


if bool(DOCKER_ENVIRONMENT):
    print(f"--- Scheduler service started ---")
    print()
