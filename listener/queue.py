from aiohttp import ClientSession
from typing import Awaitable, Callable, TypeVar, Generic, ParamSpec
from asyncio import Lock
from functools import wraps
import logging

from census import with_page
from entities import Character

default_logger = logging.getLogger("unnamed RequestQueue")

queue_lock = Lock()

P = ParamSpec("P")


def with_size_check(func: Callable[P, None]) -> Callable[P, Awaitable[None]]:
    """
    After calling the wrapped function, call `RequestQueue._request` if necessary.
    Also logs the ID count.
    NOTE: the output function is asynchronous.
    """

    @wraps(func)
    async def inner(*args, **kwargs) -> None:
        async with queue_lock:
            func(*args, **kwargs)
            queue = args[0]
            queue.logger.debug(f"{len(queue)} IDs in the queue")
            if queue.should_request():
                await queue._request()

    return inner


T = TypeVar("T")


class RequestQueue(Generic[T]):
    """
    Handles periodically requesting PS2 objects and pushing them to the database.
    """

    def __init__(
        self,
        requester: Callable[[set[int]], Awaitable[list[T]]],
        put: Callable[[list[T]], Awaitable[None]],
        min_size: int = 20,
        logger: logging.Logger | None = None,
    ):
        self.req = requester
        self.put = put
        self.min = min_size
        self.logger = logger or default_logger
        self._queue: set[int] = set()

    @with_size_check
    def extend(self, ids: list[int]) -> None:
        """Add a list of IDs to the queue."""
        self._queue.update(ids)

    @with_size_check
    def add(self, id: int) -> None:
        """Add an ID to the queue"""
        self._queue.add(id)

    async def _request(self) -> None:
        """
        Request all objects in the queue, then push them to the database.
        This is done automatically after `add` or `extend`.
        """
        self.logger.info(f"Requesting {len(self)} IDs")
        chars = await self.req(self._queue)
        self._queue.clear()
        await self.put(chars)

    def should_request(self) -> bool:
        return len(self._queue) >= self.min

    def __len__(self) -> int:
        return len(self._queue)
