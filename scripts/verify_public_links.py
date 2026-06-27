from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class PublicTarget:
    name: str
    url: str
    expected_text: str | None = None


PUBLIC_TARGETS = (
    PublicTarget("Repository", "https://github.com/xinjian0101/novel-workbench", "Novel Workbench"),
    PublicTarget("Pages demo", "https://xinjian0101.github.io/novel-workbench/", "Moon Archive"),
    PublicTarget(
        "Release wheel",
        "https://github.com/xinjian0101/novel-workbench/releases/download/v0.1.1/novel_workbench-0.1.1-py3-none-any.whl",
    ),
    PublicTarget(
        "CI badge",
        "https://github.com/xinjian0101/novel-workbench/actions/workflows/ci.yml/badge.svg",
        "passing",
    ),
    PublicTarget(
        "Pages badge",
        "https://github.com/xinjian0101/novel-workbench/actions/workflows/pages.yml/badge.svg",
        "passing",
    ),
    PublicTarget("Stars badge", "https://img.shields.io/github/stars/xinjian0101/novel-workbench?label=stars", "Stars"),
)


def verify_target(target: PublicTarget, *, timeout: float) -> str:
    request = Request(target.url, headers={"User-Agent": "novel-workbench-link-check"})
    try:
        with urlopen(request, timeout=timeout) as response:
            status = response.status
            content = response.read(256_000)
    except HTTPError as exc:
        raise RuntimeError(f"{target.name}: HTTP {exc.code} for {target.url}") from exc
    except URLError as exc:
        raise RuntimeError(f"{target.name}: unable to reach {target.url}: {exc.reason}") from exc

    if status < 200 or status >= 400:
        raise RuntimeError(f"{target.name}: HTTP {status} for {target.url}")
    if target.expected_text is not None:
        body = content.decode("utf-8", errors="ignore").lower()
        if target.expected_text.lower() not in body:
            raise RuntimeError(f"{target.name}: expected text not found: {target.expected_text}")
    return f"OK {target.name}: HTTP {status}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify public launch links for Novel Workbench.")
    parser.add_argument("--offline", action="store_true", help="List checked URLs without network requests.")
    parser.add_argument("--timeout", type=float, default=15.0, help="Per-request timeout in seconds.")
    args = parser.parse_args(argv)

    if args.offline:
        for target in PUBLIC_TARGETS:
            print(f"CHECK {target.name}: {target.url}")
        return 0

    failures: list[str] = []
    for target in PUBLIC_TARGETS:
        try:
            print(verify_target(target, timeout=args.timeout))
        except RuntimeError as exc:
            failures.append(str(exc))
            print(f"FAIL {exc}")
    if failures:
        print(f"Public link verification failed: {len(failures)} issue(s).", file=sys.stderr)
        return 1
    print("Public link verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
