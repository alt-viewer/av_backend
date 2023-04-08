import toolz.curried as toolz

from database.types import DB, Collection


async def count(db: DB, collection: Collection) -> int:
    pipeline = [{"_id": ""}]
    return await db[collection].count_documents()
