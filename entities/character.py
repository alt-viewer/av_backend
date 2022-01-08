from dataclasses import dataclass
from typing import List
from datetime import datetime

from entities.faction import Faction
from entities.item import Item


@dataclass
class Character:
    name: str
    id: str
    items: List[Item]
    outfit_tag: str
    outfit_id: str
    faction_id: int
    last_login: datetime
