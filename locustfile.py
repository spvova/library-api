from locust import HttpUser, task, between


class BookUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        """
        Завантажуємо всі книги і зберігаємо їх ID
        """
        response = self.client.get("/books/")

        self.book_ids = []

        if response.status_code == 200:
            data = response.json()

            # підтримка двох форматів API:
            # 1) просто list
            # 2) {"items": [...]}

            if isinstance(data, dict):
                books = data.get("items", [])
            else:
                books = data

            self.book_ids = [
                book.get("_id") or book.get("id")
                for book in books
                if book.get("_id") or book.get("id")
            ]

    @task(4)
    def get_all_books(self):
        self.client.get("/books/", name="get_books")

    @task(2)
    def get_books_pagination(self):
        self.client.get(
            "/books?limit=10&offset=0",
            name="pagination"
        )

    @task(4)
    def cycle_through_books(self):
        """
        Проходимось по всіх існуючих книгах (без 404)
        """
        if not self.book_ids:
            return

        for book_id in self.book_ids:
            self.client.get(
                f"/books/{book_id}",
                name="book_by_id"
            )