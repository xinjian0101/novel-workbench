# PyPI Publishing

Novel Workbench is already packaged as a Python source distribution and wheel. This page documents the path from the verified local package build to a public package index release.

Publishing to PyPI requires maintainer account access and should not be automated from a local checkout without explicit release approval.

## Package Identity

- Package name: `novel-workbench`
- Import package: `novel_workbench`
- Console command: `novel`
- Current version source: `pyproject.toml`
- License: MIT
- Python support: 3.10+

## Release Preconditions

Run these checks before publishing:

```powershell
python scripts/check.py
python scripts/release_check.py
```

Confirm:

- The working tree is clean.
- `CHANGELOG.md` has release notes for the version.
- `docs/RELEASE_TEMPLATE.md` has the release summary.
- `README.md` install instructions are current.
- The GitHub `CI`, `Release`, and `Pages` workflows are green for the release tag.

## Build Artifacts

The release check builds:

- `dist/novel_workbench-0.1.0.tar.gz`
- `dist/novel_workbench-0.1.0-py3-none-any.whl`

The wheel is installed into a temporary virtual environment without reaching package indexes. The smoke test runs:

```powershell
novel --version
novel --workspace <temp> sample
novel --workspace <temp> stats moon-archive
novel --workspace <temp> export moon-archive <temp>\exports\moon-archive.md
```

## TestPyPI Dry Run

Use TestPyPI first when validating credentials and metadata:

```powershell
python -m pip install --upgrade twine
python -m twine check dist/*
python -m twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps novel-workbench
novel --version
```

## PyPI Release

After the dry run succeeds and release approval is complete:

```powershell
python -m twine check dist/*
python -m twine upload dist/*
python -m pip install --upgrade novel-workbench
novel --version
```

## Post-Release Updates

After the first PyPI release:

- Add the PyPI install command to `README.md`.
- Add the PyPI package URL to `pyproject.toml` project URLs.
- Add PyPI to `docs/DISTRIBUTION.md` canonical links.
- Verify the package page renders README content correctly.
- Keep the GitHub install command as a source install fallback.

## Manual Controls

PyPI publishing requires:

- A maintainer-owned PyPI account.
- Trusted publishing or an API token configured outside the repository.
- A release approval decision for the version.
- A final check that no private workspaces, manuscripts, exports, or secrets are included in the artifact.
