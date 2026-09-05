#!/usr/bin/env python3
"""Verify sitemap exclusions and the required index-control state."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
CLASSIFICATIONS = ROOT / "seo" / "sitemap-exclusions.csv"
ALLOWED = {
    "ready-for-sitemap",
    "enrich-then-index",
    "hold-low-content",
    "hold-template-family",
    "exclude-preview",
}
HELD = {"hold-low-content", "hold-template-family"}
ROBOTS_RE = re.compile(r"""<meta\b[^>]*\bname=["']robots["'][^>]*>""", re.I)
CONTENT_RE = re.compile(r"""\bcontent=["']([^"']*)["']""", re.I)


def sitemap_paths() -> set[str]:
    document = ET.parse(SITEMAP)
    paths: set[str] = set()
    for element in document.getroot().iter():
        if element.tag.rsplit("}", 1)[-1] != "loc" or not element.text:
            continue
        path = unquote(urlparse(element.text.strip()).path).lstrip("/")
        paths.add(path or "index.html")
    return paths


def classified_rows() -> tuple[dict[str, str], Counter[str]]:
    with CLASSIFICATIONS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    paths = [row["path"].strip() for row in rows]
    duplicates = sorted(path for path, count in Counter(paths).items() if count > 1)
    if duplicates:
        raise SystemExit(f"Duplicate classification rows: {duplicates}")

    invalid = sorted({row["classification"].strip() for row in rows} - ALLOWED)
    if invalid:
        raise SystemExit(f"Unknown classifications: {invalid}")

    classifications = {
        row["path"].strip(): row["classification"].strip() for row in rows
    }
    return classifications, Counter(classifications.values())


def robots_directives(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    matches = ROBOTS_RE.findall(source)
    if len(matches) != 1:
        raise SystemExit(f"{path.name}: expected one robots meta tag, found {len(matches)}")
    content = CONTENT_RE.search(matches[0])
    if not content:
        raise SystemExit(f"{path.name}: robots meta tag has no content")
    return {item.strip().lower() for item in content.group(1).split(",") if item.strip()}


def main() -> None:
    indexed = sitemap_paths()
    root_html = {path.name for path in ROOT.glob("*.html")}
    omitted = root_html - indexed
    classifications, counts = classified_rows()
    classified = set(classifications)

    missing = sorted(omitted - classified)
    stale = sorted(classified - omitted)
    if missing or stale:
        if missing:
            print("Missing classifications:")
            print("\n".join(f"  - {path}" for path in missing))
        if stale:
            print("Stale classifications (page removed or now indexed):")
            print("\n".join(f"  - {path}" for path in stale))
        raise SystemExit(1)

    held = {path for path, label in classifications.items() if label in HELD}
    missing_noindex = sorted(
        path for path in held if "noindex" not in robots_directives(ROOT / path)
    )
    if missing_noindex:
        print("Held pages missing noindex:")
        print("\n".join(f"  - {path}" for path in missing_noindex[:50]))
        raise SystemExit(1)

    held_in_sitemap = sorted(held & indexed)
    if held_in_sitemap:
        print("Held pages unexpectedly present in sitemap:")
        print("\n".join(f"  - {path}" for path in held_in_sitemap[:50]))
        raise SystemExit(1)

    print(f"Validated {len(classified)} sitemap exclusions.")
    for name in sorted(counts):
        print(f"  {name}: {counts[name]}")
    print(f"  noindex enforced: {len(held)}")


if __name__ == "__main__":
    main()
