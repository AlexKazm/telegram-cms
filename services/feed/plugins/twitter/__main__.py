import json
import asyncio
import os
from enum import Enum, IntEnum
from typing import List, Optional

import tweepy
from pydantic import BaseModel
from tortoise import Tortoise

from services.core.utils import generator, database_config
from services.telegram.utils import telegram_logger

AUTOPILOT = True if os.environ.get("FEED_AUTOPILOT") == 'True' else False
consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
loop = asyncio.get_event_loop()


# https://developer.twitter.com/en/application/in-review

class ChannelType(IntEnum):
    tag = 1
    author = 2


class Channel(BaseModel):
    type: ChannelType
    source: str
    is_ready: bool


class MessageType(Enum):
    delete = 1
    post = 2


class Message(BaseModel):
    message_type: MessageType
    id: Optional[int]
    text: Optional[str]
    user: Optional[dict]
    entities: Optional[dict]
    extended_entities: Optional[dict]

    in_reply_to_status_id: Optional[int]
    in_reply_to_status_id_str: Optional[str]
    in_reply_to_user_id: Optional[int]
    in_reply_to_user_id_str: Optional[str]
    in_reply_to_screen_name: Optional[str]

    timestamp_ms: Optional[int]
    created_at: Optional[str]

    delete: Optional[dict]


class TwitterStreamListener(tweepy.StreamListener):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    def on_status(self, status):
        print(status.text)

    def on_connect(self):
        print("connected")

    def on_disconnect(self, notice):
        print("disconnect")

    def on_error(self, status_code):
        print("error")

    def on_exception(self, exception):
        print("exception")

    def on_event(self, status):
        print("event")

    def on_timeout(self):
        print("timeout")

    def on_warning(self, notice):
        print("warning")

    def on_data(self, raw_data):
        data = json.loads(raw_data)

        try:
            assert data['delete'] is not None
            message_type = MessageType.delete
        except KeyError:
            message_type = MessageType.post

        message = Message(message_type=message_type, **data)

        print(
            f"@{message.user['screen_name']}, verified: {message.user['verified']}: {message.text}",
            f"background_image_url: {message.user['profile_background_image_url']}",
            f"avatar_url: {message.user['profile_image_url_https']}",
            # f"banner_url: {message.user['profile_banner_url']}"
            f"entities: {message.entities}",
            f"extended_entities: {message.extended_entities}"
        )

        super(TwitterStreamListener, self).on_data(raw_data)


class StreamController:

    def __init__(self, listener: TwitterStreamListener, channels: List[Channel]):
        self.listener: TwitterStreamListener = listener
        self.stream: tweepy.Stream = tweepy.Stream(auth=TwitterStreamListener.api.auth, listener=listener)
        self.channels: List[Channel] = channels

        self.tracks = []
        self.follows = []

        print(f"--- TwitterStream: {self.stream} inited ---")

    async def run(self):
        await Tortoise.init(database_config)
        await Tortoise.generate_schemas()
        async for channel in generator(self.channels):

            if channel.type == ChannelType.tag:
                self.tracks.append(channel.source)

            elif channel.type == ChannelType.author:
                self.follows.append(channel.source)

        self.stream.filter(follow=self.follows, track=self.tracks, is_async=True)

        await telegram_logger(
            f"--- TwitterStream: {self.stream} {'started' if self.stream.running else 'not started'}---")


user: tweepy.models.User = TwitterStreamListener.api.get_user('ThePSF')

controller = StreamController(
    listener=TwitterStreamListener(),
    channels=[
        Channel(
            type=ChannelType.tag,
            source="#blacklivesmatter",
            is_ready=True
        ),
        Channel(
            type=ChannelType.author,
            source=str(user.id),
            is_ready=True
        )
    ]
)

if AUTOPILOT:
    print(f"--- Twitter Feed service started ---")
    print()

    loop.run_until_complete(controller.run())
