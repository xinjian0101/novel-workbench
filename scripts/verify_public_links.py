from __future__ import annotations

import argparse
import html
import re
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
    PublicTarget("Pages RSS feed", "https://xinjian0101.github.io/novel-workbench/feed.xml", "Moon Archive - Novel Workbench"),
    PublicTarget("Pages LLM guide", "https://xinjian0101.github.io/novel-workbench/llms.txt", "Context JSON"),
    PublicTarget("Pages web manifest", "https://xinjian0101.github.io/novel-workbench/site.webmanifest", "Moon Archive - Novel Workbench"),
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


def parse_stars_badge(svg: str) -> int:
    values = [html.unescape(match) for match in re.findall(r"<text[^>]*>([^<]+)</text>", svg)]
    for value in reversed(values):
        normalized = value.strip().lower().replace(",", "")
        multiplier = 1
        if normalized.endswith("k"):
            multiplier = 1000
            normalized = normalized[:-1]
        if normalized.endswith("m"):
            multiplier = 1_000_000
            normalized = normalized[:-1]
        try:
            return int(float(normalized) * multiplier)
        except ValueError:
            continue
    raise RuntimeError("Stars badge: unable to parse star count")


def verify_target(target: PublicTarget, *, timeout: float) -> tuple[str, int | None]:
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
    text = content.decode("utf-8", errors="ignore")
    if target.expected_text is not None:
        body = text.lower()
        if target.expected_text.lower() not in body:
            raise RuntimeError(f"{target.name}: expected text not found: {target.expected_text}")
    if target.name == "Stars badge":
        stars = parse_stars_badge(text)
        return f"OK {target.name}: HTTP {status} (stars: {stars})", stars
    return f"OK {target.name}: HTTP {status}", None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify public launch links for Novel Workbench.")
    parser.add_argument("--offline", action="store_true", help="List checked URLs without network requests.")
    parser.add_argument("--min-stars", type=int, default=0, help="Fail unless the stars badge reports at least this count.")
    parser.add_argument("--timeout", type=float, default=15.0, help="Per-request timeout in seconds.")
    args = parser.parse_args(argv)

    if args.offline:
        for target in PUBLIC_TARGETS:
            print(f"CHECK {target.name}: {target.url}")
        return 0

    failures: list[str] = []
    stars_count: int | None = None
    for target in PUBLIC_TARGETS:
        try:
            message, stars = verify_target(target, timeout=args.timeout)
            print(message)
            if stars is not None:
                stars_count = stars
        except RuntimeError as exc:
            failures.append(str(exc))
            print(f"FAIL {exc}")
    if args.min_stars and (stars_count is None or stars_count < args.min_stars):
        failures.append(f"Stars badge: expected at least {args.min_stars}, found {stars_count}")
        print(f"FAIL Stars badge: expected at least {args.min_stars}, found {stars_count}")
    if failures:
        print(f"Public link verification failed: {len(failures)} issue(s).", file=sys.stderr)
        return 1
    print("Public link verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
