from dataclasses import dataclass
from typing import Iterable

from entities.character import MatchCharDict
from eggs import replace_with
from entities.abstracts import HasInventory


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
    return "[" + ",\n".join(map(str, ms)) + "]"
