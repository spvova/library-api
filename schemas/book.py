from pydantic import BaseModel, ConfigDict
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

class Book(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: str