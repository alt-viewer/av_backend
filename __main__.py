import aiohttp
import asyncio
import toolz.curried
import sys
import gql
from toolz import curry
from dotenv import load_dotenv


from listener import LoginListener, event_reducer
from census import get_characters
from database import log_task, push_chars, get_sessions
from logger import with_logger

API_URL = "http://localhost:8080/graphql"


async def main():
    load_dotenv()
    async with get_sessions(API_URL) as (asession, db):
        # Create dependencies of the listener
        dispatch = event_reducer(asession, db)
        listener = LoginListener(asession, dispatch)

        try:
            await listener.listen()
        except KeyboardInterrupt:
            await listener.stop()
            sys.exit(0)


asyncio.run(main())
