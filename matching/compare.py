from itertools import combinations
from typing import Iterable
import toolz.curried as toolz

from matching.partition import group
from entities import MatchCharDict, Match

THRESHOLD = 80


def set_ratio(xs: set, ys: set) -> float:
    """
    Get the percentage of items in `ys` that are in `xs`
    """
    ratio = len(xs.intersection(ys)) / len(xs)
    return round(ratio * 100, 2)


@toolz.curry
def compare(char1: MatchCharDict, char2: MatchCharDict) -> float:
    """
    Get the percentage of items belonging to `char2` that belong to `char1`
    """
    item_ids = toolz.compose(toolz.map(toolz.get_in(["xid"])), toolz.get_in(["items"]))
    is1, is2 = item_ids(char1), item_ids(char2)
    return set_ratio(set(is1), set(is2))


def pair_chars(
    chars: Iterable[MatchCharDict],
) -> Iterable[tuple[MatchCharDict, MatchCharDict]]:
    return combinations(chars, 2)


def search(c: MatchCharDict, cs: list[MatchCharDict]) -> list[Match]:
    """
    Find all matches for `c` in `cs`.

    NOTE:
        `c` will always be the first in Match.peers
        and the other character will be the second.
    """
    # Eliminate all characters that don't have a similar number of items
    grouped = group(cs)
    group_key = round(len(c["items"]) / 10) * 10
    chosen = grouped[group_key]

    # Linear search through the remaining characters
    passed: list[Match] = []
    for c2 in chosen:
        # Skip the target
        if c2["id"] == c["id"]:
            continue

        ratio = compare(c, c2)
        if ratio >= THRESHOLD:
            passed.append(Match([c, c2], ratio))
    return passed
