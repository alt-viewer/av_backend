from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from entities.abstracts.jsonable import Jsonable


@dataclass
class Item(Jsonable):
    """An account-level item possessed by a character."""

    id: int
    last_recorded: datetime
    uid: str | None = None

    def json(self) -> dict:
        return {"xid": self.id, "last_recorded": self.last_recorded.isoformat()}

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
