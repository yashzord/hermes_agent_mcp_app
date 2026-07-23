# Project: Personal MCP App + Hermes Agent Setup

> This document is the single source of truth for this project. It is written so
> that ANY builder agent (Hermes Agent via WebUI — the default — or Claude Code
> as backup) can pick up any phase and implement it, and so that I (the owner)
> can understand every step. Builder: read this whole file before writing code,
> keep a running CHANGELOG.md, and explain non-obvious decisions in docs/.

## 1. What we are building (plain English)

Three roles, one pipeline:

1. **The BUILDER — Hermes Agent (used via Hermes WebUI, never the TUI).**
   NousResearch's open-source coding agent, running locally with a Gemini
   free-tier brain, driven from a browser tab. It implements the phases in
   this document: writes the Python, runs commands, debugs, deploys.
   Claude Code is the BACKUP builder — this doc works as instructions for
   either agent, so if Hermes gets stuck on a phase, hand the same doc to
   Claude Code.

2. **The PRODUCT — "Recall", an MCP App** (see §3): a Model Context Protocol
   server exposing tools AND an interactive UI (the official "MCP Apps"
   extension, stable 2026-01-26). The UI is an HTML resource declared with a
   `ui://` URI, linked to a tool via metadata, rendered by the host in a
   sandboxed iframe, talking back over MCP JSON-RPC. Deployed as a remote
   MCP server.

3. **The RUNTIME HOST — Claude.ai**: where the finished app is used. Added as
   a custom connector; it renders the flip-card widget inline in chat. (Any
   other Apps-capable host works too.) Claude.ai plays no role in building.

Optional bonus (stretch): Hermes can ALSO consume the deployed server as an
MCP client — e.g. "make flashcards from this article" in the WebUI — but this
is not required for v1.

### Mental model
```
  YOU ──(browser: Hermes WebUI)──► HERMES AGENT ──builds──► RECALL SERVER
                                   (Gemini brain)           (deployed remote)
                                                                  │
  YOU ──(browser: Claude.ai)──── uses the app ◄── renders widget ─┘
```

No terminals in daily use. Terminal appears only for one-time install/setup
commands (installing Hermes, WebUI, and initial config).

## 2. Decisions already made

| Decision | Choice | Why |
|---|---|---|
| Server language | Python, FastMCP (`fastmcp` on PyPI) | De-facto standard for Python MCP servers; supports Apps (in-conversation UIs); matches Hermes's language |
| Transport | stdio locally, Streamable HTTP for deployment | FastMCP supports both natively |
| Deployment target | Fly.io / Railway / Render (small container) or Vercel Python | Cloudflare Workers is JS-native, so dropped; pick whichever is easiest at Phase 3 |
| UI layer | MCP Apps extension (`io.modelcontextprotocol/ui`), single HTML resource, no framework to start | Keep the iframe payload simple and auditable |
| Builder agent | Hermes Agent (NousResearch) via Hermes WebUI; Claude Code as backup | Owner wants Hermes to do the building, browser interface only |
| Agent interface | Hermes WebUI (github.com/nesquena/hermes-webui) — NO terminal/TUI for daily use | Browser chat with full CLI parity; owner does not want a TUI |
| Model brain | claude-code backend (revised 2026-07-22; Gemini free tier paused) | See §4 — Gemini free tier too small for agent loops (5 req/min, ~250/day) |
| Repo | One personal GitHub repo, monorepo layout (see §5) | Everything hand-off-able in one place |

## 3. What the app does — DECIDED: "Recall", a spaced-repetition flashcard app

The killer loop: Hermes (terminal) is the card FACTORY — "make flashcards from
this article/session" → it calls `add_card` with its model writing the Q/A pairs.
Claude.ai (chat) is the STUDY ROOM — "quiz me" → the MCP App UI renders
flip-cards inline; tap to reveal, tap Again/Hard/Good/Easy to grade; the server
schedules the next review. Two clients, one shared deck database.

### v1 tools (exactly four)
| Tool | Args | Behavior |
|---|---|---|
| `add_card` | front, back, deck="default" | Insert card, schedule immediately due |
| `review_next` | deck? | Return next due card; links the flashcard UI resource |
| `grade_card` | card_id, rating (again/hard/good/easy) | Apply SM-2, reschedule; called BY the UI iframe via the host |
| `stats` | deck? | Cards total / due today / reviewed today / streak |

### v1 UI (one `ui://recall/flashcard` resource)
- Card front → tap/click to flip → back + four grade buttons → next card loads.
- Thin progress bar ("3 of 7 due"). Session-complete state with stats.
- Each grade button fires `grade_card` through the host (bidirectional
  messaging — this is the part that exercises the MCP Apps protocol).

### Scheduling
- SM-2 algorithm (classic Anki-style). ~30 lines. Store per-card: ease factor,
  interval, due date, review count. Keep it boring and correct.

### Data model (SQLite)
- `cards(id, deck, front, back, ease, interval_days, due_at, created_at)`
- `reviews(id, card_id, rating, reviewed_at)`

### Seed content
- Ship a starter deck of ~20 cards about MCP/MCP Apps/Hermes concepts, so
  studying the app teaches the stack it's built on.

### Explicitly OUT of v1
- Editing/deleting cards via UI, images/media on cards, multiple users,
  deck sharing, fancy animations. Add later if wanted.

## 4. Model brain — DECIDED (revised 2026-07-22): claude-code backend, Gemini paused

- Primary: Hermes's `claude-code` backend — Hermes drives the locally installed
  Claude Code CLI (official headless interface), billed against the owner's
  Claude subscription. Chosen after Gemini free tier proved too small for agent
  loops (see below). Note: this shares the subscription's usage budget with any
  interactive Claude Code sessions.
- Paused, not dropped: Google Gemini API free tier (`gemini` provider,
  `gemini-flash-latest`). Reality check from Phase 1: the alias resolved to
  gemini-3.6-flash at 5 requests/minute and ~250 requests/day free — the
  original "~1,500 req/day" assumption was stale. That burns out mid-phase.
  Per-key limits: https://aistudio.google.com/rate-limit
- Fallback candidates if claude-code is unavailable: Groq free tier (key on
  hand) or OpenRouter free tier (`qwen/qwen3-coder:free`) — config change only.
- Hermes requires >= 64K context; all of the above clear this.

Rules:
- Keep model IDs in Hermes config only, never hardcoded in the app.
- Agent loops burn REQUESTS (every tool call = a request); throttling means
  the per-day/minute cap, not a broken setup.
- No OAuth-token proxy hacks against any provider's consumer subscription.
  (The claude-code backend is NOT this — it uses the official Claude Code
  CLI headless mode, not scraped tokens.)
  Paid upgrade shortlist if ever needed: GLM Coding Plan Lite (~$10/mo flat)
  or DeepSeek direct API (pay-per-token). Both drop in via config.

## 5. Repo layout

```
my-mcp-app/
├── PROJECT.md              # this file
├── CHANGELOG.md            # Claude Code keeps this updated
├── server/                 # the MCP server + app (Python / FastMCP)
│   ├── src/
│   │   ├── server.py       # FastMCP entry, tool registration
│   │   ├── tools/          # one module per tool
│   │   └── ui/             # the ui:// HTML resource (plain HTML/JS file)
│   ├── pyproject.toml      # uv-managed project
│   └── Dockerfile          # for container deploy (Phase 3)
├── hermes/                 # my Hermes config, versioned
│   ├── config.yaml.example # mcp_servers block pointing at deployed server
│   └── notes.md            # setup commands I ran, gotchas
└── docs/
    └── architecture.md     # diagrams + explanations Claude Code writes as it goes
```

## 6. Phases (each is a clean handoff to the builder agent)

### Phase 0 — Set up the builder (owner + a few terminal commands, one time)
- Install Hermes Agent (standard installer), configure the Gemini free-tier
  provider per §4 (API key from AI Studio, Gemini Flash model).
- Install Hermes WebUI (github.com/nesquena/hermes-webui), bind to localhost.
  If remote access is ever wanted: auth + Tailscale/SSH tunnel, never raw.
- Acceptance: from the WebUI in a browser, Hermes answers a prompt and can
  run a shell command / write a file in a scratch directory.
- This is the ONLY phase the owner does by hand. Everything below is done by
  telling the builder (Hermes WebUI chat, or Claude Code as backup):
  "read PROJECT.md and implement Phase N".

### Phase 1 — Repo + project scaffold (~small)
- Init repo, layout per §5, uv-managed Python project in `server/` with
  `fastmcp`, ruff for lint/format, a `dev` script running the server over stdio.
- Acceptance: MCP Inspector (`npx @modelcontextprotocol/inspector`) connects
  and lists a `ping` tool.

### Phase 2 — Core tools, no UI (~small)
- Implement the four tools from §3 with in-memory state first.
- Acceptance: all tools callable from MCP Inspector with correct schemas;
  SM-2 rescheduling verified with a scripted sequence of grades.

### Phase 3 — MCP Apps UI (~medium)
- Add the Apps extension via FastMCP's Apps support: register the `ui://`
  resource (`text/html;profile=mcp-app`), link it to `review_next`, implement
  the iframe↔host messaging (grade buttons fire `grade_card`). Read FastMCP's
  current Apps docs (gofastmcp.com) AND the official ext-apps spec first —
  both moved fast in 2026.
- Acceptance: UI renders and round-trips a grade in a supporting host
  (Claude.ai custom connector once deployed, or the ext-apps dev host).

### Phase 4 — Deploy as a remote server (~medium)
- Streamable HTTP transport, containerize (Dockerfile), deploy to Fly.io /
  Railway / Render (owner picks; all fine). Replace in-memory state with
  SQLite on a persistent volume. Auth: start with no-auth + unguessable URL,
  upgrade to OAuth if it ever holds real data.
- Acceptance: added to Claude.ai as a custom connector; a full study session
  (review → flip → grade → reschedule) works end-to-end in chat.

### Phase 5 — Stretch (optional)
- Wire the deployed server into Hermes itself under `mcp_servers:` with tool
  filtering, so "make flashcards from this article" works in the WebUI.
- Persistence hardening, a second UI view (stats dashboard), card editing.

## 7. Rules for the builder agent (Hermes or Claude Code)

1. Read this file + CHANGELOG.md at session start; update CHANGELOG at session end.
2. One phase per session unless told otherwise. Don't skip acceptance criteria.
3. Before using ext-apps SDK APIs, check the repo's current docs — spec is young.
   If a phase fails twice in a row, STOP and report what's blocking instead of
   thrashing; the owner may hand the phase to the backup builder.
4. Explain anything non-obvious in docs/architecture.md in plain language;
   the owner wants to understand everything, not just have it work.
5. Never commit secrets. `.env` and `~/.hermes` contents stay out of git.
6. No OAuth-token proxy hacks. §4 is non-negotiable.

## 8. Key references
- MCP spec: modelcontextprotocol.io
- MCP Apps extension (spec + SDK): github.com/modelcontextprotocol/ext-apps
- Hermes Agent: github.com/NousResearch/hermes-agent + hermes-agent.nousresearch.com/docs
- FastMCP (server framework + Apps/UI docs): gofastmcp.com and github.com/PrefectHQ/fastmcp
- Official MCP Python SDK (underlying reference impl): github.com/modelcontextprotocol/python-sdk
