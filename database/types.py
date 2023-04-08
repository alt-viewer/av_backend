from typing import TypeAlias
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabse,
    AsyncIOMotorCollection,
    AsyncIOMotorCursor,
)
from typing import Literal

# DB-related aliases
DBClient: TypeAlias = AsyncIOMotorClient
DB: TypeAlias = AsyncIOMotorDatabse
DBCollection: TypeAlias = AsyncIOMotorCollection
Cursor: TypeAlias = AsyncIOMotorCursor
Filter: TypeAlias = dict

# Domain-specific aliases
XID: TypeAlias = int
UID: TypeAlias = int
Collection = Literal["Character"]
