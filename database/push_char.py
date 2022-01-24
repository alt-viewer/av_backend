from gql import gql
from gql.client import AsyncClientSession
from typing import Iterator

from entities.character import Character
from database.filter_new import new_chars
from database.converters.char_json import char_jsons

query = gql(
    """
mutation addCharacters($characters: [AddCharacterInput!]!) {
  addCharacter(input: $characters) {
    numUids
  }
}
"""
)


async def push_chars(client: AsyncClientSession, chars: Iterator[Character]) -> None:
    lchars = list(chars)  # this generator needs to be reused
    new = await new_chars(client, lchars)
    await client.execute(query, variable_values={"characters": char_jsons(new)})
