"""
Check for any new `ItemAddedContext`s
"""
from argparse import ArgumentParser
import asyncio
from aiohttp import ClientSession
import logging
import os
import sys

# Set working directory to project root
currentdir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, currentdir)

from database import sessions, DB
from entities import ItemAddedContext, Servers
from census import census_url
from listener import (
    LoginListener,
    Dispatch,
)

context_logger = logging.getLogger("found context")
context_logger.setLevel(logging.INFO)


def diff_contexts(sample: set[str]) -> set[str]:
    return sample - set(e.value for e in ItemAddedContext)


def dispatch(session: ClientSession, db: DB, contexts: set[str]) -> Dispatch:
    def dispatcher(event: dict) -> None:
        payload = event["payload"]
        event_type = payload.get("event_name")
        if not event_type:
            return
        if event_type == "ItemAdded":
            context = payload["context"]
            contexts.add(context)
            context_logger.info(f" {context}")

    return dispatcher


async def stop_in(minutes: int, listener: LoginListener) -> None:
    SECONDS_IN_A_MINUTE = 60
    seconds = minutes * SECONDS_IN_A_MINUTE
    await asyncio.sleep(seconds)
    await listener.stop()


async def listen_for(minutes: int) -> set[str]:
    """Listen for `minutes` and return all item added contexts found"""
    async with sessions() as (session, db):
        contexts: set[str] = set()
        dispatcher = dispatch(session, db, contexts)
        listener = LoginListener(session, dispatcher)
        asyncio.create_task(listener.listen())
        await stop_in(minutes, listener)
    return contexts


def show_contexts(cs: set[str]) -> str:
    return "{\n" + "\n\t".join(cs) + "\n}"


async def main():
    parser = ArgumentParser(
        prog="update-item-added-contexts",
        description="Listen to the `ItemAdded` event stream for a while and output any unknown `ItemAddedContext`s",
    )

    parser.add_argument(
        "time",
        default=15,
        help="How many minutes to listen for. A larger amount of time will create a better sample",
        type=int,
    )
    args = parser.parse_args()
    found = await listen_for(args.time)
    new = diff_contexts(found)
    print("-" * 16)
    print("RESULTS")
    print(show_contexts(new) if new else "No new contexts discovered")


if __name__ == "__main__":
    asyncio.run(main())
