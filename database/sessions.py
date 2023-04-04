from aiohttp import ClientSession
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabse,
    AsyncIOMotorCollection,
)
from typing import AsyncIterator
from contextlib import asynccontextmanager
import json

from database.types import DB


def load_db_config() -> dict:
    with open("data/db/config.json") as f:
        return json.load(f)


config = load_db_config()


def _session_factory():
    # Singletons
    session: ClientSession | None = None
    database: AsyncIOMotorClient | None = None

    @asynccontextmanager
    async def get_sessions() -> AsyncIterator[tuple[ClientSession, DB]]:
        """
        Create an AIOHTTP session and a MongoDB database reference.
        """
        nonlocal session, database
        try:
            if not session or not database:
                session = ClientSession()
                database = AsyncIOMotorClient(config["host_name"], config["port"])[
                    config["dbName"]
                ]
            yield (session, database)
        finally:
            if session:
                await session.close()

    return get_sessions


get_sessions = _session_factory()
