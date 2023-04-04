from typing import TypeAlias
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabse,
    AsyncIOMotorCollection,
    AsyncIOMotorCursor,
)

DBClient: TypeAlias = AsyncIOMotorClient
DB: TypeAlias = AsyncIOMotorDatabse
Collection: TypeAlias = AsyncIOMotorCollection
Cursor: TypeAlias = AsyncIOMotorCursor
Filter: TypeAlias = dict
XID: TypeAlias = int
