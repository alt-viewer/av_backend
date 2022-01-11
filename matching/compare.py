from typing import Iterator, List
from thefuzz.fuzz import ratio
import toolz.curried
from datetime import datetime

from entities.match import Match
from entities.character import Character
from entities.item import Item


def item_ids(char: Character) -> List[int]:
    return list(map(lambda i: i.id, char.items))


def compare(
    char1: Character, char2: Character, min_confidence: int = 70
) -> Match | None:
    is1, is2 = item_ids(char1), item_ids(char2)
    # Comparing 2 characters with no account items is not
    # a useful comparison
    if len(is1) == 0 or len(is2) == 0:
        return None

    confidence = ratio(is1, is2)
    if confidence > min_confidence:
        return Match(char1.id, char2.id, datetime.now(), confidence)
    return None
