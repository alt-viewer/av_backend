import logging
from sys import getsizeof
from math import ceil
from aiohttp import ClientSession
import toolz.curried as toolz
from datetime import datetime, timedelta
import asyncio

from entities import Character
from payloads import LoginPayload
from queries import get_character

# placeholder
db: dict[int, Character] = {}
character_logger = logging.getLogger("characters")


get_id = toolz.get_in(["character_id"])


async def log_db():
    while True:
        character_logger.info(f"{len(db)} characters recorded. Memory used: {size(db)}")
        await asyncio.sleep(15)


def size(obj) -> str:
    in_bytes = getsizeof(obj)
    a = 0
    acc: float = in_bytes
    suffixes = ("kB", "MB", "GB", "TB")
    while acc > 1000:
        a += 1
        acc = acc / 1000
    return f"{ceil(acc)}{suffixes[a]}"


# TODO: batch the character queries
@toolz.curry
async def handle_character(session: ClientSession, payload: LoginPayload) -> None:
    id = payload.character_id
    char = db.get(id)
    # Ignore spam logins
    if char:
        # Using the payload's timestamp so that delays in executing
        # this coroutine don't affect this calculation.
        delta = datetime.fromtimestamp(payload.timestamp) - char.last_login
        if delta < timedelta(minutes=15):
            return character_logger.info(
                f"Ignored character {id}. Time since last login: {delta}"
            )

    # Update the character if they're new or it's been a
    # while since they last logged in.
    try:
        db[id] = await get_character(session, str(id))
        character_logger.info(f"Added new character {id}")
    except ValueError as e:  # Ignore characters that don't have items
        character_logger.debug(f"Ignored {id} due to no items")
