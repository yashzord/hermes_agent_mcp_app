# Deploying Recall (Phase 4)

The code is deploy-ready: `RECALL_TRANSPORT=http` serves Streamable HTTP, the
Dockerfile persists the SQLite deck on a `/data` volume. What remains needs your
cloud account, so this stays a guided step. Exact host CLI commands are best
confirmed live at deploy time (versions drift) rather than pasted from here.

## What the host must provide

1. Build from the `server/Dockerfile`.
2. A **public HTTPS URL** - Claude.ai connectors require https.
3. **Always-on** (do not spin down on idle) - a connector must answer on demand.
4. A **persistent volume mounted at `/data`** - SQLite needs a real disk, or the
   deck resets on every redeploy.
5. Route external traffic to container `PORT` (default 8000).

Fly.io, Railway, and Render all satisfy these (§2). Fly.io is a good default for
a tiny always-on container with a volume; Railway is the simplest GitHub->deploy.
All need a card for a persistent volume - verify current pricing before picking.

## Railway (the chosen host)

The server lives in `server/`, so Railway must build from there. Set the service's
**Root Directory** to `server` (Settings -> Source -> Root Directory). That scopes
the build context to `server/`, and Railway auto-detects `server/Dockerfile`.
Railway injects `PORT` and the app binds `0.0.0.0:$PORT` - both handled.

Steps:
1. Railway -> New Project -> Deploy from GitHub repo -> this repo.
2. Service -> Settings -> Source -> **Root Directory** = `server`. Save (redeploys).
3. Service -> Settings -> Networking -> Public Networking -> Generate Domain.
   MCP endpoint is `https://<domain>/mcp/`.
4. Leave Healthcheck Path empty (no `/` route) and Serverless/scale-to-zero OFF
   (a connector must answer on demand).
5. Optional: add a Volume mounted at `/data` for persistence. Without it the app
   still runs; the seed deck just reloads on each restart.

Validated locally with `docker build server/` then running with an injected PORT -
the container serves `/mcp/` (307).

## Shape of the deploy (any host)

1. Point the host at this repo, build context `server/`.
2. Create a volume and mount it at `/data`.
3. Deploy. The container starts `uv run python src/server.py` in http mode.
4. Note the public URL; the MCP endpoint is `https://<your-app>/mcp/`.
5. Smoke test with the Inspector against the remote URL before wiring Claude.ai.

## Add to Claude.ai

1. Claude.ai -> Settings -> Connectors -> Add custom connector.
2. Name it Recall, URL `https://<your-app>/mcp/`.
3. Auth: start with none (unguessable URL). Upgrade to OAuth if it ever holds
   real data (PROJECT.md §4/§6).
4. In a chat: "quiz me from the mcp-basics deck" -> `review_next` runs, the
   flashcard widget renders inline. Flip a card, grade it - `grade_card` fires
   through the host and the next card loads. That round-trip is the Phase 4
   (and true Phase 3) acceptance.

## Security notes

- No secrets are baked into the image. `RECALL_DB` is just a path.
- Start with no-auth + an unguessable URL; the deck is study content, not
  sensitive data. Add OAuth before storing anything real.
