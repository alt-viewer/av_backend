from dataclasses import dataclass
from typing import List
from datetime import datetime

from entities.faction import Factions
from entities.item import Item
from entities.server import Servers


@dataclass
class Character:
    name: str
    id: int
    items: List[Item]
    outfit_tag: str | None
    outfit_id: int | None
    faction_id: Factions
    last_login: datetime
    server_id: Servers
    battle_rank: int
