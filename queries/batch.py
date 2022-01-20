from typing import Callable, TypeVar, Sequence, Awaitable, Iterator, Any
from functools import wraps
from asyncio import gather, Future
import toolz.curried as toolz

ReturnType = TypeVar("ReturnType")


def with_page(page_size: int = 100):
    def outer(
        func: Callable[[Sequence], Awaitable[ReturnType]]
    ) -> Callable[[Sequence], Awaitable[list[ReturnType]]]:
        @wraps(func)
        def inner(xs):
            pages = toolz.partition_all(page_size, xs)
            return gather(*map(func, pages))

        return inner

    return outer
