# Recall - architecture

Plain-language map of how the pieces fit, for anyone picking this up.

## The whole system in one picture

```
  Card FACTORY                         Card STUDY ROOM
  (Hermes WebUI / any MCP client)      (Claude.ai chat)
        │  "make flashcards"                 │  "quiz me"
        │  add_card                          │  review_next
        ▼                                     ▼
   ┌──────────────────────────  Recall MCP server  ──────────────────────────┐
   │  FastMCP app (server/src/server.py)                                      │
   │    tools: ping, add_card, review_next, grade_card, stats                 │
   │    UI resource: ui://recall/flashcard  (rendered in a sandboxed iframe)  │
   │  scheduling: sm2.py (pure)      storage: state.py -> SQLite (/data)       │
   └──────────────────────────────────────────────────────────────────────────┘
```

Two clients, one shared deck. The chat host renders the flip-card widget inline
and the widget talks back to the server through the host.

## Layers

- **`sm2.py`** - the spaced-repetition math, and nothing else. A pure
  `schedule(ease, interval, review_number, rating)` function. No database, no
  clock, so it is trivially testable (`tests/test_sm2.py`, plus a `__main__`
  self-check). Keeping it pure is why the scheduling stays "boring and correct".

- **`state.py`** - persistence. A `State` class over SQLite with two tables
  (`cards`, `reviews`) matching PROJECT.md §4. It calls `sm2.schedule` but owns
  no scheduling logic itself. Opens a fresh connection per operation (fine for a
  one-container personal app). Seeds a ~20-card starter deck the first time the
  database is empty (`seed.py`).

- **`tools/`** - one thin module per tool. Each is a plain function; FastMCP
  derives the JSON schema from the signature. They call `state`.

- **`server.py`** - wiring only. Registers the tools and the `ui://` resource,
  links `review_next` to the UI via `AppConfig(resource_uri=...)`, and picks the
  transport from `RECALL_TRANSPORT` (stdio for local dev / MCP Inspector, http
  for deployment).

- **`ui/flashcard.html`** - the widget. Self-contained HTML/CSS/JS. It talks to
  the host over **JSON-RPC 2.0 via postMessage** (the ext-apps 2026-01-26
  protocol): grade buttons send `tools/call` for `grade_card` then `review_next`;
  the opening card arrives as a `ui/notifications/tool-result` notification.

## Why an MCP App (not just tools)

Plain tools can add and grade cards, but the *study* experience wants a real
card you tap to flip and grade. The MCP Apps extension lets the server ship that
UI as a resource the host renders inline, with the iframe calling back into the
same tools. `review_next` carries `ui.resourceUri` in its metadata, which is the
signal that tells a supporting host to render the widget when the tool runs.

## Transports

- **stdio** (default): the server reads/writes over stdin/stdout. Used by local
  dev and MCP Inspector. `./dev.sh` runs this.
- **http** (Streamable HTTP): `RECALL_TRANSPORT=http` starts a Uvicorn server on
  `PORT` (default 8000) at `/mcp/`. This is what a remote host (Claude.ai
  connector) talks to. The Dockerfile sets this.

## Data

`RECALL_DB` points at the SQLite file. Locally it defaults to `recall.db` in the
working directory (gitignored). In the container it is `/data/recall.db` on a
mounted volume so the deck survives restarts and redeploys.
