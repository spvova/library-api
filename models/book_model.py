from sqlalchemy import Column, String, Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase
import uuid
from enum import Enum

class BookStatus(str, Enum):
    AVAILABLE = 'available'
    ISSUED = 'issued'

class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = 'books'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(BookStatus), nullable=False)
    year = Column(Integer, nullable=False)