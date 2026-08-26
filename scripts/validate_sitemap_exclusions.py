#!/usr/bin/env python3
"""Verify that every root HTML page outside sitemap.xml has one classification."""

from __future__ import annotations

import csv
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


def sitemap_paths() -> set[str]:
    document = ET.parse(SITEMAP)
    paths: set[str] = set()
    for element in document.getroot().iter():
        if element.tag.rsplit("}", 1)[-1] != "loc" or not element.text:
            continue
        path = unquote(urlparse(element.text.strip()).path).lstrip("/")
        paths.add(path or "index.html")
    return paths


def classified_paths() -> tuple[set[str], Counter[str]]:
    with CLASSIFICATIONS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    paths = [row["path"].strip() for row in rows]
    duplicates = sorted(path for path, count in Counter(paths).items() if count > 1)
    if duplicates:
        raise SystemExit(f"Duplicate classification rows: {duplicates}")

    invalid = sorted({row["classification"] for row in rows} - ALLOWED)
    if invalid:
        raise SystemExit(f"Unknown classifications: {invalid}")

    return set(paths), Counter(row["classification"] for row in rows)


def main() -> None:
    indexed = sitemap_paths()
    root_html = {path.name for path in ROOT.glob("*.html")}
    omitted = root_html - indexed
    classified, counts = classified_paths()

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

    print(f"Validated {len(classified)} sitemap exclusions.")
    for name in sorted(counts):
        print(f"  {name}: {counts[name]}")


if __name__ == "__main__":
    main()
