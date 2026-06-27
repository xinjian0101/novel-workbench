# Release Template

## Version

`vX.Y.Z`

## Summary

One or two sentences explaining why this release matters.

## Highlights

- 
- 
- 

## Verification

```powershell
python scripts/check.py
python scripts/release_check.py
```

Expected local result:

- `python scripts/check.py` reports `All checks passed.`
- `python scripts/release_check.py` reports `Release package check passed.`

GitHub Actions:

- CI passed
- Release workflow passed on Linux, macOS, and Windows

## Upgrade Notes

- 

## Known Limitations

- 
