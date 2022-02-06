import aiohttp
import asyncio
import toolz.curried
import sys
import gql
from toolz import curry


from listener import LoginListener, CharacterQueue
from queries import get_characters
from database import log_task, push_chars, GQLTransport
from logger import with_logger

API_URL = "http://localhost:8080/graphql"


async def main():
    async with aiohttp.ClientSession() as asession:
        transport = GQLTransport(API_URL, client_session=asession)
        async with gql.Client(transport=transport) as gsession:
            # Create dependencies of the listener
            getter = curry(get_characters)(asession)
            putter = curry(push_chars)(gsession)
            queue = CharacterQueue(getter, putter)
            listener = LoginListener(asession, queue)

            # Logging tasks
            asyncio.create_task(log_task(gsession))

            try:
                await listener.listen()
            except KeyboardInterrupt:
                await listener.stop()
                sys.exit(0)


asyncio.run(main())
