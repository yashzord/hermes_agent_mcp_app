# Deploying Recall

The code is deploy-ready: `RECALL_TRANSPORT=http` serves Streamable HTTP and the
`server/Dockerfile` runs it. This project is **deployed live on Render**; the
sections below record how, and how any host would work.

## Live deployment (current)

- **Host:** Render (free plan), Docker from the `render.yaml` blueprint.
- **URL:** `https://recall-mcp-wa3n.onrender.com/mcp`
- **Build:** `dockerfilePath: ./server/Dockerfile`, `dockerContext: ./server`.
- **Config:** `render.yaml` sets `RECALL_DB=/app/recall.db`. Render's free plan has
  **no persistent disk**, so the SQLite deck lives on the container's ephemeral
  filesystem and the ~20-card seed deck simply reloads on each restart. That's
  fine for study content; add a paid disk mounted at `/data` (and drop the
  `RECALL_DB` override) if the deck ever needs to persist.
- **Transport mode:** stateless HTTP + JSON response + permissive CORS
  (`server/src/server.py`). Stateless is the official MCP Apps server pattern and
  sidesteps the Claude proxy GET-stream bug (anthropics/claude-ai-mcp#636).

### Free-plan caveats (honest)
- **Cold starts:** a free Render service spins down after ~15 min idle and takes a
  few seconds to wake. A client's first call after idle may lag. Upgrade to a paid
  instance for always-on.
- **No disk:** see above - the deck reseeds on restart.

### Redeploys
`autoDeploy` is on: pushing to `main` triggers a new Render build automatically.
No manual step.

## Why Render (and not Railway/Fly)

Railway was tried first and abandoned - its Metal builder failed every build (a
platform issue, not our code). Render built and ran the same `server/Dockerfile`
first try. Fly.io also satisfies the requirements and is a fine alternative for a
tiny always-on container with a volume.

## What any host must provide

1. Build from `server/Dockerfile` (build context `server/`).
2. A **public HTTPS URL** - remote MCP clients require https.
3. Route external traffic to container `PORT` (the app binds `0.0.0.0:$PORT`).
4. Optional: a **persistent volume at `/data`** + drop the `RECALL_DB` override, if
   the deck must survive restarts. Without it the seed deck reloads each start.
5. For a connector that must answer instantly, keep the instance **always-on**
   (paid tier) rather than scale-to-zero.

## Connecting a client

The MCP endpoint is `https://recall-mcp-wa3n.onrender.com/mcp`. Where the
interactive widget actually renders depends on the client - see
`docs/architecture.md` and the vault's "Hosts & Where It Renders" note. In short:

- **MCPJam** (`npx -y @mcpjam/inspector@latest`) and the official ext-apps
  **basic-host**: render + drive the flashcard widget. Proven.
- **Claude.ai web (custom connector):** tool calls work, but the widget does
  **not** render inline - a Claude-side custom-connector limitation (#636), not a
  bug in Recall. The result shows as text.

To add to Claude.ai anyway (tools-as-text): Settings -> Connectors -> Add custom
connector -> URL `https://recall-mcp-wa3n.onrender.com/mcp`, no auth.

## Security notes

- No secrets are baked into the image. `RECALL_DB` is just a path.
- No-auth + an unguessable URL is acceptable because the deck is study content,
  not sensitive data. Add OAuth before storing anything real (PROJECT.md §4/§6).
