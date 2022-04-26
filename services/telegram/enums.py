from enum import Enum, IntEnum


class CallbackResult(IntEnum):
    SUCCESS = 1
    FAILED = 2


class ChatType(Enum):
    CHANNEL = "channel"
    PRIVATE = "private"


class DataSubscriptionType(IntEnum):
    telegram = 1
    instagram = 2
