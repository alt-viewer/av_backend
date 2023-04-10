from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from typing import TypedDict

from entities.abstracts import Jsonable
from entities.primitive import XID


@dataclass
class Item(Jsonable):
    """An account-level item possessed by a character."""

    # PS2 ID - referred to as XID in the DB
    id: int | None
    last_recorded: datetime
    # DB ID - referred to as ID in the DB
    uid: str | None = None

    def json(self) -> dict:
        return {
            "xid": self.id,
            "_id": self.uid,
            "lastRecorded": self.last_recorded.isoformat(),
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


class ItemDict(TypedDict):
    xid: XID
    lastRecorded: datetime
