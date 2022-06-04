from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from typing import TypeAlias

from entities.faction import Factions
from entities.item import Item, ItemDict
from entities.enums import Servers
from entities.abstracts.jsonable import Jsonable
from entities.abstracts.inventory import HasInventory


@dataclass
class Character(Jsonable, HasInventory):
    # Census-side
    name: str
    id: int
    items: list[Item]
    outfit_tag: str | None
    outfit_id: int | None
    faction_id: Factions
    last_login: datetime
    server_id: Servers
    battle_rank: int

    # Internal-side
    uid: str | None

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
            "uid": self.uid,
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
        uid: str = None,
    ) -> "Character":
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
            uid or self.uid,
        )

    def __str__(self) -> str:
        return f"""
        Character(
            name={self.name},
            xid={self.id},
            items={self._hide_items()},
            outfit_tag={self.outfit_tag},
            outfit_id={self.outfit_id},
            faction_id={self.faction_id},
            last_login={self.last_login},
            server_id={self.server_id},
            battle_rank={self.battle_rank},
            uid={self.uid}
        )
        """

    def __repr__(self) -> str:
        return f"""
        Character(
            name={self.name},
            xid={self.id},
            items={self.items},
            outfit_tag={self.outfit_tag},
            outfit_id={self.outfit_id},
            faction_id={self.faction_id},
            last_login={self.last_login},
            server_id={self.server_id},
            battle_rank={self.battle_rank},
            uid={self.uid}
        )
        """

    def _hide_items(self) -> str:
        return f"<{len(self.items)} items>"


@dataclass
class DBCharacter(Character):
    peers: list[int]
    eliminated: list[int]

    def json(self) -> dict:
        return {**super().json(), "peers": self.peers, "eliminated": self.eliminated}


@dataclass
class MatchChar:
    """A partial Character used for comparing characters."""

    uid: str
    last_login: datetime
    items: list[Item]
    eliminated: list[str]


# Necessary because working with Python classes
# is extremely slow.
# Shape: {
#     id: str  (Character UID),
#     last_login: str (datetime string),
#     items: list[ItemDict],
#     eliminated: list[str]  (Character UIDs)
# }
MatchCharDict: TypeAlias = dict
