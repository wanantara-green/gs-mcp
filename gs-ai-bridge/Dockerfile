# gs-ai-bridge — FastAPI yang menjembatani map.html (publik) ke DeepSeek +
# geoserver-mcp (4 tool read-only). Key DeepSeek dibaca dari env, tidak pernah
# ke browser. Listen di port 8080; Coolify/Traefik yang menambah HTTPS domain.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
    CMD curl -fsS http://localhost:8080/health || exit 1

CMD ["uvicorn", "gs_ai_bridge.main:app", "--host", "0.0.0.0", "--port", "8080"]
