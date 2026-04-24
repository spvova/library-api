# Library API

Сучасний REST API для управління бібліотекою, розроблений з використанням FastAPI, SQLAlchemy та PostgreSQL.

## Функціональність

### Ендпоінти

1. **GET /books** - Отримання всіх книг з фільтрацією та курсорною пагінацією
   - Параметри: `status`, `author`, `sort_by` (title|year), `sort_order` (asc|desc), `cursor` (ID книги), `limit`
   - Статус: 200 OK

2. **GET /books/{book_id}** - Отримання книги по ID
   - Статус: 200 OK або 404 Not Found

3. **POST /books** - Додавання нової книги
   - Статус: 201 Created
   - Body: `{ "title", "author", "description", "status", "year" }`

4. **DELETE /books/{book_id}** - Видалення книги (ідемпотентне)
   - Статус: 204 No Content

### Атрибути книги

- `id` - UUID (генерується автоматично)
- `title` - Назва книги
- `author` - Автор
- `description` - Опис (опціонально)
- `status` - Статус: `available` або `issued`
- `year` - Рік випуску

## Встановлення та запуск

### Вимоги

- Docker та Docker Compose
- АБО Python 3.12+ та PostgreSQL

### 1. Запуск через Docker Compose (рекомендується)

```bash
docker-compose up --build
```

API буде доступний на http://localhost:8000
PostgreSQL буде доступний на localhost:5435

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

### 2. Локальний запуск

#### Встановлення залежностей

```bash
# Активуйте віртуальне середовище
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Встановіть залежності
pip install -e ".[dev]"
```

#### Налаштування БД

Переконайтеся, що PostgreSQL запущена на `localhost:5435` з:
- User: `rest_lab2`
- Password: `rest_lab2`
- Database: `rest_lab2`

АБО встановіть змінну середовища:
```bash
export DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

#### Запуск сервера

```bash
python -m uvicorn main:app --reload
```

### Запуск тестів

```bash
pytest -v
```

Тесты використовують SQLite in-memory базу для ізоляції.

## Структура проекту

```
.
├── api/              # Маршрути API
├── models/           # SQLAlchemy моделі
├── schemas/          # Pydantic схеми для валідації
├── services/         # Бізнес-логіка
├── repository/       # Доступ до даних
├── tests/            # Юніт тести
├── main.py          # Точка входу FastAPI
├── database.py      # Конфігурація БД
├── Dockerfile       # Docker образ для API
├── docker-compose.yml # Оркестрація контейнерів
└── pyproject.toml   # Конфігурація проекту
```

## Приклади використання

### Отримання всіх книг

```bash
curl http://localhost:8000/books
```

### Фільтрація за статусом

```bash
curl "http://localhost:8000/books?status=available"
```

### Пагінація

```bash
# Перша сторінка
curl "http://localhost:8000/books?limit=5"

# Наступна сторінка (cursor - ID останньої книги з попередньої сторінки)
curl "http://localhost:8000/books?cursor=123e4567-e89b-12d3-a456-426614174000&limit=5"
```

### Сортування

```bash
curl "http://localhost:8000/books?sort_by=title&sort_order=desc"
```

### Додавання книги

```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Война и мир",
    "author": "Лев Толстой",
    "description": "Роман-эпопея",
    "status": "available",
    "year": 1869
  }'
```

### Видалення книги

```bash
curl -X DELETE http://localhost:8000/books/{book_id}
```

## Технологічний стек

- **FastAPI** - Веб-фреймворк
- **SQLAlchemy** - ORM для взаємодії з БД
- **PostgreSQL** - Реляційна база даних
- **asyncpg** - Асинхронний драйвер для PostgreSQL
- **Pydantic** - Валідація даних
- **pytest** - Фреймворк для тестування
- **Docker** - Контейнеризація

## Розробка

### Отримання залежностей для розробки

```bash
pip install -e ".[dev]"
```

### Форматування коду (опціонально)

```bash
pip install black flake8
black .
flake8 .
```

## Ліцензія

MIT
