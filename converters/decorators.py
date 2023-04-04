from typing import Callable, TypeVar, ParamSpec, Awaitable
from functools import wraps

T = TypeVar("T")
P = ParamSpec("P")


def with_conversion(converter: Callable[[dict], T]):
    """
    After the decorated async function has returned, apply `converter` to each result.
    Useful for REST or database queries.
    """

    def decorate(
        func: Callable[P, Awaitable[list[dict]]]
    ) -> Callable[P, Awaitable[list[T]]]:
        @wraps(func)
        async def inner(*args: P.args, **kwargs: P.kwargs) -> list[T]:
            xs = await func(*args, **kwargs)
            return [converter(x) for x in xs]

        return inner

    return decorate
