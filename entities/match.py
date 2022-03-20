from dataclasses import dataclass

from entities.character import MatchCharDict


@dataclass
class Match:
    peers: list[MatchCharDict]
    confidence: float
