"""Validate the generated image sitemap and the published image markup it represents."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "published-image-sitemap.json"
SITEMAP = ROOT / "image-sitemap.xml"
ROBOTS = ROOT / "robots.txt"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
IMAGE_NS = "http://www.google.com/schemas/sitemap-image/1.1"
NS = {"sm": SITEMAP_NS, "image": IMAGE_NS}
DEPRECATED_IMAGE_ELEMENTS = {"caption", "geo_location", "license", "title"}


class Images(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "img":
            self.images.append({key.lower(): value or "" for key, value in attrs})


def fail(message: str) -> None:
    print(f"Image sitemap validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        document = ET.parse(SITEMAP)
    except (OSError, json.JSONDecodeError, ET.ParseError) as error:
        fail(str(error))

    origin = manifest.get("siteOrigin")
    entries = manifest.get("entries")
    if not isinstance(origin, str) or not isinstance(entries, list):
        fail("manifest is malformed")
    root = document.getroot()
    if root.tag != f"{{{SITEMAP_NS}}}urlset":
        fail("root urlset namespace is missing or incorrect")

    expected: dict[str, list[str]] = {}
    for entry in entries:
        page = entry.get("page")
        canonical = entry.get("canonical")
        images = entry.get("images")
        if not isinstance(page, str) or not isinstance(canonical, str) or not isinstance(images, list):
            fail("manifest entry is malformed")
        html = (ROOT / page).read_text(encoding="utf-8")
        parser = Images()
        parser.feed(html)
        expected[canonical] = []
        for image in images:
            if not isinstance(image, str) or not (ROOT / image).is_file():
                fail(f"missing asset: {image}")
            matching = [attributes for attributes in parser.images if attributes.get("src") == image]
            if len(matching) != 1:
                fail(f"{image} is not a normal img source in {page}")
            attributes = matching[0]
            if not attributes.get("alt", "").strip():
                fail(f"{image} needs meaningful alt text in {page}")
            try:
                if int(attributes.get("width", "0")) <= 0 or int(attributes.get("height", "0")) <= 0:
                    fail(f"{image} needs positive width and height in {page}")
            except ValueError:
                fail(f"{image} has non-numeric dimensions in {page}")
            if page == "index.html" and image == "assets/images/illustrations/homepage/homepage-property-hero-representative-v1.png":
                if attributes.get("fetchpriority") != "high" or attributes.get("loading") == "lazy":
                    fail("homepage hero needs high priority and must not be lazy-loaded")
            elif attributes.get("loading") != "lazy" or attributes.get("decoding") != "async":
                fail(f"{image} needs lazy loading and async decoding in {page}")
            expected[canonical].append(f"{origin}/{image}")

    actual: dict[str, list[str]] = {}
    for url in root.findall("sm:url", NS):
        loc = url.findtext("sm:loc", namespaces=NS)
        if not loc:
            fail("URL entry without a canonical loc")
        if loc in actual:
            fail(f"duplicate canonical page: {loc}")
        images: list[str] = []
        for image in url.findall("image:image", NS):
            children = list(image)
            if len(children) != 1 or children[0].tag != f"{{{IMAGE_NS}}}loc" or not children[0].text:
                fail(f"{loc} has image metadata other than required image:loc")
            images.append(children[0].text)
        actual[loc] = images

    for node in root.iter():
        if node.tag.startswith(f"{{{IMAGE_NS}}}") and node.tag.rsplit("}", 1)[-1] in DEPRECATED_IMAGE_ELEMENTS:
            fail(f"deprecated image sitemap element: {node.tag}")
    if actual != expected:
        fail("canonical page/image URL map does not match the source manifest")
    if len({image for values in actual.values() for image in values}) != sum(len(values) for values in actual.values()):
        fail("duplicate image URL")

    robots = ROBOTS.read_text(encoding="utf-8")
    if f"Sitemap: {origin}/image-sitemap.xml" not in robots:
        fail("robots.txt does not advertise image-sitemap.xml")

    hero = (ROOT / "index.html").read_text(encoding="utf-8")
    hero_source = "assets/images/illustrations/homepage/homepage-property-hero-representative-v1.png"
    required_hero_tokens = (
        "<picture class=\"hero-media\">",
        hero_source,
        "Generated illustration of a broad residential property for Dallas-Fort Worth general contractor services.",
        "<p class=\"hero-image-disclosure\">General contractor services — Dallas–Fort Worth</p>",
    )
    if not all(token in hero for token in required_hero_tokens):
        fail("homepage hero lacks required accessible image markup")
    styles = (ROOT / "styles.css").read_text(encoding="utf-8")
    required_style_tokens = (".hero-media img", "object-fit: cover", "object-position: 63% center")
    if not all(token in styles for token in required_style_tokens):
        fail("homepage hero lacks responsive image-fit rules")
    if hero_source in styles:
        fail("homepage hero image must not depend on a CSS-only source")

    print(f"Validated image sitemap: {len(actual)} canonical pages and {sum(len(images) for images in actual.values())} image URLs.")


if __name__ == "__main__":
    main()
