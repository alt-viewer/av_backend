from typing import Callable, TypeVar, Sequence, Awaitable, Iterator, Any
from functools import wraps
from asyncio import gather, Future
import toolz.curried as toolz

ReturnType = TypeVar("ReturnType")


async def gathercat(
    f: Callable[[Sequence], Awaitable[list[list[ReturnType]]]],
    pages: Iterator[Sequence],
) -> Awaitable[Iterator[ReturnType]]:
    """Map an async function to a set of pages, then join each
    page of results into one list of results"""
    results = await gather(*map(f, pages))
    return toolz.concat(results)


def with_page(page_size: int = 100):
    def outer(
        func: Callable[[Sequence], Awaitable[ReturnType]]
    ) -> Callable[[Iterator], Awaitable[list[ReturnType]]]:
        @wraps(func)
        def inner(xs):
            pages = toolz.partition_all(page_size, xs)
            return gathercat(func, pages)

        return inner

    return outer
