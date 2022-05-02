import toolz.curried as toolz
from enum import Enum

from entities import Character
from converters import load_char
from database.gql import GQLClient, query

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


def make_query(id_type: str) -> str:
    """Choose the query signature based on the type of ID"""
    headers = {"uid": UID_HEADER, "xid": XID_HEADER}
    return headers[id_type] + BODY


async def get_char_by_id(
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
            load_char,
            variables={"id": id_},
        )
    )
