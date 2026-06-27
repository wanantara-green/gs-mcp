"""gs-ai-bridge — jembatan aman antara map.html (publik) dan DeepSeek + GeoServer.

Browser TIDAK pernah memegang kredensial apa pun: kunci DeepSeek hanya ada di
sisi server (env var), dan model hanya boleh memanggil 4 tool GeoServer
read-only via geoserver-mcp.
"""

__version__ = "0.1.0"
