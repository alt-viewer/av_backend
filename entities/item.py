from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from typing import TypedDict

from entities.abstracts import Jsonable
from entities.primitive import XID
from entities.enums import Factions


@dataclass
class Item(Jsonable):
    """An account-level item possessed by a character."""

    # PS2 ID - referred to as XID in the DB
    id: XID | None
    last_recorded: datetime
    # DB ID - referred to as ID in the DB
    uid: str | None = None

    def json(self) -> dict:
        """
        Convert this instance to a JSON-compatible dict.

        NOTE: `lastRecorded` is left as a `datetime` to allow the user to decide which format they want
        """
        return {
            "xid": self.id,
            "_id": self.uid,
            "lastRecorded": self.last_recorded,
        }

    @property
    def __key(self) -> tuple:
        """Get the attributes to hash by"""
        return (self.id,)

    def __hash__(self) -> int:
        return hash(self.__key)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return self.__key == other.__key


@dataclass
class ItemInfo:
    xid: XID
    type_id: XID
    category_id: XID
    vehicle_weapon: bool
    name: str
    faction_id: Factions


class ItemDict(TypedDict):
    xid: XID
    type_id: XID
    category_id: XID
    name: str
    is_vehicle_weapon: bool
    lastRecorded: datetime
