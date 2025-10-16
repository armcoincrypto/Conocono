from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DRY_RUN = False  # set to False to actually delete

PROTECT = {
    "app_fastapi.py",
    "requirements.txt",
    "requirements-dev.txt",
    "pytest.ini",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.override.yml",
    "ai-code-writer",
    "scan_project.py",
    "conocono_doctor.py",
    "cleanup_conocono.py",
    "test_api.py",
    ".git",
    ".gitmodules",
    ".gitignore",
}

DELETE_PATTERNS = [
    "ai-code-writer/app_fastapi.py",  # remove duplicate if present
    "*.iml",
    "*.local",
    ".DS_Store",
    ".pytest_cache",
    ".mypy_cache",
    "**/__pycache__",
]


def skip_path(p: Path) -> bool:
    # never touch the venv or its contents
    try:
        if p.is_relative_to(ROOT / ".venv"):
            return True
    except AttributeError:
        # Fallback for older Python (not needed on 3.11+, but kept harmless)
        try:
            p.relative_to(ROOT / ".venv")
            return True
        except ValueError:
            pass
    return False


def is_protected(p: Path) -> bool:
    try:
        rel = p.relative_to(ROOT)
    except ValueError:
        return True
    first = rel.parts[0] if rel.parts else str(rel)
    return first in PROTECT or str(rel) in PROTECT


def remove(p: Path) -> None:
    if p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
    else:
        try:
            p.unlink()
        except FileNotFoundError:
            pass


def main() -> int:
    candidates = []
    for pat in DELETE_PATTERNS:
        for p in ROOT.glob(pat):
            if not p.exists():
                continue
            if skip_path(p):
                continue
            if is_protected(p):
                continue
            candidates.append(p)

    uniq, seen = [], set()
    for p in candidates:
        r = p.resolve()
        if r not in seen:
            uniq.append(p)
            seen.add(r)

    print("DRY_RUN:", DRY_RUN)
    print("Delete candidates:")
    if not uniq:
        print("  (none)")
        return 0
    for p in uniq:
        print(" -", p.relative_to(ROOT))
    if not DRY_RUN:
        for p in uniq:
            remove(p)
        print(f"\nDeleted {len(uniq)} item(s).")
    else:
        print("\nNothing deleted (DRY_RUN=True). Set DRY_RUN=False to apply.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
