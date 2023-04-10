import toolz.curried as toolz

from entities import Character
from entities.converters import char_from_db, with_conversion
from database.sessions import DB


@toolz.curry
@with_conversion(char_from_db)
async def get_chars_by_name(db: DB, names: list[str]) -> list[Character]:
    return await db.characters.find({"name": {"$in": names}})


@toolz.curry
@with_conversion(char_from_db)
async def get_char_by_xid(db: DB, xid: int) -> list[Character]:
    return await db.characters.find_one({"xid": xid})


@toolz.curry
@with_conversion(char_from_db)
async def get_char_by_uid(db: DB, uid: int) -> list[Character]:
    return await db.characters.find_one({"uid": uid})
