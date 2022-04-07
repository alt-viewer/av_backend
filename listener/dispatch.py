from asyncio import create_task
import logging
from typing import Callable, TypeAlias
from aiohttp import ClientSession

from listener.queue import RequestQueue
from queries import get_characters, with_page
from database import push_chars, GQLClient
from entities import Character

Event: TypeAlias = dict
Dispatch: TypeAlias = Callable[[Event], None]

event_logger = logging.getLogger("event reducer")
char_logger = logging.getLogger("character")
item_logger = logging.getLogger("item")


def event_reducer(aiohttp_session: ClientSession, gql_session: GQLClient) -> Dispatch:
    """
    Get a dispatch function.
    Given a PS2 websocket event, this function will schedule some task to handle it.
    This may be updating the database with a new character or item.

    If the event is unknown, a warning will be logged.
    Currently supported events:
        PlayerLogin:
            Puts the character ID in a queue that will
            request the characters from Census in batches.
            The responses are used to update the database.
        ItemAdded:
            Similar to PlayerLogin but for items.
            Updates the character's items if it exists in the database.
            Otherwise, inserts the characters into the database.
    """
    char_queue = RequestQueue[Character](
        with_page()(get_characters(aiohttp_session)),
        push_chars(gql_session),
        logger=char_logger,
    )

    def dispatch(event: Event) -> None:
        payload = event["payload"]
        event_type = payload.get("event_name")
        if event_type == "PlayerLogin":
            create_task(char_queue.add(payload["character_id"]))
            char_logger.debug(f"Queued character {payload['character_id']}")
        elif event_type == "ItemAdded":
            item_logger.debug(
                "Item event received, but handling has yet to be implemented"
            )
        else:
            event_logger.warn(f"Ignoring event: {event}")

    return dispatch
