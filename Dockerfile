FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY alembic alembic
COPY alembic.ini alembic.ini
COPY src src
RUN uv sync --frozen --no-dev

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY --from=builder /app/alembic alembic
COPY --from=builder /app/alembic.ini alembic.ini
COPY --from=builder /app/src src
COPY --from=builder /app/pyproject.toml pyproject.toml

ENV PATH="/app/.venv/bin:$PATH" \
    ORG_CATALOG_API_KEY=local-dev-key \
    ORG_CATALOG_DATABASE_URL=postgresql+asyncpg://org_user:org_pass@db:5432/org_catalog

EXPOSE 8000

CMD ["/bin/sh", "-c", "alembic upgrade head && uvicorn org_catalog.main:app --host 0.0.0.0 --port 8000"]
