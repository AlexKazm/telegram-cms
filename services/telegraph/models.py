from typing import List, Optional

from pydantic import BaseModel
from tortoise import fields

from services.core.models import TimestampedMixin, AbstractBaseModel
from services.core.enums import Database


class TelegraphPage(AbstractBaseModel, TimestampedMixin):
    title = fields.CharField(
        default=None, null=True, index=True, max_length=512
    )

    url = fields.CharField(
        default=None, null=True, index=True, max_length=1024
    )

    class Meta:
        table = 'TelegraphPage'
        default_connection = Database.telegramcms.name

    class Serializer(BaseModel):
        id: Optional[int]
        title: Optional[str]
        url: Optional[str]

    serializer = Serializer

    def __str__(self):
        return str(self.__repr__())


class TelegraphAccount(AbstractBaseModel, TimestampedMixin):
    # https://telegra.ph/api#editAccountInfo
    short_name = fields.CharField(
        default=None, null=True, index=True, max_length=32
    )

    author_name = fields.CharField(
        default=None, null=True, index=True, max_length=128
    )

    author_url = fields.CharField(
        default=None, null=True, index=True, max_length=512
    )

    access_token = fields.CharField(
        default=None, null=True, index=True, max_length=128
    )

    auth_url = fields.CharField(
        default=None, null=True, index=True, max_length=512
    )

    class Meta:
        table = 'TelegraphAccount'
        default_connection = Database.telegramcms.name

    class Serializer(BaseModel):
        id: Optional[int]
        short_name: Optional[str]
        author_name: Optional[str]
        author_url: Optional[str]
        access_token: Optional[str]
        auth_url: Optional[str]

    class ContentSerializer(BaseModel):
        # https://telegra.ph/api#NodeElement
        tag: Optional[str]
        children: List[str]
        attrs: Optional[dict]

    serializer = Serializer

    def __str__(self):
        return str(self.__repr__())
