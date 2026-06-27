"""FastAPI app untuk gs-ai-bridge.

Endpoint:
  GET  /health  -> cek hidup
  POST /ask     -> {"pertanyaan": "..."}  ->  {"answer": "..."}

CORS dikunci ke ALLOWED_ORIGIN (default https://training-02.wanantara.org),
sehingga hanya peta training-02 yang boleh memanggil dari browser.
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import __version__
from .deepseek import DeepSeekError, answer_question

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("gs-ai-bridge")

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "https://training-02.wanantara.org")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGIN.split(",") if o.strip()]

app = FastAPI(title="gs-ai-bridge", version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class AskRequest(BaseModel):
    pertanyaan: str | None = None
    question: str | None = None  # alias bahasa Inggris, opsional

    def text(self) -> str:
        return (self.pertanyaan or self.question or "").strip()


class AskResponse(BaseModel):
    answer: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "gs-ai-bridge", "version": __version__}


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    question = req.text()
    if not question:
        raise HTTPException(status_code=400, detail="Field 'pertanyaan' wajib diisi.")

    try:
        answer = await answer_question(question)
    except DeepSeekError as e:
        logger.error("DeepSeek error: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # noqa: BLE001
        logger.exception("ask gagal")
        raise HTTPException(status_code=502, detail=f"Gagal memproses pertanyaan: {e}")

    return AskResponse(answer=answer)
