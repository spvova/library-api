from typing import List, Optional, Union
from bson import ObjectId
from models.book_model import BookStatus

class BookRepository:
    def __init__(self, db):
        self.collection = db["books"]

    def _serialize(self, document: dict) -> dict:
        return {
            "id": str(document["_id"]),
            "title": document["title"],
            "author": document["author"],
            "description": document.get("description"),
            "status": document["status"],
            "year": document["year"],
        }

    async def get_books(
        self,
        status: Optional[Union[str, BookStatus]] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = 'asc',
        offset: int = 0,
        limit: int = 10
    ) -> dict:
        query = {}

        if status:
            query["status"] = status.value if isinstance(status, BookStatus) else status

        if author:
            query["author"] = author

        if sort_by == 'title':
            sort_field = 'title'
        elif sort_by == 'year':
            sort_field = 'year'
        else:
            sort_field = '_id'

        sort_direction = 1 if sort_order == 'asc' else -1
        cursor = self.collection.find(query).sort(sort_field, sort_direction).skip(offset).limit(limit + 1)
        documents = await cursor.to_list(length=limit + 1)

        has_next = len(documents) > limit
        items = [self._serialize(document) for document in documents[:limit]]
        next_offset = offset + limit if has_next else None

        return {
            'items': items,
            'next_offset': next_offset,
        }

    async def get_book_by_id(self, book_id: str) -> Optional[dict]:
        try:
            oid = ObjectId(book_id)
        except Exception:
            return None

        document = await self.collection.find_one({"_id": oid})
        return self._serialize(document) if document else None

    async def add_book(self, book_data: dict) -> dict:
        if 'status' in book_data and isinstance(book_data['status'], BookStatus):
            book_data['status'] = book_data['status'].value

        result = await self.collection.insert_one(book_data)
        document = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize(document)

    async def delete_book(self, book_id: str) -> bool:
        try:
            oid = ObjectId(book_id)
        except Exception:
            return False

        response = await self.collection.delete_one({"_id": oid})
        return response.deleted_count > 0