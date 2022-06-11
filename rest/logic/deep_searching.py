from typing import Iterable

from rest.models.searching import CharacterResult, Confidence, Outfit
from database import GQLClient, get_char
from matching import find_matches
from entities import MatchCharDict, Character
from queries import gathercat


def confidence(items: int) -> Confidence:
    if items < 10:
        return Confidence.LOW
    elif items < 20:
        return Confidence.MEDIUM
    else:
        return Confidence.HIGH


def to_result(match: Character) -> CharacterResult:
    inventory = len(match.items)
    return CharacterResult(
        match.name,
        match.id,
        Outfit(
            match.outfit_tag,
            match.outfit_id,
        ),
        match.faction_id,
        match.server_id,
        match.last_login,
        match.battle_rank,
        inventory,
        confidence(inventory),
    )


async def find_matches_deep(session: GQLClient, name: str) -> Iterable[CharacterResult]:
    chars = await get_char(session, names=[name])
    if not chars:
        raise ValueError("Character not found in local DB")
    matches = await find_matches(session, chars[0])
    match_chars = await gathercat(lambda m: get_char(session, uid=m["id"]), matches)
    return map(to_result, match_chars)
