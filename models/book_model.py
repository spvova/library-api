from pydantic import BaseModel, UUID4
from typing import Optional
from enum import Enum

class BookStatus(str, Enum):
    AVAILABLE = 'available'
    ISSUED = 'issued'

class Book(BaseModel):
    id: UUID4
    title: str
    author: str
    description: Optional[str] = None
    status: BookStatus
    year: int