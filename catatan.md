```markdown
# Struktur Coolify — wanantara-green

## Aplikasi

### 1. gs-mcp
| | Detail |
|---|---|
| **Repo** | `wanantara-green/gs-mcp` (branch `main`) |
| **Type** | Docker Compose |
| **Container** | `postgis`, `geoserver`, `geoserver-mcp` |
| **Port** | PostGIS `5433`, GeoServer `9597`, MCP `8001` |

**URL:**
- `http://jiwzrwxkxft33e2131tdroxs.103.197.188.59.sslip.io`
- `https://geoserver.app.wanantara.org` → GeoServer
- `http://w7mm8u2fkmoj14dajseb7up5.103.197.188.59.sslip.io`  
- `https://geoserver-mcp.app.wanantara.org` → MCP SSE

**File penting:**
- `/workspace/gs-mcp/docker-compose.yaml` — Konfigurasi Docker Compose
- `/workspace/gs-mcp/geoserver-mcp/Dockerfile` — Dockerfile MCP
- `/workspace/gs-mcp/geoserver-mcp/pyproject.toml` — Python package MCP
- `/workspace/gs-mcp/geoserver-mcp/src/geoserver_mcp/main.py` — Entry point MCP server

### 2. training-02
| | Detail |
|---|---|
| **Repo** | `wanantara-green/training-02` (branch `main`) |
| **Type** | Static (nginx:alpine) |
| **Port** | 80 |

**URL:**
- `http://v8vvqv56u4i01sjzbbsp2mhn.103.197.188.59.sslip.io`
- `https://training-02.wanantara.org` → WebGIS Peta Zonasi

**File penting:**
- `/workspace/training-02/map.html` — Peta interaktif utama (~1362 baris)
- `/workspace/training-02/js/config.js` — Konfigurasi URL (GeoServer + MCP)
- `/workspace/training-02/js/app.js` — Sistem modul pelatihan (quiz, progress)
- `/workspace/training-02/js/modul-data.js` — Data fallback modul
- `/workspace/training-02/index.html` — Landing page
- `/workspace/training-02/modul.html` — Halaman modul
- `/workspace/training-02/geojson/` — 30 file GeoJSON + 30 file SLD

## Services

### hermes-agent-with-webui
| | Detail |
|---|---|
| **UUID** | `udodihj1cgyjfi6iyi25f90w` |
| **Container** | `hermes-agent`, `hermes-webui` |
| **Fungsi** | Agent AI + Web UI (tempat kita sekarang) |

### supabase
| | Detail |
|---|---|
| **UUID** | `y104otpw4gnhcjorko3omn4o` |
| **Container** | Kong, Studio, DB, Auth, Storage, Realtime, Edge Functions, dll (15 container) |
| **Workspace** | `zonasiluwu` |
| **Service Role Key** | Tersimpan di `config.yaml` (JWT valid sampai 2126) |

## Koneksi Antar Aplikasi

```
training-02 (map.html)
    │
    ├── WFS fetch ──► https://geoserver.app.wanantara.org/geoserver/zonasiluwu/ows
    │                      │
    │                      └── GeoServer ──► PostGIS (30 tabel)
    │
    └── MCP SSE ────► https://geoserver-mcp.app.wanantara.org/sse
                           │
                           └── mcp-proxy ──► geoserver-mcp (stdio)
                                                  │
                                                  └── GeoServer REST API
```

## Cara Edit & Push Repo

Agent memiliki akses read/write ke **kedua repo** via GitHub token.

```python
import subprocess

# Baca token
with open("/home/hermeswebui/.hermes/webui/attachments/e29d09d2065f/environment.txt") as f:
    token = f.read().strip()

# Edit file di /workspace/training-02/ atau /workspace/gs-mcp/
# Lalu commit & push:
repo = f"https://{token}@github.com/wanantara-green/REPO_NAME.git"
subprocess.run(["git", "-C", "/workspace/REPO_NAME", "add", "-A"])
subprocess.run(["git", "-C", "/workspace/REPO_NAME", "commit", "-m", "pesan commit"])
subprocess.run(["git", "-C", "/workspace/REPO_NAME", "push", repo, "main"])
```

## Credential

| Credential | Lokasi |
|---|---|
| GitHub Token | `/home/hermeswebui/.hermes/webui/attachments/e29d09d2065f/environment.txt` |
| Coolify API Token | `/home/hermeswebui/.hermes/config.yaml` → `mcp_servers.supabase-coolify.env.COOLIFY_API_TOKEN` |
| Supabase Service Role Key | `/home/hermeswebui/.hermes/config.yaml` → `mcp_servers.supabase-coolify.env.SUPABASE_SERVICE_ROLE_KEY` |
| GeoServer Admin | `admin` / `geoserver` |
| PostGIS | `geoserver` / `geoserver` (port 5433) |

## Perintah Penting

```bash
# Cek endpoint
curl -s https://geoserver.app.wanantara.org/geoserver/rest/workspaces.json -u admin:geoserver
curl -s https://geoserver-mcp.app.wanantara.org/sse
curl -s https://training-02.wanantara.org/js/config.js

# Redeploy training-02 (stop → start trigger rebuild)
# Via Coolify API atau Dashboard

# Cek cache Cloudflare
curl -sv https://training-02.wanantara.org/js/config.js 2>&1 | grep cf-cache
```