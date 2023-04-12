from pydantic import BaseModel
from datetime import datetime

from entities import XID, Servers


class LoginPayload(BaseModel):
    character_id: XID
    event_name: str
    timestamp: datetime
    world_id: Servers
