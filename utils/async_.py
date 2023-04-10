from asyncio import gather
from typing import TypeVar
from collections.abc import Callable, Iterable, Awaitable
from toolz import curry

T = TypeVar("T")
R = TypeVar("R")


@curry
async def map_async(f: Callable[[T], Awaitable[R]], xs: Iterable[T]) -> list[R]:
    return await gather(*(f(x) for x in xs))
