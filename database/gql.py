from gql.transport.aiohttp import AIOHTTPTransport
from gql.client import AsyncClientSession, Client
from gql import gql
from gql.transport.aiohttp import AIOHTTPTransport
from aiohttp import ClientSession
from typing import TypeAlias, TypeVar, Callable, Iterable
from contextlib import asynccontextmanager, AsyncExitStack
from re import compile

GQLClient: TypeAlias = AsyncClientSession


class GQLTransport(AIOHTTPTransport):
    """This is a transport that reuses an existing aiohttp.ClientSession"""

    def __init__(self, *args, client_session: ClientSession, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = client_session

    async def connect(self) -> None:
        pass

    async def close(self) -> None:
        pass


@asynccontextmanager
async def get_sessions(url: str):
    """
    Create an AIOHTTP session and a GQL client.
    Returns (AIOHTTP session, GQL session)
    """
    async with AsyncExitStack() as stack:
        transport = AIOHTTPTransport(url)
        gsession = await stack.enter_async_context(Client(transport=transport))
        # Get the AIOHTTP session from the gql.Client's transport
        yield (gsession.transport.session, gsession)


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

    res = await session.execute(gql(query_literal), variable_values=query_vars)
    return map(converter, res[data_key])
