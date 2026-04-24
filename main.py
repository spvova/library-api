from fastapi import FastAPI
from api.books import router as books_router
from database import client

app = FastAPI()

@app.on_event("shutdown")
def shutdown():
    client.close()

app.include_router(books_router, prefix="/books")