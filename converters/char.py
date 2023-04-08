from datetime import datetime
from typing import Iterator
import toolz.curried as toolz
import logging

from payloads import CharacterPayload
from entities import Character, Factions, Servers
from converters.item import items_from_census, items_from_db
from logger import log_filter
from utils.dict import has_all

char_logger = logging.getLogger("character")


def parse_timestamp(t: str) -> datetime:
    """Convert a PS2 timestamp to a valid ISO timestamp"""
    # The API returns an invalid fffff... portion
    # See: https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
    return datetime.fromisoformat(t[:-2])


def cast_char(char_data: dict) -> dict:
    """Cast the types of the character response to the appropriate types"""
    return {
        **char_data,
        # Explicit conversion needed since Enum doesn't do it
        "faction_id": int(char_data["faction_id"]),
        "world_id": int(char_data["world_id"]),
    }


def make_char(char: CharacterPayload) -> Character:
    """Build a Character from a CharacterPayload."""
    if not char.items:
        raise ValueError("Character lacks items")

    return Character(
        char.name.first,
        char.character_id,
        items_from_census(char.items),
        char.outfit.alias if char.outfit else None,
        char.outfit.outfit_id if char.outfit else None,
        char.faction_id,
        parse_timestamp(char.times.last_login_date),
        char.world_id,
        char.battle_rank.value,
        None,
    )


def chars_from_census(raw_chars: list[dict]) -> Iterator[Character]:
    """Convert many characters from a PS2 API response"""
    return toolz.pipe(
        raw_chars,
        # Ignore characters that have no items or server
        log_filter(char_logger, has_all(["items", "world_id"])),
        toolz.map(toolz.compose(make_char, lambda c: CharacterPayload(**c), cast_char)),
    )


def char_from_db(d: dict) -> Character:
    """
    Load a character from the database.
    Use `char_from_census` for the PS2 API.
    """
    items = d.get("items")
    return Character(
        d["name"],
        d["xid"],
        items_from_db(items) if items else [],
        d.get("outfitTag"),
        d.get("outfitID"),
        d["factionID"],
        d["lastLogin"],
        d["serverID"],
        d["battleRank"],
        d["_id"],
    )
