"""
This route will find matches by comparing characters in memory rather than by hash.
It is more accurate, but slower.
"""

from fastapi import APIRouter, HTTPException
from operator import methodcaller
import toolz.curried as toolz

from database import get_chars_by_name, get_sessions
from rest.logic import find_matches_deep
from rest.models.searching import CharacterResult

GQL_URL = "http://localhost:8080/graphql"

router = APIRouter(prefix="/deep-search", tags=["search"])


@router.get("/{name}")
async def main_route(name: str) -> list[CharacterResult]:
    if not name:
        raise HTTPException(status_code=401, detail="You must provide a character name")

    async with get_sessions() as (_, db):
        char_results = await get_chars_by_name(db, [name])
        if not char_results:
            raise HTTPException(status_code=404, detail="Character unavailable")

        return toolz.pipe(
            await find_matches_deep(db, char_results[0]),
            toolz.map(methodcaller("json")),
            list,
        )


deep_search_router = router
