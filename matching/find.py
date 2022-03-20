from asyncio import gather
import toolz.curried as toolz
from typing import Iterable, Awaitable

from database import count, GQLClient, get_match_char_page
from entities import Character, Match, NodeTypes, MatchCharDict
from matching.compare import search

PAGE_SIZE = 10000


def to_match_char(c: Character) -> MatchCharDict:
    WHITELIST = ["last_login", "items", "eliminated"]
    uid = c.uid
    return toolz.keyfilter(lambda k: k in WHITELIST, c.json()) | {"uid": uid}


@toolz.curry
async def match_of_page(
    session: GQLClient, char: Character, offset: int
) -> list[Match]:
    return search(char.json(), await get_match_char_page(session, PAGE_SIZE, offset))


async def find_matches(session: GQLClient, char: Character) -> list[Match]:
    # Doing an extra query has a cost but enables
    # requesting the pages in parallel
    n = await count(session, NodeTypes.CHARACTER)

    # Spawn page requests and pipe the pages into the matching function
    offsets = range(0, n, PAGE_SIZE)
    return toolz.concat(await gather(*map(match_of_page(session, char), offsets)))
