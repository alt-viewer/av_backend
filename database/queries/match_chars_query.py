import toolz.curried as toolz

from entities import MatchCharDict
from converters import convert_matchchar
from database.gql import GQLClient, query

template = """
    query get_match_chars($first: Int, $offset: Int) {
        queryCharacter(first: $first, offset: $offset) {
            id,
            xid,
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


async def get_match_char_page(
    session: GQLClient, page_size: int, offset: int
) -> list[MatchCharDict]:
    """Gets a minimalist view of a page of characters."""
    return list(
        await query(
            session,
            template,
            toolz.identity,
            variables={"first": page_size, "offset": offset},
        )
    )
