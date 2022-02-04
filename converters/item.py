import toolz.curried as toolz
from datetime import datetime

from payloads import ItemObj
from entities import Item


def load_item(i: dict) -> Item:
    """Load a single database item."""
    return Item(i["xid"], datetime.fromisoformat(i["last_recorded"]))


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
