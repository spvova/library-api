from typing import List, Optional
from uuid import uuid4
from models.book_model import Book

books: List[Book] = []

def get_all_books() -> List[Book]:
    return books.copy()

def get_book_by_id(book_id: str) -> Optional[Book]:
    for book in books:
        if str(book.id) == book_id:
            return book
    return None

def add_book(book_data: dict) -> Book:
    book = Book(id=uuid4(), **book_data)
    books.append(book)
    return book

def delete_book(book_id: str) -> bool:
    for i, book in enumerate(books):
        if str(book.id) == book_id:
            books.pop(i)
            return True
    return False

def get_books_filtered(status: Optional[str] = None, author: Optional[str] = None, sort_by: Optional[str] = None, sort_order: str = 'asc') -> List[Book]:
    filtered = books[:]
    if status:
        filtered = [b for b in filtered if b.status.value == status]
    if author:
        filtered = [b for b in filtered if b.author == author]
    if sort_by:
        reverse = sort_order == 'desc'
        if sort_by == 'title':
            filtered.sort(key=lambda b: b.title, reverse=reverse)
        elif sort_by == 'year':
            filtered.sort(key=lambda b: b.year, reverse=reverse)
    return filtered