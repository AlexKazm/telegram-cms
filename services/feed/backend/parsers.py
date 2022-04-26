import feedparser


class DefaultRSSParser:

    @staticmethod
    async def parse_raw(rss: str):
        rss: feedparser.FeedParserDict = feedparser.parse(rss)
        return rss
