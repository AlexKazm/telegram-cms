from datetime import datetime

from pyrogram import Client, Message as PMessage

from services.telegram.enums import CallbackResult


class ExceptionStatement:
    def __init__(self, result: CallbackResult, message: PMessage, exception: Exception):
        self.result = result
        self.message = message
        self.exception = exception
        self.timestamp = datetime.now()
