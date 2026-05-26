import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncGenerator

MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "mongo_admin")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGODB_DB = os.getenv("MONGODB_DB", "library")

MONGODB_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGODB_DB}?authSource=admin"

client = AsyncIOMotorClient(MONGODB_URL)
database = client[MONGODB_DB]

async def get_db() -> AsyncGenerator:
    yield database