#!/usr/bin/env python3
"""Build a MikroTik RouterOS-compatible hosts adlist from anti-AD."""

from __future__ import annotations

import argparse
import re
import sys
import time
from http.client import IncompleteRead
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_SOURCE = "https://anti-ad.net/domains.txt"
DEFAULT_OUTPUT = "adlist.txt"
DEFAULT_MIN_DOMAINS = 50_000
USER_AGENT = (
    "zzpice/routeros-adlist "
    "(+https://github.com/zzpice/routeros-adlist)"
)

_LABEL_RE = re.compile(r"^[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?$", re.IGNORECASE)


def download(url: str, retries: int = 3, timeout: int = 30) -> str:
    """Download UTF-8 text with a small retry budget and explicit User-Agent."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", 200)
                if status != 200:
                    raise RuntimeError(f"unexpected HTTP status: {status}")
                content_type = response.headers.get_content_type()
                if content_type not in {"text/plain", "application/octet-stream"}:
                    raise RuntimeError(f"unexpected content type: {content_type}")
                return response.read().decode("utf-8")
        except (OSError, IncompleteRead, UnicodeDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(attempt * 2)
    raise RuntimeError(f"failed to download {url}: {last_error}")


def normalize_domain(raw: str) -> str | None:
    """Return a normalized domain, or None when the line is not a valid domain."""
    domain = raw.strip().lower().rstrip(".")
    if not domain or len(domain) > 253 or "." not in domain:
        return None

    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        return None

    labels = domain.split(".")
    if any(len(label) > 63 or not _LABEL_RE.fullmatch(label) for label in labels):
        return None
    return domain


def parse_domains(text: str) -> tuple[list[str], int]:
    """Parse anti-AD's one-domain-per-line format and report rejected data lines."""
    domains: set[str] = set()
    rejected = 0

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        domain = normalize_domain(line)
        if domain is None:
            rejected += 1
            continue
        domains.add(domain)

    return sorted(domains), rejected


def build(source_url: str, output: Path, min_domains: int) -> int:
    text = download(source_url)
    domains, rejected = parse_domains(text)

    if len(domains) < min_domains:
        raise RuntimeError(
            f"validation failed: only {len(domains):,} valid domains "
            f"(minimum {min_domains:,}); rejected {rejected:,} lines"
        )

    if rejected > max(100, len(domains) // 100):
        raise RuntimeError(
            f"validation failed: rejected {rejected:,} data lines out of "
            f"{len(domains) + rejected:,}"
        )

    content = "".join(f"0.0.0.0 {domain}\n" for domain in domains)
    output.write_text(content, encoding="utf-8", newline="\n")
    print(f"Wrote {len(domains):,} domains to {output}; rejected {rejected:,} lines.")
    return len(domains)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert anti-AD's domain list to a RouterOS-compatible hosts adlist."
    )
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="source URL")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="output file")
    parser.add_argument(
        "--min-domains",
        type=int,
        default=DEFAULT_MIN_DOMAINS,
        help="fail when fewer valid domains are found",
    )
    args = parser.parse_args()

    try:
        build(args.source, Path(args.output), args.min_domains)
    except (OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
