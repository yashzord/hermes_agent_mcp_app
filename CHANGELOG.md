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
- Next: Phase 2 (four core tools, in-memory state) - builder: Hermes once
  usage window resets, else Claude Code.
