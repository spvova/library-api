from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from schemas.book import BookCreate, Book, BookListResponse
from services.book_service import BookService
from repository.book_repository import BookRepository
from database import get_db

router = APIRouter()

@router.get("/", response_model=BookListResponse)
async def get_books(
    status: Optional[str] = Query(None, description="Filter by status: available or issued"),
    author: Optional[str] = Query(None, description="Filter by author"),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$", description="Sort by title or year"),
    sort_order: str = Query('asc', pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of books to return"),
    db = Depends(get_db)
):
    repo = BookRepository(db)
    service = BookService(repo)
    books = await service.get_books(status=status, author=author, sort_by=sort_by, sort_order=sort_order, offset=offset, limit=limit)
    return books

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: str, db = Depends(get_db)):
    repo = BookRepository(db)
    service = BookService(repo)
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/", response_model=Book, status_code=201)
async def add_book(book: BookCreate, db = Depends(get_db)):
    repo = BookRepository(db)
    service = BookService(repo)
    new_book = await service.add_book(book.model_dump())
    return new_book

@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str, db = Depends(get_db)):
    repo = BookRepository(db)
    service = BookService(repo)
    await service.delete_book(book_id)
    return