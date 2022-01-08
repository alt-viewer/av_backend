from typing import Optional, Iterator, List
from thefuzz.fuzz import ratio
import toolz.curried
from datetime import datetime

from entities.match import Match
from entities.character import Character
from entities.item import Item


def item_ids(char: Character) -> List[str]:
    return list(map(lambda i: i.id, char.items))


def compare(
    char1: Character, char2: Character, min_confidence: int = 70
) -> Optional[Match]:
    confidence = ratio(item_ids(char1), item_ids(char2))
    if confidence > min_confidence:
        return Match(char1.id, char2.id, datetime.now(), confidence)
    return None
