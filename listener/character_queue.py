from aiohttp import ClientSession
from typing import Awaitable, Callable
from asyncio import Lock
from functools import wraps
import logging

from queries import with_page
from entities import Character

logger = logging.getLogger("character queue")

char_lock = Lock()


def with_check(func: Callable[..., None]) -> Callable[..., Awaitable[None]]:
    @wraps(func)
    async def inner(queue: "CharacterQueue", *args, **kwargs):
        async with char_lock:
            func(queue, *args, **kwargs)
            logger.debug(f"{len(queue)} characters in the queue")
            if queue.should_request():
                await queue.request()

    return inner


class CharacterQueue:
    """
    Handles periodically requesting characters.
    Avoids requesting a small number of characters.
    """

    def __init__(
        self,
        requester: Callable[[list[int]], Awaitable[list[Character]]],
        put_chars: Callable[[list[Character]], Awaitable[None]],
        min_size: int = 20,
    ):
        self.req = with_page()(requester)
        self.min = min_size
        self.put = put_chars
        self._queue: set[int] = set()

    @with_check
    def extend(self, ids: list[int]) -> None:
        """
        Add a list of character IDs to the queue.
        """
        self._queue.update(ids)

    @with_check
    def add(self, id: int) -> None:
        """Add a character ID to the queue"""
        self._queue.add(id)

    async def request(self) -> None:
        logger.info(f"Requesting {len(self)} characters")
        chars = await self.req(self._queue)
        self._queue.clear()
        await self.put(chars)

    def should_request(self) -> bool:
        return len(self._queue) >= self.min

    def __len__(self) -> int:
        return len(self._queue)
