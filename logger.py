import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
global_logger = logging.getLogger("global_logger")


def with_logger(logger: logging.Logger):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            output = func(*args, **kwargs)
            logger.debug(f"{func} called with {args=}, {kwargs=}. {output=}")
            return output

        return inner

    return outer
