from operator import methodcaller
from typing import Iterator

from entities.abstracts.jsonable import Jsonable


_to_json = methodcaller("json")


def convert_json(xs: Iterator[Jsonable]) -> list[dict]:
    return list(map(_to_json, xs))
