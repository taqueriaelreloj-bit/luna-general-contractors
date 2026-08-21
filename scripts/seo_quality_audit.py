#!/usr/bin/env python3
"""Audit production HTML for technical, structural, and trust-related SEO issues.

The audit uses only Python's standard library so it can run locally and in
GitHub Actions without installing packages. It reads production URLs from the
sitemap, checks the corresponding files, and writes a concise Markdown report.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


DOMAIN = "https://lunageneralcontractors.com"
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
SPACE_RE = re.compile(r"\s+")
BAD_COPY_PATTERNS = {
    "awkward city phrase": re.compile(r"\bin\s+Serving\s+[A-Z]", re.I),
    "incorrect city article": re.compile(
        r"\b(?:a|A)\s+(?:Allen|Arlington|Euless|Irving|Ovilla)\b"
    ),
    "placeholder gallery copy": re.compile(r"This gallery is ready", re.I),
}


def clean(value: str) -> str:
    return SPACE_RE.sub(" ", html.unescape(value or "")).strip()


@dataclass
class PageData:
    path: Path
    html_lang: str = ""
    title: str = ""
    metas: dict[str, str] = field(default_factory=dict)
    canonical: list[str] = field(default_factory=list)
    headings: list[tuple[int, str]] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    ids: set[str] = field(default_factory=set)
    schemas: list[str] = field(default_factory=list)
    stylesheets: list[str] = field(default_factory=list)
    visible_text: list[str] = field(default_factory=list)

    @property
    def words(self) -> int:
        text = clean(" ".join(self.visible_text))
        return len(re.findall(r"\b[\w’'-]+\b", text))

    def heading_values(self, level: int) -> list[str]:
        return [text for found_level, text in self.headings if found_level == level]


class AuditHTMLParser(HTMLParser):
    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.page = PageData(path=path)
        self._capture_title = False
        self._heading_level: int | None = None
        self._capture_schema = False
        self._skip_text_depth = 0
        self._buffer: list[str] = []

    @staticmethod
    def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {key.lower(): value or "" for key, value in attrs}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        data = self.attrs_dict(attrs)
        element_id = data.get("id")
        if element_id:
            self.page.ids.add(element_id)

        if tag == "html":
            self.page.html_lang = data.get("lang", "")
        elif tag == "title":
            self._capture_title = True
            self._buffer = []
        elif tag == "meta":
            key = (data.get("name") or data.get("property") or "").lower()
            if key:
                self.page.metas[key] = clean(data.get("content", ""))
        elif tag == "link":
            rel = {part.lower() for part in data.get("rel", "").split()}
            href = data.get("href", "")
            if "canonical" in rel and href:
                self.page.canonical.append(href)
            if "stylesheet" in rel and href:
                self.page.stylesheets.append(href)
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_level = int(tag[1])
            self._buffer = []
        elif tag == "a":
            href = data.get("href")
            if href:
                self.page.links.append(href)
        elif tag == "img":
            self.page.images.append(data)
        elif tag == "script":
            self._skip_text_depth += 1
            if data.get("type", "").lower() == "application/ld+json":
                self._capture_schema = True
                self._buffer = []
        elif tag in {"style", "template", "noscript"}:
            self._skip_text_depth += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title" and self._capture_title:
            self.page.title = clean("".join(self._buffer))
            self._capture_title = False
            self._buffer = []
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._heading_level:
            self.page.headings.append((self._heading_level, clean("".join(self._buffer))))
            self._heading_level = None
            self._buffer = []
        elif tag == "script":
            if self._capture_schema:
                self.page.schemas.append("".join(self._buffer).strip())
                self._capture_schema = False
                self._buffer = []
            self._skip_text_depth = max(0, self._skip_text_depth - 1)
        elif tag in {"style", "template", "noscript"}:
            self._skip_text_depth = max(0, self._skip_text_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._capture_title or self._heading_level or self._capture_schema:
            self._buffer.append(data)
        if not self._skip_text_depth and clean(data):
            self.page.visible_text.append(data)


@dataclass
class Finding:
    severity: str
    page: str
    message: str


class Auditor:
    def __init__(self, root: Path, base_url: str = DOMAIN):
        self.root = root.resolve()
        self.base_url = base_url.rstrip("/")
        self.findings: list[Finding] = []
        self.pages: dict[str, PageData] = {}
        self.sitemap_entries: set[str] = set()
        self.discovered_root_pages: set[str] = set()
        self.noindex_pages: set[str] = set()

    def add(self, severity: str, page: str, message: str) -> None:
        self.findings.append(Finding(severity, page, message))

    def sitemap_paths(self) -> list[str]:
        sitemap = self.root / "sitemap.xml"
        if not sitemap.exists():
            self.add("critical", "sitemap.xml", "Missing sitemap.xml")
            return []
        try:
            tree = ET.parse(sitemap)
        except ET.ParseError as exc:
            self.add("critical", "sitemap.xml", f"Invalid XML: {exc}")
            return []

        paths: list[str] = []
        seen: set[str] = set()
        for loc in tree.findall(".//sm:loc", SITEMAP_NS):
            url = clean(loc.text or "")
            parsed = urlparse(url)
            expected_host = urlparse(self.base_url).netloc
            if parsed.scheme != "https" or parsed.netloc != expected_host:
                self.add("critical", "sitemap.xml", f"Unexpected sitemap URL: {url}")
                continue
            path = unquote(parsed.path.lstrip("/")) or "index.html"
            if path in seen:
                self.add("critical", "sitemap.xml", f"Duplicate URL for {path}")
                continue
            seen.add(path)
            paths.append(path)
        return paths

    def parse_page(self, relative: str, in_sitemap: bool = True) -> PageData | None:
        path = self.root / relative
        if not path.exists():
            self.add("critical", relative, "Listed in sitemap but file is missing")
            return None
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            self.add("critical", relative, f"Not valid UTF-8: {exc}")
            return None
        parser = AuditHTMLParser(path)
        try:
            parser.feed(source)
        except Exception as exc:  # HTMLParser is tolerant; surface unexpected failures.
            self.add("critical", relative, f"HTML parser error: {exc}")
            return None
        page = parser.page
        self.pages[relative] = page
        self.audit_page(relative, page, source, in_sitemap)
        return page

    def expected_canonical(self, relative: str) -> str:
        return f"{self.base_url}/" if relative == "index.html" else f"{self.base_url}/{relative}"

    def audit_page(
        self, relative: str, page: PageData, source: str, in_sitemap: bool
    ) -> None:
        if not page.html_lang:
            self.add("warning", relative, "Missing language on the <html> element")

        if not page.title:
            self.add("critical", relative, "Missing <title>")
        elif not 25 <= len(page.title) <= 75:
            self.add("warning", relative, f"Title length is {len(page.title)} characters")

        description = page.metas.get("description", "")
        if not description:
            self.add("critical", relative, "Missing meta description")
        elif not 70 <= len(description) <= 175:
            self.add("warning", relative, f"Meta description length is {len(description)} characters")

        h1_values = [value for value in page.heading_values(1) if value]
        if len(h1_values) != 1:
            self.add("critical", relative, f"Expected exactly one H1; found {len(h1_values)}")

        robots = page.metas.get("robots", "")
        is_noindex = "noindex" in robots.lower()
        if is_noindex:
            self.noindex_pages.add(relative)

        if len(page.canonical) != 1:
            self.add("critical", relative, f"Expected one canonical URL; found {len(page.canonical)}")
        elif (
            not (is_noindex and not in_sitemap)
            and page.canonical[0].rstrip("/") != self.expected_canonical(relative).rstrip("/")
        ):
            self.add("critical", relative, f"Canonical points to {page.canonical[0]}")

        if "viewport" not in page.metas:
            self.add("critical", relative, "Missing viewport meta tag")
        if is_noindex and in_sitemap:
            self.add("critical", relative, "Sitemap page is marked noindex")
        if not is_noindex and "max-image-preview:large" not in robots.lower():
            self.add("warning", relative, "Robots meta does not allow large image previews explicitly")

        for key in ("og:title", "og:description", "og:url", "og:image"):
            if not page.metas.get(key):
                self.add("warning", relative, f"Missing {key}")
        if not page.metas.get("twitter:card"):
            self.add("warning", relative, "Missing twitter:card")

        seen_h2 = False
        previous_level = 0
        for level, value in page.headings:
            if not value:
                self.add("critical", relative, f"Empty H{level}")
            if level == 2:
                seen_h2 = True
            if level >= 3 and not seen_h2:
                self.add("warning", relative, f"H{level} appears before the first H2: {value[:80]}")
            if previous_level and level > previous_level + 1:
                self.add("warning", relative, f"Heading jumps from H{previous_level} to H{level}: {value[:80]}")
            previous_level = level

        for index, image in enumerate(page.images, start=1):
            src = image.get("src", "")
            if not clean(image.get("alt", "")):
                self.add("warning", relative, f"Image {index} is missing useful alt text: {src[:100]}")
            if not image.get("width") or not image.get("height"):
                self.add("warning", relative, f"Image {index} has no explicit dimensions: {src[:100]}")
            if "&sig=" in src and "?" not in src:
                self.add("critical", relative, f"Malformed image URL: {src}")

        normalized_styles = [item.split("?", 1)[0] for item in page.stylesheets]
        for stylesheet in sorted(set(normalized_styles)):
            if normalized_styles.count(stylesheet) > 1:
                self.add("warning", relative, f"Stylesheet loaded more than once: {stylesheet}")

        if page.words < 180:
            self.add("warning", relative, f"Thin visible content: approximately {page.words} words")
        if len([href for href in page.links if self.is_internal(href)]) < 3:
            self.add("warning", relative, "Fewer than three crawlable internal links")

        visible = clean(" ".join(page.visible_text))
        for label, pattern in BAD_COPY_PATTERNS.items():
            match = pattern.search(visible)
            if match:
                self.add("critical", relative, f"{label}: “{match.group(0)}”")

        for schema_index, raw in enumerate(page.schemas, start=1):
            if not raw:
                self.add("critical", relative, f"Empty JSON-LD block {schema_index}")
                continue
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                self.add("critical", relative, f"Invalid JSON-LD block {schema_index}: {exc}")

    def is_internal(self, href: str) -> bool:
        parsed = urlparse(html.unescape(href))
        if parsed.scheme in {"tel", "mailto", "sms", "javascript", "data"}:
            return False
        if parsed.scheme in {"http", "https"}:
            return parsed.netloc == urlparse(self.base_url).netloc
        return bool(parsed.path or parsed.fragment)

    def resolve_internal(self, source: str, href: str) -> tuple[str, str] | None:
        value = html.unescape(href).strip()
        parsed = urlparse(value)
        if parsed.scheme in {"tel", "mailto", "sms", "javascript", "data"}:
            return None
        if parsed.scheme in {"http", "https"}:
            if parsed.netloc != urlparse(self.base_url).netloc:
                return None
            target = unquote(parsed.path.lstrip("/")) or "index.html"
        else:
            if not parsed.path:
                target = source
            elif parsed.path.startswith("/"):
                target = unquote(parsed.path.lstrip("/")) or "index.html"
            else:
                target_path = (Path(source).parent / unquote(parsed.path)).as_posix()
                target = str(Path(target_path))
        return target, unquote(parsed.fragment)

    def audit_links(self) -> None:
        for relative, page in self.pages.items():
            for href in page.links:
                resolved = self.resolve_internal(relative, href)
                if not resolved:
                    continue
                target, fragment = resolved
                if target.startswith("../") or target not in self.pages:
                    candidate = self.root / target
                    if not candidate.exists():
                        self.add("critical", relative, f"Broken internal link: {href}")
                        continue
                if fragment:
                    target_page = self.pages.get(target)
                    if target_page and fragment not in target_page.ids:
                        self.add("warning", relative, f"Link fragment not found: {href}")

    def audit_uniqueness(self) -> None:
        fields: dict[str, dict[str, list[str]]] = {
            "title": defaultdict(list),
            "description": defaultdict(list),
            "H1": defaultdict(list),
        }
        for relative, page in self.pages.items():
            if relative in self.noindex_pages:
                continue
            if page.title:
                fields["title"][page.title.lower()].append(relative)
            description = page.metas.get("description", "")
            if description:
                fields["description"][description.lower()].append(relative)
            h1 = page.heading_values(1)
            if len(h1) == 1:
                fields["H1"][h1[0].lower()].append(relative)

        for label, values in fields.items():
            for _, pages in values.items():
                if len(pages) > 1:
                    sample = ", ".join(pages[:6])
                    self.add("critical", sample, f"Duplicate {label} across {len(pages)} pages")

    def run(self) -> None:
        sitemap_paths = self.sitemap_paths()
        self.sitemap_entries = set(sitemap_paths)
        self.discovered_root_pages = {
            path.name for path in self.root.glob("*.html") if path.is_file()
        }
        paths = sorted(self.sitemap_entries | self.discovered_root_pages)
        for relative in paths:
            page = self.parse_page(relative, relative in self.sitemap_entries)
            if (
                page
                and relative not in self.sitemap_entries
                and relative not in self.noindex_pages
            ):
                self.add(
                    "warning",
                    relative,
                    "Indexable root HTML is not listed in the sitemap",
                )
        self.audit_links()
        self.audit_uniqueness()

    def report(self) -> str:
        critical = [item for item in self.findings if item.severity == "critical"]
        warnings = [item for item in self.findings if item.severity == "warning"]
        lines = [
            "# Luna General Contractors — SEO Quality Audit",
            "",
            f"- Root HTML and sitemap pages checked: **{len(self.pages)}**",
            f"- URLs listed in sitemap: **{len(self.sitemap_entries)}**",
            f"- Indexable root pages omitted from sitemap: **{len(self.discovered_root_pages - self.sitemap_entries - self.noindex_pages)}**",
            f"- Critical findings: **{len(critical)}**",
            f"- Warnings: **{len(warnings)}**",
            "",
        ]
        for heading, items in (("Critical findings", critical), ("Warnings", warnings)):
            lines.extend([f"## {heading}", ""])
            if not items:
                lines.append("None. ✅")
            else:
                for item in items[:200]:
                    lines.append(f"- `{item.page}` — {item.message}")
                if len(items) > 200:
                    lines.append(f"- …and {len(items) - 200} additional findings.")
            lines.append("")
        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--report", type=Path, default=Path("seo-audit-report.md"))
    parser.add_argument("--base-url", default=DOMAIN)
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on critical findings")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    auditor = Auditor(args.root, args.base_url)
    auditor.run()
    report = auditor.report()
    args.report.write_text(report, encoding="utf-8")
    print(report)
    has_critical = any(item.severity == "critical" for item in auditor.findings)
    return 1 if args.strict and has_critical else 0


if __name__ == "__main__":
    sys.exit(main())
