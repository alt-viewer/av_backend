from dataclasses import dataclass
from datetime import datetime


@dataclass
class Item:
    """An account-level item possessed by a character."""

    id: int
    last_recorded: datetime

    def json(self) -> dict:
        return {"xid": self.id, "last_recorded": self.last_recorded.isoformat()}
