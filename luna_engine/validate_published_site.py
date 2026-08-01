from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://lunageneralcontractors.com"
IGNORE_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


def local_target(current: Path, href: str) -> Path | None:
    href = href.strip()
    if not href or href.startswith("#") or href.startswith(IGNORE_SCHEMES):
        return None
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc not in {"lunageneralcontractors.com", "www.lunageneralcontractors.com"}:
            return None
        path = parsed.path.lstrip("/") or "index.html"
        return ROOT / path
    path = parsed.path
    if not path:
        return None
    if path.startswith("/"):
        return ROOT / (path.lstrip("/") or "index.html")
    return (current.parent / path).resolve()


def main() -> None:
    manifest_path = ROOT / "luna_engine" / "dist" / "manifest.json"
    if not manifest_path.exists():
        raise SystemExit("Missing Luna Engine manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    generated = manifest.get("pages", [])
    if len(generated) != 504:
        raise SystemExit(f"Expected 504 generated local pages, found {len(generated)}")

    article_manifest = ROOT / "luna_engine" / "article-manifest.txt"
    articles = [line.strip() for line in article_manifest.read_text(encoding="utf-8").splitlines() if line.strip()] if article_manifest.exists() else []

    expected = generated + articles
    missing = [name for name in expected if not (ROOT / name).exists()]
    if missing:
        raise SystemExit(f"Missing published file: {missing[0]}")

    sitemap = ROOT / "sitemap.xml"
    tree = ET.parse(sitemap)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [node.text for node in tree.findall("sm:url/sm:loc", ns) if node.text]
    if len(urls) != len(set(urls)):
        raise SystemExit("Duplicate URL detected in sitemap.xml")
    sitemap_set = set(urls)
    for name in expected:
        url = f"{DOMAIN}/{name}"
        if url not in sitemap_set:
            raise SystemExit(f"Sitemap missing {url}")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {DOMAIN}/sitemap.xml" not in robots:
        raise SystemExit("robots.txt does not declare the sitemap")
    if "Disallow: /" in robots:
        raise SystemExit("robots.txt blocks the entire site")

    broken: list[tuple[str, str]] = []
    duplicate_titles: dict[str, str] = {}
    duplicate_canonicals: dict[str, str] = {}

    html_files = sorted(ROOT.glob("*.html"))
    for page in html_files:
        html = page.read_text(encoding="utf-8")
        title_match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
        canonical_match = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html, re.I)
        if not title_match:
            raise SystemExit(f"{page.name}: missing title")
        if not canonical_match:
            raise SystemExit(f"{page.name}: missing canonical")
        title = re.sub(r"\s+", " ", title_match.group(1)).strip()
        canonical = canonical_match.group(1).strip()
        if title in duplicate_titles:
            raise SystemExit(f"Duplicate title in {duplicate_titles[title]} and {page.name}: {title}")
        if canonical in duplicate_canonicals:
            raise SystemExit(f"Duplicate canonical in {duplicate_canonicals[canonical]} and {page.name}: {canonical}")
        duplicate_titles[title] = page.name
        duplicate_canonicals[canonical] = page.name

        for href in re.findall(r'href=["\']([^"\']+)', html, re.I):
            target = local_target(page, href)
            if target is None:
                continue
            try:
                target.relative_to(ROOT)
            except ValueError:
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                broken.append((page.name, href))

    if broken:
        page, href = broken[0]
        raise SystemExit(f"Broken internal link in {page}: {href} ({len(broken)} total)")

    print(
        f"Validated {len(generated)} local pages, {len(articles)} generated articles, "
        f"{len(html_files)} root HTML files, {len(urls)} sitemap URLs and all internal links."
    )


if __name__ == "__main__":
    main()
