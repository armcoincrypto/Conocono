from __future__ import annotations

import os
import re
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# --- App ---------------------------------------------------------------------
app = FastAPI(title="Conocono API", version="1.0.0")


# --- Models ------------------------------------------------------------------
class Health(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    model: str | None = None  # echo which model was used (or None if fallback)


# --- Secret masking & env snapshot -------------------------------------------
SECRET_PATTERNS = [
    re.compile(pat, re.I)
    for pat in [
        r"secret",
        r"token",
        r"apikey",
        r"api_key",
        r"password",
        r"passwd",
        r"authorization",
        r"auth",
        r"bearer",
        r"private",
        r"session",
        r"cookie",
        r"credential",
        r"key",
    ]
]

SAFE_ENV_WHITELIST = {
    "HOSTNAME",
    "SHELL",
    "USER",
    "HOME",
    "PWD",
    "PYTHONPATH",
    "PYTHONVERSION",
    "VIRTUAL_ENV",
    "PATH",
    "COLIMA_DEFAULT",
    "DOCKER_HOST",
}


def _mask(v: str) -> str:
    if not v:
        return v
    if len(v) <= 8:
        return "*" * len(v)
    return v[:2] + "*" * (len(v) - 4) + v[-2:]


def _is_secret_key(k: str) -> bool:
    return any(p.search(k) for p in SECRET_PATTERNS)


def safe_env_snapshot() -> Dict[str, str]:
    out: Dict[str, str] = {}
    for k, v in os.environ.items():
        if k in SAFE_ENV_WHITELIST:
            out[k] = v
        elif _is_secret_key(k):
            out[k] = _mask(v)
    return out


# --- OpenAI client (optional; graceful fallback if not configured) -----------
_OPENAI_AVAILABLE = True
try:
    from openai import OpenAI  # pip install openai>=1.0
except Exception:
    _OPENAI_AVAILABLE = False

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client: "OpenAI | None" = None
if _OPENAI_AVAILABLE and OPENAI_API_KEY:
    try:
        _client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
    except Exception:
        _client = None  # leave None; endpoint will fall back


# --- Routes ------------------------------------------------------------------
@app.get("/health", response_model=Health)
def health() -> Health:
    return Health()


@app.get("/sum")
def sum_route(a: float = Query(...), b: float = Query(...)) -> Dict[str, float]:
    return {"a": a, "b": b, "sum": a + b}


@app.get("/debug")
def debug_route() -> Dict[str, Any]:
    return {
        "app": {"name": "Conocono API", "version": "1.0.0"},
        "env": safe_env_snapshot(),
        "cwd": os.getcwd(),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    If OpenAI is configured (OPENAI_API_KEY present), call the model.
    Otherwise, return a friendly fallback so the route always works.
    """
    if not (_OPENAI_AVAILABLE and _client and OPENAI_API_KEY):
        return ChatResponse(message="Hello! 👋 (fallback; no OpenAI configured)", model=None)

    try:
        resp = _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": req.message}],
            temperature=0.7,
            max_tokens=120,
        )
        text = resp.choices[0].message.content.strip()
        return ChatResponse(message=text, model=OPENAI_MODEL)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")


# --- Entry point -------------------------------------------------------------
if __name__ == "__main__":
    import sys

    import uvicorn  # pip install uvicorn[standard]

    if "--serve" in sys.argv:
        uvicorn.run("app_fastapi:app", host="127.0.0.1", port=8000, reload=False)
