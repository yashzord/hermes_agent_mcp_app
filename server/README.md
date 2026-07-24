# Recall MCP server

The Recall flashcard MCP server: 5 tools (`ping`, `add_card`, `review_next`,
`grade_card`, `stats`) plus the `ui://recall/flashcard` MCP Apps widget, over
SQLite with SM-2 scheduling.

## Run locally

```bash
# stdio (MCP Inspector / dev)
./dev.sh

# HTTP (Streamable HTTP on :8000, what a remote host connects to)
RECALL_TRANSPORT=http PORT=8000 uv run python src/server.py
```

## Test

```bash
uv run pytest            # SM-2 + SQLite integration tests
uv run python src/sm2.py # SM-2 self-check
```

## More

- Live deploy + hosts that render the widget: [`../docs/deploy.md`](../docs/deploy.md)
- How the pieces fit: [`../docs/architecture.md`](../docs/architecture.md)
- Full annotated code tour: [`../docs/WALKTHROUGH.md`](../docs/WALKTHROUGH.md)
