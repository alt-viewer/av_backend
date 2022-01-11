from aiohttp import ClientSession
from listener import LoginListener, handle_character
import asyncio


async def main():
    async with ClientSession() as session:
        listener = LoginListener(session, handle_character(session))
        await listener.listen()


asyncio.run(main())
