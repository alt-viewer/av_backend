from typing import TypeAlias
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabse,
    AsyncIOMotorCollection,
)

DBClient: TypeAlias = AsyncIOMotorClient
DB: TypeAlias = AsyncIOMotorDatabse
Collection: TypeAlias = AsyncIOMotorCollection
