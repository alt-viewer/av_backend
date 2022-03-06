import logging
from functools import wraps
from typing import Callable, TypeVar, Iterable, Iterator
import toolz.curried as toolz
from asyncio import TimeoutError as AsyncTimeout


def set_up_loggers(loggers: dict[str, int]) -> None:
    for name, level in loggers.items():
        l = logging.getLogger(name)
        l.setLevel(level)


def with_logger(
    logger: logging.Logger,
    format: str = "{0} called with args={1}, kwargs={2}. output={3}",
):
    """Wrap a function with logging.
    The format will be filled with 0: func, 1: args, 2: kwargs, 3: output
    """

    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            output = func(*args, **kwargs)
            logger.debug(format.format(func, args, kwargs, output))
            return output

        return inner

    return outer


T = TypeVar("T")


def log_filter(
    logger: logging.Logger,
    pred: Callable[[T], bool],
    format: str = "Ignoring {item} due to failing {predicate}",
) -> Callable[[Iterable[T]], Iterator[T]]:
    """Filter the list and log any items that fail the predicate"""

    def wrapper(item: T) -> bool:
        res = pred(item)
        if not res:
            logger.debug(format.format(item=item, predicate=pred))
        return res

    return toolz.filter(wrapper)


def with_retry(
    logger: logging.Logger,
    n: int = 5,
):
    def wrapper(func):
        async def inner(*args, **kwargs):
            for try_ in range(n):
                try:
                    return await func(*args, **kwargs)
                except AsyncTimeout:
                    logger.debug(f"Failed {func} {try_+1} times. Retrying...")

        return inner

    return wrapper


logging.basicConfig(level=logging.WARNING)
global_logger = logging.getLogger("global_logger")

# Set up the named loggers
LOGGER_SETTINGS = {
    "character": logging.INFO,
    "character queue": logging.INFO,
    "db": logging.INFO,
    "websocket": logging.INFO,
}

set_up_loggers(LOGGER_SETTINGS)
