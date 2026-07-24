# Changelog

All notable changes to this project, kept by the builder agent per PROJECT.md §7.

## 2026-07-22
- Repo initialized with PROJECT.md and this changelog. No code yet.
- Phase 0 COMPLETE: Hermes Agent installed (gemini provider, gemini-flash-latest,
  local backend, DuckDuckGo search, trimmed CLI toolset), Hermes WebUI running on
  127.0.0.1:8787. Acceptance passed: prompt answered, shell command run, file
  written and read back from ~/hermes-scratch via WebUI. Details in hermes/notes.md.
- Phase 1 COMPLETE (Hermes scaffolded ~80%, Claude Code finished as backup
  builder after Hermes hit Gemini free-tier quota, then the Claude subscription
  usage cap): uv project in server/ with fastmcp + ruff, src/server.py with a
  ping tool (src/tools/ping.py), dev.sh stdio entrypoint, Dockerfile stub for
  Phase 4. Acceptance passed: MCP Inspector CLI lists the ping tool over stdio
  and tools/call returns "pong". Model brain revised to claude-sonnet-5 via
  Anthropic (PROJECT.md §4).

## 2026-07-23
- Phase 2 COMPLETE. Hermes (Bedrock deepseek.v3.2, after Gemini/Groq/Claude
  all hit limits - see hermes/notes.md) built the four §3 tools with in-memory
  state and SM-2 scheduling: add_card, review_next, grade_card, stats over
  src/state.py. Claude Code (backup) verified and cleaned up: removed unused
  pydantic Input classes and stray test scripts Hermes left, ran ruff, added a
  pytest suite (server/tests/test_sm2.py, 6 tests), and added state.due_count()
  so review_next reports how many cards are due.
- Acceptance passed: MCP Inspector lists all 5 tools (ping + four) over stdio;
  SM-2 verified by tests - ease floor 1.3 holds, `again` resets interval to 1,
  intervals grow on repeated `good`.
- Known simplification: ease is capped at 2.5, so `easy` does not accelerate a
  card beyond the default rate (conservative vs textbook SM-2; fine for v1).
- Next: Phase 3 (MCP Apps UI) - builder Hermes.

## 2026-07-23 (later)
- Phase 3 COMPLETE. MCP Apps UI: ui://recall/flashcard HTML resource
  (text/html;profile=mcp-app) registered, linked to review_next via
  AppConfig(resource_uri=...) so hosts render the flip-card widget.
- Split build: Hermes (Bedrock deepseek.v3.2) wrote the server-side wiring and
  the HTML/CSS. It correctly inspected FastMCP's real Apps API but (a) misused
  resource_uri on the resource - server wouldn't even import - and (b)
  hallucinated the browser postMessage protocol ("mcp/callTool"). Claude Code
  (backup) landed Hermes's own resource fix and rewrote the iframe bridge to the
  actual ext-apps 2026-01-26 protocol: JSON-RPC 2.0 over postMessage, tools/call
  for grade_card/review_next, ui/notifications/tool-result for the opening card.
  Also dropped alert() (blocked in sandboxed iframes) and fixed the flip logic.
- Acceptance (as far as stdio allows): server imports; resource lists + serves;
  review_next carries ui.resourceUri; full add->review->grade->reschedule
  round-trip verified in-process, and structuredContent field names match what
  the UI reads. True browser round-trip proves out with Phase 4's Claude.ai
  connector.
- Next: Phase 4 (deploy as remote server, SQLite, Claude.ai connector).

## 2026-07-23 (Phase 4 - roles flipped)
- Role change: Claude Code is now primary builder; Hermes becomes final reviewer
  via WebUI (PROJECT.md §6b).
- Phase 4 code COMPLETE and verified locally:
  - Extracted SM-2 into a pure, testable module (src/sm2.py) with a __main__
    self-check.
  - Replaced in-memory state with SQLite (src/state.py): cards + reviews tables
    (§4 data model), fresh connection per op, seeds a ~20-card starter deck
    (src/seed.py) on an empty DB. Persists across restarts.
  - Env-driven transport in server.py: stdio (dev/Inspector) or http (Streamable
    HTTP) via RECALL_TRANSPORT; Dockerfile serves http with the DB on a /data
    volume.
  - Tests restructured: pure SM-2 tests + SQLite integration incl. seed and
    persistence (12 tests). Ruff clean.
  - Docs: docs/architecture.md (system map) and docs/deploy.md (deploy + Claude.ai
    connector steps).
  - Verified: Inspector lists all 5 tools over stdio and serves the seeded deck;
    HTTP transport boots on Uvicorn and responds at /mcp/.
- Remaining (needs owner's cloud account, guided): pick a host, deploy the
  container with a /data volume, add the URL to Claude.ai, run a live study
  session. That live round-trip is the Phase 4 (and true Phase 3) acceptance.
- Then: Phase 5 stretch (wire deployed server into Hermes), and Hermes reviews.

## 2026-07-24 (DEPLOYED - Phase 4 acceptance MET)
- Live on Render: https://recall-mcp-wa3n.onrender.com/mcp (free plan, Docker
  from render.yaml blueprint, build context server/). Railway was abandoned -
  its Metal builder failed every build (platform issue, not our code); Render
  built and ran the same Dockerfile first try.
- Deploy debugging (via Render MCP logs/metrics): app healthy throughout (no
  crash, ~17% mem). Apparent flakiness was (a) deploy rollover running two
  instances briefly, and (b) a wrong stateless_http+json_response experiment
  that returned 405 on the client's GET event-stream. Reverted to standard
  stateful Streamable HTTP - the mode Claude.ai connects to.
- ACCEPTANCE MET: added to Claude.ai as a custom connector; "quiz me from the
  mcp-basics deck" called review_next and rendered the interactive flip-card
  widget inline in chat. Full MCP Apps round-trip working in a real host.
- Remaining: exercise the grade buttons in the widget (fires grade_card via the
  host), then optional Phase 5 (wire the deployed server into Hermes as a
  text tool-client - "make flashcards from this article"). Note: Hermes cannot
  render the widget (only tool calls); Apps-capable hosts are Claude.ai, Goose,
  VS Code, ChatGPT.
