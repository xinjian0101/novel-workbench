from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REPOSITORY = "xinjian0101/novel-workbench"
API_URL = f"https://api.github.com/repos/{REPOSITORY}"
LATEST_RELEASE_API_URL = f"{API_URL}/releases/latest"
EXPECTED_DESCRIPTION_TEXT = ("local-first", "cli", "writing", "novels")
EXPECTED_HOMEPAGE = "https://xinjian0101.github.io/novel-workbench/"
EXPECTED_TOPICS = {
    "author-tools",
    "cli",
    "creative-writing",
    "fiction",
    "local-first",
    "markdown",
    "novel",
    "novel-writing",
    "python",
    "static-site",
    "writing",
    "writing-tools",
}
EXPECTED_RELEASE = "v0.1.1"


def fetch_json(url: str, *, timeout: float) -> dict[str, object]:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "novel-workbench-metadata-check",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            content = response.read(256_000)
    except HTTPError as exc:
        raise RuntimeError(f"GitHub metadata: HTTP {exc.code} for {url}") from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub metadata: unable to reach {url}: {exc.reason}") from exc
    return json.loads(content.decode("utf-8"))


def fetch_repo_metadata(*, timeout: float) -> dict[str, object]:
    metadata = fetch_json(API_URL, timeout=timeout)
    metadata["latest_release"] = fetch_json(LATEST_RELEASE_API_URL, timeout=timeout)
    return metadata


def check_metadata(metadata: dict[str, object], *, min_stars: int = 0) -> tuple[bool, list[str]]:
    messages: list[str] = []
    ok = True

    if metadata.get("private") is False:
        messages.append("OK visibility: repository is public")
    else:
        messages.append("FAIL visibility: repository is not public")
        ok = False

    description = str(metadata.get("description") or "")
    description_lower = description.lower()
    missing_description = [text for text in EXPECTED_DESCRIPTION_TEXT if text not in description_lower]
    if missing_description:
        messages.append(f"FAIL description: missing {', '.join(missing_description)}")
        ok = False
    else:
        messages.append("OK description: includes local-first CLI writing position")

    homepage = str(metadata.get("homepage") or "")
    if homepage == EXPECTED_HOMEPAGE:
        messages.append(f"OK homepage: {homepage}")
    else:
        messages.append(f"FAIL homepage: expected {EXPECTED_HOMEPAGE}, found {homepage or '<empty>'}")
        ok = False

    topics = {str(topic) for topic in metadata.get("topics", [])}
    missing_topics = sorted(EXPECTED_TOPICS - topics)
    if missing_topics:
        messages.append(f"FAIL topics: missing {', '.join(missing_topics)}")
        ok = False
    else:
        messages.append("OK topics: discovery topics are present")

    latest_release = metadata.get("latest_release")
    if isinstance(latest_release, dict) and latest_release.get("tag_name") == EXPECTED_RELEASE:
        messages.append(f"OK latest release: {EXPECTED_RELEASE}")
    else:
        messages.append(f"FAIL latest release: expected {EXPECTED_RELEASE}")
        ok = False

    stars = int(metadata.get("stargazers_count") or 0)
    if min_stars and stars < min_stars:
        messages.append(f"FAIL stars: expected at least {min_stars}, found {stars}")
        ok = False
    else:
        messages.append(f"OK stars: {stars}")

    return ok, messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify public GitHub metadata for Novel Workbench.")
    parser.add_argument("--offline", action="store_true", help="Print expected metadata without calling GitHub.")
    parser.add_argument("--min-stars", type=int, default=0, help="Fail unless GitHub reports at least this count.")
    parser.add_argument("--timeout", type=float, default=15.0, help="GitHub API request timeout in seconds.")
    args = parser.parse_args(argv)

    if args.offline:
        print(f"CHECK Repository: {REPOSITORY}")
        print(f"CHECK Homepage: {EXPECTED_HOMEPAGE}")
        print(f"CHECK Latest release: {EXPECTED_RELEASE}")
        print("CHECK Topics: " + ", ".join(sorted(EXPECTED_TOPICS)))
        return 0

    try:
        metadata = fetch_repo_metadata(timeout=args.timeout)
        ok, messages = check_metadata(metadata, min_stars=args.min_stars)
    except RuntimeError as exc:
        print(f"FAIL {exc}")
        return 1

    for message in messages:
        print(message)
    if not ok:
        print("GitHub metadata verification failed.", file=sys.stderr)
        return 1
    print("GitHub metadata verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
