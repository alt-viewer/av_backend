from operator import methodcaller
from typing import Iterable

from entities.abstracts import Jsonable


_to_json = methodcaller("json")


def convert_json(xs: Iterable[Jsonable]) -> list[dict]:
    """Convert a list of Jsonables to their JSON form"""
    return list(map(_to_json, xs))
