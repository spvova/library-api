import base64
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, and_
from typing import List, Optional, Union
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
    ) -> dict:
        query = select(Book)

        if status:
            if isinstance(status, str):
                status = BookStatus(status)
            query = query.where(Book.status == status)

        if author:
            query = query.where(Book.author == author)

        if sort_by == 'title':
            sort_field = Book.title
        elif sort_by == 'year':
            sort_field = Book.year
        else:
            sort_field = Book.id

        if cursor:
            try:
                decoded = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
                last_id = decoded.get('id')
                last_value = decoded.get('value')
            except Exception:
                last_id = None
                last_value = None

            if last_id:
                if sort_by == 'title':
                    if sort_order == 'asc':
                        condition = or_(
                            Book.title > last_value,
                            and_(Book.title == last_value, Book.id > last_id),
                        )
                    else:
                        condition = or_(
                            Book.title < last_value,
                            and_(Book.title == last_value, Book.id < last_id),
                        )
                elif sort_by == 'year':
                    if sort_order == 'asc':
                        condition = or_(
                            Book.year > last_value,
                            and_(Book.year == last_value, Book.id > last_id),
                        )
                    else:
                        condition = or_(
                            Book.year < last_value,
                            and_(Book.year == last_value, Book.id < last_id),
                        )
                else:
                    condition = Book.id > last_id if sort_order == 'asc' else Book.id < last_id
                query = query.where(condition)

        if sort_order == 'asc':
            order_by = [sort_field.asc(), Book.id.asc()] if sort_field is not Book.id else [Book.id.asc()]
        else:
            order_by = [sort_field.desc(), Book.id.desc()] if sort_field is not Book.id else [Book.id.desc()]

        query = query.order_by(*order_by).limit(limit + 1)
        result = await self.session.execute(query)
        rows = result.scalars().all()

        has_next = len(rows) > limit
        items = rows[:limit]

        next_cursor = None
        if has_next:
            last_item = rows[limit - 1]
            cursor_payload = {"id": last_item.id}
            if sort_by == 'title':
                cursor_payload["value"] = last_item.title
            elif sort_by == 'year':
                cursor_payload["value"] = last_item.year
            next_cursor = base64.urlsafe_b64encode(json.dumps(cursor_payload).encode()).decode()

        return {
            'items': items,
            'next_cursor': next_cursor,
        }

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