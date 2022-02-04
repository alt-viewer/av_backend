from gql import gql
from gql.client import AsyncClientSession
from typing import Iterator
import toolz.curried as toolz

from entities.character import Item
from database.converters.json import convert_json

query = gql(
    """
mutation addItems($items: [AddItemInput!]!) {
  addItem(input: $items, upsert: true) {
    item {
      id
    }
  }
}
"""
)


async def push_items(
    client: AsyncClientSession, items: Iterator[Item]
) -> Iterator[str]:
    """Add/update the given items in the database and return their internal IDs"""
    res = await client.execute(query, variable_values={"items": convert_json(items)})
    return map(toolz.get_in(["id"]), res["addItem"])
