from aiohttp import ClientSession
import toolz.curried as toolz
from datetime import datetime

from queries.api_query import query
from entities import Factions, Item, Character, Servers
from payloads import CharacterPayload, ItemObj
from queries.batch import with_page

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


def cast_char(char_data: dict) -> dict:
    """Cast the types of the character response to the appropriate types"""
    return {
        **char_data,
        # Explicit conversion needed since Enum doesn't do it
        "faction_id": int(char_data["faction_id"]),
        "world_id": int(char_data["world_id"]),
    }


convert_payload = lambda xs: toolz.map(
    toolz.compose(lambda c: CharacterPayload(**c), cast_char)
)(toolz.compose(toolz.do(print), toolz.get_in(["character_list"]), toolz.do(print))(xs))


def make_char(char: CharacterPayload) -> Character:
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


parse_characters = toolz.compose(toolz.map(make_char), convert_payload)


def make_params(fields: list[str], joins: list[str], character_id: str) -> dict:
    return {
        "character_id": character_id,
        "c:show": ",".join(fields),
        "c:resolve": ",".join(joins),
    }


@toolz.curry
async def get_characters(
    session: ClientSession, ids: str, fields: list[str] = None, joins: list[str] = None
) -> Character:
    fs = fields or DEFAULT_FIELDS
    js = joins or DEFAULT_JOINS
    url = query("character", params=make_params(fs, js, ",".join(ids)))
    async with session.get(url) as res:
        json = await res.json()
        if not res.ok:
            raise RuntimeError(res.reason)
        return parse_characters(json)


paged_get_chars = lambda session: with_page(get_characters(session))
