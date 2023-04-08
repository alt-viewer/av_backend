from typing import Container, TypeVar, Callable, Hashable
import toolz.curried as toolz


@toolz.curry
def omit(blacklist: Container[Hashable], d: dict) -> dict:
    """Return a new dictionary without the blacklisted keys."""
    return toolz.keyfilter(lambda k: k not in blacklist, d)


@toolz.curry
def pick(whitelist: Container[Hashable], d: dict) -> dict:
    return toolz.keyfilter(lambda k: k in whitelist, d)


K = TypeVar("K")
V = TypeVar("V")


@toolz.curry
def replace_with(k: K, new_k: K, f: Callable[[V], V], d: dict[K, V]) -> dict[K, V]:
    """
    Return a new dictionary where the old key `k`
    is replaced by `new_k`: `f` of the old value of `k`
    """
    x = d[k]
    return omit([k], d) | {new_k: x}


@toolz.curry
def has_all(required: list[str], d: dict) -> bool:
    return all(k in d for k in required)
