# Manual Actions

No external platform setup is required for local development, testing, or package builds.

## Required Before Public GitHub Launch

1. Item name: create the public GitHub repository and set repository metadata.
2. Why manual: repository ownership, visibility, topics, social preview, and remote URL require account-level access.
3. Platform: GitHub.
4. Action path: create repository, push this worktree, enable Actions, add topics from `docs/GITHUB_LAUNCH.md`, and prepare the first release.
5. Fields: repository name, description, topics, website URL if any, social preview image if any.
6. Field sources: `README.md`, `pyproject.toml`, and project branding decisions.
7. Verification: repository page renders README, Actions runs the CI workflow, and issue templates appear when creating a new issue.
8. Risks and notes: confirm `workspace/`, `exports/`, `.env`, and manuscript files are not committed.
9. Blocking status: blocks public launch, but not local development or tests.

## Optional: Internal Package Distribution

1. Item name: publish a built wheel to an internal package registry.
2. Why manual: registry choice, credentials, and release approval depend on the organization.
3. Platform: the organization's package registry or artifact store.
4. Action path: create a package/project if needed, then upload the wheel from `dist/`.
5. Fields: package name, version, release notes, access permissions.
6. Field sources: `pyproject.toml`, `README.md`, and the generated files in `dist/`.
7. Verification: install the uploaded wheel in a clean Python 3.10+ environment and run `novel --version`.
8. Risks and notes: do not upload drafts from `workspace/` or exported manuscripts from `exports/`.
9. Blocking status: not blocking local development, tests, or local builds.

## Optional: Public PyPI Release

1. Item name: publish `novel-workbench` to PyPI.
2. Why manual: PyPI account ownership, trusted publishing setup, API credentials, and release approval require maintainer-controlled access outside the repository.
3. Platform: PyPI and optionally TestPyPI.
4. Action path: run `python scripts/check.py`, run `python scripts/release_check.py`, validate artifacts with `twine check`, upload to TestPyPI, verify install, then upload the approved release to PyPI.
5. Fields: package name, version, release notes, project URLs, maintainer account, trusted publisher or API token.
6. Field sources: `pyproject.toml`, `CHANGELOG.md`, `docs/RELEASE_TEMPLATE.md`, and `docs/PYPI_PUBLISHING.md`.
7. Verification: install `novel-workbench` in a clean Python 3.10+ environment, run `novel --version`, create a sample project, and export a manuscript.
8. Risks and notes: never commit PyPI credentials; confirm no local workspaces, manuscripts, exports, or secrets are included in release artifacts.
9. Blocking status: not blocking local development, tests, GitHub Pages, or GitHub source installs; blocks claiming PyPI install support in README.
