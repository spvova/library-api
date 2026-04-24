from fastapi import FastAPI
from api.books import router as books_router
from database import engine
from models.book_model import Base
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(books_router)