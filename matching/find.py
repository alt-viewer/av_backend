"""The IO shell around `matching.compare.search`"""

from asyncio import gather
import toolz.curried as toolz
from typing import Iterable, Awaitable
from operator import attrgetter

from database import count, DBClient, get_match_char_page
from entities import Character, Match, NodeTypes, MatchCharDict
from matching.compare import search
from queries import gathercat
from utils import pick, replace_with

PAGE_SIZE = 10000


def to_match_char(c: Character) -> MatchCharDict:
    return toolz.pipe(
        c,
        Character.json,
        pick(["uid", "xid", "last_login", "items", "eliminated"]),
        replace_with("uid", "id", toolz.identity),
    )


@toolz.curry
async def match_of_page(
    session: DBClient, char: MatchCharDict, offset: int
) -> Iterable[Match]:
    return search(char, await get_match_char_page(session, PAGE_SIZE, offset))


@toolz.curry
async def find_matches(session: DBClient, char: Character) -> Iterable[Match]:
    """
    Search for matches for a character in the database
    """
    # Doing an extra query has a cost but enables
    # requesting the pages in parallel
    n = await count(session, NodeTypes.CHARACTER)

    # Spawn page requests and pipe the pages into the matching function
    offsets = range(0, n, PAGE_SIZE)
    as_mc = to_match_char(char)
    return await gathercat(match_of_page(session, as_mc), offsets)
