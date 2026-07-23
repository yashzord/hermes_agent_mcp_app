# Hermes setup notes (Phase 0, done 2026-07-22)

Commands run, in order:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.zshrc
# key added during wizard; equivalent: echo 'GEMINI_API_KEY=...' >> ~/.hermes/.env
```

Wizard choices:
- Setup mode: Full setup (NOT Nous Portal - we bring our own Gemini key per PROJECT.md §4)
- Provider: gemini, Base URL default (https://generativelanguage.googleapis.com/v1beta)
- Model: `gemini-flash-latest` (alias tracks current stable Flash)
- Terminal backend: Local
- Chat platforms: none
- Search provider: DuckDuckGo (`backend: ddgs` in config.yaml) - zero-key
- CLI toolset trimmed to: clarify, code_execution, file, memory, session_search,
  skills, terminal, todo, web

WebUI:

```bash
cd ~/Projects/personal
git clone https://github.com/nesquena/hermes-webui.git hermes-webui
cd hermes-webui
python3 bootstrap.py     # first run; daemon after: ./ctl.sh start|status|stop
```

- Binds 127.0.0.1:8787, auto-discovers ~/.hermes. Health: curl http://127.0.0.1:8787/health

Gotchas:
- Gemini "Tier check: could not verify" during wizard is harmless.
- First tools screen was accepted with defaults by accident; re-running
  `hermes setup` and Enter-ing through preserved everything else.
- Throttling mid-session = free-tier request cap (~1.5K req/day), not breakage.

Config lives in ~/.hermes/ (config.yaml, .env) - never committed.
config.yaml.example to be added when the deployed MCP server exists (Phase 5).
