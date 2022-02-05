from gql.transport.aiohttp import AIOHTTPTransport
from gql.client import AsyncClientSession
from aiohttp import ClientSession
from typing import TypeAlias

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
