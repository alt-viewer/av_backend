from aiohttp import ClientSession
import toolz.curried as toolz
from datetime import datetime

from queries.api_query import query
from entities import Factions, Item, Character, Servers
from payloads import CharacterPayload, ItemObj

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


def parse_timestamp(t: str) -> datetime:
    # The API returns an invalid fffff... portion
    # See: https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
    return datetime.fromisoformat(t[:-2])


def parse_items(items: list[ItemObj]) -> list[Item]:
    now = datetime.now()
    return toolz.pipe(
        items,
        # account_level might not exist but it could be false if it exists
        toolz.filter(lambda i: i.account_level),
        toolz.map(lambda i: Item(i.item_id, now)),
        list,
    )


def convert_payload(data: dict) -> CharacterPayload:
    char_data = toolz.get_in(["character_list", 0], data)
    converted = {
        **char_data,
        # Explicit conversion needed since Enum doesn't do it
        "faction_id": int(char_data["faction_id"]),
        "world_id": int(char_data["world_id"]),
    }
    return CharacterPayload(**converted)


def parse_character(data: dict) -> Character:
    char = convert_payload(data)
    if not char.items:
        raise ValueError("Character lacks items")

    return Character(
        char.name.first,
        char.character_id,
        parse_items(char.items),
        char.outfit.alias if char.outfit else None,
        char.outfit.outfit_id if char.outfit else None,
        char.faction_id,
        parse_timestamp(char.times.last_login_date),
        char.world_id,
        char.battle_rank.value,
    )


def make_params(fields: list[str], joins: list[str], character_id: str) -> dict:
    return {
        "character_id": character_id,
        "c:show": ",".join(fields),
        "c:resolve": ",".join(joins),
    }


async def get_character(
    session: ClientSession, id: str, fields: list[str] = None, joins: list[str] = None
) -> Character:
    fs = fields or DEFAULT_FIELDS
    js = joins or DEFAULT_JOINS
    url = query("character", params=make_params(fs, js, id))
    async with session.get(url) as res:
        json = await res.json()
        if not res.ok:
            raise RuntimeError(res.reason)
        return parse_character(json)
