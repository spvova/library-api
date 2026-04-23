from pydantic import BaseModel
from typing import Optional
from models.book_model import BookStatus

class BookBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    status: BookStatus
    year: int

class BookCreate(BookBase):
    pass