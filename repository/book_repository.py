from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional, Union
from uuid import UUID
from models.book_model import Book, BookStatus

class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_books(
        self,
        status: Optional[Union[str, BookStatus]] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = 'asc',
        cursor: Optional[str] = None,
        limit: int = 10
    ) -> List[Book]:
        query = select(Book)
        
        if status:
            if isinstance(status, str):
                status = BookStatus(status)
            query = query.where(Book.status == status)
        
        if author:
            query = query.where(Book.author == author)
        
        if cursor:
            # Convert cursor to UUID
            try:
                cursor_uuid = UUID(cursor)
                query = query.where(Book.id > cursor_uuid)
            except (ValueError, TypeError):
                pass  # Invalid cursor, ignore
        
        if sort_by:
            if sort_by == 'title':
                order = Book.title.asc() if sort_order == 'asc' else Book.title.desc()
            elif sort_by == 'year':
                order = Book.year.asc() if sort_order == 'asc' else Book.year.desc()
            else:
                order = None
            if order is not None:
                query = query.order_by(order)
        else:
            # For cursor pagination, default sort by id
            query = query.order_by(Book.id.asc())
        
        query = query.limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_book_by_id(self, book_id: str) -> Optional[Book]:
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_book(self, book_data: dict) -> Book:
        # Convert string status to enum if needed
        if 'status' in book_data and isinstance(book_data['status'], str):
            book_data['status'] = BookStatus(book_data['status'])
        
        book = Book(**book_data)
        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book)
        return book

    async def delete_book(self, book_id: str) -> bool:
        query = delete(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0