# uv preinstalled in this base image (avoids a cross-image COPY --from).
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Build context is server/ (Railway Root Directory = server; locally:
# docker build server/). Install deps first for layer caching.
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
