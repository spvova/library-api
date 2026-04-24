import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongo_admin:password@localhost:27017/?authSource=admin")
MONGODB_DB = os.getenv("MONGODB_DB", "books")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[MONGODB_DB]

async def get_db():
    return database