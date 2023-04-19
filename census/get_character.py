from aiohttp import ClientSession
import toolz.curried as toolz
from datetime import datetime
from typing import Iterable

from census.api_query import census_url
from entities import Factions, Item, Character, Servers
from entities.payloads import CharacterPayload, ItemObj
from utils import with_page
from entities.converters import chars_from_census

DEFAULT_FIELDS = [
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
]


def make_params(fields: list[str], joins: list[str], character_id: str) -> dict:
    return {
        "character_id": character_id,
        "c:show": ",".join(fields),
        "c:resolve": ",".join(joins),
        "c:lang": "en",
    }


async def get_raw_chars(
    session: ClientSession,
    ids: Iterable[int],
    fields: list[str] | None = None,
    joins: list[str] | None = None,
    item_query: str | None = None,
) -> list[dict]:
    fs = fields or DEFAULT_FIELDS
    js = joins or DEFAULT_JOINS
    joined = ",".join(map(str, ids))
    url = census_url("character", params=make_params(fs, js, joined))
    async with session.get(url) as res:
        if not res.ok:
            raise RuntimeError(res.reason)
        json = await res.json()
    return json["character_list"]


@toolz.curry
async def get_characters(
    session: ClientSession,
    ids: Iterable[int],
    fields: list[str] | None = None,
    joins: list[str] | None = None,
) -> list[Character]:
    json = await get_raw_chars(session, ids)
    return list(chars_from_census(json))


paged_get_chars = lambda session: with_page(get_characters(session))
