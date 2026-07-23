FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install deps first for layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

COPY src ./src

# Serve over Streamable HTTP; keep the SQLite deck on a mounted volume so it
# survives restarts/redeploys. Point your host's volume at /data.
ENV RECALL_TRANSPORT=http \
    RECALL_DB=/data/recall.db \
    PORT=8000
EXPOSE 8000
VOLUME ["/data"]

CMD ["uv", "run", "python", "src/server.py"]
