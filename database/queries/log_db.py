from asyncio import sleep
import logging
from toolz import get_in

from database.types import DB
from database.queries.count_query import count

db_logger = logging.getLogger("db")


async def log_task(db: DB) -> None:
    while True:
        char_count = count(db, "characters")
        db_logger.info(f"{char_count or 0} characters recorded")
        await sleep(30)
