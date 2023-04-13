from census.api_query import (
    Filter,
    filtered_census_query,
    param_factory,
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


get_items: filtered_census_query[ItemInfoFilter] = filtered_census_query(
    "item", make_params, to_item_info
)
