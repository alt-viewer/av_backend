from aiohttp import ClientSession
import toolz.curried as toolz
from collections.abc import Iterable

from census.api_query import census_url, param_factory, with_ids
from entities import XID, ItemInfo
from entities.converters import with_conversion, to_item_info


@toolz.curry
@with_conversion(to_item_info)
async def get_items(session: ClientSession, ids: Iterable[XID]) -> list[dict]:
    pass
