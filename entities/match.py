from dataclasses import dataclass
from datetime import datetime
from typing import List

# TODO: this structure needs more thought
@dataclass
class Match:
    char1_id: int
    char2_id: int
    matched_at: datetime
    confidence: int
