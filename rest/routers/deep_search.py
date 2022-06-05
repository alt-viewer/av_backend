"""
This route will find matches by comparing characters in memory rather than by hash.
It is more accurate, but slower.
"""

from fastapi import APIRouter, HTTPException

from database import get_char, get_sessions
from rest.logic import find_matches_deep
from rest.models.searching import CharacterResult

GQL_URL = "http://localhost:8080/graphql"

router = APIRouter(prefix="/deep-search", tags=["search"])


@router.get("/")
async def no_name() -> str:
    return "You must provide a character name"


@router.get("/{name}")
async def main_route(name: str) -> list[CharacterResult]:
    async with get_sessions(GQL_URL) as (_, gql_session):
        char_results = await get_char(gql_session, names=[name])
        if not char_results:
            raise HTTPException(status_code=404, detail="Character unavailable")

        return await find_matches_deep(gql_session, char_results[0])


deep_search_router = router
