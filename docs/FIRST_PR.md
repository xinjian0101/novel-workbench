# First Pull Request Guide

Use this guide when making a first contribution to Novel Workbench.

## Choose a Small Issue

Start with one of the current contributor entry points:

- [#9 Add editor workflow recipes](https://github.com/xinjian0101/novel-workbench/issues/9)
- [#8 Design a local editor handoff workflow](https://github.com/xinjian0101/novel-workbench/issues/8)

Good first PRs usually touch one document, one command, or one tightly scoped test area.

## Local Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Before Editing

Run the current quality gate:

```powershell
python scripts/check.py
```

If it fails before your changes, mention that in the issue or PR before mixing unrelated fixes into the same branch.

## Make a Focused Change

- Keep manuscript data local and user-controlled.
- Do not add account requirements, telemetry, background network calls, or cloud services.
- Avoid committing `workspace/`, `exports/`, `backups/`, `.env`, private drafts, or generated local test output.
- Update docs when command behavior or visible output changes.
- Add or update tests when behavior changes.

## Verify

Run:

```powershell
python scripts/check.py
```

For narrow docs-only changes, this still matters because the launch audit and package smoke test protect the public repository surface.

## Open the Pull Request

Include:

- The issue number, for example `Closes #9`.
- A short summary of what changed.
- The exact verification command you ran.
- Notes about any intentionally deferred follow-up.

Keep the PR small enough that a reviewer can understand it without reconstructing unrelated context.
