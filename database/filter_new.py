from gql import gql
from gql.client import AsyncClientSession
from operator import attrgetter
from toolz import get_in

from entities import Character

query = gql(
    """
query inDB($xids: [Int64!]!) {
    queryCharacter(filter: {
        xid: {
        in: $xids
        }
    }) {
    xid
    }
}
    """
)


async def new_chars(
    client: AsyncClientSession, chars: list[Character]
) -> list[Character]:
    res = await client.execute(
        query, variable_values={"xids": list(map(attrgetter("id"), chars))}
    )
    exists = get_in(["queryCharacter"], res)
    return list(filter(lambda c: c.id not in exists, chars))
