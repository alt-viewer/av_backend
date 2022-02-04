from aiohttp import ClientSession
import toolz.curried as toolz
from datetime import datetime
from typing import Iterator

from queries.api_query import query
from entities import Factions, Item, Character, Servers
from payloads import CharacterPayload, ItemObj
from queries.batch import with_page
from converters import parse_characters

DEFAULT_FIELDS = [
    "items",
    "outfit.alias",
    "outfit.outfit_id",
    "world_id",
    "times.last_login_date",
    "name.first",
    "character_id",
    "faction_id",
    "battle_rank.value",
]

DEFAULT_JOINS = [
    "outfit",
    "world",
    "item",
]


def make_params(fields: list[str], joins: list[str], character_id: str) -> dict:
    return {
        "character_id": character_id,
        "c:show": ",".join(fields),
        "c:resolve": ",".join(joins),
    }


@toolz.curry
async def get_characters(
    session: ClientSession,
    ids: Iterator[int],
    fields: list[str] = None,
    joins: list[str] = None,
) -> Iterator[Character]:
    fs = fields or DEFAULT_FIELDS
    js = joins or DEFAULT_JOINS
    joined = ",".join(map(str, ids))
    url = query("character", params=make_params(fs, js, joined))
    async with session.get(url) as res:
        json = await res.json()
        if not res.ok:
            raise RuntimeError(res.reason)
        return parse_characters(json)


paged_get_chars = lambda session: with_page(get_characters(session))
