from dataclasses import dataclass
from datetime import datetime


@dataclass
class Item:
    id: str
    last_recorded: datetime
