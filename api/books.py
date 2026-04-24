from flask_restful import Resource, reqparse
from flask import request
from flasgger import swag_from
from schemas.book import BookCreate, Book
from services.book_service import BookService
from repository.book_repository import BookRepository
from database import get_db
import asyncio
from typing import List, Optional

class BooksResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('status', type=str, location='args', help='Filter by status: available or issued')
        self.parser.add_argument('author', type=str, location='args', help='Filter by author')
        self.parser.add_argument('sort_by', type=str, location='args', choices=['title', 'year'], help='Sort by title or year')
        self.parser.add_argument('sort_order', type=str, location='args', default='asc', choices=['asc', 'desc'], help='Sort order: asc or desc')
        self.parser.add_argument('offset', type=int, location='args', default=0, help='Offset for pagination')
        self.parser.add_argument('limit', type=int, location='args', default=10, help='Number of books to return (1-100)')

    @swag_from({
        'tags': ['Books'],
        'parameters': [
            {
                'name': 'status',
                'in': 'query',
                'type': 'string',
                'enum': ['available', 'issued'],
                'description': 'Filter by status'
            },
            {
                'name': 'author',
                'in': 'query',
                'type': 'string',
                'description': 'Filter by author'
            },
            {
                'name': 'sort_by',
                'in': 'query',
                'type': 'string',
                'enum': ['title', 'year'],
                'description': 'Sort by title or year'
            },
            {
                'name': 'sort_order',
                'in': 'query',
                'type': 'string',
                'enum': ['asc', 'desc'],
                'default': 'asc',
                'description': 'Sort order'
            },
            {
                'name': 'offset',
                'in': 'query',
                'type': 'integer',
                'default': 0,
                'minimum': 0,
                'description': 'Offset for pagination'
            },
            {
                'name': 'limit',
                'in': 'query',
                'type': 'integer',
                'default': 10,
                'minimum': 1,
                'maximum': 100,
                'description': 'Number of books to return'
            }
        ],
        'responses': {
            '200': {
                'description': 'List of books',
                'schema': {
                    'type': 'array',
                    'items': {'$ref': '#/definitions/Book'}
                }
            }
        }
    })
    def get(self):
        args = self.parser.parse_args()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._get_books_async(args))
            return result
        finally:
            loop.close()

    async def _get_books_async(self, args):
        db = await get_db()
        repo = BookRepository(db)
        service = BookService(repo)
        books = await service.get_books(
            status=args['status'],
            author=args['author'],
            sort_by=args['sort_by'],
            sort_order=args['sort_order'],
            offset=args['offset'],
            limit=args['limit']
        )
        return [book.model_dump() for book in books], 200

    @swag_from({
        'tags': ['Books'],
        'parameters': [
            {
                'name': 'book',
                'in': 'body',
                'required': True,
                'schema': {'$ref': '#/definitions/BookCreate'}
            }
        ],
        'responses': {
            '201': {
                'description': 'Book created',
                'schema': {'$ref': '#/definitions/Book'}
            },
            '400': {
                'description': 'Invalid input'
            }
        }
    })
    def post(self):
        data = request.get_json()
        try:
            book_data = BookCreate(**data)
        except Exception as e:
            return {'message': f'Invalid input: {str(e)}'}, 400

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._add_book_async(book_data))
            return result
        finally:
            loop.close()

    async def _add_book_async(self, book_data):
        db = await get_db()
        repo = BookRepository(db)
        service = BookService(repo)
        new_book = await service.add_book(book_data.model_dump())
        return new_book.model_dump(), 201


class BookResource(Resource):
    @swag_from({
        'tags': ['Books'],
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'string',
                'required': True,
                'description': 'Book ID'
            }
        ],
        'responses': {
            '200': {
                'description': 'Book details',
                'schema': {'$ref': '#/definitions/Book'}
            },
            '404': {
                'description': 'Book not found'
            }
        }
    })
    def get(self, book_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._get_book_async(book_id))
            return result
        finally:
            loop.close()

    async def _get_book_async(self, book_id):
        db = await get_db()
        repo = BookRepository(db)
        service = BookService(repo)
        book = await service.get_book_by_id(book_id)
        if not book:
            return {'message': 'Book not found'}, 404
        return book.model_dump(), 200

    @swag_from({
        'tags': ['Books'],
        'parameters': [
            {
                'name': 'book_id',
                'in': 'path',
                'type': 'string',
                'required': True,
                'description': 'Book ID'
            }
        ],
        'responses': {
            '204': {
                'description': 'Book deleted'
            },
            '404': {
                'description': 'Book not found'
            }
        }
    })
    def delete(self, book_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._delete_book_async(book_id))
            return result
        finally:
            loop.close()

    async def _delete_book_async(self, book_id):
        db = await get_db()
        repo = BookRepository(db)
        service = BookService(repo)
        deleted = await service.delete_book(book_id)
        if not deleted:
            return {'message': 'Book not found'}, 404
        return '', 204