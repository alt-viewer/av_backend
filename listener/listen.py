from entities.character import Character
import toolz.curried as toolz
import aiohttp
import asyncio
from datetime import datetime, timedelta
import logging

from queries import get_character, query
from entities import Character

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

# placeholder
db: dict[str, Character] = {}

get_id = toolz.get_in(["character_id"])

logging.basicConfig(level=logging.DEBUG)
socket_logger = logging.getLogger("websocket")
character_logger = logging.getLogger("characters")


@toolz.curry
async def handle_character(session: aiohttp.ClientSession, payload: dict) -> None:
    id = get_id(payload)
    char = db.get(id)
    # Ignore spam logins
    if char:
        # Using the payload's timestamp so that delays in executing
        # this coroutine don't affect this calculation.
        delta = datetime.fromtimestamp(payload["timestamp"]) - char.last_login
        if delta < timedelta(minutes=15):
            return character_logger.info(
                f"Ignored character {id}. Time since last login: {delta}"
            )

    # Update the character if they're new or it's been a
    # while since they last logged in.
    db[id] = await get_character(session, id)
    character_logger.info(f"Added new character {id}")


def is_login_event(payload: dict) -> bool:
    return payload.get("event_name") == "PlayerLogin"


async def log_db():
    while True:
        character_logger.debug(f"Current database: {db}")
        await asyncio.sleep(15)


class LoginListener:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.handle_char = handle_character(session)
        self.run = True
        self.queue: dict[str, asyncio.Task] = {}

    async def listen(self):
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
                    self.queue_char(payload)

    def queue_char(self, payload: dict) -> None:
        """Add a character to the queue. Cancel existing entries for that character."""
        id = get_id(payload)
        if id in self.queue:
            character_logger.debug(f"Cancelled request for {id}")
            self.queue[id].cancel()
        coro = self.handle_char(payload)
        task = asyncio.create_task(coro)
        self.queue[id] = task
        character_logger.debug(f"Queued character {id}")

    async def stop(self):
        self.run = False
