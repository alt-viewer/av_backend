from entities.character import Character
import toolz.curried as toolz
import aiohttp
import asyncio
import logging
from queue import Queue
from typing import Callable, Awaitable

from queries import query
from entities import Character
from payloads import LoginPayload
from listener.character_queue import CharacterQueue

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

socket_logger = logging.getLogger("websocket")
character_logger = logging.getLogger("character")


def is_login_event(payload: dict) -> bool:
    return payload.get("event_name") == "PlayerLogin"


class LoginListener:
    def __init__(self, session: aiohttp.ClientSession, queue: "CharacterQueue"):
        """
        func is an async function that will be called on LoginPayloads.
        It should perform a side effect on the data.
        """
        self.session = session
        self.queue = queue
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

                if is_login_event(payload):
                    self.queue_char(LoginPayload(**payload))

    def queue_char(self, payload: LoginPayload) -> None:
        """Add a character to the queue"""
        id = payload.character_id
        asyncio.create_task(self.queue.add(id))
        character_logger.debug(f"Queued character {id}")

    async def stop(self):
        self.run = False
