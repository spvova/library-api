from repository.book_repository import BookRepository

class BookService:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    def get_books(self, status=None, author=None, sort_by=None, sort_order='asc', offset=0, limit=10):
        return self.repo.get_books(status, author, sort_by, sort_order, offset, limit)

    def get_book_by_id(self, book_id):
        return self.repo.get_book_by_id(book_id)

    def add_book(self, book_data):
        return self.repo.add_book(book_data)

    def delete_book(self, book_id):
        return self.repo.delete_book(book_id)