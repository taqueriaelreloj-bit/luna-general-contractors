#!/usr/bin/env python3
"""Update sitemap lastmod only for pages with meaningful repository changes."""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse


URL_BLOCK_RE = re.compile(r"<url>.*?</url>", re.S)
LOC_RE = re.compile(r"<loc>(.*?)</loc>", re.S)
LASTMOD_RE = re.compile(r"<lastmod>.*?</lastmod>", re.S)


def changed_html_files(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", "*.html"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return {
        line.strip().lstrip("./")
        for line in result.stdout.splitlines()
        if line.strip().endswith(".html")
    }


def url_to_file(url: str) -> str:
    path = unquote(urlparse(url.strip()).path).lstrip("/")
    return path or "index.html"


def update_sitemap(sitemap: Path, changed: set[str], stamp: str) -> int:
    source = sitemap.read_text(encoding="utf-8")
    updated_count = 0

    def replace_block(match: re.Match[str]) -> str:
        nonlocal updated_count
        block = match.group(0)
        loc_match = LOC_RE.search(block)
        if not loc_match or url_to_file(loc_match.group(1)) not in changed:
            return block
        replacement = f"<lastmod>{stamp}</lastmod>"
        if LASTMOD_RE.search(block):
            revised = LASTMOD_RE.sub(replacement, block, count=1)
        else:
            revised = block.replace("</loc>", f"</loc>{replacement}", 1)
        if revised != block:
            updated_count += 1
        return revised

    revised = URL_BLOCK_RE.sub(replace_block, source)
    if revised != source:
        sitemap.write_text(revised, encoding="utf-8")
    return updated_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--sitemap", default="sitemap.xml")
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()

    root = args.root.resolve()
    changed = changed_html_files(root)
    count = update_sitemap(root / args.sitemap, changed, args.date)
    print(f"Meaningfully changed HTML pages: {len(changed)}")
    print(f"Sitemap lastmod entries updated: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
