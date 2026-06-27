"""Loop tool-calling DeepSeek.

Kunci DeepSeek dibaca dari env (DEEPSEEK_API_KEY) — tidak pernah dikirim ke
browser. DeepSeek API kompatibel-OpenAI, jadi kita pakai endpoint
/chat/completions dengan parameter `tools` + `tool_choice`.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx

from .mcp_client import ToolNotAllowed, call_tool
from .tools import TOOL_SCHEMAS

logger = logging.getLogger("gs-ai-bridge.deepseek")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
WORKSPACE = os.getenv("GEOSERVER_WORKSPACE", "zonasiluwu")
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "6"))
TOOL_RESULT_CHAR_LIMIT = int(os.getenv("TOOL_RESULT_CHAR_LIMIT", "12000"))

SYSTEM_PROMPT = f"""Anda adalah asisten WebGIS untuk peta "Rencana Zonasi Kabupaten Luwu".
Data spasial tersimpan di GeoServer pada workspace '{WORKSPACE}' (sekitar 30 layer zonasi).

Aturan:
- Gunakan tool yang tersedia untuk mengambil data NYATA dari GeoServer. Jangan pernah
  mengarang nama layer, jumlah fitur, atau nilai atribut.
- Bila belum tahu nama layer, panggil list_layers dulu.
- Untuk menyaring/menghitung fitur, pakai ekspresi CQL pada parameter 'filter' di query_features.
- Semua tool bersifat read-only; Anda tidak bisa dan tidak boleh mengubah apa pun.
- Jawab dalam Bahasa Indonesia yang ringkas, jelas, dan langsung ke inti.
- Bila relevan, sebutkan nama layer dan angka hasil query.
- Jika pertanyaan di luar konteks data zonasi Luwu, jawab seperlunya tanpa memanggil tool."""


class DeepSeekError(RuntimeError):
    pass


async def answer_question(question: str) -> str:
    if not DEEPSEEK_API_KEY:
        raise DeepSeekError("DEEPSEEK_API_KEY belum di-set di environment server.")

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    async with httpx.AsyncClient(timeout=httpx.Timeout(90.0)) as client:
        for _ in range(MAX_TOOL_ROUNDS):
            data = await _chat(client, messages)
            message = data["choices"][0]["message"]
            messages.append(message)

            tool_calls = message.get("tool_calls")
            if not tool_calls:
                return (message.get("content") or "").strip() or "(jawaban kosong)"

            for tc in tool_calls:
                messages.append(await _run_tool_call(tc))

    return "Maaf, permintaan ini terlalu kompleks (batas iterasi tool tercapai)."


async def _run_tool_call(tc: dict[str, Any]) -> dict[str, Any]:
    name = tc.get("function", {}).get("name", "")
    raw_args = tc.get("function", {}).get("arguments") or "{}"
    try:
        args = json.loads(raw_args)
    except json.JSONDecodeError:
        args = {}

    try:
        result = await call_tool(name, args)
    except ToolNotAllowed as e:
        result = f"ERROR: {e}"
    except Exception as e:  # noqa: BLE001 - kembalikan error ke model, jangan crash request
        logger.exception("tool %s gagal", name)
        result = f"ERROR menjalankan tool '{name}': {e}"

    return {
        "role": "tool",
        "tool_call_id": tc.get("id"),
        "content": result[:TOOL_RESULT_CHAR_LIMIT],
    }


async def _chat(client: httpx.AsyncClient, messages: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "tools": TOOL_SCHEMAS,
        "tool_choice": "auto",
        "temperature": 0.2,
    }
    resp = await client.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    if resp.status_code >= 400:
        raise DeepSeekError(f"DeepSeek API {resp.status_code}: {resp.text[:500]}")
    return resp.json()
