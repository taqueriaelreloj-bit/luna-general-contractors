#!/usr/bin/env python3
"""Validate the generated component-card image contract.

Component cards are intentionally distinct from the five page-owned gallery
scenes.  This validator checks immutable bytes, mapping coverage and rendered
service-guide markup so an aggregate rebuild cannot restore shared SVGs or
photo placements into the three material-card slots.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "component-card-imagery.json"
GUIDES = ROOT / "content" / "service-guide-manifest.json"
OWNED = ROOT / "content" / "page-owned-imagery.json"
EXPECTED_PAGES = 878
EXPECTED_IMAGES = 2634
EXPECTED_OWNED = 5045

SECTION = re.compile(r'<section\b(?=[^>]*\bid=["\']service-materials["\'])[^>]*>(.*?)</section>', re.I | re.S)
CARD = re.compile(r'<article\b(?=[^>]*\bclass=["\'][^"\']*\bsg-card\b[^"\']*["\'])[^>]*>(.*?)</article>', re.I | re.S)
TAG = re.compile(r'<img\b[^>]*>', re.I)
MARKED = re.compile(r'<img\b(?=[^>]*\bdata-component-card-image=["\']true["\'])[^>]*>', re.I)
ATTR = re.compile(r'\b([\w:-]+)=["\']([^"\']*)["\']', re.I)


def fail(message: str) -> None:
    raise SystemExit(f"Component card validation failed: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def webp_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:30]
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        fail(f"invalid WebP header: {path.relative_to(ROOT)}")
    kind = data[12:16]
    if kind == b"VP8 ":
        return (int.from_bytes(data[26:28], "little") & 16383, int.from_bytes(data[28:30], "little") & 16383)
    if kind == b"VP8X":
        return (1 + int.from_bytes(data[24:27], "little"), 1 + int.from_bytes(data[27:30], "little"))
    if kind == b"VP8L":
        packed = int.from_bytes(data[21:25], "little")
        return ((packed & 16383) + 1, ((packed >> 14) & 16383) + 1)
    fail(f"unsupported WebP payload: {path.relative_to(ROOT)}")


def attrs(tag: str) -> dict[str, str]:
    return {name.lower(): value for name, value in ATTR.findall(tag)}


def safe_component_path(value: object, owner: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{owner}: missing component path")
    path = PurePosixPath(value)
    if (
        "\\" in value
        or ":" in value
        or path.is_absolute()
        or ".." in path.parts
        or path.suffix.lower() != ".webp"
        or not value.startswith("assets/images/illustrations/component-owned/")
    ):
        fail(f"{owner}: unsafe component path {value!r}")
    return value


def required_text(value: object, label: str, owner: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{owner}: missing {label}")
    return value.strip()


def main() -> None:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        guides = json.loads(GUIDES.read_text(encoding="utf-8"))
        owned = json.loads(OWNED.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(str(error))
    if (
        not isinstance(data, dict)
        or data.get("schema_version") != 1
        or data.get("provenance") != "generated-component-card-assets"
        or data.get("page_count") != EXPECTED_PAGES
        or data.get("image_count") != EXPECTED_IMAGES
        or not isinstance(data.get("assets"), list)
        or len(data["assets"]) != EXPECTED_IMAGES
    ):
        fail("invalid component manifest contract")
    if not isinstance(guides, list) or len(guides) != EXPECTED_PAGES:
        fail("service guide target roster is invalid")
    targets = {row.get("file") for row in guides if isinstance(row, dict)}
    if len(targets) != EXPECTED_PAGES or not all(isinstance(page, str) for page in targets):
        fail("service guide target roster is malformed")
    if not isinstance(owned, dict) or len(owned) != 1009:
        fail("five-scene owner manifest changed")

    owned_paths: set[str] = set()
    owned_hashes: set[str] = set()
    for entry in owned.values():
        images = entry.get("images") if isinstance(entry, dict) else None
        if not isinstance(images, list) or len(images) != 5:
            fail("five-scene owner manifest is malformed")
        for image in images:
            source = image.get("src") if isinstance(image, dict) else None
            if not isinstance(source, str) or source in owned_paths:
                fail("five-scene paths are not exclusive")
            asset = ROOT / source
            if not asset.is_file() or asset.is_symlink():
                fail(f"missing five-scene asset: {source}")
            owned_paths.add(source)
            owned_hashes.add(sha256(asset))
    if len(owned_paths) != EXPECTED_OWNED:
        fail("five-scene contract is not exactly 5045 paths")

    by_page: dict[str, list[dict[str, object]]] = {}
    sources: set[str] = set()
    hashes: set[str] = set()
    for raw in data["assets"]:
        if not isinstance(raw, dict):
            fail("component asset is not an object")
        page = required_text(raw.get("page_file"), "page_file", "component manifest")
        if page not in targets:
            fail(f"component target is outside the guide roster: {page}")
        slot = raw.get("slot")
        if slot not in (1, 2, 3):
            fail(f"{page}: invalid slot")
        source = safe_component_path(raw.get("path"), page)
        subject = required_text(raw.get("subject"), "subject", page)
        service = required_text(raw.get("service"), "service", page)
        city = required_text(raw.get("city"), "city", page)
        caption = required_text(raw.get("caption"), "caption", page)
        alt = required_text(raw.get("alt"), "alt", page)
        if city.casefold() not in caption.casefold() or city.casefold() not in alt.casefold():
            fail(f"{page}: caption and alt must include the page city or region")
        if any(len(value) > maximum for value, maximum in ((subject, 120), (caption, 120), (alt, 160))):
            fail(f"{page}: subject/caption/alt is too long")
        if re.search(r"\b(?:completed project|before\s*(?:and|&)\s*after|verified case study|luna project|actual project)\b", f"{subject} {caption} {alt}", re.I):
            fail(f"{page}: component copy makes a project claim")
        width, height, byte_count, declared_hash = raw.get("width"), raw.get("height"), raw.get("bytes"), raw.get("sha256")
        if not all(isinstance(value, int) and value > 0 for value in (width, height, byte_count)) or not isinstance(declared_hash, str):
            fail(f"{page}: invalid component dimensions or hash")
        asset = ROOT / source
        if asset.is_symlink() or not asset.is_file() or asset.stat().st_size != byte_count:
            fail(f"{page}: component bytes missing or wrong size")
        actual_hash = sha256(asset)
        if actual_hash != declared_hash or webp_dimensions(asset) != (width, height):
            fail(f"{page}: component integrity mismatch")
        if source in sources or source in owned_paths or actual_hash in hashes or actual_hash in owned_hashes:
            fail(f"{page}: component asset is not exclusive")
        sources.add(source)
        hashes.add(actual_hash)
        by_page.setdefault(page, []).append(raw)
    if set(by_page) != targets or any(sorted(row["slot"] for row in rows) != [1, 2, 3] for rows in by_page.values()):
        fail("component mapping does not cover every guide page and slot")

    html_pages = {path.name: path.read_text(encoding="utf-8") for path in ROOT.glob("*.html")}
    for page, records in by_page.items():
        body = html_pages.get(page, "")
        section = SECTION.search(body)
        if not section:
            fail(f"{page}: missing service-materials section")
        cards = CARD.findall(section.group(1))
        if len(cards) != 3:
            fail(f"{page}: expected exactly three material cards")
        for record, card in zip(sorted(records, key=lambda row: row["slot"]), cards):
            marked = MARKED.findall(card)
            if len(marked) != 1 or len(TAG.findall(card)) != 1:
                fail(f"{page}: slot {record['slot']} retains a legacy image")
            image_attrs = attrs(marked[0])
            if image_attrs.get("src") != record["path"] or image_attrs.get("alt") != record["alt"]:
                fail(f"{page}: slot {record['slot']} does not match its mapping")
            if f'data-component-card-slot="{record["slot"]}"' not in card or str(record["caption"]) not in card:
                fail(f"{page}: slot {record['slot']} lacks slot or caption metadata")
            if "sg-card-body" not in card or "<details>" not in card or not re.search(r'<a\b[^>]*\bhref=["\']https?://', card, re.I):
                fail(f"{page}: slot {record['slot']} lost educational content or official link")

    for page, body in html_pages.items():
        marker_count = body.count('data-component-card-image="true"')
        if page in targets and marker_count != 3:
            fail(f"{page}: expected three component markers")
        if page not in targets and marker_count:
            fail(f"{page}: unexpected component marker")
    css = (ROOT / "service-guides.css").read_text(encoding="utf-8")
    if re.search(r"\.sg-card--component-image[^\{]*\{[^}]*object-fit\s*:\s*cover", css, re.I):
        fail("component cards must not crop their generated images")
    print(f"Component cards are current: {len(by_page)} pages, {len(sources)} exclusive images.")


if __name__ == "__main__":
    main()
