import toolz.curried as toolz
from typing import Iterator

from database.db_client import client
from database.mutation import mutations
from entities import Character


async def push_chars(chars: list[Character]) -> None:
    txn = client.txn()
    try:
        for char in chars:
            txn.mutate(set_obj=char.json())
        txn.commit()
    finally:
        txn.discard()
