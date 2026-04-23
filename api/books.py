from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from schemas.book import BookCreate
from models.book_model import Book
from services.book_service import BookService

router = APIRouter()

service = BookService()

@router.get("/", response_model=List[Book])
async def get_books(
    status: Optional[str] = Query(None, description="Filter by status: available or issued"),
    author: Optional[str] = Query(None, description="Filter by author"),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$", description="Sort by title or year"),
    sort_order: str = Query('asc', pattern="^(asc|desc)$", description="Sort order: asc or desc")
):
    return service.get_books(status=status, author=author, sort_by=sort_by, sort_order=sort_order)

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: str):
    book = service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=Book, status_code=201)
async def add_book(book: BookCreate):
    return service.add_book(book.dict())

@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str):
    service.delete_book(book_id)
    return