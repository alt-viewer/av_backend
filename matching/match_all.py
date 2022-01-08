from itertools import combinations
import toolz.curried
from typing import List, Iterator

from entities.character import Character
from entities.match import Match
from matching.compare import compare


def match_all(characters: List[Character]) -> Iterator[Match]:
    """
    Compare all characters in a list against each other.
    """
    pairs = combinations(characters, 2)
    return filter(None, map(lambda pair: compare(*pair), pairs))
