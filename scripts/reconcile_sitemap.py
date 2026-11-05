#!/usr/bin/env python3
"""Check or apply full canonical-page sitemap coverage without rebuilding content."""

from __future__ import annotations

import argparse
import csv
from html.parser import HTMLParser
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lunageneralcontractors.com"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ROBOTS_RE = re.compile(r'''<meta\b[^>]*\bname=["']robots["'][^>]*>''', re.I)
INDEX_TAG = '<meta name="robots" content="index, follow, max-image-preview:large">'


class Metadata(HTMLParser):
    def __init__(self, source: str):
        super().__init__()
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "link" and values.get("rel", "").lower() == "canonical":
            self.canonicals.append(values.get("href", ""))
        if tag == "meta" and values.get("name", "").lower() == "robots":
            self.robots.append(values.get("content", ""))


def page_url(filename: str) -> str:
    return f"{DOMAIN}/" if filename == "index.html" else f"{DOMAIN}/{filename}"


def reconcile(root: Path, apply: bool = False) -> tuple[int, int]:
    """Fail closed on canonical/coverage errors; preserve content and image ownership."""
    with (root / "seo/sitemap-exclusions.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    excluded = {row["path"].strip() for row in rows}
    if len(excluded) != len(rows):
        raise ValueError("Duplicate sitemap exclusions")
    pages = {path.name: path for path in root.glob("*.html")}
    if excluded - pages.keys():
        raise ValueError(f"Exclusions name missing pages: {sorted(excluded - pages.keys())}")
    expected = {page_url(name) for name in pages if name not in excluded}
    changes: dict[Path, str] = {}
    for name, path in sorted(pages.items()):
        source = path.read_text(encoding="utf-8")
        metadata = Metadata(source)
        if len(metadata.robots) != 1:
            raise ValueError(f"{name}: expected one robots meta tag")
        directives = {item.strip().lower() for item in metadata.robots[0].split(",")}
        if name in excluded:
            if "noindex" not in directives:
                raise ValueError(f"{name}: excluded page must remain noindex")
            continue
        if metadata.canonicals != [page_url(name)]:
            raise ValueError(f"{name}: expected exactly one self-referencing canonical")
        if directives & {"noindex", "nofollow", "none"}:
            if len(ROBOTS_RE.findall(source)) != 1:
                raise ValueError(f"{name}: cannot safely replace robots tag")
            changes[path] = ROBOTS_RE.sub(INDEX_TAG, source, count=1)

    sitemap = root / "sitemap.xml"
    document = ET.parse(sitemap)
    tree = document.getroot()
    if tree.tag != f"{{{NS}}}urlset":
        raise ValueError("Sitemap must have the standard urlset namespace")
    current: dict[str, ET.Element] = {}
    for entry in tree:
        loc = entry.find(f"{{{NS}}}loc")
        if loc is None or not loc.text or loc.text in current:
            raise ValueError("Sitemap has a missing or duplicate loc")
        if loc.text not in {page_url(name) for name in pages}:
            raise ValueError(f"Unknown or non-canonical sitemap URL: {loc.text}")
        current[loc.text] = entry
    missing = sorted(expected - current.keys())
    extra = sorted(current.keys() - expected)
    if not apply and (changes or missing or extra):
        raise ValueError(f"Coverage mismatch: {len(missing)} missing URLs, {len(extra)} excluded URLs, {len(changes)} pages blocking indexing")
    if apply:
        for path, source in changes.items():
            path.write_text(source, encoding="utf-8")
        for url in extra:
            tree.remove(current[url])
        for url in missing:
            entry = ET.SubElement(tree, f"{{{NS}}}url")
            ET.SubElement(entry, f"{{{NS}}}loc").text = url
        if missing or extra:
            ET.register_namespace("", NS)
            ET.indent(document, space="  ")
            document.write(sitemap, encoding="utf-8", xml_declaration=True)
    return len(expected), len(excluded)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        included, excluded = reconcile(args.root, apply=args.apply)
    except (ValueError, OSError, ET.ParseError) as error:
        raise SystemExit(str(error)) from error
    print(f"Verified {included} canonical sitemap URLs and {excluded} explicit noindex exclusions.")


if __name__ == "__main__":
    main()
