from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from entities import Factions, Servers


class Confidence(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Outfit(BaseModel):
    tag: str | None
    id: int | None


class CharacterResult(BaseModel):
    name: str
    id: int
    outfit: Outfit
    faction_id: Factions
    server_id: Servers
    last_login: datetime
    battle_rank: int

    n_items: int
    confidence: Confidence
