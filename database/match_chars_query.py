from gql import gql
from gql.client import AsyncClientSession
from toolz import get_in

from entities import MatchChar
from converters import convert_matchchar

query = gql(
    """
    query get_match_chars {
  queryCharacter(filter: {
      name: {
          regexp: "/.*/"
      }
  }) {
      id,
      last_login,
      items {
          xid,
          last_recorded
      },
      eliminated {
        id
      }
  }
}
            """
)


async def get_match_chars(session: AsyncClientSession) -> list[MatchChar]:
    """This query is designed for generating matches between characters."""
    res = await session.execute(query)
    chars = get_in(["queryCharacter"], res)
    return list(map(convert_matchchar, chars))
