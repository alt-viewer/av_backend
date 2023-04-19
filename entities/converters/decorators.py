from functools import wraps
from typing import Any, ParamSpec, TypeAlias, TypeVar, Generic
import toolz.curried as toolz
from collections.abc import Sequence, Awaitable, Callable

T = TypeVar("T")
P = ParamSpec("P")

# Forward references can't be used in unions
# See https://stackoverflow.com/a/72644857
JSONValue: TypeAlias = "int | str | JSON | list[JSON]"
JSON: TypeAlias = dict[str, JSONValue]


class Converter(Generic[T]):
    def __init__(self, cast: Callable[[JSON], dict[str, Any]], construct: type[T]):
        self.cast = cast
        self.construct = construct

    def __call__(self, json: JSON) -> T:
        return toolz.pipe(
            json,
            self.cast,
            lambda casted: self.construct(**casted),
        )


def with_conversion(
    converter: Converter[T],
) -> Callable[[Callable[P, Awaitable[list[JSON]]]], Callable[P, Awaitable[list[T]]]]:
    """
    After the decorated async function has returned, apply `converter` to each result.
    Useful for REST or database queries.
    """

    def decorate(
        func: Callable[P, Awaitable[list[JSON]]]
    ) -> Callable[P, Awaitable[list[T]]]:
        @wraps(func)
        async def inner(*args: P.args, **kwargs: P.kwargs) -> list[T]:
            xs = await func(*args, **kwargs)
            return [converter(x) for x in xs]

        return inner

    return decorate


# NOTE: left here for backwards-compatibility
def converter(
    cast: Callable[[JSON], dict[str, Any]], construct: type[T]
) -> Converter[T]:
    """Make a function that converts a JSON response to the desired type"""
    return Converter(cast, construct)
