from aiohttp import ClientSession
import toolz.curried as toolz
from datetime import datetime

from queries.api_query import query
from entities import Factions, Item, Character, Servers

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


def parse_items(items: list[dict]) -> list[Item]:
    now = datetime.now()
    return toolz.pipe(
        items,
        # account_level might not exist but it could be false if it exists
        toolz.filter(lambda i: bool(i.get("account_level"))),
        toolz.map(lambda i: Item(i["item_id"], now)),
        list,
    )


def parse_character(data: dict) -> Character:
    char = toolz.get_in(["character_list", 0], data)
    get = toolz.flip(toolz.get_in)(char)
    return Character(
        get(["name", "first"]),
        get(["character_id"]),
        parse_items(get(["items"])),
        get(["outfit", "alias"]),
        get(["outfit", "outfit_id"]),
        Factions(int(get(["faction_id"]))),
        parse_timestamp(get(["times", "last_login_date"])),
        Servers(int(get(["world_id"]))),
        int(get(["battle_rank", "value"])),
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
