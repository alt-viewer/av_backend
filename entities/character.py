from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel

from entities.faction import Factions
from entities.item import Item
from entities.server import Servers


@dataclass
class Character:
    name: str
    id: int
    items: list[Item]
    outfit_tag: str | None
    outfit_id: int | None
    faction_id: Factions
    last_login: datetime
    server_id: Servers
    battle_rank: int

    def json(self) -> dict:
        return {
            "name": self.name,
            "xid": self.id,
            "outfit_tag": self.outfit_tag,
            "outfit_id": self.outfit_id,
            "faction_id": self.faction_id.value,
            "server_id": self.server_id.value,
            "battle_rank": self.battle_rank,
            "last_login": self.last_login.isoformat(),
            "items": list(map(lambda i: i.json(), self.items)),
        }


@dataclass
class DBCharacter(Character):
    peers: list[int]
    eliminated: list[int]

    def json(self) -> dict:
        return {**super().json(), "peers": self.peers, "eliminated": self.eliminated}


class MatchChar(BaseModel):
    """A partial Character used for comparing characters."""

    uid: int
    last_login: datetime
    items: list[Item]
    eliminated: list[int]
