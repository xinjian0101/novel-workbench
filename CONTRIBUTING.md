# Contributing

Thanks for improving Novel Workbench. Keep contributions focused and easy to review.

First-time contributors can use [docs/FIRST_PR.md](docs/FIRST_PR.md) for a concrete issue-to-PR workflow.
Maintainer review and release gates are documented in [docs/MAINTAINER_GUIDE.md](docs/MAINTAINER_GUIDE.md).

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Before Opening a Pull Request

Run:

```powershell
python scripts/check.py
```

## Contribution Guidelines

- Keep the local-first model intact.
- Do not add network calls, telemetry, or cloud dependencies without a design discussion.
- Include tests for user-visible behavior.
- Update README or command help when CLI behavior changes.
- Prefer small, reviewable pull requests over broad rewrites.

## Commit Scope

Good first contributions include:

- command help improvements
- import/export formats
- progress reporting
- validation and error messages
- tests for edge cases
- documentation examples

Current contributor entry points are listed in [docs/COMMUNITY.md](docs/COMMUNITY.md).
