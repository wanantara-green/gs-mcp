# GeoServer MCP Stack

Stack: **GeoServer** + **PostGIS** + **GeoServer MCP**

## Struktur

```
├── .env                      # Environment variables
├── docker-compose.yaml       # Docker Compose stack
├── README.md
└── geoserver-mcp/            # GeoServer MCP server source
    ├── Dockerfile
    ├── pyproject.toml
    ├── smithery.yaml
    └── src/
        └── geoserver_mcp/
            ├── __init__.py
            └── main.py
```

## Quick Start

```bash
docker compose up -d --build
```

| Service       | URL                                      |
|---------------|------------------------------------------|
| GeoServer     | http://localhost:9597/geoserver          |
| PostGIS       | host: `postgis` port: 5432              |
| GeoServer MCP | http://localhost:8000/sse               |