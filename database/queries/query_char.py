import toolz.curried as toolz
from enum import Enum

from entities import Character
from converters import char_from_db
from database.gql import GQLClient, query

# Template for get_char_by_id
UID_HEADER = """
query get_single_char ($id: ID!) {
  getCharacter(id: $id) {
"""

XID_HEADER = """
query get_single_char ($id: Int64!) {
  getCharacter(xid: $id) {
"""

BODY = """
    name,
    uid: id,
    xid,
    outfit_tag,
    outfit_id,
    faction_id,
    last_login,
    server_id,
    battle_rank,
    items {
      id,
      last_recorded
    }
  }
}
"""

# Template for get_char_by_name
BY_NAME_TEMPLATE = """
query get_chars_by_name($names: [String!]!) {
	queryCharacter(filter: {
		name: {in: $names}
	}) {
		name,
		uid: id,
		xid,
		faction_id,
		outfit_id,
		outfit_tag,
		server_id,
		battle_rank,
		last_login,
		peers { name },
		eliminated { name },
        items {
            xid,
            last_recorded
        }
    }
}
"""


def make_query(id_type: str) -> str:
    """Choose the query signature based on the type of ID"""
    headers = {"uid": UID_HEADER, "xid": XID_HEADER}
    return headers[id_type] + BODY


async def by_id(
    session: GQLClient, uid: str = None, xid: int = None
) -> list[Character]:
    """Get a character by uid or xid."""
    if not any((uid, xid)):
        raise ValueError("Either uid or xid must be passed.")
    id_, literal = (uid, make_query("uid")) if uid else (xid, make_query("xid"))

    return list(
        await query(
            session,
            literal,
            char_from_db,
            variables={"id": id_},
        )
    )


async def by_name(session: GQLClient, names: list[str]) -> list[Character]:
    return list(
        await query(session, BY_NAME_TEMPLATE, char_from_db, variables={"names": names})
    )


@toolz.curry
async def get_char(
    session: GQLClient, names: list[str] = None, uid: str = None, xid: int = None
) -> list[Character]:
    """Get a character by name, uid, or xid."""
    # Comparing against None to have a more intuitive error if an empty string/list is passed
    if names is not None:
        return await by_name(session, names)
    elif uid is not None or xid is not None:
        return await by_id(session, uid, xid)
    else:
        raise ValueError("A name, uid, or xid must be provided.")
