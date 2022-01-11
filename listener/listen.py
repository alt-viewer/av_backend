from entities.character import Character
import toolz.curried as toolz
import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging
from sys import getsizeof
from math import ceil
from typing import Callable, Coroutine

from queries import get_character, query
from entities import Character
from payloads import LoginPayload
from listener.handle_char import handle_character, get_id, character_logger, log_db

PAYLOAD = {
    "service": "event",
    "action": "subscribe",
    "worlds": [
        "1",  # Connery
        "10",  # Miller
        "13",  # Cobalt
        "17",  # Emerald
        "40",  # Soltech
    ],
    "eventNames": ["PlayerLogin"],
}
logging.basicConfig(level=logging.DEBUG)
socket_logger = logging.getLogger("websocket")


def is_login_event(payload: dict) -> bool:
    return payload.get("event_name") == "PlayerLogin"


class LoginListener:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        func: Callable[[LoginPayload], Coroutine[None, None, None]],
    ):
        """
        func is an async function that will be called on LoginPayloads.
        It should perform a side effect on the data.
        """
        self.session = session
        self.handle_char = handle_character(session)
        self.run = True
        self.queue: dict[int, asyncio.Task] = {}
        self.func = func

    async def listen(self):
        """
        This is the main loop of the listener. It will listen to the
        login event stream and call the given function on login payloads.
        """
        url = query(websocket=True)
        asyncio.create_task(log_db())
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

                if is_login_event(payload):
                    self.queue_char(LoginPayload(**payload))

    def queue_char(self, payload: LoginPayload) -> None:
        """Add a character to the queue. Cancel existing entries for that character."""
        id = payload.character_id
        if id in self.queue:
            character_logger.debug(f"Cancelled request for {id}")
            self.queue[id].cancel()
        coro = self.func(payload)
        task = asyncio.create_task(coro)
        self.queue[id] = task
        character_logger.debug(f"Queued character {id}")

    async def stop(self):
        self.run = False
