from telegraph import Telegraph
from tortoise.transactions import in_transaction

from services.telegraph.models import TelegraphPage
from services.telegraph.plugins import TelegraphPlugin
from services.core.enums import Database
from services.core.utils import generator


class TelegraphController:
    @staticmethod
    async def create_page(title: str, html: str):
        async with in_transaction(Database.telegramcms.name) as connection:
            query = 'select title, url from "TelegraphPage" order by -id limit 5'
            q_len, q_result = await connection.execute_query(query)

        last_pages = []
        [last_pages.append(page) async for page in generator(q_result) if q_result]

        page_url = await TelegraphPlugin.create_page(title=title, html=html, last_pages=last_pages)

        # await TelegraphPage.create(
        #     title=title,
        #     url=page_url
        # )
        return page_url
