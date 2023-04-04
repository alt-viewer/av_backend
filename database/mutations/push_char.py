from gql import gql
from typing import Iterable, Iterable, Container, Hashable
from operator import attrgetter, methodcaller
import toolz.curried as toolz

from entities.character import Character, Item
from database.gql import GQLClient
from converters import convert_json, item_intersection
from database.mutations.push_items import push_items
from utils import omit

query = gql(
    """
mutation addCharacters($characters: [AddCharacterInput!]!) {
  addCharacter(input: $characters, upsert: true) {
    numUids
  }
}
"""
)


def zip_with(f, *iterables) -> Iterable:
    return (f(*args) for args in zip(*iterables))


def aggregate_items(chars: list[Character]) -> set[Item]:
    """Get the set of items from a list of characters."""
    return set(toolz.mapcat(attrgetter("items"), chars))


def uids(items: list[dict]) -> list[str]:
    """Convert a list of items to their uids"""
    return list(map(attrgetter("uid"), items))


def upsertable(char: Character, item_ids: list[str]) -> dict:
    """
    Convert a character to its JSON form
    and convert all its items to UIDs.
    """
    json_items = list(map(lambda i: {"id": i}, item_ids))
    return toolz.pipe(
        char,
        methodcaller("json"),
        # Ignore the UID member of the character because it will be unset
        omit(["uid"]),
        lambda j: {**j, "items": json_items},
    )


async def patch_chars(client: GQLClient, chars: list[Character]) -> Iterable[dict]:
    """
    Upsert the items from each character, then construct the character's JSON.

    This is needed because nested upserts aren't possible with DGraph.
    Therefore, I have to create/update all items, then reference them
    in the character query.
    """
    # Get the set of unique items from the characters
    char_items = list(map(attrgetter("items"), chars))
    all_items = toolz.concat(char_items)
    db_items = await push_items(client, all_items)  # Get the uids of the upserted items

    # Replace each character's items with the uids for their items.
    # Flipping because I want to get back the db items that intersect
    item_inter = toolz.flip(item_intersection)(db_items)
    patch_convert = toolz.compose(uids, item_inter)
    patched_items = map(patch_convert, char_items)
    return zip_with(upsertable, chars, patched_items)


@toolz.curry
async def push_chars(client: GQLClient, chars: Iterable[Character]) -> None:
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
            "characters": patched,
        },
    )
