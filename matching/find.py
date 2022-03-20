from asyncio import gather
import toolz.curried as toolz
from typing import Iterable, Awaitable
from operator import attrgetter

from database import count, GQLClient, get_match_char_page
from entities import Character, Match, NodeTypes, MatchCharDict
from matching.compare import search
from queries import gathercat
from eggs import pick, replace_with

PAGE_SIZE = 10000


def to_match_char(c: Character) -> MatchCharDict:
    return toolz.pipe(
        c,
        Character.json,
        pick(["uid", "last_login", "items", "eliminated"]),
        replace_with("uid", "id", toolz.identity),
    )


@toolz.curry
async def match_of_page(
    session: GQLClient, char: MatchCharDict, offset: int
) -> list[Match]:
    return search(char, await get_match_char_page(session, PAGE_SIZE, offset))


async def find_matches(session: GQLClient, char: Character) -> Iterable[Match]:
    # Doing an extra query has a cost but enables
    # requesting the pages in parallel
    n = await count(session, NodeTypes.CHARACTER)

    # Spawn page requests and pipe the pages into the matching function
    offsets = range(0, n, PAGE_SIZE)
    as_mc = to_match_char(char)
    return await gathercat(match_of_page(session, as_mc), offsets)
