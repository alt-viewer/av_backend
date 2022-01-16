import logging
from sys import getsizeof
from math import ceil
from aiohttp import ClientSession
import toolz.curried as toolz
from datetime import datetime, timedelta
import asyncio

from entities import Character
from payloads import LoginPayload
from queries.get_character import get_characters

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


def is_spam(payload: LoginPayload, threshold: int = 15) -> bool:
    """
    Get whether a character has logged in within <threshold> minutes
    """
    id = payload.character_id
    char = db.get(id)
    if char:
        # Using the payload's timestamp so that delays in executing
        # this coroutine don't affect this calculation.
        delta = datetime.fromtimestamp(payload.timestamp) - char.last_login
        if delta < timedelta(minutes=threshold):
            character_logger.info(
                f"Ignored character {id}. Time since last login: {delta}"
            )
            return True
    return False


@toolz.curry
async def handle_characters(
    session: ClientSession, payloads: list[LoginPayload]
) -> None:
    genuine = filter(is_spam, payloads)
    ids = map(lambda p: p.character_id, genuine)
    chars = await get_characters(session, ids)
    for char in chars:
        db[char.id] = char
    character_logger.info(f"Added new character {id}")
