from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel

from entities.faction import Factions
from entities.item import Item
from entities.server import Servers
from entities.abstracts.jsonable import Jsonable


@dataclass
class Character(Jsonable):
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

    def update(
        self,
        name: str = None,
        id: int = None,
        items: list[Item] = None,
        outfit_tag: str | None = None,
        outfit_id: int | None = None,
        faction_id: Factions = None,
        last_login: datetime = None,
        server_id: Servers = None,
        battle_rank: int = None,
    ) -> Character:
        """Create a new character with the union of the new and old attributes"""
        return Character(
            name or self.name,
            id or self.id,
            items or self.items,
            outfit_tag or self.outfit_tag,
            outfit_id or self.outfit_id,
            faction_id or self.faction_id,
            last_login or self.last_login,
            server_id or self.server_id,
            battle_rank or self.battle_rank,
        )


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
