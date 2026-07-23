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
