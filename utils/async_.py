from asyncio import gather
from typing import TypeVar
from collections.abc import Callable, Iterable, Awaitable, Sequence
import toolz.curried as toolz
from functools import wraps

T = TypeVar("T")
R = TypeVar("R")


@toolz.curry
async def map_async(f: Callable[[T], Awaitable[R]], xs: Iterable[T]) -> list[R]:
    return await gather(*(f(x) for x in xs))


async def gathercat(
    f: Callable[[T], Awaitable[Iterable[R]]],
    xs: Iterable[T],
) -> Iterable[R]:
    """Map an async function to an iterable and concat the results."""
    results = await gather(*map(f, xs))
    return toolz.concat(results)


def with_page(page_size: int = 100):
    """Split a large list into smaller lists, then call `func` on them concurrently"""

    def outer(
        func: Callable[[Sequence], Awaitable[R]]
    ) -> Callable[[Iterable], Awaitable[list[R]]]:
        @wraps(func)
        def inner(xs):
            pages = toolz.partition_all(page_size, xs)
            return gathercat(func, pages)

        return inner

    return outer
