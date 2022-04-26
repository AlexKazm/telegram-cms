import hashlib

from typing import List, Optional

from pydantic import BaseModel
from tortoise import fields
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.exceptions import IntegrityError

from services.core.models import TimestampedMixin, AbstractBaseModel
from services.core.enums import Database
from services.telegram.enums import DataSubscriptionType
from services.core.utils import generator
from services.feed.models import FeedUrl


class TelegramApplication(AbstractBaseModel, TimestampedMixin):
    config = fields.JSONField(
        default=None, null=True, blank=True)

    is_online = fields.BooleanField(
        default=False, null=True
    )

    is_active = fields.BooleanField(
        default=True,
        null=True,
        blank=True
    )

    class Meta:
        table = 'TelegramApplication'
        default_connection = Database.telegramcms.name

    class Serializer(BaseModel):
        id: Optional[int]
        config: Optional[dict]

    serializer = Serializer

    def __str__(self):
        return str(self.__repr__())

    # async def save(
    #         self, using_db: Optional[BaseDBAsyncClient] = None,
    #         update_fields: Optional[List[str]] = None) -> None:
    #     if not bool(self.config['workers']):
    #         self.config['workers'] = 1
    #     return await super(TelegramApplication, self).save(using_db, update_fields)


class DefaultDataSubscription(AbstractBaseModel, TimestampedMixin):
    source_name = fields.CharField(
        default=None, null=True, blank=True, max_length=255)
    source_url = fields.CharField(
        default=None, null=True, blank=True, max_length=512)
    subscriber_type = fields.IntEnumField(
        enum_type=DataSubscriptionType, default=DataSubscriptionType.telegram, null=True)
    subscriber_data = fields.JSONField(
        default=True, null=True)
    content_hash = fields.CharField(
        default=None, null=True, blank=True, max_length=512)

    class Meta:
        table = 'DefaultDataSubscription'
        default_connection = Database.telegramcms.name

    def __str__(self):
        return str(self.__repr__())

    async def is_match_hashes(self, content_data: dict):
        if hash(hashlib.md5(bytes(content_data)).hexdigest()) == hash(self.content_hash):
            return True
        return False

    @staticmethod
    async def filter_rss_subscriptions_by_url(data: FeedUrl.serializer):
        feed_url: FeedUrl.serializer = data['feed_url']
        content: dict = data['content']
        subscriptions: List[DefaultDataSubscription] = await DefaultDataSubscription.filter(
            source_url=feed_url
        )

        async for subscription in generator(subscriptions):
            subscription: DefaultDataSubscription
            if await subscription.is_match_hashes(content):
                subscriptions.remove(subscription)

        return subscriptions

    async def save(
            self, using_db: Optional[BaseDBAsyncClient] = None,
            update_fields: Optional[List[str]] = None) -> None:
        if not self.content_hash:
            self.content_hash = hashlib.md5(bytes(self.subscriber_data)).hexdigest()
        return await super(DefaultDataSubscription, self).save(using_db, update_fields)


class TelegramInvitedUser(AbstractBaseModel, TimestampedMixin):
    user_id = fields.IntField(
        default=None, null=True, blank=True, unique=False
    )

    chat_username = fields.CharField(
        default=None, null=True, blank=True, unique=False, max_length=512
    )

    with_error = fields.BooleanField(default=False, null=True)
    success = fields.BooleanField(default=True, null=True)

    error = fields.CharField(max_length=512, defaut=None, null=True)

    class Meta:
        table = 'TelegramInvitedUser'
        default_connection = Database.telegramcms.name

    def __str__(self):
        return str(self.__repr__())

    async def try_create(user_id: int, chat_username: str, with_error: bool = None,
                         success: bool = None, error: str = None):
        try:
            await TelegramInvitedUser.create(
                user_id=user_id, chat_username=chat_username, with_error=with_error,
                success=success, error=error
            )
        except IntegrityError:
            pass


class TelegramUser(AbstractBaseModel, TimestampedMixin):
    user_id = fields.IntField(
        default=None, null=True, blank=True, unique=True
    )
    data = fields.JSONField(
        default=None, null=True, blank=True
    )

    async def is_already_invited_to(self, chat_username: str):
        if await TelegramInvitedUser.exists(user_id=self.user_id, chat_username=chat_username):
            return True
        else:
            return False

    async def get_username(self):
        if self.data['username']:
            return self.data['username']
        else:
            return None

    async def get_phone(self):
        if self.data['phone']:
            return self.data['phone']
        else:
            return None

    class Meta:
        table = 'TelegramUser'
        default_connection = Database.telegramcms.name

    def __str__(self):
        return str(self.__repr__())

    async def save(
            self, using_db: Optional[BaseDBAsyncClient] = None,
            update_fields: Optional[List[str]] = None, force_create: bool = False,
            force_update: bool = False, ) -> None:
        if not await TelegramUser.exists(user_id=self.user_id):
            return await super(TelegramUser, self).save(
                using_db=using_db, update_fields=update_fields,
                force_create=force_create, force_update=force_update)

        return await TelegramUser.get(user_id=self.user_id)


class TelegramMessage(AbstractBaseModel, TimestampedMixin):
    message_id = fields.IntField(
        default=None, null=False, blank=False)

    date = fields.DatetimeField(
        default=None, null=True, blank=True)

    text = fields.TextField(
        default=None, null=True, blank=True)

    chat = fields.JSONField(
        default=None, null=True, blank=True)

    from_user = fields.JSONField(
        default=None, null=True, blank=True)

    photo = fields.JSONField(
        default=None, null=True, blank=True)

    media = fields.IntField(
        default=None, null=True, blank=True)

    audio = fields.JSONField(
        default=None, null=True, blank=True)

    document = fields.JSONField(
        default=None, null=True, blank=True)

    sticker = fields.JSONField(
        default=None, null=True, blank=True)

    animation = fields.JSONField(
        default=None, null=True, blank=True)

    game = fields.JSONField(
        default=None, null=True, blank=True)

    video = fields.JSONField(
        default=None, null=True, blank=True)

    voice = fields.JSONField(
        default=None, null=True, blank=True)

    video_note = fields.JSONField(
        default=None, null=True, blank=True)

    caption = fields.JSONField(
        default=None, null=True, blank=True)

    contact = fields.JSONField(
        default=None, null=True, blank=True)

    location = fields.JSONField(
        default=None, null=True, blank=True)

    venue = fields.JSONField(
        default=None, null=True, blank=True)

    web_page = fields.JSONField(
        default=None, null=True, blank=True)

    dice = fields.JSONField(
        default=None, null=True, blank=True)

    new_chat_members = fields.TextField(
        default=None, null=True, blank=True)

    left_chat_member = fields.JSONField(
        default=None, null=True, blank=True)

    new_chat_title = fields.CharField(
        max_length=255, default=None, null=True, blank=True)

    new_chat_photo = fields.TextField(
        default=None, null=True, blank=True)

    delete_chat_photo = fields.BooleanField(
        default=None, null=True, blank=True)

    group_chat_created = fields.BooleanField(
        default=None, null=True, blank=True)

    supergroup_chat_created = fields.BooleanField(
        default=None, null=True, blank=True)

    channel_chat_created = fields.BooleanField(
        default=None, null=True, blank=True)

    migrate_to_chat_id = fields.IntField(
        default=None, null=True, blank=True)

    migrate_from_chat_id = fields.IntField(
        default=None, null=True, blank=True)

    pinned_message = fields.JSONField(
        default=None, null=True, blank=True)

    game_high_score = fields.JSONField(
        default=None, null=True, blank=True)

    via_bot = fields.BooleanField(
        default=None, null=True)

    matches = fields.JSONField(
        default=None, null=True, blank=True)

    command = fields.CharField(
        max_length=255, default=None, null=True, blank=True)

    media_group_id = fields.CharField(
        max_length=255, default=None, null=True, blank=True)

    views = fields.IntField(
        default=None, null=True, blank=False)

    forward_from = fields.JSONField(
        default=None, null=True, blank=True)

    forward_sender_name = fields.CharField(
        max_length=255, default=None, null=True, blank=True)

    forward_from_chat = fields.JSONField(
        default=None, null=True, blank=True)

    forward_from_message_id = fields.IntField(
        default=None, null=True, blank=True)

    forward_signature = fields.CharField(
        max_length=255, default=None, null=True, blank=True)

    forward_date = fields.DatetimeField(
        default=None, null=True, blank=True)

    reply_to_message = fields.JSONField(
        default=None, null=True, blank=True)

    author_signature = fields.CharField(
        max_length=1024, default=None, null=True, blank=True)

    edit_date = fields.DatetimeField(
        default=None, null=True, blank=True)

    entities = fields.TextField(
        default=None, null=True, blank=True)

    caption_entities = fields.CharField(
        max_length=1024, default=None, null=True, blank=True)

    reply_markup = fields.JSONField(
        default=None, null=True, blank=True)

    is_mentioned = fields.BooleanField(
        default=None, null=True)

    is_empty = fields.BooleanField(
        default=None, null=True)

    service = fields.BooleanField(
        default=None, null=True)

    is_scheduled = fields.BooleanField(
        default=None, null=True)

    is_from_scheduled = fields.BooleanField(
        default=None, null=True)

    is_outgoing = fields.BooleanField(
        default=None, null=True)

    class Meta:
        table = 'TelegramMessage'
        default_connection = Database.telegramcms.name

    def __str__(self):
        return str(self.__repr__())
