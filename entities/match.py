from dataclasses import dataclass
from datetime import datetime
from typing import List

# TODO: this structure needs more thought
@dataclass
class Match:
    char1_id: str
    char2_id: str
    matched_at: datetime
    confidence: int
