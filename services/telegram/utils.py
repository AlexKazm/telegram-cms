import json

from pyrogram import Client, Message as PyrogramMessage

from services.core.utils import logger
from services.telegram.enums import CallbackResult
from services.telegram.api.models import Message


async def telegram_logger(message):
    await logger(f" [telegram]: {message}")


class MessageParser:

    @staticmethod
    async def del_attr_by_key(data, key):
        for attr in json.loads(json.dumps(data)):
            if type(data[attr]) == dict:
                await MessageParser.del_attr_by_key(data[attr], key)

            if attr == key:
                data.pop(attr)

        return data

    @staticmethod
    async def parse(message: PyrogramMessage, client_session: Client, controller):
        callback = controller.callback

        json_data: dict = json.loads(str(message))
        json_data = await MessageParser.del_attr_by_key(json_data, "_")

        try:
            await callback(controller, CallbackResult.SUCCESS, Message(**json_data))
        except Exception as e:
            await callback(controller, CallbackResult.FAILED, message, e)
