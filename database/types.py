from typing import TypeAlias
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabse,
    AsyncIOMotorCollection,
    AsyncIOMotorCursor,
)
from typing import Literal, NewType

# DB-related aliases
DBClient: TypeAlias = AsyncIOMotorClient
DB: TypeAlias = AsyncIOMotorDatabse
DBCollection: TypeAlias = AsyncIOMotorCollection
Cursor: TypeAlias = AsyncIOMotorCursor
Filter = NewType("Filter", dict)

# Domain-specific aliases
XID = NewType("XID", int)
UID = NewType("UID", int)
Collection = Literal["characters"]
