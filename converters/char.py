from datetime import datetime
from typing import Iterator
import toolz.curried as toolz
import logging

# datetime.fromisoformat doesn't play nicely with DGraph's
# RFC datetimes
from dateutil.parser import parse as parse_rfc

from payloads import CharacterPayload
from entities import Character, Factions, Servers
from converters.item import parse_char_items, load_items
from logger import log_filter

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
        parse_char_items(char.items),
        char.outfit.alias if char.outfit else None,
        char.outfit.outfit_id if char.outfit else None,
        char.faction_id,
        parse_timestamp(char.times.last_login_date),
        char.world_id,
        char.battle_rank.value,
        None,
    )


@toolz.curry
def has_all(required: list[str], d: dict) -> bool:
    return all(k in d for k in required)


def parse_characters(raw_chars: list[dict]) -> Iterator[Character]:
    """Convert many characters from a PS2 API response"""
    return toolz.pipe(
        raw_chars,
        # Ignore characters that have no items or server
        log_filter(char_logger, has_all(["items", "world_id"])),
        toolz.map(toolz.compose(make_char, lambda c: CharacterPayload(**c), cast_char)),
    )


def load_char(char: dict) -> Character:
    """
    Load a character from the database.
    Use `parse_characters` for the PS2 API.
    """
    return Character(
        char["name"],
        char["xid"],
        load_items(char["items"]),
        char["outfit_tag"],
        char["outfit_id"],
        Factions(int(char["faction_id"])),
        parse_rfc(char["last_login"]),
        Servers(int(char["server_id"])),
        char["battle_rank"],
        char["uid"],
    )
