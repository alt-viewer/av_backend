from dataclasses import dataclass
from typing import Iterable, TypedDict
from datetime import datetime

from entities.item import Item, ItemDict
from utils import replace_with
from entities.abstracts import HasInventory
from entities.primitive import UID, XID


@dataclass
class MatchChar:
    """A partial Character used for comparing characters."""

    uid: str
    last_login: datetime
    items: list[Item]
    eliminated: list[str]


class MatchCharDict(TypedDict):
    _id: UID
    xid: XID
    lastLogin: datetime
    items: list[ItemDict]


@dataclass
class Match(HasInventory):
    peers: list[MatchCharDict]
    confidence: float

    def __str__(self) -> str:
        return f"Match(confidence={self.confidence}, peers={self._hide_items()})"

    def __repr__(self) -> str:
        return f"Match(confidence={self.confidence}, peers={self.peers})"

    def _hide_items(self) -> str:
        return str(list(map(replace_with("items", "item_count", len), self.peers)))


def show_matches(ms: Iterable[Match]) -> str:
    return "[" + ",\n\t".join(map(str, ms)) + "]"
