from fastapi import APIRouter, HTTPException, Query, Depends, Header, status
from typing import Optional
from auth.jwt_service import verify_token
from schemas.book import BookCreate, Book, BookListResponse
from services.book_service import BookService
from repository.book_repository import BookRepository
from database import get_db

router = APIRouter()


async def verify_token_dependency(authorization: Optional[str] = Header(None)) -> str:
    """Verify JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload.get("sub")


@router.get("/", response_model=BookListResponse)
async def get_books(
    status: Optional[str] = Query(None, description="Filter by status: available or issued"),
    author: Optional[str] = Query(None, description="Filter by author"),
    sort_by: Optional[str] = Query(None, pattern="^(title|year)$", description="Sort by title or year"),
    sort_order: str = Query('asc', pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of books to return"),
    current_user: str = Depends(verify_token_dependency),
    db = Depends(get_db)
):
    repo = BookRepository(db)
    service = BookService(repo)
    books = await service.get_books(status=status, author=author, sort_by=sort_by, sort_order=sort_order, offset=offset, limit=limit)
    return books


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: str, current_user: str = Depends(verify_token_dependency), db = Depends(get_db)):
    repo = BookRepository(db)
    service = BookService(repo)
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=Book, status_code=201)
async def add_book(book: BookCreate, current_user: str = Depends(verify_token_dependency), db = Depends(get_db)):
    repo = BookRepository(db)
    service = BookService(repo)
    new_book = await service.add_book(book.model_dump())
    return new_book


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: str, current_user: str = Depends(verify_token_dependency), db = Depends(get_db)):
    repo = BookRepository(db)
    service = BookService(repo)
    await service.delete_book(book_id)
    return