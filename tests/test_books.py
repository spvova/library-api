import os
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from models.book_model import BookStatus
from repository.book_repository import BookRepository
from services.book_service import BookService

@pytest.fixture(scope="function")
async def db():
    mongo_url = os.getenv("MONGODB_URL", "mongodb://mongo_admin:password@localhost:27017/?authSource=admin")
    db_name = os.getenv("MONGODB_DB", "library_test")
    client = AsyncIOMotorClient(mongo_url)
    database = client[db_name]
    await database["books"].delete_many({})
    yield database
    client.close()

@pytest.fixture
async def service(db):
    repo = BookRepository(db)
    return BookService(repo)

@pytest.mark.asyncio
async def test_add_book(service):
    book_data = {
        'title': 'Test Book',
        'author': 'Test Author',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    }
    book = await service.add_book(book_data)
    assert book['title'] == 'Test Book'
    assert book['author'] == 'Test Author'
    assert book['status'] == BookStatus.AVAILABLE.value
    assert book['year'] == 2020
    assert book['id'] is not None

@pytest.mark.asyncio
async def test_get_books(service):
    await service.add_book({
        'title': 'Book1',
        'author': 'Author1',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    })
    await service.add_book({
        'title': 'Book2',
        'author': 'Author2',
        'status': BookStatus.ISSUED,
        'year': 2021
    })
    books = await service.get_books()
    assert len(books) == 2

@pytest.mark.asyncio
async def test_get_book_by_id(service):
    book = await service.add_book({
        'title': 'Book1',
        'author': 'Author1',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    })
    retrieved = await service.get_book_by_id(book['id'])
    assert retrieved is not None
    assert retrieved['id'] == book['id']
    assert retrieved['title'] == 'Book1'

@pytest.mark.asyncio
async def test_delete_book(service):
    book = await service.add_book({
        'title': 'Book1',
        'author': 'Author1',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    })
    deleted = await service.delete_book(book['id'])
    assert deleted is True
    books = await service.get_books()
    assert len(books) == 0

@pytest.mark.asyncio
async def test_delete_nonexistent_book(service):
    deleted = await service.delete_book('000000000000000000000000')
    assert deleted is False

@pytest.mark.asyncio
async def test_filter_by_status(service):
    await service.add_book({
        'title': 'Book1',
        'author': 'Author1',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    })
    await service.add_book({
        'title': 'Book2',
        'author': 'Author2',
        'status': BookStatus.ISSUED,
        'year': 2021
    })
    available = await service.get_books(status=BookStatus.AVAILABLE)
    assert len(available) == 1
    assert available[0]['status'] == BookStatus.AVAILABLE.value

@pytest.mark.asyncio
async def test_filter_by_author(service):
    await service.add_book({
        'title': 'Book1',
        'author': 'Author1',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    })
    await service.add_book({
        'title': 'Book2',
        'author': 'Author2',
        'status': BookStatus.AVAILABLE,
        'year': 2021
    })
    books = await service.get_books(author='Author1')
    assert len(books) == 1
    assert books[0]['author'] == 'Author1'

@pytest.mark.asyncio
async def test_sort_by_title(service):
    await service.add_book({
        'title': 'B Book',
        'author': 'Author1',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    })
    await service.add_book({
        'title': 'A Book',
        'author': 'Author2',
        'status': BookStatus.AVAILABLE,
        'year': 2021
    })
    sorted_books = await service.get_books(sort_by='title', sort_order='asc')
    assert sorted_books[0]['title'] == 'A Book'
    assert sorted_books[1]['title'] == 'B Book'

@pytest.mark.asyncio
async def test_pagination(service):
    for i in range(15):
        await service.add_book({
            'title': f'Book {i+1}',
            'author': f'Author {i+1}',
            'status': BookStatus.AVAILABLE,
            'year': 2020 + i
        })

    page1 = await service.get_books(offset=0, limit=5)
    assert len(page1) == 5

    page2 = await service.get_books(offset=5, limit=5)
    assert len(page2) == 5
    assert page1[0]['id'] != page2[0]['id']
