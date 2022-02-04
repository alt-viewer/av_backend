from dataclasses import dataclass
from datetime import datetime

from entities.abstracts.jsonable import Jsonable


@dataclass
class Item(Jsonable):
    """An account-level item possessed by a character."""

    id: int
    last_recorded: datetime

    def json(self) -> dict:
        return {"xid": self.id, "last_recorded": self.last_recorded.isoformat()}
