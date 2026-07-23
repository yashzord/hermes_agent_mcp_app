#!/usr/bin/env sh
# Run the Recall MCP server over stdio (Phase 1 dev entrypoint).
cd "$(dirname "$0")" && exec uv run python src/server.py
