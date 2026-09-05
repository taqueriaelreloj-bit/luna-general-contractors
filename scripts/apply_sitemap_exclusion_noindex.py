#!/usr/bin/env python3
"""Apply noindex controls declared by seo/sitemap-exclusions.csv.

Only hold-template-family and hold-low-content pages are changed. The script is
idempotent and removes those URLs from sitemap.xml if a generator adds them.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "seo" / "sitemap-exclusions.csv"
SITEMAP = ROOT / "sitemap.xml"
DOMAIN = "https://lunageneralcontractors.com"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
HELD = {"hold-template-family", "hold-low-content"}
ROBOTS_RE = re.compile(r"""<meta\b[^>]*\bname=["']robots["'][^>]*>""", re.I)
NOINDEX_TAG = '<meta name="robots" content="noindex, follow">'


def held_pages() -> set[str]:
    with INVENTORY.open(newline="", encoding="utf-8") as handle:
        return {
            row["path"].strip()
            for row in csv.DictReader(handle)
            if row["classification"].strip() in HELD
        }


def apply_noindex(relative: str) -> bool:
    path = ROOT / relative
    if not path.exists():
        raise SystemExit(f"Missing held page: {relative}")
    source = path.read_text(encoding="utf-8")
    matches = list(ROBOTS_RE.finditer(source))
    if len(matches) != 1:
        raise SystemExit(f"{relative}: expected one robots meta tag, found {len(matches)}")
    current = matches[0].group(0)
    if "noindex" in current.lower():
        return False
    updated = source[: matches[0].start()] + NOINDEX_TAG + source[matches[0].end() :]
    path.write_text(updated, encoding="utf-8")
    return True


def remove_from_sitemap(targets: set[str]) -> int:
    ET.register_namespace("", SITEMAP_NS)
    document = ET.parse(SITEMAP)
    root = document.getroot()
    removed = 0
    for url_node in list(root):
        loc = next(
            (child for child in url_node if child.tag.rsplit("}", 1)[-1] == "loc"),
            None,
        )
        if loc is None or not loc.text:
            continue
        parsed = urlparse(loc.text.strip())
        if parsed.netloc != urlparse(DOMAIN).netloc:
            continue
        relative = unquote(parsed.path).lstrip("/") or "index.html"
        if relative in targets:
            root.remove(url_node)
            removed += 1
    if removed:
        document.write(SITEMAP, encoding="utf-8", xml_declaration=True)
    return removed


def main() -> None:
    targets = held_pages()
    changed = sum(apply_noindex(relative) for relative in sorted(targets))
    removed = remove_from_sitemap(targets)
    print(
        f"Enforced noindex, follow on {len(targets)} held pages "
        f"({changed} HTML updates; {removed} sitemap removals)."
    )


if __name__ == "__main__":
    main()
