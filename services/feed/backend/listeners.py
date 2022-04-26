import asyncio
from typing import List, Callable

import feedparser

from services.core.utils import generator, html_text_regex_cleaner
from services.feed.models import RSS, FeedUrl


class DefaultRSSListener:
    GLOBAL_SAFE_SLEEP_TIME = 5

    @staticmethod
    async def catch_updates(updates: feedparser.FeedParserDict, sender) -> None:
        async for publication in generator(updates.entries):
            publication: feedparser.FeedParserDict

            await asyncio.sleep(DefaultRSSListener.GLOBAL_SAFE_SLEEP_TIME)

            try:
                channel_img_url = updates.feed.image['href']
                feed_url: FeedUrl = updates.feed_url

                if not await RSS.exists(source_id=str(publication.id).split("/")[-1]):
                    model = await RSS.create(
                        feed_url=feed_url,
                        source_id=str(publication.id).split("/")[-1],
                        title=publication.title,
                        img_url=channel_img_url,
                        clean_title_detail=await html_text_regex_cleaner(publication.title),
                        title_detail=publication.title_detail,
                        url=publication.guid,
                        description=publication.description,
                        content=publication.content[0]['value'],
                        clear_content=await html_text_regex_cleaner(publication.content[0]['value']),
                        published=publication.published,
                        published_parsed=publication.published_parsed,
                    )

                else:
                    model = await RSS.get(source_id=str(publication.id).split("/")[-1])

                data = {
                    "id": model.id,
                    "source_id": model.source_id,
                    "title": model.title,
                    "content": publication.content[0]['value'],
                    "clean_content": model.clear_content,
                    "feed_url": await feed_url.serialize(),
                    "img_url": model.img_url,
                    "url": model.url,
                }
                await sender.send(data)

            except AttributeError:
                pass
