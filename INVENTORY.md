# Project Inventory — Conocono

- Root: `/Users/gev/Conocono`
- Python: `3.13.7 (main, Aug 14 2025, 11:12:11) [Clang 17.0.0 (clang-1700.0.13.3)]`
- Files: **91**, Dirs: **8**

## Traits
- python: **True**
- node: **False**
- docker: **True**
- makefile: **True**
- precommit: **False**
- git_repo: **False**

## Frameworks & Tools (detected in files)
- aiogram: **True**
- fastapi: **True**
- flask: **False**
- telethon: **False**
- ccxt: **False**
- pytest: **True**
- pre-commit: **True**
- aiogram_installed_version: **None**

## Likely entry points
- `ai-code-writer/add_cli_autotest.py`
- `ai-code-writer/app_fastapi.py`
- `ai-code-writer/checksum_cli.py`
- `ai-code-writer/cleanup.py`
- `ai-code-writer/cli.py`
- `ai-code-writer/code_writer.py`
- `ai-code-writer/dev_doctor.py`
- `ai-code-writer/examples/a.py`
- `ai-code-writer/examples/add_cli.py`
- `ai-code-writer/examples/all_flags.py`
- `ai-code-writer/examples/app.py`
- `ai-code-writer/examples/b.py`
- `ai-code-writer/examples/c.py`
- `ai-code-writer/examples/checksum_cli_gen.py`
- `ai-code-writer/examples/echo.py`
- `ai-code-writer/examples/echo_click.py`
- `ai-code-writer/examples/echo_gem.py`
- `ai-code-writer/examples/fib.py`
- `ai-code-writer/examples/fib_custom.py`
- `ai-code-writer/examples/fib_gemini.py`
- `ai-code-writer/examples/flag_test.py`
- `ai-code-writer/examples/gen.py`
- `ai-code-writer/examples/gen_test.py`
- `ai-code-writer/examples/greet.py`
- `ai-code-writer/examples/hello.py`
- `ai-code-writer/examples/hello_local.py`
- `ai-code-writer/examples/post_cmd_test.py`
- `ai-code-writer/examples/q.py`
- `ai-code-writer/examples/sandbox.py`
- `ai-code-writer/examples/v1.py`
- `ai-code-writer/examples/v2.py`
- `ai-code-writer/examples/v3.py`
- `ai-code-writer/examples/watcher.py`
- `ai-code-writer/stats_csv.py`
- `ai-code-writer/test_exec.py`
- `ai-code-writer/unit_ok.py`
- `main.py`
- `scan_project.py`

## Python compile (syntax check)
- OK files: **46**
- With errors: **0**

## File type summary
- `.py`: 46
- `(no ext)`: 10
- `(dir)`: 8
- `.sh`: 7
- `.yml`: 6
- `.json`: 5
- `.xml`: 5
- `.txt`: 3
- `.example`: 2
- `.ini`: 2
- `.iml`: 1
- `.local`: 1
- `.lock`: 1
- `.md`: 1
- `.yaml`: 1

## Key files (first lines)
### requirements.txt
```
google-generativeai
python-dotenv

```
### Dockerfile
```
FROM python:3.11-slim
WORKDIR /app
COPY app_fastapi.py /app/
RUN pip install --no-cache-dir fastapi uvicorn
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; \
r=urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).status; \
sys.exit(0 if r==200 else 1)"

CMD ["uvicorn","app_fastapi:app","--host","0.0.0.0","--port","8000"]
```
### docker-compose.yml
```
services:
  sum-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    restart: unless-stopped

```
### Makefile
```
.PHONY: serve serve-reload api-test
serve:
\t./.venv/bin/python3 app_fastapi.py --serve
serve-reload:
\t./.venv/bin/uvicorn app_fastapi:app --reload
api-test:
\t./.venv/bin/python3 - <<'PY'
from fastapi.testclient import TestClient
from app_fastapi import app
c = TestClient(app)
print("/health:", c.get("/health").status_code, c.get("/health").json())
print("/sum:", c.get("/sum", params={"a":2,"b":3}).status_code, c.get("/sum", params={"a":2,"b":3}).json())
PY
```

## Next steps
- Fix any syntax errors listed above (open the file, go to the shown line/column).
- If you expect an aiogram bot, ensure `aiogram==3.*` is installed in your venv.
- If you intend to use GitHub, you can now `git init` and push (ask me for the commands).
