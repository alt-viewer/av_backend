from aiohttp import ClientSession
from listener import LoginListener, handle_characters
import asyncio


async def main():
    async with ClientSession() as session:
        listener = LoginListener(session, handle_characters(session))
        await listener.listen()


asyncio.run(main())
