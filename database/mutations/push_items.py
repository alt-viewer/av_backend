from gql import gql
from typing import Iterator
import toolz.curried as toolz

from entities import Item
from converters import convert_json, char_from_db
from database.gql import GQLClient

query = gql(
    """
mutation addItems($items: [AddItemInput!]!) {
  addItem(input: $items, upsert: true) {
    item {
      id,
      xid,
      last_recorded
    }
  }
}
"""
)


async def push_items(client: GQLClient, items: Iterator[Item]) -> list[Item]:
    """Add/update the given items in the database and return {uid, xid, last_recorded}"""
    unique_items = iter(set(items))
    res = await client.execute(
        query, variable_values={"items": convert_json(unique_items)}
    )
    return toolz.pipe(
        res,
        toolz.get_in(["addItem", "item"]),
        char_from_db,
    )

