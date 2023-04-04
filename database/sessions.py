from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabse
from typing import TypeAlias, TypeVar, Callable, Iterable, AsyncIterator
from contextlib import asynccontextmanager
from re import compile
import json

DBClient: TypeAlias = AsyncIOMotorClient
DB: TypeAlias = AsyncIOMotorDatabse


def load_db_config() -> dict:
    with open("data/db/config.json") as f:
        return json.load(f)


config = load_db_config()


@asynccontextmanager
async def get_sessions(
    url: str,
) -> AsyncIterator[tuple[ClientSession, DB]]:
    """
    Create an AIOHTTP session and a MongoDB database.
    Returns (AIOHTTP session, MongoDB database)
    """
    try:
        session = ClientSession()
        database = AsyncIOMotorClient(config["host_name"], config["port"])[
            config["dbName"]
        ]
        yield (session, database)
    finally:
        await session.close()


# Gets the query type from query literal
query_name = compile("(query|get|aggregate|add|delete|update)[A-Z]\w+")
Converted = TypeVar("Converted")


async def query(
    session: GQLClient,
    query_literal: str,
    converter: Callable[[dict], Converted],
    variables: dict = None,
    key: str = None,
) -> Iterable[Converted]:
    """
    Convenience function around `GQLClient.execute`.

    Args:
        query_literal:
            The GraphQL query.
        converter:
            A function that transforms a result dict into the desired type.
            This will be applied to each result of the query.
        variables:
            The variables to insert into the query.
        key:
            The key to fetch the data from in the response (E.G aggregateCharacter or queryItem).
            If this is not passed, it will be determined automatically. Pass this for extra performance.
    """
    query_vars = variables or {}
    # Find the name of the query
    if key:
        data_key = key
    else:
        match = query_name.search(query_literal)
        if not match:
            raise ValueError("Invalid query")
        data_key = match.group(0)

    res = (await session.execute(gql(query_literal), variable_values=query_vars))[
        data_key
    ]
    # Sometimes a query will return a single dict instead of a list
    return map(converter, res if isinstance(res, list) else [res])
