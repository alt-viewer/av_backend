from typing import Callable, TypeVar, ParamSpec, Awaitable, Any, TypeAlias, Type
from functools import wraps
import toolz.curried as toolz

T = TypeVar("T")
P = ParamSpec("P")

JSONValue: TypeAlias = int | str | "JSON" | list["JSON"]
JSON: TypeAlias = dict[str, JSONValue]
Converter: TypeAlias = Callable[[JSON], T]


def with_conversion(converter: Converter):
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


def converter(cast: Callable[[JSON], dict[str, Any]], construct: Type) -> Converter:
    return toolz.compose(
        lambda d: construct(**d),
        cast,
    )
