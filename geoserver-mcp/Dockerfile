# GeoServer MCP — exposed over SSE so the Hermes agent (a separate container)
# can reach it across the Docker network.
#
# geoserver-mcp itself speaks MCP over *stdio* only (main.py calls mcp.run()
# with no transport). mcp-proxy wraps it as a stdio child process and serves
# it as an SSE endpoint at http://0.0.0.0:8000/sse.
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Build/runtime deps: curl for healthchecks, gcc/build-essential/git for the
# geoserver-rest + seaborn dependency chain.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc build-essential git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install the local geoserver-mcp package + the stdio->SSE bridge.
RUN pip install --upgrade pip setuptools wheel \
    && pip install . mcp-proxy

EXPOSE 8000

# geoserver-mcp reads GEOSERVER_URL / GEOSERVER_USER / GEOSERVER_PASSWORD from
# the environment (see get_geoserver() in main.py); --pass-environment forwards
# them to the spawned stdio server. mcp-proxy 0.5.x uses --sse-host/--sse-port
# and takes the wrapped command as a positional arg (no "--" separator).
CMD ["mcp-proxy", "--sse-host", "0.0.0.0", "--sse-port", "8000", "--pass-environment", "geoserver-mcp"]
