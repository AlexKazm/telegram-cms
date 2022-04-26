from tortoise import Tortoise

from services.core.settings import application, templates
from services.admin.api.controllers import AdminAPIController
from services.core.utils import DEFAULT_HOST, DEBUG, database_config

admin_api_controller = AdminAPIController(application, templates, DEFAULT_HOST, DEBUG)
application.title = 'Telegram Admin API'


# before server starts event
@application.on_event("startup")
async def startup():
    await Tortoise.init(database_config)
    await Tortoise.generate_schemas()


# on server shutdown event
@application.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()

