import aiohttp
import asyncio
import toolz.curried
import sys
import gql
from toolz import curry


from listener import LoginListener, event_reducer
from av_backend.queries import get_characters
from av_backend.database import log_task, push_chars, GQLTransport, get_sessions
from av_backend.logger import with_logger

API_URL = "http://localhost:8080/graphql"


async def main():
    async with get_sessions(API_URL) as (asession, gsession):
        # Create dependencies of the listener
        dispatch = event_reducer(asession, gsession)
        listener = LoginListener(asession, dispatch)

        # Logging tasks
        asyncio.create_task(log_task(gsession))

        try:
            await listener.listen()
        except KeyboardInterrupt:
            await listener.stop()
            sys.exit(0)


asyncio.run(main())
