from repository.book_repository import get_books_filtered, get_book_by_id, add_book, delete_book

class BookService:
    def get_books(self, status=None, author=None, sort_by=None, sort_order='asc'):
        return get_books_filtered(status, author, sort_by, sort_order)

    def get_book_by_id(self, book_id):
        return get_book_by_id(book_id)

    def add_book(self, book_data):
        return add_book(book_data)

    def delete_book(self, book_id):
        return delete_book(book_id)