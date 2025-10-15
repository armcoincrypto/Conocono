from __future__ import annotations
from fastapi import FastAPI, Query

app = FastAPI(title="Conocono API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/sum")
def sum_(a: float = Query(...), b: float = Query(...)):
    return {"a": a, "b": b, "sum": a + b}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_fastapi:app", host="127.0.0.1", port=8000, reload=True)
