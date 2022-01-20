from math import ceil
from sys import getsizeof
import logging
import asyncio
from typing import Iterator

from entities import Character

db: dict[int, Character] = {}
character_logger = logging.getLogger("characters")


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


async def push_db(chars: Iterator[Character]) -> None:
    for char in chars:
        db[char.id] = char
