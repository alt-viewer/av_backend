from motor import MotorCursor
from typing import AsyncGenerator, TypeAlias, Callable
import toolz.curried as toolz

from database.types import Collection, Filter


def id_range_filter(custom_filter: Filter | None = None) -> Callable[[int], Filter]:
    """
    Make a function that gets the next set of documents after `uid`.
    The resulting filter will build on top of `custom_filter`.
    NOTE: `custom_filter` must not define `_id`.
    """
    filter = (custom_filter or {}) | {"_id": {"$gt": -1}}

    def add_id(uid: int) -> Filter:
        filter["_id"]["$gt"] = uid
        return filter

    return add_id


# Adapted from https://www.codementor.io/@arpitbhayani/fast-and-efficient-pagination-in-mongodb-9095flbqr
async def paged_collection(
    page_size: int, collection: Collection, filter: Filter | None = None
) -> AsyncGenerator[list[dict], None]:
    """
    Lazily request pages from the collection of size `page_size` according to `filter`.
    """
    make_filter = id_range_filter(filter)
    get_page = lambda f: collection.find(f).limit(page_size).to_list()
    page = await get_page(filter)
    while page:
        yield page
        last_id = toolz.last(page)["_id"]
        page = await get_page(make_filter(last_id))
