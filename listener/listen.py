from entities.character import Character
import toolz.curried as toolz
import aiohttp
import asyncio
import logging
from queue import Queue
from typing import Callable, Awaitable

from queries import query
from entities import Character
from listener.queue import RequestQueue
from listener.dispatch import Dispatch
from listener.subscribe import subscription, with_worlds, with_events, LIVE_WORLDS

# Listening to player logins
PAYLOAD = toolz.pipe(
    {}, subscription, with_worlds(LIVE_WORLDS), with_events(["PlayerLogin"])
)

socket_logger = logging.getLogger("websocket")
character_logger = logging.getLogger("character")


class LoginListener:
    def __init__(self, session: aiohttp.ClientSession, dispatch: Dispatch):
        """
        func is an async function that will be called on LoginPayloads.
        It should perform a side effect on the data.
        """
        self.session = session
        self.dispatch = dispatch
        self.run = True

    async def listen(self):
        """
        This is the main loop of the listener. It will listen to the
        login event stream and call the given function on login payloads.
        """
        url = query(websocket=True)
        async with self.session.ws_connect(url) as ws:
            await ws.send_json(PAYLOAD)  # Subscribe to logins
            socket_logger.info("Created websocket connection")
            while self.run:
                res = await ws.receive_json()
                socket_logger.debug(f"Received new payload: {res}")
                payload = res.get("payload")
                # Ignore status updates
                if not payload:
                    continue

                self.dispatch(res)

    async def stop(self):
        self.run = False
