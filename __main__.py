from aiohttp import ClientSession
import asyncio
import toolz.curried
from logging import getLogger
import sys

from listener import LoginListener, CharacterQueue
from queries import get_characters
from database import push_db, log_db
from logger import with_logger


async def main():
    async with ClientSession() as session:
        # Create dependencies of the listener
        getter = toolz.curry(get_characters)(session)
        queue = CharacterQueue(getter, push_db)
        listener = LoginListener(session, queue)

        # Logging tasks
        asyncio.create_task(log_db())

        try:
            await listener.listen()
        except KeyboardInterrupt:
            await listener.stop()
            sys.exit(0)


asyncio.run(main())
