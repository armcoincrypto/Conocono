.PHONY: dev-install test docker-up docker-down docker-logs docker-restart serve serve-reload api-test pycheck smoke-live smoke-local

serve:
	./.venv/bin/uvicorn app_fastapi:app --host 127.0.0.1 --port 8000

serve-reload:
	./.venv/bin/uvicorn app_fastapi:app --reload --host 127.0.0.1 --port 8000

api-test:
	./.venv/bin/pytest -q test_api.py::test_health test_api.py::test_sum

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-restart:
	docker compose down && docker compose up --build

dev-install:
	./.venv/bin/pip install -r requirements-dev.txt

test:
	./.venv/bin/pytest

pycheck:
	@./.venv/bin/python - <<'PYCK'
import compileall, sys
ok = compileall.compile_dir(".", quiet=1, force=True)
print("pycheck:", "OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
PYCK

smoke-live:
	@echo "==> Checking existing server at http://127.0.0.1:8000/health"
	@if curl -sf http://127.0.0.1:8000/health >/dev/null; then \
	  echo "Health:"; curl -sf http://127.0.0.1:8000/health | ./.venv/bin/python -c "import sys,json;print(json.load(sys.stdin))"; \
	  echo "Sum:"; curl -sf "http://127.0.0.1:8000/sum?a=2&b=3" | ./.venv/bin/python -c "import sys,json;print(json.load(sys.stdin))"; \
	else \
	  echo "No server responding on :8000. Start one with 'make serve' or 'make docker-up' and rerun 'make smoke-live'."; \
	  exit 1; \
	fi

smoke-local:
	@echo "==> Starting temporary uvicorn on 127.0.0.1:8001"
	@./.venv/bin/uvicorn app_fastapi:app --host 127.0.0.1 --port 8001 & echo $$! > .uv.pid
	@printf "==> Waiting for health..."
	@i=0; until curl -sf http://127.0.0.1:8001/health >/dev/null; do i=$$((i+1)); [ $$i -gt 60 ] && echo " timeout" && exit 1; printf "."; sleep 0.2; done; echo "\nHealthy after $$i checks"
	@echo "Health:"; curl -sf http://127.0.0.1:8001/health | ./.venv/bin/python -c "import sys,json;print(json.load(sys.stdin))"
	@echo "Sum:"; curl -sf "http://127.0.0.1:8001/sum?a=2&b=3" | ./.venv/bin/python -c "import sys,json;print(json.load(sys.stdin))"
	@echo "==> Stopping temporary server"; kill `cat .uv.pid` >/dev/null 2>/dev/null || true; rm -f .uv.pid
