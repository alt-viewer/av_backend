import logging
from asyncio import create_task, gather
from collections.abc import Awaitable, Callable, Iterable, Sequence
from datetime import datetime
from functools import partial, wraps
from typing import NewType, TypeAlias, NamedTuple
from operator import attrgetter

import toolz.curried as toolz
from aiohttp import ClientSession

from census import get_characters, get_items
from database import DB, push_chars
from entities import XID, Character, Item, ItemInfo
from entities.payloads import ItemAdded
from listener.filter_item import is_account_wide
from listener.queue import RequestQueue
from utils import with_page

Event = NewType("Event", dict)
Dispatch: TypeAlias = Callable[[Event], None]
CharItem = NamedTuple(
    "CharItem", [("char_id", XID), ("item_id", XID), ("timestamp", datetime)]
)

event_logger = logging.getLogger("event reducer")
char_logger = logging.getLogger("character")

payload = toolz.get("payload")


def to_item_added(payload: dict) -> ItemAdded:
    return toolz.pipe(
        payload,
        lambda p: {**p, "world_id": int(p["world_id"])},
        lambda p: ItemAdded(**p),
    )


def to_char_item(event: ItemAdded) -> CharItem:
    return CharItem(
        event.character_id,
        event.item_id,
        event.timestamp,
    )


def to_item(info: ItemInfo, timestamp: datetime) -> Item:
    return Item(info.xid, timestamp)


def add_item(char: Character, item: ItemInfo, timestamp: datetime) -> Character:
    char.update(items=[*char.items, to_item(item, timestamp)])
    return char


@toolz.curry
async def update_inventories(
    session: ClientSession, events: Sequence[CharItem]
) -> Iterable[Character]:
    char_ids = map(attrgetter("char_id"), events)
    item_ids = map(attrgetter("item_id"), events)
    timestamps = map(attrgetter("timestamp"), events)

    # The order of IDs is preserved by the Census API
    chars, items = await gather(
        get_characters(session, char_ids),
        get_items(session, {"item_ids": list(item_ids)}),
    )
    return toolz.pipe(
        zip(chars, items, timestamps),
        toolz.map(lambda pair: add_item(*pair)),
    )


def event_reducer(session: ClientSession, db: DB) -> Dispatch:
    """
    Get a dispatch function.
    Given a PS2 websocket event, this function will schedule some task to handle it.
    This may be updating the database with a new character or item.

    If the event is unknown, a warning will be logged.
    Currently supported events:
        ItemAdded:
            Adds the item to the owner's inventory if the owner is already in the database.
            Otherwise, inserts the character into the database.
    """
    SUPPORTED = {
        "ItemAdded",
    }
    char_queue: RequestQueue[CharItem] = RequestQueue(
        update_inventories(session),
        push_chars(db),
        logger=char_logger,
    )

    def dispatch(event: Event) -> None:
        payload = event["payload"]
        event_type = payload.get("event_name")
        if event_type is None or event_type not in SUPPORTED:
            event_logger.warn(f"Ignoring event: {event}")

        # Filter ItemAdded events for account wide items
        if event_type == "ItemAdded" and is_account_wide(
            item_added := to_item_added(payload)
        ):
            char_item = to_char_item(item_added)
            create_task(char_queue.add(char_item))
            char_logger.debug(f"Queued character {payload['character_id']}")

    return dispatch
