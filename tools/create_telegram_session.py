import asyncio

from pyrogram import Client

# cli = Client(
#     session_name="Izek",
#     api_id=1737210,
#     api_hash="44e646caaffef74ccbeca02e083ce0b1",
#     workdir="services/telegram/sessions")

# +44 7308 370209
# client = Client(
#     session_name='DanWashington', api_id=1548046, api_hash="86fd19337fbdafe5d375d66830cd5953", workdir="services/telegram/sessions",
#     app_version='Telegram macOS 7.0 (204345) STABLE', device_model='MacBook Pro, macOS 10.12.6',
#     system_version='Darwin 16.7.0',lang_code='en'
#     )

# +44 7366 202498 # App title= OSXDefaultNode4
# client = Client(
#     session_name='Scorp', api_id=1699233, api_hash="6142bd9b9695935143386e14b771aed8", workdir="services/telegram/sessions",
#     app_version='Telegram macOS 7.0 (204345) STABLE', device_model='MacBook Pro, macOS 10.12.6',
#     system_version='Darwin 16.7.0',lang_code='en'
#     )

# +44 7723 486513 # App title= OSXDefaultNode4
# client = Client(
#     session_name='Crystopher',
#     api_id=1608399,
#     api_hash="93aedb282ae2b7c009aab039560f906d",
#     workdir="services/telegram/sessions",
#     app_version='Telegram macOS 7.0 (204345) STABLE',
#     device_model='MacBook Pro, macOS 10.12.6',
#     system_version='Darwin 16.7.0',
#     lang_code='en'
#     )

# +44 7735 608996 # App title= OSXDefaultNode4
client = Client(
    session_name='JohnBelsh',
    api_id=1557702,
    api_hash="37a06f9cda1531032f0278bdc7a15457",
    workdir="services/telegram/sessions",
    app_version='Telegram macOS 7.0 (204345) STABLE',
    device_model='MacBook Pro, macOS 10.12.6',
    system_version='Darwin 16.7.0',
    lang_code='en'
    )

loop = asyncio.get_event_loop()
loop.run_until_complete(client.start())
