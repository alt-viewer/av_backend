from aiohttp import ClientSession
import toolz.curried as toolz
from collections.abc import Iterable
from logging import getLogger
from typing import TypedDict

from census.api_query import (
    param_factory,
    filtered_census_query,
    finalise_query,
    Filter,
)
from entities import XID, ItemInfo
from entities.converters import to_item_info


make_params = param_factory(
    [
        "item_id",
        "item_type_id",
        "item_category_id",
        "is_vehicle_weapon",
        "name.en",
        "faction_id",
    ],
    [],
)


class ItemInfoFilter(Filter):
    item_id: list[XID]


_get_items: filtered_census_query[ItemInfoFilter] = filtered_census_query(
    "item", make_params, to_item_info
)

async def get_items(session: ClientSession, ids: list[XID]) -> list[ItemInfo]:
    return await get_items(session, ItemInfoFilters({"item_id": ids}))
