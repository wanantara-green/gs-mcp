# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack overview

Docker Compose stack (`docker-compose.yaml`) wiring six services on `app-net`:

- **postgis** (`kartoza/postgis:16-3.4`) — spatial DB. Host port `5433` → container `5432`. Holds the raw spatial tables; it is the *source of truth* for layer data.
- **geoserver** (`kartoza/geoserver:3.0.0--v2026.06.25`, **pinned** — see comment in compose; `:latest` re-inits `/opt/geoserver_data` and wipes the catalog on upgrade). Host port `9597` → `8080`. CORS opened via kartoza env (`CORS_ENABLED=true`, `CORS_ALLOWED_ORIGINS=*`) so the public `map.html` on `training-02.wanantara.org` can fetch WFS.
- **postgis-seed** (`./seed/`) — one-shot importer that runs `ogr2ogr` over every `seed/geojson/*.geojson`, reprojects to EPSG:4326, and loads into PostGIS. Idempotent: skips tables that already have rows (override with `SEED_FORCE=1`). Table name = basename lowercased — must match `init/sld/<name>.sld` so the next service can attach the right style.
- **geoserver-init** (`./init/`) — idempotent self-healing provisioner. Runs after `postgis-seed` completes successfully. Runs once per deploy after GeoServer is healthy. Creates workspace `zonasiluwu`, the `zonasiluwu_pg` PostGIS datastore, publishes every available PostGIS table as a featuretype (EPSG:4326), and uploads matching SLD styles from `init/sld/<table>.sld`. If the catalog is already complete it exits early. **Spatial data lives in PostGIS; the GeoServer volume is treated as disposable.**
- **geoserver-mcp** (`./geoserver-mcp/`) — Python MCP server (`FastMCP`, package `geoserver_mcp`) that talks to GeoServer REST via the `geoserver-rest` lib. It speaks MCP over **stdio only**; the Dockerfile wraps it with `mcp-proxy` to expose SSE on `0.0.0.0:8000/sse`. Host bind: `127.0.0.1:8001:8000` (port 8000 conflicts with Coolify API on the host).
- **gs-ai-bridge** (`./gs-ai-bridge/`) — FastAPI (`uvicorn gs_ai_bridge.main:app`, port 8080). Public-facing AI bridge for `map.html`. Receives `POST /ask {"pertanyaan": ...}`, calls DeepSeek (key server-side from `DEEPSEEK_API_KEY`), and invokes a **hard-coded whitelist of 4 read-only GeoServer MCP tools** (`list_layers`, `get_layer_info`, `query_features`, `generate_map`) enforced in `mcp_client.py`/`tools.py`. CORS is locked to `ALLOWED_ORIGIN` (default `https://training-02.wanantara.org`). Coolify/Traefik terminates HTTPS; the container only `expose`s 8080.

## Data flow

```
browser (map.html @ training-02.wanantara.org)
  ├── WFS  → geoserver:9597/geoserver/zonasiluwu/ows  → postgis (30 tables)
  └── /ask → gs-ai-bridge → DeepSeek + geoserver-mcp(SSE) → geoserver REST
```

## Common commands

```bash
# Bring the whole stack up (root of repo)
docker compose up -d --build

# Rebuild a single service after editing its source
docker compose up -d --build geoserver-mcp
docker compose up -d --build gs-ai-bridge

# Force the provisioner to re-run (e.g. after wiping the geoserver volume)
docker compose run --rm geoserver-init

# Logs
docker compose logs -f gs-ai-bridge
docker compose logs -f geoserver-mcp
docker compose logs --tail=200 geoserver-init

# Sanity-check endpoints
curl -s http://localhost:9597/geoserver/rest/workspaces.json -u admin:geoserver
curl -s http://localhost:8001/sse                      # SSE handshake
curl -s http://localhost:8080/health                   # gs-ai-bridge (if mapped)
```

### Local dev for `gs-ai-bridge` (without Docker)

```bash
cd gs-ai-bridge
pip install -r requirements.txt
export DEEPSEEK_API_KEY=sk-...
export GEOSERVER_MCP_SSE_URL=http://localhost:8001/sse
PYTHONPATH=src uvicorn gs_ai_bridge.main:app --port 8080 --reload
```

There is no test suite, linter, or build script configured in this repo.

## Things to know before editing

- **Never bump the `geoserver` image tag back to `:latest`.** The pin exists because a major-version reinit destroys the catalog volume; the `geoserver-init` rebuild only covers workspace/datastore/featuretype/SLD, not styles/layers added manually.
- **SLD files live in `init/sld/` and are baked into the `geoserver-init` image.** They used to be fetched from `raw.githubusercontent` of the `training-02` repo; do not reintroduce that dependency. SLD `version="1.1.0"` declarations are rewritten to `1.0.0` on upload (see `upload_style()` in `init/init.py`) — the file content uses SLD 1.0 constructs.
- **GeoJSON in `seed/geojson/` is gitignored** (only `Dockerfile`, `seed.sh`, `README.md`, and `geojson/.gitignore` are tracked). Do not `git add -f` the GeoJSON — it's ~164 MB and will bloat the repo. **Source of truth for the data is the maintainer's shapefiles**, which are converted to GeoJSON (shp→geojson) and dropped into `seed/geojson/` by hand. The files are regenerable any time, so they are the canonical backup/restore path — there is no DB dump to keep in sync. (The 30 files are also recoverable from the `training-02` repo git history at `3e00032^`, before that repo's `geojson/` folder was deleted — but the maintainer's shapefiles are the upstream source.)
- **Do not re-add `-lco FID=id` to `seed/seed.sh`.** Several GeoJSON files have duplicate or non-integer `id` properties; forcing them into the PK causes `duplicate key` / `Wrong field type` failures. Default `ogc_fid` auto-increment works for all 30.
- **`geoserver-mcp` is stdio-only.** Any change to how it's launched must go through `mcp-proxy` (see `geoserver-mcp/Dockerfile`). `--pass-environment` is required so the wrapped process inherits `GEOSERVER_*` vars.
- **`gs-ai-bridge` read-only contract is enforced server-side**, not just by prompting. When adding tools, update the whitelist in `gs-ai-bridge/src/gs_ai_bridge/mcp_client.py` and `tools.py` — do not assume the model will respect a prompt-level restriction.
- `.env` is gitignored (and was previously committed by mistake — see recent commit history). Secrets like `DEEPSEEK_API_KEY` belong in Coolify env vars, never in the repo.

## Deployment context (`catatan.md`)

Production runs on Coolify under `wanantara-green/gs-mcp` and exposes:
- `https://geoserver.app.wanantara.org` → GeoServer
- `https://geoserver-mcp.app.wanantara.org/sse` → MCP SSE
- `https://training-02.wanantara.org` → consumer (separate repo `wanantara-green/training-02`, contains `map.html` + `js/config.js` pointing at the above URLs)

The companion `training-02` repo is **not** in this working directory; if a task involves `map.html`, `js/config.js`, or GeoJSON fallbacks, those files live in that sibling repo.

## Seeding production PostGIS (one-time per environment)

Because `seed/geojson/*.geojson` is gitignored, a fresh Coolify deploy comes up with an empty `postgis-seed/geojson` folder and seeds nothing. **The GeoJSON must be placed on the server manually before the first `postgis-seed` run.** PostGIS is on a persistent volume (`postgis-data`), so this is genuinely a one-time step per environment.

Recommended path on the Coolify host (`/workspace/gs-mcp/` per `catatan.md`):

```bash
cd /workspace/gs-mcp
# Place the GeoJSON into seed/geojson/ from your own copy. The maintainer keeps
# these regenerated from shapefiles (shp→geojson); copy them up to the host, e.g.:
#   scp ./seed/geojson/*.geojson user@host:/workspace/gs-mcp/seed/geojson/
# (Do NOT clone training-02 for this — its geojson/ folder was removed in 3e00032.)

docker compose up -d --build postgis-seed geoserver-init
# Verify: [seed] selesai: total=30 import=30 ... ; [init] selesai: featuretype 30/30, style 30/30.
```

On subsequent redeploys, `postgis-seed` skips every table (idempotent) — no action needed unless GeoJSON changes (then re-run with `SEED_FORCE=1`).
