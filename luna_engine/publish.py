from __future__ import annotations

import json
import shutil
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "luna_engine"
DIST = ENGINE / "dist"
MANIFEST = DIST / "manifest.json"
SITEMAP = ROOT / "sitemap.xml"
DOMAIN = "https://lunageneralcontractors.com"


def load_manifest() -> list[str]:
    if not MANIFEST.exists():
        raise SystemExit("Missing Luna Engine manifest")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pages = data.get("pages", [])
    if not pages:
        raise SystemExit("Luna Engine manifest contains no pages")
    return pages


def publish_pages(pages: list[str]) -> None:
    for filename in pages:
        source = DIST / filename
        if not source.exists():
            raise SystemExit(f"Missing generated page: {source}")
        html = source.read_text(encoding="utf-8")
        # Luna Engine previews live in a subfolder, but production pages live at site root.
        html = html.replace('href="../../styles.css"', 'href="/styles.css"')
        html = html.replace('href="../../index.html"', 'href="/"')
        html = html.replace('href="../../service-areas.html"', 'href="/service-areas.html"')
        html = html.replace('href="../../articles.html"', 'href="/articles.html"')
        (ROOT / filename).write_text(html + "\n", encoding="utf-8")


def existing_non_engine_urls(engine_names: set[str]) -> set[str]:
    urls: set[str] = {f"{DOMAIN}/"}
    if not SITEMAP.exists():
        return urls
    try:
        tree = ET.parse(SITEMAP)
    except ET.ParseError:
        return urls
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for loc in tree.findall("sm:url/sm:loc", namespace):
        if not loc.text:
            continue
        url = loc.text.strip()
        filename = url.removeprefix(f"{DOMAIN}/")
        if filename and filename in engine_names:
            continue
        urls.add(url)
    return urls


def write_sitemap(pages: list[str]) -> None:
    engine_names = set(pages)
    urls = existing_non_engine_urls(engine_names)
    urls.update(f"{DOMAIN}/{filename}" for filename in pages)
    today = date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in sorted(urls, key=lambda value: (value != f"{DOMAIN}/", value)):
        lines.append(f"  <url><loc>{url}</loc><lastmod>{today}</lastmod></url>")
    lines.append("</urlset>")
    SITEMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    pages = load_manifest()
    publish_pages(pages)
    write_sitemap(pages)
    print(f"Published {len(pages)} Luna Engine pages to the site root")
    print(f"Updated sitemap.xml with generated URLs")


if __name__ == "__main__":
    main()
