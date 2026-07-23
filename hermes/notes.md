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

## Provider saga (2026-07-22, during Phases 1-2)

Chronology: Gemini free tier (5 req/min, ~250/day on gemini-3.6-flash - died
mid-phase) → claude-code backend (worked, but subscription had no spare usage)
→ Groq free tier via custom endpoint (per-request cap smaller than Hermes's own
system prompt: HTTP 413 even in a fresh session) → AWS Bedrock, deepseek.v3.2,
billed to bonus credits. That one stuck.

Bedrock setup that finally worked:
- Bedrock console: enable model access, create long-term API key.
- `hermes model` → AWS Bedrock → API key → deepseek.v3.2, region us-east-1.
- Endpoint is OpenAI-compatible: https://bedrock-mantle.us-east-1.api.aws/v1

GOTCHA that cost an hour: Hermes's custom-endpoint provider takes base_url
from the `model:` block but the api_key from the matching `custom_providers:`
entry in config.yaml. The Bedrock wizard set the env vars but left the OLD
Groq entry (with its inline api_key) in custom_providers - so every request
sent the Groq key to AWS: HTTP 401 "Invalid bearer token". Fix: replace the
stale custom_providers entry so base_url AND api_key both point at Bedrock.
Diagnose with a direct curl (Bearer token against <base_url>/chat/completions)
to prove the key before blaming anything else. Restart the WebUI
(./ctl.sh restart) after ANY credential/provider change - it reads config at
startup.
