from __future__ import annotations

import os
import re
from typing import Any, Dict

from fastapi import FastAPI, Query
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI(title="Conocono API", version="1.0.0")


class Health(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"


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


if __name__ == "__main__":
    import sys

    import uvicorn

    if "--serve" in sys.argv:
        uvicorn.run("app_fastapi:app", host="127.0.0.1", port=8000, reload=False)

# --- Minimal /chat endpoint (fallback-only) ---


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    """
    If OPENAI_* env vars are set, call an OpenAI-compatible server.
    Supported:
      - OpenAI cloud:   OPENAI_BASE_URL=https://api.openai.com/v1
      - Ollama local:   OPENAI_BASE_URL=http://127.0.0.1:11434/v1  (key can be "ollama")
    Fallback: returns a friendly static message if not configured.
    """
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if base_url and api_key and model:
        try:
            client = OpenAI(base_url=base_url, api_key=api_key)
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": req.message}],
                temperature=0.7,
                max_tokens=60,
            )
            txt = resp.choices[0].message.content if resp.choices else ""
            return {"message": txt or "Hi!", "model": model}
        except Exception as e:
            return {"detail": f"LLM error: {e.__class__.__name__}: {e}", "model": model}

    # Fallback if not configured
    return {"message": "Hello! 👋 (fallback; no OpenAI configured)", "model": None}

    # Minimal placeholder reply so the route exists and can be wired to LLM later
    return {"message": "Hello! 👋"}
