from rest.models.searching import CharacterResult
from database import GQLClient


async def find_matches_deep(session: GQLClient, name: str) -> list[CharacterResult]:
    return []
