# gs-ai-bridge

Jembatan kecil & ter-scope antara peta publik `map.html` (training-02) dan
DeepSeek, dengan akses GeoServer **read-only** lewat `geoserver-mcp`.

```
map.html (browser, tanpa kredensial)
   │  POST /ask {"pertanyaan": "..."}
   ▼
gs-ai-bridge  ── DeepSeek API (key dari env, server-side)
   │           └ 4 tool GeoServer READ-ONLY via geoserver-mcp (SSE)
   ▼
{"answer": "jawaban bahasa natural"}   (CORS dikunci ke training-02)
```

## Kenapa aman

- **Key DeepSeek tidak pernah ke browser** — hanya dibaca dari env `DEEPSEEK_API_KEY` di sisi server.
- **Tool dibatasi read-only** — hanya `list_layers`, `get_layer_info`, `query_features`,
  `generate_map`. Whitelist di-enforce di server (`mcp_client.py` + `tools.py`),
  bukan sekadar disembunyikan dari model. Tidak ada akses Coolify/Supabase/GitHub.
- **CORS dikunci** ke `https://training-02.wanantara.org` (override via `ALLOWED_ORIGIN`).

## Endpoint

| Method | Path     | Body                      | Response             |
|--------|----------|---------------------------|----------------------|
| GET    | /health  | —                         | `{"status":"ok",...}`|
| POST   | /ask     | `{"pertanyaan":"..."}`    | `{"answer":"..."}`   |

## Environment variables

| Var                     | Default                              | Catatan                                  |
|-------------------------|--------------------------------------|------------------------------------------|
| `DEEPSEEK_API_KEY`      | —                                    | **Wajib.** Set di Coolify, jangan commit.|
| `DEEPSEEK_MODEL`        | `deepseek-chat`                      |                                          |
| `DEEPSEEK_BASE_URL`     | `https://api.deepseek.com`           | API kompatibel-OpenAI.                   |
| `GEOSERVER_MCP_SSE_URL` | `http://geoserver-mcp:8000/sse`      | Hostname internal Docker `app-net`.      |
| `GEOSERVER_WORKSPACE`   | `zonasiluwu`                         | Dipakai di system prompt.                |
| `ALLOWED_ORIGIN`        | `https://training-02.wanantara.org`  | Bisa beberapa, pisahkan koma.            |
| `MAX_TOOL_ROUNDS`       | `6`                                  | Batas iterasi tool-calling.              |

## Jalankan lokal

```bash
cd gs-ai-bridge
pip install -r requirements.txt
export DEEPSEEK_API_KEY=sk-...           # jangan commit
export GEOSERVER_MCP_SSE_URL=http://localhost:8001/sse   # port host geoserver-mcp
PYTHONPATH=src uvicorn gs_ai_bridge.main:app --port 8080 --reload

curl -s localhost:8080/ask -H 'Content-Type: application/json' \
  -d '{"pertanyaan":"Ada layer apa saja di zonasi Luwu?"}' | jq
```

## Deploy via Coolify

1. Service `gs-ai-bridge` sudah ada di `docker-compose.yaml` (build context `./gs-ai-bridge`).
2. Di Coolify → service `gs-ai-bridge` → **Environment Variables**, set `DEEPSEEK_API_KEY`.
3. Tambahkan domain (mis. `gs-ai.app.wanantara.org`) lewat Traefik — container `expose` port `8080`.
4. Update `js/config.js` di training-02 agar menunjuk ke `https://gs-ai.app.wanantara.org/ask`.

## Integrasi front-end (map.html)

```js
async function tanyaAI(pertanyaan) {
  const r = await fetch("https://gs-ai.app.wanantara.org/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pertanyaan }),
  });
  if (!r.ok) throw new Error("Bridge error " + r.status);
  const { answer } = await r.json();
  return answer;
}
```
