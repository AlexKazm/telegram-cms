import time

import databases
from fastapi import Request, WebSocket
from fastapi.background import BackgroundTasks
from fastapi.templating import Jinja2Templates


from services.telegram.controllers import TelegramController
from services.core.utils import Request as aiorequests
from services.telegram.models import TelegramApplication
from services.admin.models import AdminPlugin


# https://pypi.org/project/fastapi-admin/
# https://www.tutorialsteacher.com/articles/geocoding-rest-api-positionstack
# https://www.bugsnag.com/blog/grpc-and-microservices-architecture


class AdminAPIController:

    def __init__(self, application, templates, host, debug):
        self.application = application
        self.templates: Jinja2Templates = templates
        # self.database: databases.Database = database
        self.host = host
        self.debug = debug
        self.main()

    def main(self):
        @self.application.get('/')
        async def main(request: Request):
            return self.templates.TemplateResponse(
                "main.html", {
                    "request": request,
                    "host": self.host,
                    "debug": self.debug
                }
            )

        @self.application.get('/login')
        async def login(request: Request):
            return self.templates.TemplateResponse(
                "admin/login.html", {
                    "request": request,
                    "host": self.host,
                    "debug": self.debug
                }
            )

        @self.application.get('/admin/marketplace')
        async def marketplace(request: Request):
            return self.templates.TemplateResponse(
                "admin/marketplace.html", {
                    "request": request,
                    "plugins": await AdminPlugin.all(),
                }
            )

        @self.application.get('/admin')
        async def admin(request: Request):
            return self.templates.TemplateResponse(
                "admin/main.html", {
                    "request": request,
                    "host": self.host,
                    "debug": self.debug,
                    "applications": await TelegramApplication.all(),
                    "plugins": await AdminPlugin.all(),
                    # "plugins": {
                    #     "search_form": True,
                    #     "calendar": True,
                    #     "right_navbar": False,
                    #     "sales": False,
                    #     "last_publications": True,
                    #     "last_members": True,
                    #     "todo_list": True,
                    #     "visitors": False,
                    #     "sales_graph": False,
                    # }
                }
            )

        # socket connection handler
        @self.application.websocket('/ws')
        async def messages_updates(websocket: WebSocket):
            await websocket.accept()
            # await admin_consumer.update_socket(websocket)

            while True:
                # command, result = await admin_consumer.get_result()
                command, result = "1", "2"
                await websocket.send_text(f"[{time.ctime()}]: Command - [{command}] Result - {result}")
