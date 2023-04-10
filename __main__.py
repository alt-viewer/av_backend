import aiohttp
import asyncio
import toolz.curried
import sys
from toolz import curry
from dotenv import load_dotenv


from listener import LoginListener, event_reducer
from census import get_characters
from database import log_task, push_chars, sessions
from logger import with_logger


async def main():
    load_dotenv()
    async with sessions() as (asession, db):
        # Create dependencies of the listener
        dispatch = event_reducer(asession, db)
        listener = LoginListener(asession, dispatch)

        try:
            await listener.listen()
        except KeyboardInterrupt:
            await listener.stop()
            sys.exit(0)


asyncio.run(main())
