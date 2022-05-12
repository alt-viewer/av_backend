"""The IO shell around `matching.compare.search`"""

from asyncio import gather
import toolz.curried as toolz
from typing import Iterable, Awaitable
from operator import attrgetter

from av_backend.database import count, GQLClient, get_match_char_page
from av_backend.entities import Character, Match, NodeTypes, MatchCharDict
from av_backend.matching.compare import search
from av_backend.queries import gathercat
from av_backend.eggs import pick, replace_with

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
    session: GQLClient, char: MatchCharDict, offset: int
) -> Iterable[Match]:
    return search(char, await get_match_char_page(session, PAGE_SIZE, offset))


@toolz.curry
async def find_matches(session: GQLClient, char: Character) -> Iterable[Match]:
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
