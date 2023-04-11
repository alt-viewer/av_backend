import toolz.curried as toolz
from datetime import datetime
from typing import Iterable

from entities.payloads import ItemObj
from entities import Item, ItemInfo, Factions, XID
from entities.converters.decorators import converter


def is_neutral(item: ItemObj) -> bool:
    """Check if an item is of a neutral faction"""
    if not item.faction_info:
        return True
    ifaction = item.faction_info.faction_id
    return ifaction == 0 or ifaction == None


def load_item(i: dict) -> Item:
    """Load a single database item."""
    return Item(i.get("xid"), i["last_recorded"], i.get("_id"))


def items_from_db(items: list[dict]) -> list[Item]:
    """
    Use this when converting items from the database.
    Use `items_from_census` when converting from the PS2 API
    """
    return toolz.pipe(items, toolz.map(load_item), list)


def items_from_census(items: list[ItemObj]) -> list[Item]:
    """
    Use this when converting from the PS2 API
    Use `items_from_db` when converting items from the database.

    """
    now = datetime.now()
    return toolz.pipe(
        items,
        # Remove faction-specific items and character-level items
        toolz.filter(lambda i: is_neutral(i)),
        toolz.map(lambda i: Item(i.item_id, now)),
        list,
    )


def cast_item_info(d: dict) -> dict:
    return {
        "xid": XID(d["item_id"]),
        "type_id": XID(d["item_type_id"]),
        "category_id": XID(d["item_category_id"]),
        "vehicle_weapon": bool(int(d["is_vehicle_weapon"])),
        "name": d["name"]["en"],
        "faction_id": Factions(int(d["faction_id"])),
    }


to_item_info = converter(cast_item_info, ItemInfo)


def item_intersection(xs: Iterable[Item], ys: Iterable[Item]) -> set[Item]:
    # Avoid reconstructing a set
    as_set = xs if isinstance(xs, set) else set(xs)
    return as_set.intersection(ys)
