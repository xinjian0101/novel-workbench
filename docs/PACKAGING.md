# Packaging and Releases

Novel Workbench ships as a standard Python source distribution and wheel.

## Local Package Check

Run the full project check:

```powershell
python scripts/check.py
```

Run only the packaging smoke test:

```powershell
python scripts/release_check.py
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

## Pages Demo

The `Pages` workflow builds a static demo site with:

```powershell
python scripts/build_pages_demo.py public
```

It uploads the generated `public/` directory as a GitHub Pages artifact. The site contains `index.html`, `manuscript.html`, and `context.json`, matching the user-facing `novel export-site` output.
