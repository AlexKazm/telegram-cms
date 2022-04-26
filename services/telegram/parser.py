import aiohttp
import asyncio
import async_timeout
import feedparser

import pprint

INTERVAL = 60


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


async def fetchfeeds(loop, feedurls):
    for feed in feedurls:
        async with aiohttp.ClientSession(loop=loop) as session:
            html = await fetch(session, feed)
            rss = feedparser.parse(html)
            print(rss)
            # if rss_feed['last']:
            #     if rss_feed['last']['title'] != rss['entries'][0]['title'] and rss_feed['last']['link'] != \
            #             rss['entries'][0]['link']:
            #         print("new entry")
            #         rss_feed['last'] = rss['entries'][0]
            #
            #         print("MSG {}".format(rss_feed['last']['title']))
            #         print("MSG {}".format(rss_feed['last']['link']))
            # else:
            #     rss_feed['last'] = rss['entries'][0]

    await asyncio.sleep(INTERVAL)


loop = asyncio.get_event_loop()
loop.run_until_complete(fetchfeeds(loop, [
    'https://inform-ua.info/feed/rss/ukraine'
]))
