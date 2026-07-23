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
