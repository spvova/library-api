import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models.book_model import Base, BookStatus
from services.book_service import BookService
from repository.book_repository import BookRepository

@pytest.fixture(scope="function")
async def engine():
    """Create an in-memory SQLite database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def session(engine):
    """Create a new database session for a test"""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
async def service(session):
    """Create a service with a test repository"""
    repo = BookRepository(session)
    return BookService(repo)

@pytest.mark.asyncio
async def test_add_book(service):
    """Test adding a new book"""
    book_data = {
        'title': 'Test Book',
        'author': 'Test Author',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    }
    book = await service.add_book(book_data)
    assert book.title == 'Test Book'
    assert book.author == 'Test Author'
    assert book.status == BookStatus.AVAILABLE
    assert book.year == 2020
    assert book.id is not None

@pytest.mark.asyncio
async def test_get_books(service):
    """Test retrieving all books"""
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
    assert len(books['items']) == 2

@pytest.mark.asyncio
async def test_get_book_by_id(service):
    """Test retrieving a book by ID"""
    book = await service.add_book({
        'title': 'Book1',
        'author': 'Author1',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    })
    retrieved = await service.get_book_by_id(str(book.id))
    assert retrieved is not None
    assert retrieved.id == book.id
    assert retrieved.title == 'Book1'

@pytest.mark.asyncio
async def test_delete_book(service):
    """Test deleting a book"""
    book = await service.add_book({
        'title': 'Book1',
        'author': 'Author1',
        'status': BookStatus.AVAILABLE,
        'year': 2020
    })
    deleted = await service.delete_book(str(book.id))
    assert deleted is True
    books = await service.get_books()
    assert len(books['items']) == 0

@pytest.mark.asyncio
async def test_delete_nonexistent_book(service):
    """Test deleting a non-existent book returns False"""
    deleted = await service.delete_book('nonexistent-id')
    assert deleted is False

@pytest.mark.asyncio
async def test_filter_by_status(service):
    """Test filtering books by status"""
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
    assert len(available['items']) == 1
    assert available['items'][0].status == BookStatus.AVAILABLE

@pytest.mark.asyncio
async def test_filter_by_author(service):
    """Test filtering books by author"""
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
    assert len(books['items']) == 1
    assert books['items'][0].author == 'Author1'

@pytest.mark.asyncio
async def test_sort_by_title(service):
    """Test sorting books by title"""
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
    assert sorted_books['items'][0].title == 'A Book'
    assert sorted_books['items'][1].title == 'B Book'

@pytest.mark.asyncio
async def test_pagination(service):
    """Test pagination with cursor"""
    for i in range(15):
        await service.add_book({
            'title': f'Book {i+1}',
            'author': f'Author {i+1}',
            'status': BookStatus.AVAILABLE,
            'year': 2020 + i
        })
    
    page1 = await service.get_books(limit=5)
    assert len(page1['items']) == 5
    assert page1['next_cursor'] is not None

    page2 = await service.get_books(cursor=page1['next_cursor'], limit=5)
    assert len(page2['items']) == 5
    assert page2['next_cursor'] is not None
    assert page1['items'][0].id != page2['items'][0].id

@pytest.mark.asyncio
async def test_filter_by_status_str(service):
    await service.add_book({'title': 'Book1', 'author': 'Author1', 'status': 'available', 'year': 2020})
    await service.add_book({'title': 'Book2', 'author': 'Author2', 'status': 'issued', 'year': 2021})
    available = await service.get_books(status='available')
    assert len(available['items']) == 1
    assert available['items'][0].status == 'available'

@pytest.mark.asyncio
async def test_sort_by_title_str(service):
    await service.add_book({'title': 'B Book', 'author': 'Author1', 'status': 'available', 'year': 2020})
    await service.add_book({'title': 'A Book', 'author': 'Author2', 'status': 'available', 'year': 2021})
    sorted_books = await service.get_books(sort_by='title', sort_order='asc')
    assert sorted_books['items'][0].title == 'A Book'
    assert sorted_books['items'][1].title == 'B Book'