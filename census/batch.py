from typing import Callable, TypeVar, Sequence, Awaitable, Iterator, Any, Iterable
from functools import wraps
from asyncio import gather, Future
import toolz.curried as toolz

T = TypeVar("T")
ReturnType = TypeVar("ReturnType")


async def gathercat(
    f: Callable[[T], Awaitable[Iterable[ReturnType]]],
    xs: Iterable[T],
) -> Iterable[ReturnType]:
    """Map an async function to an iterable and concat the results."""
    results = await gather(*map(f, xs))
    return toolz.concat(results)


def with_page(page_size: int = 100):
    """Split a large list into smaller lists, then call `func` on them concurrently"""

    def outer(
        func: Callable[[Sequence], Awaitable[ReturnType]]
    ) -> Callable[[Iterator], Awaitable[list[ReturnType]]]:
        @wraps(func)
        def inner(xs):
            pages = toolz.partition_all(page_size, xs)
            return gathercat(func, pages)

        return inner

    return outer
