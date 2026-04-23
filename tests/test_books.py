import pytest
from services.book_service import BookService
from repository.book_repository import books

@pytest.fixture(autouse=True)
def clear_books():
    books.clear()

def test_add_book():
    service = BookService()
    book_data = {'title': 'Test Book', 'author': 'Test Author', 'status': 'available', 'year': 2020}
    book = service.add_book(book_data)
    assert book.title == 'Test Book'
    assert book.author == 'Test Author'
    assert book.status == 'available'
    assert book.year == 2020
    assert book.id is not None

def test_get_books():
    service = BookService()
    service.add_book({'title': 'Book1', 'author': 'Author1', 'status': 'available', 'year': 2020})
    service.add_book({'title': 'Book2', 'author': 'Author2', 'status': 'issued', 'year': 2021})
    books = service.get_books()
    assert len(books) == 2

def test_get_book_by_id():
    service = BookService()
    book = service.add_book({'title': 'Book1', 'author': 'Author1', 'status': 'available', 'year': 2020})
    retrieved = service.get_book_by_id(str(book.id))
    assert retrieved == book

def test_delete_book():
    service = BookService()
    book = service.add_book({'title': 'Book1', 'author': 'Author1', 'status': 'available', 'year': 2020})
    deleted = service.delete_book(str(book.id))
    assert deleted == True
    books = service.get_books()
    assert len(books) == 0

def test_delete_nonexistent_book():
    service = BookService()
    deleted = service.delete_book('nonexistent')
    assert deleted == False

def test_filter_by_status():
    service = BookService()
    service.add_book({'title': 'Book1', 'author': 'Author1', 'status': 'available', 'year': 2020})
    service.add_book({'title': 'Book2', 'author': 'Author2', 'status': 'issued', 'year': 2021})
    available = service.get_books(status='available')
    assert len(available) == 1
    assert available[0].status == 'available'

def test_sort_by_title():
    service = BookService()
    service.add_book({'title': 'B Book', 'author': 'Author1', 'status': 'available', 'year': 2020})
    service.add_book({'title': 'A Book', 'author': 'Author2', 'status': 'available', 'year': 2021})
    sorted_books = service.get_books(sort_by='title', sort_order='asc')
    assert sorted_books[0].title == 'A Book'
    assert sorted_books[1].title == 'B Book'