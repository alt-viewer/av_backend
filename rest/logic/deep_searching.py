from typing import Iterable
import toolz.curried as toolz

from rest.models.searching import CharacterResult, Confidence, Outfit
from database import GQLClient, get_char
from matching import find_matches
from entities import MatchCharDict, Character, Match
from queries import gathercat


def get_peer(m: Match) -> dict:
    """Gets the other character in a match"""
    # Assuming that the requested character is always peers[0]
    return toolz.second(m.peers)


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
        name=match.name,
        id=match.id,
        outfit=Outfit(
            tag=match.outfit_tag,
            id=match.outfit_id,
        ),
        faction_id=match.faction_id,
        server_id=match.server_id,
        last_login=match.last_login,
        battle_rank=match.battle_rank,
        n_items=inventory,
        confidence=confidence(inventory),
    )


async def find_matches_deep(
    session: GQLClient, char: Character
) -> Iterable[CharacterResult]:
    matches = await find_matches(session, char)
    match_chars = await gathercat(
        toolz.compose(lambda c: get_char(session, uid=c["id"]), get_peer), matches
    )
    return map(to_result, match_chars)
