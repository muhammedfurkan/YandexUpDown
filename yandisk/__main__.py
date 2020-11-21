
import asyncio
import importlib
from logging import WARN, basicConfig, getLogger
from os import environ

from . import client
from .commands import ALL_COMMANDS

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=WARN)

loop = asyncio.get_event_loop()


async def main():
    await client.start(bot_token=environ.get("BOT_TOKEN"))
    for command in ALL_COMMANDS:
        importlib.import_module("yandisk.commands." + command)

loop.run_until_complete(main())
loop.run_forever()
