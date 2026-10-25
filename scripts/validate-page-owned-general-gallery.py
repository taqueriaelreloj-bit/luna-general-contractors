#!/usr/bin/env python3
"""Validate the standalone browse gallery without changing image ownership."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "page-owned-imagery.json"
DATA = ROOT / "content" / "page-owned-gallery-data.json"
COMPONENT_MANIFEST = ROOT / "content" / "component-card-imagery.json"
COMPONENT_DATA = ROOT / "content" / "component-card-gallery-data.json"
GENERAL_DATA = ROOT / "content" / "general-gallery-data.json"
GALLERY = ROOT / "gallery.html"
GALLERY_CSS = ROOT / "page-owned-general-gallery.css"
PAGE_OWNED_CSS = ROOT / "page-owned-imagery.css"
SITE_SCRIPT = ROOT / "script.js"
EXCLUSIONS = ROOT / "seo" / "sitemap-exclusions.csv"
SITEMAP = ROOT / "sitemap.xml"
IMAGE_SITEMAP = ROOT / "image-sitemap.xml"
DOMAIN = "https://lunageneralcontractors.com"
PAGE_COUNT = 1009
SCENE_COUNT = 5045
COMPONENT_COUNT = 2634
GENERAL_COUNT = SCENE_COUNT + COMPONENT_COUNT
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


def gallery_builder_module():
    path = ROOT / "scripts" / "build-page-owned-general-gallery.py"
    spec = importlib.util.spec_from_file_location("general_gallery_builder", path)
    if spec is None or spec.loader is None:
        fail("cannot load the general gallery builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

    builder = gallery_builder_module()
    components = builder.build_component_records() if COMPONENT_MANIFEST.exists() else None
    browse_records = expected
    expected_source = "content/page-owned-gallery-data.json"
    required = [
        '<meta name="robots" content="noindex, follow">',
        f'<link rel="canonical" href="{DOMAIN}/gallery.html">',
        'data-general-gallery-service',
        'data-general-gallery-city',
        'data-general-gallery-previous',
        'data-general-gallery-next',
        'data-general-gallery-lightbox',
        'data-general-gallery-lightbox-image',
        'data-general-gallery-lightbox-close',
    ]
    if components is not None:
        component_data = json.loads(COMPONENT_DATA.read_text(encoding="utf-8"))
        if component_data != components or len(component_data) != COMPONENT_COUNT:
            fail("component gallery data is not an exact 2634-record manifest projection")
        component_sources = [str(record.get("src", "")) for record in component_data if isinstance(record, dict)]
        component_hashes = [str(record.get("sha256", "")) for record in component_data if isinstance(record, dict)]
        if len(component_sources) != len(set(component_sources)) or len(component_hashes) != len(set(component_hashes)):
            fail("component gallery data repeats an asset path or hash")
        if any(record.get("kind") != "component-card" or record.get("mediaType") != "materials-equipment" for record in component_data):
            fail("component gallery records lack their materials-equipment type")
        browse_records = builder.combined_records(expected, components)
        general_data = json.loads(GENERAL_DATA.read_text(encoding="utf-8"))
        if general_data != browse_records or len(general_data) != GENERAL_COUNT:
            fail("combined gallery data is not an exact 7679-record projection")
        all_sources = [str(record.get("src", "")) for record in general_data if isinstance(record, dict)]
        if len(all_sources) != len(set(all_sources)):
            fail("combined gallery data repeats an asset source")
        if any(record.get("kind") not in {"page-owned-scene", "component-card"} for record in general_data):
            fail("combined gallery data has an unknown record kind")
        expected_source = "content/general-gallery-data.json"
        required.extend((
            '<h1>Service &amp; Materials Gallery</h1>',
            'data-general-gallery-source="content/general-gallery-data.json"',
            'data-general-gallery-type',
            'Materials &amp; equipment',
            'general-gallery__filters--typed',
            'page-owned-general-gallery.css?v=20261025-component-gallery-1',
        ))
    else:
        required.extend((
            '<h1>Service &amp; Design Gallery</h1>',
            'data-general-gallery-source="content/page-owned-gallery-data.json"',
            'page-owned-general-gallery.css?v=20261025-full-image-1',
        ))

    document = GALLERY.read_text(encoding="utf-8")
    if not all(token in document for token in required):
        fail("gallery document lacks required metadata or controls")
    if document.count('data-general-gallery-card="true"') != PAGE_SIZE:
        fail(f"gallery fallback must contain exactly {PAGE_SIZE} cards")
    fallback_sources = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', document, flags=re.I)
    if fallback_sources != [record["src"] for record in browse_records[:PAGE_SIZE]]:
        fail("gallery fallback cards do not match the first paginated records")
    if re.search(r"(?:completed project|before\s*(?:and|&amp;)\s*after|verified case study)", document, flags=re.I):
        fail("gallery makes an unsupported completed-project claim")
    gallery_css = GALLERY_CSS.read_text(encoding="utf-8")
    if (
        ".general-gallery__image{width:100%;height:100%;aspect-ratio:auto;object-fit:contain" not in gallery_css
        or ".general-gallery__grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));" not in gallery_css
        or "@media(max-width:900px){.general-gallery__grid{grid-template-columns:repeat(3,minmax(0,1fr))}" not in gallery_css
        or ".general-gallery__grid{grid-template-columns:repeat(2,minmax(0,1fr));" not in gallery_css
        or ".general-gallery__lightbox" not in gallery_css
    ):
        fail("general gallery no longer guarantees full-image responsive presentation")
    page_owned_css = PAGE_OWNED_CSS.read_text(encoding="utf-8")
    if ".page-owned-gallery__thumbnail img{object-fit:contain;background:#111820}" not in page_owned_css:
        fail("shared five-scene gallery no longer guarantees contained thumbnails")
    site_script = SITE_SCRIPT.read_text(encoding="utf-8")
    if not all(token in site_script for token in (
        "data-general-gallery-open",
        "showModal",
        "moveLightbox",
        "data-general-gallery-lightbox-owner",
    )):
        fail("gallery script lacks accessible expanded-image navigation")

    with EXCLUSIONS.open(newline="", encoding="utf-8") as handle:
        rows = {row["path"].strip(): row["classification"].strip() for row in csv.DictReader(handle)}
    if rows.get("gallery.html") != "exclude-utility":
        fail("gallery.html lacks the required exclude-utility classification")
    gallery_url = f"{DOMAIN}/gallery.html"
    if gallery_url in xml_locs(SITEMAP):
        fail("gallery.html unexpectedly appears in sitemap.xml")
    if gallery_url in xml_locs(IMAGE_SITEMAP):
        fail("gallery.html unexpectedly appears in image-sitemap.xml")
    print(f"Validated general gallery: {PAGE_COUNT} scene owners, {len(browse_records)} records, {PAGE_SIZE}-card pagination.")


if __name__ == "__main__":
    main()
