#!/usr/bin/env python3
"""Preserve the verified Spanish Mansfield case after project regeneration."""

from __future__ import annotations

import re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ENGLISH = ROOT / "gray-subway-kitchen-backsplash-mansfield.html"
SPANISH = ROOT / "proyecto-backsplash-cocina-mansfield.html"
PROJECTS = ROOT / "projects.html"
SITEMAP = ROOT / "sitemap.xml"
SPANISH_NAME = "proyecto-backsplash-cocina-mansfield.html"
SPANISH_URL = f"https://lunageneralcontractors.com/{SPANISH_NAME}"
OLD_TITLE = (
    "<title>Gray Subway Tile Kitchen Backsplash in Mansfield "
    "| Luna General Contractors</title>"
)
NEW_TITLE = "<title>Mansfield Gray Subway Tile Backsplash | Luna</title>"
CANONICAL = (
    '<link rel="canonical" '
    'href="https://lunageneralcontractors.com/'
    'gray-subway-kitchen-backsplash-mansfield.html">'
)
ALTERNATES = (
    CANONICAL
    + '<link rel="alternate" hreflang="en-US" '
    'href="https://lunageneralcontractors.com/'
    'gray-subway-kitchen-backsplash-mansfield.html">'
    + '<link rel="alternate" hreflang="es-US" '
    f'href="{SPANISH_URL}">'
    + '<link rel="alternate" hreflang="x-default" '
    'href="https://lunageneralcontractors.com/'
    'gray-subway-kitchen-backsplash-mansfield.html">'
)
SPANISH_INDEX_LINK = (
    '<a class="seo-text-link" '
    f'href="{SPANISH_NAME}" lang="es">Ver en español →</a>'
)


def patch_english() -> None:
    source = ENGLISH.read_text(encoding="utf-8")
    if OLD_TITLE in source:
        source = source.replace(OLD_TITLE, NEW_TITLE, 1)
    elif NEW_TITLE not in source:
        raise SystemExit("Mansfield English case title was not recognized")

    if 'hreflang="es-US"' not in source:
        if CANONICAL not in source:
            raise SystemExit("Mansfield English canonical was not found")
        source = source.replace(CANONICAL, ALTERNATES, 1)

    if f'href="{SPANISH_NAME}" lang="es"' not in source:
        match = re.search(r'<nav class="breadcrumbs">.*?</nav>', source, re.S)
        if not match:
            raise SystemExit("Mansfield English breadcrumb was not found")
        switcher = (
            '<p class="language-switch"><a '
            f'href="{SPANISH_NAME}" lang="es">'
            "Leer este caso en español →</a></p>"
        )
        source = source[: match.end()] + switcher + source[match.end() :]

    if 'property="og:image"' not in source:
        anchor = (
            '<meta property="og:url" '
            'content="https://lunageneralcontractors.com/'
            'gray-subway-kitchen-backsplash-mansfield.html">'
        )
        social = (
            anchor
            + '<meta property="og:image" '
            'content="https://lunageneralcontractors.com/20180530-181936.webp">'
            + '<meta property="og:image:width" content="720">'
            + '<meta property="og:image:height" content="405">'
            + '<meta property="og:image:alt" '
            'content="Gray subway tile kitchen backsplash installation '
            'in Mansfield Texas">'
            + '<meta name="twitter:card" content="summary_large_image">'
            + '<meta name="twitter:image" '
            'content="https://lunageneralcontractors.com/20180530-181936.webp">'
        )
        if anchor not in source:
            raise SystemExit("Mansfield English og:url was not found")
        source = source.replace(anchor, social, 1)

    source = source.replace(
        'loading="lazy" width="1200" height="900"',
        'loading="lazy" decoding="async" width="720" height="405"',
    )
    ENGLISH.write_text(source, encoding="utf-8")


def patch_project_index() -> None:
    source = PROJECTS.read_text(encoding="utf-8")
    if f'href="{SPANISH_NAME}"' not in source:
        anchor = (
            '<a class="seo-text-link" '
            'href="gray-subway-kitchen-backsplash-mansfield.html">'
            "View project →</a>"
        )
        if anchor not in source:
            raise SystemExit("Mansfield project-index link was not found")
        source = source.replace(anchor, anchor + SPANISH_INDEX_LINK, 1)
        PROJECTS.write_text(source, encoding="utf-8")


def ensure_spanish_page() -> None:
    if not SPANISH.exists():
        raise SystemExit(f"Missing {SPANISH.name}")
    source = SPANISH.read_text(encoding="utf-8")
    required = (
        "<title>",
        "<h1>",
        'rel="canonical"',
        'hreflang="en-US"',
        '"@type":"Article"',
        '"@type":"BreadcrumbList"',
        '"@type":"ImageGallery"',
        "tel:+18177845998",
        "20180530-181936.webp",
    )
    missing = [token for token in required if token not in source]
    if missing:
        raise SystemExit(f"{SPANISH.name}: missing {missing[0]}")


def ensure_sitemap() -> None:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    document = ET.parse(SITEMAP)
    root = document.getroot()
    namespace = root.tag.split("}", 1)[0].lstrip("{") if "}" in root.tag else ""
    prefix = f"{{{namespace}}}" if namespace else ""
    urls = {
        loc.text.strip()
        for loc in root.findall(f"{prefix}url/{prefix}loc")
        if loc.text
    }
    if SPANISH_URL in urls:
        return
    node = ET.SubElement(root, f"{prefix}url")
    ET.SubElement(node, f"{prefix}loc").text = SPANISH_URL
    ET.SubElement(node, f"{prefix}lastmod").text = "2026-09-05"
    ET.SubElement(node, f"{prefix}changefreq").text = "monthly"
    ET.SubElement(node, f"{prefix}priority").text = "0.6"
    document.write(SITEMAP, encoding="utf-8", xml_declaration=True)


def main() -> None:
    ensure_spanish_page()
    patch_english()
    patch_project_index()
    ensure_sitemap()
    print("Preserved the bilingual verified Mansfield kitchen case.")


if __name__ == "__main__":
    main()
