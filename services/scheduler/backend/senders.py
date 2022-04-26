from services.core.backend.transport import RPCRequest, RPCAPITransport
from services.core.backend.events import DefaultTransportMessageEvent


class DefaultSchedulerSender:
    @staticmethod
    async def send(message: dict):
        async with RPCAPITransport() as rpc:
            await rpc.send(
                service_url=rpc.scheduler,
                request=RPCRequest(
                    function='spawn',
                    event=DefaultTransportMessageEvent(
                        args={
                            "data": message
                        }
                    )
                )
            )
