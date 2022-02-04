from gql import gql
from typing import Iterator

from entities.character import Character
from database.filter_new import new_chars
from database.gql import GQLClient
from converters.json import convert_json

query = gql(
    """
mutation addCharacters($characters: [AddCharacterInput!]!) {
  addCharacter(input: $characters, upsert: true) {
    numUids
  }
}
"""
)


async def push_chars(client: GQLClient, chars: Iterator[Character]) -> None:
    lchars = list(chars)  # this generator needs to be reused
    new = await new_chars(client, lchars)
    await client.execute(query, variable_values={"characters": convert_json(iter(new))})
