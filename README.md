# Conocono — Sum API (FastAPI)

## Быстрый старт (локально)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
make test              # запустить все тесты
make serve             # поднять API на 127.0.0.1:8000
make smoke-local       # временный сервер :8001 + смоки
