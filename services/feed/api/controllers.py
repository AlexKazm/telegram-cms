import os
from typing import List
from importlib import import_module

from fastapi import Request, WebSocket
from fastapi.responses import RedirectResponse
from fastapi.background import BackgroundTasks

from services.core.utils import Request as aiorequests, generator, serialize_iterable
from services.telegram.backend.middlewares import DefaultTelegramMiddleware
from services.feed.models import FeedUrl, Feed, FeedRequest, RSS


class FeedAPIController:

    def __init__(self, application):
        self.application = application
        self.main()

    def main(self):
        @self.application.get('/')
        async def main(request: Request):
            return RedirectResponse('/docs')

        @self.application.get('/rss_feed/list/', response_model=List[Feed.serializer])
        async def get_feed_list(request: Request):
            response = []
            await serialize_iterable(await Feed.all(), generator, response.append)
            return response

        @self.application.post('/rss_feed', response_model=Feed.serializer)
        async def create_feed(request: Request, model: FeedRequest):

            """
            example: {
                "type": "rss",
                "urls": [
                    {
                        "url": "https://medium.com/feed/free-code-camp"
                    },
                    {
                        "url": "https://medium.com/feed/analytics-vidhya"
                    },
                    {
                        "url": "https://medium.com/feed/hackernoon"
                    },
                    {
                        "url": "https://medium.com/feed/better-programming"
                    },
                    {
                        "url": "https://medium.com/feed/towardsdatascience"
                    },
                    {
                        "url": "https://medium.com/feed/progate"
                    },
                    {
                        "url": "https://medium.com/feed/engineering"
                    },
                    {
                        "url": "https://medium.com/feed/quick-code"
                    },
                    {
                        "url": "https://medium.com/feed/datadriveninvestor"
                    },
                    {
                        "url": "https://medium.com/feed/tech-explained"
                    },
                    {
                        "url": "https://medium.com/feed/inside-league"
                    },
                    {
                        "url": "https://medium.com/feed/codeburst"
                    },
                    {
                        "url": "https://medium.com/feed/towards-artificial-intelligence"
                    },
                    {
                        "url": "https://medium.com/feed/swlh"
                    },
                    {
                        "url": "https://medium.com/feed/@cscalfani"
                    }
                ],
                "is_active": true,
                "is_empty": false
            }

            type: services.rss_feed.enums.FeedType
            """
            urls: List[FeedUrl] = await FeedUrl.get_from_list(model.urls)
            json_urls = [{"id": url.id, "url": url.url} async for url in generator(urls)]

            model: Feed = await Feed.create(
                type=model.type,
                urls=json_urls,
                is_active=model.is_active,
                is_empty=model.is_empty
            )
            serialized_data: Feed.serializer = await model.serialize()
            return serialized_data

        @self.application.get('/rss_feed/url/list/', response_model=List[FeedUrl.serializer])
        async def get_feed_url_list(request: Request):
            response = []
            await serialize_iterable(await FeedUrl.all(), generator, response.append)
            return response

        @self.application.post('/rss_feed/url', response_model=FeedUrl.serializer)
        async def create_feed_url(request: Request, url: str):
            model: FeedUrl = await FeedUrl.create(url=url)
            serialized_data: FeedUrl.serializer = await model.serialize()
            return serialized_data

        @self.application.delete('/rss_feed/url/', response_model=dict)
        async def delete_feed_url(request: Request, id: int):
            deleted, details = await FeedUrl.delete_with_result(id=id)
            return {"deleted": deleted, "details": details}

        @self.application.put('/rss_feed/url')
        async def update_feed_url(request: Request, model: FeedUrl.serializer):
            updated, details = await FeedUrl.update_with_result(model)
            return {"updated": updated, "details": details}

        @self.application.get('/rss_feed/fetch_all_rss/')
        async def get_fetch_all_rss_feeds(request: Request):
            if not DefaultTelegramMiddleware.controller.started:
                await DefaultTelegramMiddleware.controller.fetch(interval=3)
                return True
            else:
                return {
                    "status": "fetching already started"
                }

        @self.application.get('/rss_feed/stop_all_rss_fetching/')
        async def stop_rss_fetching(request: Request):
            if DefaultTelegramMiddleware.controller.started:
                DefaultTelegramMiddleware.controller.started = False
                return True
            else:
                return {
                    "status": "fetching already stoped"
                }

        @self.application.get('/rss/get_list/', response_model=List[RSS.serializer])
        async def get_rss_list(request: Request):
            response: List[RSS.serializer] = []
            async for model in generator(await RSS.all()):
                response.append(RSS.serializer(**model.__dict__))
            return response
