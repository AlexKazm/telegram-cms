from enum import Enum

from pydantic import BaseModel


class TransportMessageEventType(Enum):
    updates = 'updates'


class DefaultTransportMessageEvent(BaseModel):
    type: TransportMessageEventType = TransportMessageEventType.updates
    args: dict
