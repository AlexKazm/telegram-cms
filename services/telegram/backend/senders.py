from services.core.backend.transport import RPCRequest, RPCAPITransport
from services.core.backend.events import DefaultTransportMessageEvent


class DefaultTelegramChannelSender:
    @staticmethod
    async def send(application: str, chat_username: str, message: dict):
        async with RPCAPITransport() as rpc:
            await rpc.send(
                service_url=rpc.telegram,
                request=RPCRequest(
                    function='send_message',
                    event=DefaultTransportMessageEvent(
                        args={
                            "application": application,
                            "chat_username": chat_username,
                            "message": {
                                "body": message['body'],
                                "image": message['image']
                            }
                        }
                    )
                ),

            )
