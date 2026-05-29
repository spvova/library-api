FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

ENV PATH="/app/.venv/bin:$PATH"

# Тепер Docker знатиме, де шукати flask або python
CMD ["flask", "--app", "main.py", "run", "--host=0.0.0.0"]