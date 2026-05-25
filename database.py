import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncGenerator

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB = os.getenv("MONGODB_DB", "library")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[MONGODB_DB]

async def get_db() -> AsyncGenerator:
    yield database