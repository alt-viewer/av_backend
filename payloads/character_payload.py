from pydantic import BaseModel
from datetime import datetime

from entities import Servers, Factions


class FactionInfo(BaseModel):
    faction_id: int | None


class ItemObj(BaseModel):
    item_id: int
    account_level: bool | None
    stack_size: int | None
    faction_info: FactionInfo | None


class OutfitObj(BaseModel):
    outfit_id: int
    member_since_date: datetime
    outfit_id_merged: int
    name: str
    name_lower: str
    alias: str | None
    alias_lower: str | None
    time_created: int
    time_created_date: datetime
    leader_character_id: int
    member_count: int


class TimesObj(BaseModel):
    last_login_date: str


class NameObj(BaseModel):
    first: str


class BattleRankObj(BaseModel):
    value: int


class CharacterPayload(BaseModel):
    items: list[ItemObj] | None
    outfit: OutfitObj | None
    world_id: Servers
    times: TimesObj
    name: NameObj
    character_id: int
    faction_id: Factions
    battle_rank: BattleRankObj
