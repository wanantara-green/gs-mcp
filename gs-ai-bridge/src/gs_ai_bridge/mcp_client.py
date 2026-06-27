"""Klien MCP (SSE) ke service geoserver-mcp.

Membuka koneksi SSE singkat per panggilan tool, melakukan handshake MCP,
memanggil tool, lalu menutup koneksi. Sederhana & tahan-error untuk skala
pelatihan. Whitelist tool di-enforce DI SINI — bukan hanya di skema yang
dikirim ke model — sehingga read-only adalah jaminan server-side.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client

from .tools import ALLOWED_TOOL_NAMES

logger = logging.getLogger("gs-ai-bridge.mcp")

SSE_URL = os.getenv("GEOSERVER_MCP_SSE_URL", "http://geoserver-mcp:8000/sse")


class ToolNotAllowed(Exception):
    """Diangkat bila model mencoba memanggil tool di luar whitelist read-only."""


def _flatten(result: Any) -> str:
    """Gabungkan konten teks dari CallToolResult menjadi string biasa."""
    parts: list[str] = []
    for item in getattr(result, "content", None) or []:
        text = getattr(item, "text", None)
        if text is not None:
            parts.append(text)
    if getattr(result, "isError", False):
        return "ERROR dari GeoServer: " + ("\n".join(parts) if parts else "(tanpa detail)")
    return "\n".join(parts) if parts else "(tidak ada konten)"


async def call_tool(name: str, arguments: dict[str, Any]) -> str:
    """Panggil satu tool read-only di geoserver-mcp dan kembalikan hasilnya sebagai teks."""
    if name not in ALLOWED_TOOL_NAMES:
        raise ToolNotAllowed(
            f"Tool '{name}' tidak diizinkan. Hanya tool read-only berikut yang tersedia: "
            f"{', '.join(sorted(ALLOWED_TOOL_NAMES))}."
        )

    logger.info("call_tool %s args=%s", name, arguments)
    async with sse_client(SSE_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
            return _flatten(result)
