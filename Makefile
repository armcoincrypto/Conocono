.PHONY: venv install serve serve-reload api-test

venv:
	python3 -m venv .venv

install: venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install -r requirements.txt

serve:
	./.venv/bin/uvicorn app_fastapi:app --host 127.0.0.1 --port 8000

serve-reload:
	./.venv/bin/uvicorn app_fastapi:app --reload --host 127.0.0.1 --port 8000

api-test:
	./.venv/bin/python - <<'PY'
from fastapi.testclient import TestClient
from app_fastapi import app
c = TestClient(app)
print("/health:", c.get("/health").status_code, c.get("/health").json())
print("/sum:", c.get("/sum", params={"a":2,"b":3}).status_code, c.get("/sum", params={"a":2,"b":3}).json())
PY

docker-up:
\tdocker compose up --build

docker-down:
\tdocker compose down

docker-logs:
\tdocker compose logs -f

docker-restart:
\tdocker compose down && docker compose up --build
