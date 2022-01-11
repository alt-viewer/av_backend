from dataclasses import dataclass
from datetime import datetime


@dataclass
class Item:
    """An account-level item possessed by a character."""

    id: str
    last_recorded: datetime
