from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run(command: list[str], cwd: Path, *, env: dict[str, str] | None = None) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True, env=env)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    release_tmp_root = root / "runtime" / "release-temp"
    for relative in ["build", "dist", "src/novel_workbench.egg-info"]:
        target = root / relative
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
    if release_tmp_root.exists():
        shutil.rmtree(release_tmp_root, ignore_errors=True)
    release_tmp_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env["TMP"] = str(release_tmp_root)
    env["TEMP"] = str(release_tmp_root)
    run([sys.executable, "-m", "build", "--no-isolation"], root, env=env)

    wheels = sorted(dist_dir.glob("novel_workbench-*.whl"))
    sdists = sorted(dist_dir.glob("novel_workbench-*.tar.gz"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected one wheel, found {len(wheels)}.")
    if len(sdists) != 1:
        raise RuntimeError(f"Expected one source distribution, found {len(sdists)}.")

    with tempfile.TemporaryDirectory(prefix="novel-workbench-release-", dir=release_tmp_root) as tmp:
        tmp_path = Path(tmp)
        venv_dir = tmp_path / "venv"
        workspace = tmp_path / "workspace"
        exports = tmp_path / "exports"
        tour_exports = tmp_path / "tour-exports"
        old_tmp = os.environ.get("TMP")
        old_temp = os.environ.get("TEMP")
        try:
            os.environ["TMP"] = str(release_tmp_root)
            os.environ["TEMP"] = str(release_tmp_root)
            venv.EnvBuilder(with_pip=True).create(venv_dir)
            python = _venv_python(venv_dir)
            run([str(python), "-m", "pip", "install", "--no-index", str(wheels[0])], root, env=env)
            run([str(python), "-m", "novel_workbench.cli", "--version"], root, env=env)
            run([str(python), "-m", "novel_workbench.cli", "--workspace", str(workspace), "sample"], root, env=env)
            run([str(python), "-m", "novel_workbench.cli", "--workspace", str(workspace), "stats", "moon-archive"], root, env=env)
            run(
                [
                    str(python),
                    "-m",
                    "novel_workbench.cli",
                    "--workspace",
                    str(workspace),
                    "export",
                    "moon-archive",
                    str(exports / "moon-archive.md"),
                ],
                root,
                env=env,
            )
            if not (exports / "moon-archive.md").exists():
                raise RuntimeError("Installed wheel did not export the sample manuscript.")
            run(
                [
                    str(python),
                    "-m",
                    "novel_workbench.cli",
                    "--workspace",
                    str(workspace),
                    "tour",
                    "--output-dir",
                    str(tour_exports),
                ],
                root,
                env=env,
            )
            if not (tour_exports / "moon-archive" / "site" / "index.html").exists():
                raise RuntimeError("Installed wheel did not run the one-command tour.")
        finally:
            _restore_env("TMP", old_tmp)
            _restore_env("TEMP", old_temp)

    print("Release package check passed.")
    return 0


def _venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _restore_env(name: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


if __name__ == "__main__":
    raise SystemExit(main())
