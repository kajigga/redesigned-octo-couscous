FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --quiet --no-cache-dir uv && \
    uv sync --frozen --no-dev

COPY app/ app/

EXPOSE 8000

CMD gunicorn -w 4 -b 0.0.0.0:${PORT:-8000} "app:create_app()"
