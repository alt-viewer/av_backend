import toolz.curried as toolz
from datetime import datetime

# datetime.fromisoformat doesn't play nicely with DGraph's
# RFC datetimes
from dateutil.parser import parse as parse_rfc
from typing import Iterable

from payloads import ItemObj
from entities import Item


def load_item(i: dict) -> Item:
    """Load a single database item."""
    return Item(i["xid"], parse_rfc(i["last_recorded"]), i.get("id"))


def load_items(items: list[dict]) -> list[Item]:
    """
    Use this when converting items from the database.
    Use `parse_char_items` when converting from the PS2 API
    """
    return toolz.pipe(items, toolz.map(load_item), list)


def parse_char_items(items: list[ItemObj]) -> list[Item]:
    """
    Use this when converting from the PS2 API
    Use `load_items` when converting items from the database.

    """
    now = datetime.now()
    return toolz.pipe(
        items,
        # account_level might not exist but it could be false if it exists
        toolz.filter(lambda i: i.account_level),
        toolz.map(lambda i: Item(i.item_id, now)),
        list,
    )


def item_intersection(xs: Iterable[Item], ys: Iterable[Item]) -> set[Item]:
    # Avoid reconstructing a set
    as_set = xs if isinstance(xs, set) else set(xs)
    return as_set.intersection(ys)
