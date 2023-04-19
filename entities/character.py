from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from typing import TypeAlias

from entities.item import Item, ItemDict
from entities.enums import Servers, Factions
from entities.abstracts import Jsonable, HasInventory


@dataclass
class Character(Jsonable, HasInventory):
    # Census-side
    name: str
    xid: int
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
        """
        Convert this instance to a JSON-compatible dict.

        NOTE: `lastLogin` is left as a `datetime` to allow the user to decide which format they want.
        """
        return (
            {
                "name": self.name,
                "xid": self.xid,
                "outfitTag": self.outfit_tag,
                "outfitID": self.outfit_id,
                "factionID": self.faction_id.value,
                "serverID": self.server_id.value,
                "battleRank": self.battle_rank,
                "lastLogin": self.last_login,  # Defer handling of dates to caller
                "items": [i.json() for i in self.items],
            }
            # Avoid outputting {"_id": None}
            | ({"_id": self.uid} if self.uid is not None else {})
        )

    def update(
        self,
        name: str | None = None,
        xid: int | None = None,
        items: list[Item] | None = None,
        outfit_tag: str | None = None,
        outfit_id: int | None = None,
        faction_id: Factions | None = None,
        last_login: datetime | None = None,
        server_id: Servers | None = None,
        battle_rank: int | None = None,
        uid: str | None = None,
    ) -> "Character":
        """Create a new character with the union of the new and old attributes"""
        return Character(
            name or self.name,
            xid or self.xid,
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
            xid={self.xid},
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
            xid={self.xid},
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
