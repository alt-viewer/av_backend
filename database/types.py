from typing import TypeAlias
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
    AsyncIOMotorCursor,
)
from typing import Literal, NewType

# DB-related aliases
DBClient: TypeAlias = AsyncIOMotorClient
DB: TypeAlias = AsyncIOMotorDatabase
DBCollection: TypeAlias = AsyncIOMotorCollection
Cursor: TypeAlias = AsyncIOMotorCursor
Filter = NewType("Filter", dict)

# Domain-specific aliases
Collection = Literal["characters"]
