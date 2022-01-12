from typing import Callable, TypeVar, Sequence, Awaitable, Iterator, Any
from functools import wraps
from asyncio import gather, Future
import toolz.curried as toolz

ReturnType = TypeVar("ReturnType")


def with_page(
    func: Callable[[Sequence], Awaitable[ReturnType]], page_size: int = 100
) -> Callable[[Sequence], Awaitable[list[ReturnType]]]:
    @wraps(func)
    def inner(xs):
        pages = toolz.partition_all(page_size, xs)
        return gather(*map(func, pages))

    return inner
