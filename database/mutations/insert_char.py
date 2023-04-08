from pymongo import UpdateOne
from typing import Iterable
import toolz.curried as toolz

from database.sessions import DB
from entities import Character


@toolz.curry
async def push_chars(db: DB, chars: Iterable[Character]) -> None:
    await db.characters.bulk_write(
        [
            UpdateOne({"xid": char.xid}, {"$set": char.json()}, upsert=True)
            for char in chars
        ]
    )
