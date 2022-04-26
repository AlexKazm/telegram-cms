from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from services.telegram.models import TelegramMessage, TelegramApplication

TelegramMessageAPIModel = pydantic_model_creator(TelegramMessage)
TelegramApplicationAPIModel = pydantic_model_creator(TelegramApplication)


class TransportMessage(BaseModel):
    message: List[dict]


class TransportResponse(BaseModel):
    status: Optional[str]


class Application(BaseModel):
    session_name: str
    api_id: int
    api_hash: str
    app_version: Optional[str]
    device_model: Optional[str]
    system_version: Optional[str]
    lang_code: Optional[str]
    bot_token: Optional[str]
    workers: Optional[int] = 1
    workdir: Optional[str] = 'services/telegram/sessions/'
    phone_number: Optional[str]
    phone_code: Optional[str]
    password: Optional[str]
    force_sms: Optional[bool]
    ipv6: Optional[bool]
    proxy: Optional[dict]
    test_mode: Optional[bool]
    no_updates: Optional[bool]
    takeout: Optional[bool]


class Message(BaseModel):
    message_id: int
    date: datetime
    chat: Optional[dict]
    from_user: Optional[dict]
    phone_number: Optional[str]
    forward_from: Optional[dict]
    forward_sender_name: Optional[str]
    forward_from_chat: Optional[dict]
    forward_from_message_id: Optional[str]
    forward_signature: Optional[str]
    forward_date: Optional[datetime]
    reply_to_message: Optional[dict]
    is_mentioned: Optional[bool]
    is_empty: Optional[bool]
    service: Optional[bool]
    is_scheduled: Optional[bool]
    is_from_scheduled: Optional[bool]
    media: Optional[int]
    author_signature: Optional[str]
    edit_date: Optional[datetime]
    entities: Optional[list]
    caption_entities: Optional[str]
    audio: Optional[dict]
    document: Optional[dict]
    photo: Optional[dict]
    sticker: Optional[dict]
    animation: Optional[dict]
    game: Optional[dict]
    video: Optional[dict]
    voice: Optional[dict]
    video_note: Optional[str]
    caption: Optional[str]
    contact: Optional[str]
    location: Optional[str]
    venue: Optional[str]
    web_page: Optional[str]
    poll: Optional[dict]
    dice: Optional[dict]
    new_chat_members: Optional[list]
    left_chat_member: Optional[dict]
    new_chat_title: Optional[str]
    new_chat_photo: Optional[str]
    delete_chat_photo: Optional[bool]
    group_chat_created: Optional[bool]
    supergroup_chat_created: Optional[bool]
    channel_chat_created: Optional[bool]
    migrate_to_chat_id: Optional[int]
    migrate_from_chat_id: Optional[int]
    pinned_message: Optional[dict]
    game_high_score: Optional[dict]
    via_bot: Optional[bool]
    matches: Optional[dict]
    command: Optional[str]
    media_group_id: Optional[str]
    text: Optional[str]
    views: Optional[int]
    is_outgoing: Optional[bool]
    reply_markup: Optional[dict]
