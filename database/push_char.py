from gql import gql
from typing import Iterator
from operator import attrgetter, methodcaller
import toolz.curried as toolz

from entities.character import Character, Item
from database.filter_new import new_chars
from database.gql import GQLClient
from converters import convert_json, item_intersection
from database.push_items import push_items

query = gql(
    """
mutation addCharacters($characters: [AddCharacterInput!]!) {
  addCharacter(input: $characters, upsert: true) {
    numUids
  }
}
"""
)

# TODO
# aggregate all items into one list
# push them to the database
# for each character:
#   char.items = {i.id | i <- res_items, i in char.items}
# use sets ^

# I need a fast way to get the intersection of two sets of items
# using a certain attribute of each item
# E.G {x | x <- items1, y <- items2, x.xid == y.xid}


def aggregate_items(chars: list[Character]) -> set[Item]:
    """Get the set of items from a list of characters."""
    return set(toolz.mapcat(attrgetter("items"), chars))


def uids(items: list[dict]) -> list[str]:
    """Convert a list of items to their uids"""
    return list(map(toolz.get_in(["uid"]), items))


def upsertable(char: Character) -> dict:
    """
    Convert a character to its JSON form
    and convert all its items to UIDs.
    """
    return toolz.pipe(
        char,
        methodcaller("json"),
        lambda j: {**j, "items": uids(j["items"])},
    )


@toolz.curry
def _patch_items(db_items: list[Item], char: Character) -> Character:
    return char.update(items=list(item_intersection(db_items, char.items)))


async def patch_chars(client: GQLClient, chars: list[Character]) -> Iterator[dict]:
    """
    Upsert the items from each character, then construct the character's JSON.
    Overall time complexity: O(n^k)
    where k is the max number of items that a character may have.

    This is needed because nested upserts aren't possible with DGraph.
    Therefore, I have to create/update all items, then reference them
    in the character query.
    """
    all_items = iter(aggregate_items(chars))  # O(2n)
    db_items = await push_items(client, all_items)  # O(2n)
    patched = map(_patch_items(db_items), chars)  # O(n^2)
    return map(upsertable, patched)  # O(n^k)


async def push_chars(client: GQLClient, chars: Iterator[Character]) -> None:
    """
    Upsert the characters into the database. This is fairly expensive
    due to 2 queries and a lot of conversion. See patch_chars about complexity.

    Implementation note:
    This function does 2 queries:
    1. Upsert the items
    2. Upsert the characters, referencing the items from the upsert
    """
    lchars = list(chars)  # this generator needs to be reused
    patched = list(await patch_chars(client, lchars))
    await client.execute(
        query,
        variable_values={
            "characters": list(patched),
        },
    )
