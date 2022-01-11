from aiohttp import ClientSession
from listener.listen import LoginListener
import asyncio


async def main():
    async with ClientSession() as session:
        listener = LoginListener(session)
        await listener.listen()


asyncio.run(main())
