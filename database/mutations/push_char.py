import toolz.curried as toolz
from typing import Iterator
from operator import methodcaller
from traceback import print_exc

from database.db_client import client
from entities import Character
from database.mutations.mutation import batch_mutate


async def push_chars(chars: list[Character]) -> None:
    js = map(methodcaller("json"), chars)
    batch_mutate(client, lambda x: print_exc(), js)
