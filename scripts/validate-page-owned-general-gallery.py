#!/usr/bin/env python3
"""Validate the standalone browse gallery without changing image ownership."""

from __future__ import annotations

import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "page-owned-imagery.json"
DATA = ROOT / "content" / "page-owned-gallery-data.json"
GALLERY = ROOT / "gallery.html"
EXCLUSIONS = ROOT / "seo" / "sitemap-exclusions.csv"
SITEMAP = ROOT / "sitemap.xml"
IMAGE_SITEMAP = ROOT / "image-sitemap.xml"
DOMAIN = "https://lunageneralcontractors.com"
PAGE_COUNT = 1009
SCENE_COUNT = 5045
PAGE_SIZE = 24

# Keep validation coupled to the builder's stable, human-readable service
# grouping. Manifest labels are intentionally page-specific and are not a
# reliable filter key for the public browse gallery.
SERVICE_LABELS = {
    "backsplash-installation": "Backsplash Installation",
    "bathroom-remodeling": "Bathroom Remodeling",
    "cabinet-installation": "Cabinet Installation",
    "carpentry": "Carpentry",
    "city-landings": "Service Areas",
    "commercial-construction": "Commercial Construction",
    "concrete-driveways": "Concrete Driveways",
    "directories": "Service Directory",
    "door-installation": "Door Installation",
    "drywall": "Drywall",
    "editorial": "Service Guides",
    "fencing": "Fencing",
    "flooring": "Flooring",
    "foundation-repair": "Foundation Repair",
    "general-contractor": "General Contractor",
    "insurance-claims": "Insurance Claims",
    "kitchen-remodeling": "Kitchen Remodeling",
    "outdoor-living": "Outdoor Living",
    "painting": "Painting",
    "patio-covers": "Patio Covers",
    "pergolas": "Pergolas",
    "project-case-studies": "Planning & Design",
    "roofing": "Roofing",
    "room-additions": "Room Additions",
    "shower-remodeling": "Shower Remodeling",
    "siding": "Siding",
    "site-home": "General Contractor",
    "site-legal": "Customer Resources",
    "site-locale": "Spanish Resources",
    "site-preview": "Site Preview",
    "water-damage-restoration": "Water Damage Restoration",
    "whole-home-remodeling": "Whole-Home Remodeling",
    "window-replacement": "Window Replacement",
}


def fail(message: str) -> None:
    print(f"General gallery validation failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def city_for(entry: dict[str, object]) -> str:
    city = str(entry.get("city") or "").strip()
    if not city or re.fullmatch(r"Dallas\s*[-\u2013\u2014]\s*Fort Worth", city, flags=re.I):
        return "Dallas\u2013Fort Worth"
    return city


def service_for(category: str) -> str:
    service = SERVICE_LABELS.get(category)
    if not service:
        fail(f"unrecognized manifest category: {category}")
    return service


def service_key_for(category: str) -> str:
    return "general-contractor" if category == "site-home" else category


def expected_records(manifest: dict[str, object]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for page, raw_entry in manifest.items():
        if not isinstance(raw_entry, dict) or raw_entry.get("placement_hold"):
            fail(f"manifest has held or malformed owner: {page}")
        category = str(raw_entry.get("category") or "").strip()
        service = service_for(category)
        city = city_for(raw_entry)
        images = raw_entry.get("images")
        if not category or not service or not isinstance(images, list) or len(images) != 5:
            fail(f"manifest owner is malformed: {page}")
        for image in images:
            if not isinstance(image, dict):
                fail(f"image is malformed: {page}")
            source = image.get("src")
            if not isinstance(source, str) or not source.startswith("assets/images/"):
                fail(f"non-public source in manifest: {page}")
            records.append({
                "ownerPage": page,
                "category": category,
                "serviceKey": service_key_for(category),
                "service": service,
                "city": city,
                "slot": image.get("slot"),
                "src": source,
                "width": image.get("width"),
                "height": image.get("height"),
                "caption": f"{service} · {city}",
                "alt": f"{service} service design in {city}.",
            })
    return sorted(records, key=lambda item: (str(item["service"]).lower(), str(item["city"]).lower(), str(item["ownerPage"]), int(item["slot"])))


def xml_locs(path: Path) -> set[str]:
    root = ET.parse(path).getroot()
    return {
        element.text.strip()
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "loc" and element.text
    }


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or len(manifest) != PAGE_COUNT:
        fail(f"expected {PAGE_COUNT} manifest owners")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        fail("gallery data is not a list")
    expected = expected_records(manifest)
    if data != expected:
        fail("gallery data is not an exact manifest projection")
    if len(data) != SCENE_COUNT:
        fail(f"expected {SCENE_COUNT} data records")
    sources = [str(record.get("src", "")) for record in data if isinstance(record, dict)]
    if len(sources) != len(set(sources)):
        fail("gallery data repeats an owned source")
    for record in data:
        if not isinstance(record, dict):
            fail("gallery data contains a non-object record")
        source = record.get("src")
        page = record.get("ownerPage")
        if not isinstance(source, str) or not source.startswith("assets/images/") or "library" in source.lower():
            fail("gallery data includes a non-public or private source")
        if not isinstance(page, str) or page not in manifest:
            fail("gallery data includes an unknown owner")
        if not (ROOT / source).is_file():
            fail(f"gallery data references missing asset: {source}")

    document = GALLERY.read_text(encoding="utf-8")
    required = (
        '<meta name="robots" content="noindex, follow">',
        f'<link rel="canonical" href="{DOMAIN}/gallery.html">',
        '<h1>Service &amp; Design Gallery</h1>',
        'data-general-gallery-source="content/page-owned-gallery-data.json"',
        'data-general-gallery-service',
        'data-general-gallery-city',
        'data-general-gallery-previous',
        'data-general-gallery-next',
    )
    if not all(token in document for token in required):
        fail("gallery document lacks required metadata or controls")
    if document.count('data-general-gallery-card="true"') != PAGE_SIZE:
        fail(f"gallery fallback must contain exactly {PAGE_SIZE} cards")
    fallback_sources = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', document, flags=re.I)
    if fallback_sources != [record["src"] for record in data[:PAGE_SIZE]]:
        fail("gallery fallback cards do not match the first paginated records")
    if re.search(r"(?:completed project|before\s*(?:and|&amp;)\s*after|verified case study)", document, flags=re.I):
        fail("gallery makes an unsupported completed-project claim")

    with EXCLUSIONS.open(newline="", encoding="utf-8") as handle:
        rows = {row["path"].strip(): row["classification"].strip() for row in csv.DictReader(handle)}
    if rows.get("gallery.html") != "exclude-utility":
        fail("gallery.html lacks the required exclude-utility classification")
    gallery_url = f"{DOMAIN}/gallery.html"
    if gallery_url in xml_locs(SITEMAP):
        fail("gallery.html unexpectedly appears in sitemap.xml")
    if gallery_url in xml_locs(IMAGE_SITEMAP):
        fail("gallery.html unexpectedly appears in image-sitemap.xml")
    print(f"Validated general gallery: {PAGE_COUNT} owners, {SCENE_COUNT} records, {PAGE_SIZE}-card pagination.")


if __name__ == "__main__":
    main()
