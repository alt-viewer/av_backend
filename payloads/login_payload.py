from pydantic import BaseModel


class LoginPayload(BaseModel):
    character_id: int
    event_name: str
    timestamp: int
    world_id: int
