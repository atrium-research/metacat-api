FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /uvx /bin/

ENV UV_COMPILE_BYTE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

RUN useradd --create-home --uid 1000 app
USER app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV DATASOURCE=mock

CMD ["fastapi", "run", "/app/src/metacat_api/main.py", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EXPOSE 8000
