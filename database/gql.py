from gql.transport.aiohttp import AIOHTTPTransport
from gql.client import AsyncClientSession, Client
from aiohttp import ClientSession
from typing import TypeAlias
from contextlib import asynccontextmanager

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
    try:
        asession = ClientSession()
        transport = GQLTransport(url, client_session=asession)
        gsession = Client(transport=transport)
        yield (asession, gsession)
    finally:
        await asession.close()
        if gsession.transport:
            await gsession.transport.close()
