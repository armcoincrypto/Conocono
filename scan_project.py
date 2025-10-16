# scan_project.py
from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}

ENTRYPOINT_CANDIDATES = {
    "main.py",
    "app.py",
    "run.py",
    "server.py",
    "manage.py",
}

FRAMEWORK_HINTS = {
    "aiogram": (r"\bfrom\s+aiogram\b|\bimport\s+aiogram\b",),
    "fastapi": (r"\bfrom\s+fastapi\b|\bimport\s+fastapi\b",),
    "flask": (r"\bfrom\s+flask\b|\bimport\s+flask\b",),
    "telethon": (r"\bfrom\s+telethon\b|\bimport\s+telethon\b",),
    "ccxt": (r"\bfrom\s+ccxt\b|\bimport\s+ccxt\b",),
    "pytest": (r"\bpytest\b",),
    "pre-commit": (r"^repos:\s*\n",),  # in .pre-commit-config.yaml
}


@dataclass
class CompileIssue:
    file: str
    error: str


def is_ignored(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def list_all_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if is_ignored(p):
            continue
        files.append(p)
    return files


def build_tree(root: Path) -> str:
    """Create a text tree without external tools."""
    lines: list[str] = []

    def walk(dir_path: Path, prefix: str = ""):
        items = [
            p
            for p in sorted(dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            if not is_ignored(p)
        ]
        for i, p in enumerate(items):
            connector = "└── " if i == len(items) - 1 else "├── "
            lines.append(prefix + connector + p.name)
            if p.is_dir():
                ext = "    " if i == len(items) - 1 else "│   "
                walk(p, prefix + ext)

    lines.append(root.name + "/")
    walk(root)
    return "\n".join(lines)


def detect_traits(root: Path) -> dict:
    traits = {
        "python": any(
            (root / name).exists()
            for name in ("pyproject.toml", "requirements.txt", "setup.cfg", "setup.py")
        ),
        "node": (root / "package.json").exists(),
        "docker": (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists(),
        "makefile": (root / "Makefile").exists(),
        "precommit": (root / ".pre-commit-config.yaml").exists(),
        "git_repo": (root / ".git").exists(),
    }
    return traits


def git_quick_status(root: Path) -> dict | None:
    if not (root / ".git").exists():
        return None

    def run(*args: str) -> str | None:
        try:
            out = subprocess.run(args, cwd=root, capture_output=True, text=True, timeout=5)
            return out.stdout.strip() if out.returncode == 0 else None
        except Exception:
            return None

    return {
        "branch": run("git", "rev-parse", "--abbrev-ref", "HEAD"),
        "short_log": run("git", "--no-pager", "log", "-n", "1", "--pretty=%h %s (%cr)"),
        "status": run("git", "status", "-s"),
    }


def scan_frameworks(root: Path) -> dict:
    results = {k: False for k in FRAMEWORK_HINTS}
    for p in root.rglob("*"):
        if is_ignored(p):
            continue
        if p.is_file():
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for fw, patterns in FRAMEWORK_HINTS.items():
                for pat in patterns:
                    if re.search(pat, text, flags=re.MULTILINE):
                        results[fw] = True
            # quick path-based hint for pre-commit
            if p.name == ".pre-commit-config.yaml":
                results["pre-commit"] = True
    return results


def aiogram_installed_version() -> str | None:
    try:
        out = subprocess.run(
            [sys.executable, "-c", "import aiogram; print(aiogram.__version__)"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def ext_stats(files: list[Path]) -> dict:
    c = Counter(f.suffix.lower() if f.is_file() else "(dir)" for f in files)
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def find_entrypoints(root: Path) -> list[str]:
    hits: list[str] = []
    for p in root.rglob("*.py"):
        if is_ignored(p):
            continue
        if p.name in ENTRYPOINT_CANDIDATES:
            hits.append(str(p.relative_to(root)))
        else:
            # look for if __name__ == '__main__'
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if re.search(r"if\s+__name__\s*==\s*['\"]__main__['\"]\s*:", txt):
                hits.append(str(p.relative_to(root)))
    return sorted(set(hits))


def compile_all_py(root: Path) -> tuple[int, list[CompileIssue]]:
    ok = 0
    issues: list[CompileIssue] = []
    for p in root.rglob("*.py"):
        if is_ignored(p):
            continue
        try:
            py_compile.compile(str(p), doraise=True)
            ok += 1
        except Exception as e:
            issues.append(CompileIssue(file=str(p.relative_to(root)), error=repr(e)))
    return ok, issues


def head(path: Path, lines: int = 20) -> str | None:
    try:
        if path.exists():
            txt = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            return "\n".join(txt[:lines])
    except Exception:
        pass
    return None


def main() -> int:
    all_files = list_all_files(ROOT)
    tree_txt = build_tree(ROOT)
    traits = detect_traits(ROOT)
    frameworks = scan_frameworks(ROOT)
    aio_ver = aiogram_installed_version()
    entrypoints = find_entrypoints(ROOT)
    ok_count, issues = compile_all_py(ROOT)
    stats = ext_stats(all_files)
    git_status = git_quick_status(ROOT)

    # collect key file headers (first lines) if present
    key_heads = {}
    for fn in (
        "pyproject.toml",
        "requirements.txt",
        "package.json",
        "Dockerfile",
        "docker-compose.yml",
        "Makefile",
        "README.md",
    ):
        p = ROOT / fn
        h = head(p, 60 if fn in ("pyproject.toml", "requirements.txt") else 30)
        if h:
            key_heads[fn] = h

    data = {
        "root": str(ROOT),
        "python_version": sys.version.replace("\n", " "),
        "counts": {
            "files_total": sum(1 for f in all_files if f.is_file()),
            "dirs_total": sum(1 for f in all_files if f.is_dir()),
        },
        "by_extension": stats,
        "traits": traits,
        "frameworks_detected": {**frameworks, "aiogram_installed_version": aio_ver},
        "entrypoints_guess": entrypoints,
        "compile_summary": {
            "ok_py_files": ok_count,
            "error_files": len(issues),
        },
        "compile_issues": [issue.__dict__ for issue in issues],
        "git": git_status,
        "key_file_headers": key_heads,
    }

    # write artifacts
    (ROOT / "PROJECT_TREE.txt").write_text(tree_txt, encoding="utf-8")
    (ROOT / "INVENTORY.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Markdown report
    md = []
    md.append(f"# Project Inventory — {ROOT.name}\n")
    md.append(f"- Root: `{ROOT}`")
    md.append(f"- Python: `{data['python_version']}`")
    md.append(
        f"- Files: **{data['counts']['files_total']}**, Dirs: **{data['counts']['dirs_total']}**\n"
    )

    md.append("## Traits")
    for k, v in data["traits"].items():
        md.append(f"- {k}: **{v}**")
    md.append("")
    if data["git"]:
        md.append("## Git")
        md.append(f"- Branch: `{data['git']['branch']}`")
        md.append(f"- Last commit: `{data['git']['short_log']}`")
        if data["git"]["status"]:
            md.append("```\n" + data["git"]["status"] + "\n```")
        md.append("")
    md.append("## Frameworks & Tools (detected in files)")
    for k, v in data["frameworks_detected"].items():
        md.append(f"- {k}: **{v}**")
    md.append("")
    md.append("## Likely entry points")
    if data["entrypoints_guess"]:
        for e in data["entrypoints_guess"]:
            md.append(f"- `{e}`")
    else:
        md.append("- (none found)")

    md.append("\n## Python compile (syntax check)")
    md.append(f"- OK files: **{data['compile_summary']['ok_py_files']}**")
    md.append(f"- With errors: **{data['compile_summary']['error_files']}**")
    if data["compile_issues"]:
        md.append("\n### Errors")
        for it in data["compile_issues"]:
            md.append(f"- `{it['file']}` — `{it['error']}`")

    md.append("\n## File type summary")
    for ext, cnt in data["by_extension"].items():
        md.append(f"- `{ext or '(no ext)'}`: {cnt}")

    if data["key_file_headers"]:
        md.append("\n## Key files (first lines)")
        for fn, hdr in data["key_file_headers"].items():
            md.append(f"### {fn}\n```\n{hdr}\n```")

    md.append("\n## Next steps")
    md.append("- Fix any syntax errors listed above (open the file, go to the shown line/column).")
    md.append("- If you expect an aiogram bot, ensure `aiogram==3.*` is installed in your venv.")
    md.append(
        "- If you intend to use GitHub, you can now `git init` and push (ask me for the commands)."
    )

    (ROOT / "INVENTORY.md").write_text("\n".join(md), encoding="utf-8")

    print("Wrote PROJECT_TREE.txt, INVENTORY.json, INVENTORY.md")
    print("Open INVENTORY.md for a readable summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
