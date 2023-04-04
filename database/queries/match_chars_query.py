import toolz.curried as toolz
from typing import AsyncGenerator

from entities import MatchCharDict
from database.types import DB, Collection
from database.paging import paged_collection


def match_char_pages(
    db: DB, page_size: int
) -> AsyncGenerator[list[MatchCharDict], None]:
    projections = {
        "_id": 1,
        "xid": 1,
        "lastLogin": 1,
        "items": 1,
    }
    return paged_collection(page_size, db.characters, projections=projections)
