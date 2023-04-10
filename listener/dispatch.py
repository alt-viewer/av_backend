from asyncio import create_task
import logging
from typing import NewType, TypeAlias
from collections.abc import Callable, Iterable, Awaitable
from aiohttp import ClientSession
import toolz.curried as toolz
from functools import wraps

from listener.queue import RequestQueue
from listener.filter_item import is_account_wide
from census import get_characters, with_page
from database import push_chars, DB, XID
from entities import Character
from payloads import ItemAdded


Event = NewType("Event", dict)
CharItem: TypeAlias = dict[XID, XID]  # Mapping of (character XID, item XID)
Dispatch: TypeAlias = Callable[[Event], None]

event_logger = logging.getLogger("event reducer")
char_logger = logging.getLogger("character")

payload = toolz.get("payload")


def to_item_added(payload: dict) -> ItemAdded:
    return toolz.pipe(
        payload,
        lambda p: {**p, "world_id": int(p["world_id"])},
        lambda p: ItemAdded(**p),
    )


def with_items(func: Callable[[Iterable[int]], Awaitable[list[Character]]]):
    @wraps(func)
    async def add_items(
        session: ClientSession, events: Iterable[CharItem]
    ) -> Awaitable[list[Character]]:
        char_ids = None
        result = await get_characters(
            session,
        )
        pass


def event_reducer(aiohttp_session: ClientSession, db: DB) -> Dispatch:
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
    SUPPORTED = {"PlayerLogin", "ItemAdded"}
    char_queue: RequestQueue[int] = RequestQueue(
        with_page()(get_characters(aiohttp_session)),
        push_chars(db),
        logger=char_logger,
    )

    def dispatch(event: Event) -> None:
        payload = event["payload"]
        event_type = payload.get("event_name")
        if event_type is None or event_type not in SUPPORTED:
            event_logger.warn(f"Ignoring event: {event}")

        # Filter ItemAdded events for account wide items
        if event_type == "ItemAdded" and is_account_wide(to_item_added(payload)):
            pass

        # !TODO: stop requesting character items and take this item forward
        create_task(char_queue.add(payload["character_id"]))
        char_logger.debug(f"Queued character {payload['character_id']}")

    return dispatch
