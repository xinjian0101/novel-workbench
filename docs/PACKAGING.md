# Packaging and Releases

Novel Workbench ships as a standard Python source distribution and wheel.

PyPI release preparation lives in [docs/PYPI_PUBLISHING.md](docs/PYPI_PUBLISHING.md). That page separates verified local package checks from account-controlled publishing steps.

The current GitHub Release is [v0.1.1](https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1), with both the wheel and source distribution attached.

## Local Package Check

Run the full project check:

```powershell
python scripts/check.py
```

Run only the packaging smoke test:

```powershell
python scripts/release_check.py
```

Run the launch readiness audit:

```powershell
python scripts/launch_audit.py
```

The release check builds `dist/`, creates a temporary virtual environment, installs the wheel without reaching package indexes, then runs the installed CLI against a sample workspace.

## GitHub Release Flow

1. Confirm the working tree is clean.
2. Run:

   ```powershell
   python scripts/check.py
   ```

3. Create and push a semantic version tag:

   ```powershell
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

4. GitHub Actions runs the `Release` workflow on Linux, macOS, and Windows.
5. When the tag starts with `v`, the workflow creates or updates a GitHub Release and uploads the source distribution and wheel.

## Artifact Expectations

The release workflow produces:

- `novel_workbench-X.Y.Z.tar.gz`
- `novel_workbench-X.Y.Z-py3-none-any.whl`

Because Novel Workbench has no runtime dependencies, the wheel install smoke test uses `pip --no-index` to prove the artifact can install offline.

For the published `v0.1.1` release, users can install the wheel directly:

```powershell
python -m pip install "https://github.com/xinjian0101/novel-workbench/releases/download/v0.1.1/novel_workbench-0.1.1-py3-none-any.whl"
```

## Package Index Publishing

Do not publish to PyPI from an unreviewed local checkout. Use the verified artifacts from `python scripts/release_check.py`, then follow [docs/PYPI_PUBLISHING.md](docs/PYPI_PUBLISHING.md) for TestPyPI, PyPI, and post-release README updates.

## Pages Demo

The `Pages` workflow builds a static demo site with:

```powershell
python scripts/build_pages_demo.py public
```

It uploads the generated `public/` directory as a GitHub Pages artifact. The site contains `index.html`, `manuscript.html`, `context.json`, `social-card.svg`, `sitemap.xml`, `robots.txt`, `feed.xml`, `llms.txt`, and `site.webmanifest`, matching the user-facing `novel export-site --base-url` output.
