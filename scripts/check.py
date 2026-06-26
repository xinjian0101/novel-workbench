from __future__ import annotations

import shutil
import subprocess
import sys
import os
from pathlib import Path

SCAN_PATTERNS = [
    "TODO",
    "FIXME",
    "HACK",
    "XXX",
    "NotImplemented",
    "throw new Error",
    "console.log",
    "debugger",
    "mock",
    "placeholder",
    "hardcoded",
    "example/novel-workbench",
]

EXCLUDED_DIRS = {".git", ".pytest_cache", "__pycache__", "build", "dist"}
EXCLUDED_SUFFIXES = {".egg-info"}


def run(command: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}")
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    subprocess.run(command, cwd=cwd, check=True, env=env)


def scan_for_debug_markers(root: Path) -> None:
    matches: list[str] = []
    for path in root.rglob("*"):
        if path == Path(__file__).resolve():
            continue
        if not path.is_file() or _is_excluded(path, root):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern in line for pattern in SCAN_PATTERNS):
                matches.append(f"{path.relative_to(root)}:{line_number}: {line.strip()}")
    if matches:
        raise RuntimeError("Debug or launch-blocking markers found:\n" + "\n".join(matches))


def clean_generated(root: Path) -> None:
    for relative in ["build", "dist", ".pytest_cache", "src/novel_workbench.egg-info"]:
        target = root / relative
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
    for target in root.rglob("__pycache__"):
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    run([sys.executable, "-m", "pytest"], root)
    run([sys.executable, "-m", "compileall", "src", "tests", "scripts"], root)
    run([sys.executable, "scripts/demo.py"], root)
    run([sys.executable, "-m", "build", "--no-isolation"], root)
    scan_for_debug_markers(root)
    clean_generated(root)
    print("All checks passed.")
    return 0


def _is_excluded(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    if any(part in EXCLUDED_DIRS for part in relative_parts):
        return True
    return any(part.endswith(suffix) for part in relative_parts for suffix in EXCLUDED_SUFFIXES)


if __name__ == "__main__":
    raise SystemExit(main())
