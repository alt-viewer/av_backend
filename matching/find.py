"""The IO shell around `matching.compare.search`"""

from asyncio import gather
import toolz.curried as toolz
from typing import Iterable, Awaitable
from operator import attrgetter

from database import DB, match_char_pages
from entities import Character, Match, MatchCharDict
from matching.compare import search
from utils import gathercat
from utils import pick, replace_with

PAGE_SIZE = 10000


def to_match_char(c: Character) -> MatchCharDict:
    return toolz.pipe(
        c,
        Character.json,
        pick(["uid", "xid", "last_login", "items", "eliminated"]),
        replace_with("uid", "id", toolz.identity),
    )


# FIXME: each page relies on the next, preventing parallel execution of the queries
# TODO: test if this way is faster than the inefficient skip-limit approach
# See: https://www.mongodb.com/docs/v6.0/reference/method/cursor.skip/#pagination-example
async def searches(db: DB, char: MatchCharDict) -> Iterable[Match]:
    return toolz.concat(page async for page in match_char_pages(db, PAGE_SIZE))


@toolz.curry
async def find_matches(db: DB, char: Character) -> Iterable[Match]:
    """
    Search for matches for a character in the database
    """
    as_mc = to_match_char(char)
    return await searches(db, as_mc)
