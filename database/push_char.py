import toolz.curried as toolz

from database.db_client import client
from database.mutation import mutations
from entities import Character


async def push_chars(chars: list[Character]) -> None:
    txn = client.txn()
    try:
        req = mutations(txn, chars)
        txn.async_do_request(req)
        txn.commit()
    finally:
        txn.discard()
