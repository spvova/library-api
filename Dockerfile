FROM python:3.12-slim

WORKDIR /app

# Копіюємо утиліту uv з офіційного образу
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копіюємо файли залежностей
COPY pyproject.toml uv.lock ./

# Встановлюємо залежності системно (в контейнері віртуальне середовище не потрібне)
RUN uv sync --frozen --no-dev

# Копіюємо весь код проекту
COPY . .

# Запускаємо сервер
CMD ["uv", "run", "python", "main.py"]