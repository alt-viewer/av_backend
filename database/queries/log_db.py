from asyncio import sleep
from gql import gql
from gql.client import AsyncClientSession
import logging
from toolz import get_in

db_logger = logging.getLogger("db")

query = gql(
    """
            query count_chars {
  aggregateCharacter {
    count
  }
}
"""
)


async def log_task(client: AsyncClientSession) -> None:
    while True:
        res = await client.execute(query)
        count = get_in(["aggregateCharacter", "count"], res)
        db_logger.info(f"{count or 0} characters recorded")
        await sleep(30)
