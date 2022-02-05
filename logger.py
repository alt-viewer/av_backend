import logging
from functools import wraps

logging.basicConfig(level=logging.WARNING)
global_logger = logging.getLogger("global_logger")


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
