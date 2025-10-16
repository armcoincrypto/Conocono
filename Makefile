.PHONY: dev-install test docker-up docker-down docker-logs docker-restart serve serve-reload api-test smoke-live smoke-local

serve:
	./.venv/bin/uvicorn app_fastapi:app --host 127.0.0.1 --port 8000

serve-reload:
	./.venv/bin/uvicorn app_fastapi:app --reload --host 127.0.0.1 --port 8000

api-test:
	./.venv/bin/pytest -q test_api.py::test_health test_api.py::test_sum

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-restart:
	docker compose down && docker compose up -d --build

dev-install:
	./.venv/bin/pip install -r requirements-dev.txt

test:
	./.venv/bin/pytest

smoke-live:
	@echo "==> Checking server at http://127.0.0.1:8000/health"
	@i=0; until curl -sf http://127.0.0.1:8000/health >/dev/null; do \
		i=$$((i+1)); [ $$i -gt 120 ] && echo " timeout waiting for :8000" && exit 1; \
		printf "."; sleep 0.5; \
	done; echo "\nHealthy after $$i checks"
	@echo "Health:"; curl -sf http://127.0.0.1:8000/health | ./.venv/bin/python -c "import sys,json;print(json.load(sys.stdin))"
	@echo "Sum:"; curl -sf "http://127.0.0.1:8000/sum?a=2&b=3" | ./.venv/bin/python -c "import sys,json;print(json.load(sys.stdin))"
smoke-local:
	@echo "==> Starting temporary uvicorn on 127.0.0.1:8001"
	@./.venv/bin/uvicorn app_fastapi:app --host 127.0.0.1 --port 8001 & echo $$! > .uv.pid
	@printf "==> Waiting for health"
	@i=0; until curl -sf http://127.0.0.1:8001/health >/dev/null; do i=$$((i+1)); [ $$i -gt 60 ] && echo " timeout" && exit 1; printf "."; sleep 0.2; done; echo; echo "Healthy after $$i checks"
	@echo "Health:"; curl -sf http://127.0.0.1:8001/health | ./.venv/bin/python -c "import sys,json;print(json.load(sys.stdin))"
	@echo "Sum:"; curl -sf "http://127.0.0.1:8001/sum?a=2&b=3" | ./.venv/bin/python -c "import sys,json;print(json.load(sys.stdin))"
	@echo "==> Stopping temporary server"; kill `cat .uv.pid` >/dev/null 2>&1 || true; rm -f .uv.pid

.PHONY: ci
ci: dev-install test api-test smoke-local
	@echo "CI quick pass ✅"
