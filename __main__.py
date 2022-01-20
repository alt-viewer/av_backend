from aiohttp import ClientSession
import asyncio
import toolz.curried
from logging import getLogger

from listener import LoginListener, CharacterQueue
from queries import get_characters
from database import push_db, log_db
from logger import with_logger


async def main():
    char_logger = getLogger("characters")
    async with ClientSession() as session:
        curried_getter = toolz.curry(get_characters)(session)
        getter = with_logger(char_logger, "Requesting characters {1}")(curried_getter)
        listener = LoginListener(session, CharacterQueue(getter, push_db))
        asyncio.create_task(log_db())
        await listener.listen()


asyncio.run(main())
