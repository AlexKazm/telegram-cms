from enum import IntEnum
from typing import Optional, List

from tortoise import fields
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.exceptions import DoesNotExist, OperationalError
from pydantic import BaseModel

from services.core.models import AbstractBaseModel, TimestampedMixin
from services.core.enums import Database
from services.core.utils import generator

from services.feed.enums import FeedType


class IDFeedUrlRequest(BaseModel):
    id: int


class URLFeedUrlRequest(BaseModel):
    url: str


class FeedUrl(AbstractBaseModel, TimestampedMixin):
    url = fields.CharField(
        max_length=2014,
        default=None,
        null=True,
        blank=True,
        unique=True
    )

    def __str__(self):
        return f"{self.__repr__()} attrs: {self.__dict__}"

    class Meta:
        table = 'FeedUrl'
        default_connection = Database.telegramcms.name

    class FeedUrlSerializer(BaseModel):
        id: int
        url: Optional[str]

    serializer = FeedUrlSerializer

    @staticmethod
    async def try_get(id: int):
        try:
            return True, await FeedUrl.get(id=id)
        except DoesNotExist as details:
            return False, f"{details}"

    async def serialize(self):
        return self.serializer(
            id=self.id,
            url=self.url
        )

    async def deserialize(model: serializer):
        result, details = await FeedUrl.try_get(id=model.id)
        return result, details

    @staticmethod
    async def delete_with_result(id: int):
        result, details = await FeedUrl.try_get(id=id)
        if type(details) == FeedUrl:
            try:
                details: FeedUrl
                await details.delete()
                return True, "Deleted"

            except OperationalError as details:
                return False, f"{details}"
        else:
            return result, details

    @staticmethod
    async def update_with_result(selialized_data: serializer):
        result, details = await FeedUrl.deserialize(selialized_data)
        if type(details) == FeedUrl:
            details: FeedUrl
            data: dict = selialized_data.dict()
            data.pop('id')

            await details.update_from_dict(data)
            await details.save()
            return True, await details.serialize()
        else:
            return result, details

    @staticmethod
    async def get_from_list(urls: List[URLFeedUrlRequest]):
        response: List[FeedUrl] = []
        async for url in generator(urls):
            model: FeedUrl = await FeedUrl.get_or_create(url=url.url)
            response.append(model[0])
        return response


class FeedRequest(BaseModel):
    type: str
    urls: Optional[List[URLFeedUrlRequest]]
    is_active: Optional[bool]
    is_empty: Optional[bool]


class Feed(AbstractBaseModel, TimestampedMixin):
    type: FeedType = fields.CharEnumField(FeedType)

    urls = fields.JSONField(
        default=None,
        null=True
    )

    feeds = fields.JSONField(
        default=None,
        null=True
    )

    is_active: bool = fields.BooleanField(
        default=False,
        null=True
    )

    is_empty: bool = fields.BooleanField(
        default=None,
        null=True
    )

    class Meta:
        table = 'Feed'
        default_connection = Database.telegramcms.name

    class FeedSerializer(BaseModel):
        id: int
        type: str
        urls: Optional[List[FeedUrl.serializer]]
        is_active: Optional[bool]
        is_empty: Optional[bool]

    serializer = FeedSerializer

    def __str__(self):
        return f"{self.__repr__()} attrs: {self.__dict__}"

    async def get_urls(self) -> List[FeedUrl]:
        result: List[FeedUrl] = []
        async for urls in generator(self.urls):
            result.append(await FeedUrl.get(**urls))

        return result

    async def serialize(self):
        return self.serializer(
            id=self.id,
            type=str(self.type),
            urls=self.urls,
            is_active=self.is_active,
            is_empty=self.is_empty
        )

    async def save(
            self, using_db: Optional[BaseDBAsyncClient] = None,
            update_fields: Optional[List[str]] = None) -> None:
        if not self.urls:
            self.is_empty = True
            self.is_active = False

        return await super(Feed, self).save(using_db, update_fields)


class RSS(AbstractBaseModel, TimestampedMixin):
    feed_url: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "telegramcms.FeedUrl",
        null=True,
        default=None,
    )
    source_id = fields.CharField(index=True, max_length=64, default=None, null=True)
    title = fields.CharField(index=True, max_length=256, default=None, null=True)
    img_url = fields.CharField(max_length=1024, default=None, null=True)
    clean_title_detail = fields.CharField(index=True, max_length=512, default=None, null=True)
    title_detail = fields.JSONField(default=None, null=True)
    url = fields.CharField(max_length=1024, default=None, null=True)
    description = fields.TextField(default=None, null=True)
    content = fields.TextField(default=None, null=True)
    clear_content = fields.TextField(default=None, null=True)
    published = fields.CharField(max_length=256, default=None, null=True)
    published_parsed = fields.CharField(max_length=256, default=None, null=True)

    async def serialize(self):
        return self.serializer(
            id=self.id,
            title=self.title
        )

    class RSSSerializer(BaseModel):
        feed_url: Optional[FeedUrl.serializer]
        id: Optional[int]
        source_id: Optional[str]
        title: str
        img_url: Optional[str]
        title_detail: Optional[dict]
        clean_title_detail: Optional[str]
        url: Optional[str]
        description: Optional[str]
        content: Optional[str]
        clear_content: Optional[str]
        published: Optional[str]
        published_parsed: Optional[str]

    serializer = RSSSerializer

    class Meta:
        table = 'RSS'
        default_connection = Database.telegramcms.name

    def __str__(self):
        return f"{self.__repr__()}"
