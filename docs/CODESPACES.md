# Codespaces Quick Start

Use GitHub Codespaces when you want to try Novel Workbench or prepare a first pull request without configuring Python locally.

## Start

1. Open the repository on GitHub.
2. Choose **Code**.
3. Choose **Codespaces**.
4. Create a codespace on `master`.

The dev container installs the editable package with development dependencies:

```bash
python -m pip install -e '.[dev]'
```

## Try the CLI

Run the same tour shown in the README:

```bash
novel --workspace workspace tour --output-dir exports
```

Inspect the generated files:

```bash
ls exports/moon-archive
ls exports/moon-archive/site
```

## Verify a Change

Run the repository quality gate before opening a pull request:

```bash
python scripts/check.py
```

For a faster first smoke test while exploring:

```bash
python -m pytest -q
python scripts/launch_audit.py
```

## Data Safety

- Do not commit generated `workspace/`, `exports/`, `backups/`, `.env`, or private manuscript files.
- Codespaces is optional. The project still runs locally and offline after installation.
- Keep pull requests focused on one issue, one command, or one documentation surface.
