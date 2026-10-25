#!/usr/bin/env python3
"""Build the noindex browse gallery from the page-owned imagery manifest.

The browse page is intentionally a UI over the five images owned by every
existing public page. It does not become an additional owner in the image
sitemap and it never changes the 1,009-page / 5,045-scene contract.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "content" / "page-owned-imagery.json"
GUIDES = ROOT / "content" / "service-guide-manifest.json"
COMPONENT_MANIFEST = ROOT / "content" / "component-card-imagery.json"
OUTPUT_HTML = ROOT / "gallery.html"
OUTPUT_DATA = ROOT / "content" / "page-owned-gallery-data.json"
OUTPUT_COMPONENT_DATA = ROOT / "content" / "component-card-gallery-data.json"
OUTPUT_GENERAL_DATA = ROOT / "content" / "general-gallery-data.json"
OUTPUT_CSS = ROOT / "page-owned-general-gallery.css"
DOMAIN = "https://lunageneralcontractors.com"
PAGE_COUNT = 1009
SCENE_COUNT = 5045
COMPONENT_PAGE_COUNT = 878
COMPONENT_COUNT = 2634
PAGE_SIZE = 24

# Categories are stable manifest keys; labels vary by page and can be lower-case
# or article-specific. The browse gallery uses one concise human label for each
# category so its Service filter is predictable rather than duplicating options.
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


CROP_FIX_CSS = """.general-gallery__grid{align-items:start}.general-gallery__card{display:grid;grid-template-rows:auto 1fr}.general-gallery__visual{display:block;width:100%;aspect-ratio:4/3;overflow:hidden;padding:0;border:0;background:#111820;color:inherit;cursor:zoom-in}.general-gallery__visual:focus-visible,.general-gallery__owner:focus-visible,.general-gallery__page:focus-visible,.general-gallery__lightbox button:focus-visible{outline:3px solid #005fcc;outline-offset:3px}.general-gallery__image{width:100%;height:100%;aspect-ratio:auto;object-fit:contain;background:#111820}.general-gallery__meta{align-content:start}.general-gallery__owner{display:inline-flex;width:max-content;min-height:44px;align-items:center;color:#1c4650;font-size:.9rem;font-weight:800;line-height:1.35;text-decoration:underline;text-underline-offset:3px}.general-gallery__lightbox{width:min(100vw - 32px,1080px);max-width:1080px;margin:auto;padding:0;border:0;border-radius:10px;background:#10181c;color:#fff;box-shadow:0 24px 70px rgba(0,0,0,.55)}.general-gallery__lightbox::backdrop{background:rgba(0,0,0,.78)}.general-gallery__lightbox-content{display:grid;gap:12px;padding:14px}.general-gallery__lightbox-top{display:flex;justify-content:flex-end}.general-gallery__lightbox-close,.general-gallery__lightbox-nav{min-width:44px;min-height:44px;border:1px solid rgba(255,255,255,.7);border-radius:4px;background:#17252b;color:#fff;font:700 1rem/1 Inter,system-ui,sans-serif;cursor:pointer}.general-gallery__lightbox-stage{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:10px}.general-gallery__lightbox-figure{min-width:0;margin:0;text-align:center}.general-gallery__lightbox-image{display:block;max-width:100%;width:100%;max-height:min(72vh,760px);margin:auto;object-fit:contain;background:#05080a}.general-gallery__lightbox-caption{display:block;margin-top:10px;font-weight:800;line-height:1.4}.general-gallery__lightbox-owner{display:inline-flex;width:max-content;min-height:44px;align-items:center;color:#f3c35d;font-weight:800;text-decoration:underline;text-underline-offset:3px}.general-gallery__lightbox-nav:disabled{opacity:.45;cursor:not-allowed}@media(max-width:680px){.general-gallery__lightbox-stage{grid-template-columns:1fr}.general-gallery__lightbox-nav{width:100%}.general-gallery__lightbox-stage [data-general-gallery-lightbox-previous]{grid-row:2}.general-gallery__lightbox-stage [data-general-gallery-lightbox-next]{grid-row:3}}"""

TYPE_FILTER_CSS = """.general-gallery__filters--typed{grid-template-columns:repeat(3,minmax(0,1fr)) auto}.general-gallery__type{width:max-content;border-radius:999px;background:#e8eef0;color:#264047;padding:3px 7px;font-size:.72rem;font-weight:800;line-height:1.2}@media(max-width:1100px){.general-gallery__filters--typed{grid-template-columns:repeat(2,minmax(0,1fr)) auto}}@media(max-width:680px){.general-gallery__filters--typed{grid-template-columns:1fr;align-items:stretch}}"""

CSS = """.general-gallery-page{background:#f5f3ee;color:#17252b}.general-gallery-hero{padding:clamp(42px,7vw,84px) 0 38px;background:linear-gradient(135deg,#0b1519,#183038);color:#fff}.general-gallery-hero .eyebrow{color:#e5b24b;font-weight:800;letter-spacing:.12em;text-transform:uppercase}.general-gallery-hero h1{max-width:820px;margin:10px 0;font:800 clamp(2.5rem,6vw,4.8rem)/.96 "Barlow Condensed",sans-serif}.general-gallery-hero p{max-width:780px;margin:0;color:#dbe5e7;line-height:1.65}.general-gallery{padding:clamp(28px,5vw,60px) 0 72px}.general-gallery__filters{display:grid;grid-template-columns:repeat(2,minmax(0,1fr)) auto;gap:14px;align-items:end;margin:0 0 22px;padding:18px;background:#fff;border:1px solid #d7dad7;border-radius:8px;box-shadow:0 8px 24px rgba(20,34,39,.08)}.general-gallery__filter{display:grid;gap:7px;font-weight:800}.general-gallery__filter select{min-height:44px;border:1px solid #7e898d;border-radius:4px;padding:8px 10px;background:#fff;color:#17252b;font:inherit}.general-gallery__apply{min-height:44px;white-space:nowrap}.general-gallery__summary{margin:0 0 18px;color:#435359;font-weight:700}.general-gallery__grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}.general-gallery__card{min-width:0;overflow:hidden;background:#fff;border:1px solid #d7dad7;border-radius:7px;box-shadow:0 8px 20px rgba(20,34,39,.08)}.general-gallery__card a{display:block;color:inherit;text-decoration:none}.general-gallery__card a:focus-visible,.general-gallery__page:focus-visible{outline:3px solid #005fcc;outline-offset:3px}.general-gallery__image{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#dce3e2}.general-gallery__meta{display:grid;gap:4px;padding:12px 13px 14px}.general-gallery__caption{font-weight:800;line-height:1.35}.general-gallery__owner{color:#53636a;font-size:.9rem;line-height:1.35}.general-gallery__pagination{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:28px}.general-gallery__page{min-width:44px;min-height:44px;border:1px solid #1a2b30;border-radius:4px;background:#17252b;color:#fff;font:700 1rem/1 Inter,system-ui,sans-serif;cursor:pointer}.general-gallery__page:disabled{opacity:.48;cursor:not-allowed}.general-gallery__status{min-width:12rem;text-align:center;color:#435359;font-weight:700}.general-gallery__nojs{margin:0 0 18px;color:#435359}.general-gallery__filters select:focus-visible{outline:3px solid #005fcc;outline-offset:2px}@media(max-width:900px){.general-gallery__grid{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:680px){.general-gallery-hero{padding:42px 0 34px}.general-gallery__filters{grid-template-columns:1fr;align-items:stretch}.general-gallery__apply{width:100%}.general-gallery__grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.general-gallery__meta{padding:10px}.general-gallery__caption{font-size:.93rem}.general-gallery__owner{font-size:.82rem}.general-gallery__pagination{gap:8px}.general-gallery__status{min-width:0;font-size:.86rem}}@media(max-width:390px){.general-gallery__grid{grid-template-columns:1fr}}"""


def fail(message: str) -> None:
    raise SystemExit(f"General gallery build failed: {message}")


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
    # The homepage's five owned scenes belong with General Contractor in the
    # public browse filter rather than creating a duplicate visible option.
    return "general-contractor" if category == "site-home" else category


def build_records() -> list[dict[str, object]]:
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(str(error))
    if not isinstance(manifest, dict) or len(manifest) != PAGE_COUNT:
        fail(f"expected {PAGE_COUNT} manifest pages")

    records: list[dict[str, object]] = []
    sources: set[str] = set()
    for owner_page, entry in manifest.items():
        if not isinstance(owner_page, str) or not isinstance(entry, dict):
            fail("malformed manifest owner")
        if entry.get("placement_hold"):
            fail(f"held page cannot appear in general gallery: {owner_page}")
        category = str(entry.get("category") or "").strip()
        service = service_for(category)
        city = city_for(entry)
        images = entry.get("images")
        if not category or not service or not isinstance(images, list) or len(images) != 5:
            fail(f"{owner_page}: expected category, label, and five images")
        for image in images:
            if not isinstance(image, dict):
                fail(f"{owner_page}: malformed image")
            source = image.get("src")
            slot = image.get("slot")
            width = image.get("width")
            height = image.get("height")
            if not isinstance(source, str) or not source.startswith("assets/images/"):
                fail(f"{owner_page}: non-public image source")
            if "library" in source.lower() or not (ROOT / source).is_file():
                fail(f"{owner_page}: missing or non-public asset {source}")
            if not all(isinstance(value, int) and value > 0 for value in (slot, width, height)):
                fail(f"{owner_page}: invalid image metadata")
            if source in sources:
                fail(f"cross-page duplicate asset: {source}")
            sources.add(source)
            caption = f"{service} · {city}"
            records.append({
                "ownerPage": owner_page,
                "category": category,
                "serviceKey": service_key_for(category),
                "service": service,
                "city": city,
                "slot": slot,
                "src": source,
                "width": width,
                "height": height,
                "caption": caption,
                "alt": f"{service} service design in {city}.",
            })
    if len(records) != SCENE_COUNT or len(sources) != SCENE_COUNT:
        fail(f"expected {SCENE_COUNT} unique assignment records")
    return sorted(records, key=lambda item: (str(item["service"]).lower(), str(item["city"]).lower(), str(item["ownerPage"]), int(item["slot"])))


def build_component_records() -> list[dict[str, object]] | None:
    """Project verified component-card images into the general browse gallery.

    The component map is optional while the source tree is prepared.  When it
    exists, it must be complete: a partial materials browse inventory is not a
    publishable state.
    """
    if not COMPONENT_MANIFEST.exists():
        return None
    try:
        component_data = json.loads(COMPONENT_MANIFEST.read_text(encoding="utf-8"))
        guide_data = json.loads(GUIDES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(str(error))
    if (
        not isinstance(component_data, dict)
        or component_data.get("schema_version") != 1
        or component_data.get("page_count") != COMPONENT_PAGE_COUNT
        or component_data.get("image_count") != COMPONENT_COUNT
        or not isinstance(component_data.get("assets"), list)
        or len(component_data["assets"]) != COMPONENT_COUNT
        or not isinstance(guide_data, list)
        or len(guide_data) != COMPONENT_PAGE_COUNT
    ):
        fail("component-card manifest does not declare the exact 878-page / 2634-image contract")
    guides = {
        row.get("file"): row
        for row in guide_data
        if isinstance(row, dict) and isinstance(row.get("file"), str)
    }
    if len(guides) != COMPONENT_PAGE_COUNT:
        fail("service-guide roster is malformed for component gallery projection")

    records: list[dict[str, object]] = []
    paths: set[str] = set()
    hashes: set[str] = set()
    slots: dict[str, set[int]] = {}
    for asset in component_data["assets"]:
        if not isinstance(asset, dict):
            fail("component-card manifest contains a non-object asset")
        owner = asset.get("page_file")
        slot = asset.get("slot")
        source = asset.get("path")
        digest = asset.get("sha256")
        subject = asset.get("subject")
        service = asset.get("service")
        city = asset.get("city")
        caption = asset.get("caption")
        alt = asset.get("alt")
        width = asset.get("width")
        height = asset.get("height")
        guide = guides.get(owner)
        if (
            not isinstance(owner, str)
            or not isinstance(guide, dict)
            or not isinstance(slot, int)
            or slot not in {1, 2, 3}
            or not isinstance(source, str)
            or "\\" in source
            or ":" in source
            or ".." in source
            or not source.startswith("assets/images/illustrations/component-owned/")
            or not source.endswith(".webp")
            or not isinstance(digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or not all(isinstance(value, str) and value.strip() for value in (subject, service, city, caption, alt))
            or not all(isinstance(value, int) and value > 0 for value in (width, height))
            or not (ROOT / source).is_file()
        ):
            fail(f"invalid component gallery asset for {owner!r}")
        if source in paths or digest in hashes:
            fail(f"component gallery projection contains a duplicate source or hash: {source}")
        paths.add(source)
        hashes.add(digest)
        slots.setdefault(owner, set()).add(slot)
        category = str(guide.get("key") or "").strip()
        if not category:
            fail(f"component gallery asset lacks a guide category: {owner}")
        records.append(
            {
                "ownerPage": owner,
                "category": category,
                "serviceKey": service_key_for(category),
                "service": service.strip(),
                "city": city.strip(),
                "slot": slot,
                "src": source,
                "width": width,
                "height": height,
                "caption": caption.strip(),
                "alt": alt.strip(),
                "sha256": digest,
                "kind": "component-card",
                "mediaType": "materials-equipment",
                "typeLabel": "Materials & equipment",
            }
        )
    if set(slots) != set(guides) or any(values != {1, 2, 3} for values in slots.values()):
        fail("component gallery projection does not cover every guide page with three slots")
    if len(records) != COMPONENT_COUNT or len(paths) != COMPONENT_COUNT or len(hashes) != COMPONENT_COUNT:
        fail("component gallery projection is not exactly 2634 unique records")
    return sorted(records, key=lambda item: (str(item["service"]).lower(), str(item["city"]).lower(), str(item["ownerPage"]), int(item["slot"])))


def combined_records(page_records: list[dict[str, object]], component_records: list[dict[str, object]]) -> list[dict[str, object]]:
    page_projection = [
        {
            **record,
            "kind": "page-owned-scene",
            "mediaType": "service-design",
            "typeLabel": "Service & design",
        }
        for record in page_records
    ]
    records = page_projection + component_records
    paths = [str(record["src"]) for record in records]
    if len(records) != SCENE_COUNT + COMPONENT_COUNT or len(paths) != len(set(paths)):
        fail("combined general gallery is not an exclusive 7679-record projection")
    return sorted(
        records,
        key=lambda item: (
            str(item["service"]).lower(),
            str(item["city"]).lower(),
            str(item["ownerPage"]),
            str(item["mediaType"]),
            int(item["slot"]),
        ),
    )


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def card(record: dict[str, object]) -> str:
    badge = ""
    if isinstance(record.get("typeLabel"), str):
        badge = f'<span class="general-gallery__type">{esc(record["typeLabel"])}</span>'
    return (
        '<article class="general-gallery__card" data-general-gallery-card="true">'
        f'<a class="general-gallery__visual" href="{esc(record["ownerPage"])}" aria-label="View {esc(record["caption"])} service page">'
        f'<img class="general-gallery__image" src="{esc(record["src"])}" alt="{esc(record["alt"])}" '
        f'width="{record["width"]}" height="{record["height"]}" loading="lazy" decoding="async">'
        '</a><span class="general-gallery__meta">'
        f'<span class="general-gallery__caption">{esc(record["caption"])}</span>'
        f'{badge}'
        f'<a class="general-gallery__owner" href="{esc(record["ownerPage"])}">View service page</a>'
        '</span></article>'
    )


def build_html(records: list[dict[str, object]], component_enabled: bool) -> str:
    source = "content/general-gallery-data.json" if component_enabled else "content/page-owned-gallery-data.json"
    total = len(records)
    title = "Service &amp; Materials Gallery" if component_enabled else "Service &amp; Design Gallery"
    heading = "Browse service design and materials images" if component_enabled else "Browse service and design images"
    description = (
        "Browse Luna General Contractors service design and materials images by service and Dallas-Fort Worth area."
        if component_enabled
        else "Browse Luna General Contractors service and design images by service and Dallas-Fort Worth area."
    )
    hero_copy = (
        "Browse service design and materials images by service and Dallas-Fort Worth area. Open an image to view it in the gallery, or use its service-page link for details."
        if component_enabled
        else "Browse service and design images by service and Dallas-Fort Worth area. Open an image to view it in the gallery, or use its service-page link for details."
    )
    typed_class = " general-gallery__filters--typed" if component_enabled else ""
    type_filter = '''
        <label class="general-gallery__filter" for="general-gallery-type">Image type
          <select id="general-gallery-type" name="type" data-general-gallery-type>
            <option value="">All imagery</option>
            <option value="service-design">Service &amp; design</option>
            <option value="materials-equipment">Materials &amp; equipment</option>
          </select>
        </label>''' if component_enabled else ""
    css_version = "20261025-component-gallery-1" if component_enabled else "20261025-full-image-1"
    script_version = "20261025-component-gallery-1" if component_enabled else "20261025-gallery-lightbox-1"
    fallback = "".join(card(record) for record in records[:PAGE_SIZE])
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Luna General Contractors</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="noindex, follow">
  <link rel="canonical" href="{DOMAIN}/gallery.html">
  <link rel="icon" href="favicon.svg?v=2" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&amp;family=Inter:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css?v=20261024-home-trust-icons-1">
  <link rel="stylesheet" href="page-owned-imagery.css?v=20261025-full-image-1">
  <link rel="stylesheet" href="page-owned-general-gallery.css?v={css_version}">
</head>
<body class="general-gallery-page">
  <a class="skip-link" href="#main-content">Skip to content</a>
  <main id="main-content">
    <section class="general-gallery-hero">
      <div class="container">
        <p class="eyebrow">Luna General Contractors</p>
        <h1>{title}</h1>
        <p>{hero_copy}</p>
      </div>
    </section>
    <section class="general-gallery container" data-general-gallery="true" data-general-gallery-source="{source}" aria-labelledby="general-gallery-title">
      <h2 id="general-gallery-title" class="sr-only">{heading}</h2>
      <form class="general-gallery__filters{typed_class}" data-general-gallery-filters>
        <label class="general-gallery__filter" for="general-gallery-service">Service
          <select id="general-gallery-service" name="service" data-general-gallery-service>
            <option value="">All services</option>
          </select>
        </label>
        <label class="general-gallery__filter" for="general-gallery-city">Area
          <select id="general-gallery-city" name="city" data-general-gallery-city>
            <option value="">All areas</option>
          </select>
        </label>{type_filter}
        <button class="btn btn-gold general-gallery__apply" type="submit">Apply filters</button>
      </form>
      <p class="general-gallery__summary" data-general-gallery-summary aria-live="polite">Showing the first {PAGE_SIZE} of {total} images.</p>
      <noscript><p class="general-gallery__nojs">Showing the first {PAGE_SIZE} images. Visit an individual service page to browse its full set.</p></noscript>
      <div class="general-gallery__grid" data-general-gallery-results>{fallback}</div>
      <div class="general-gallery__pagination" data-general-gallery-pagination hidden>
        <button class="general-gallery__page" type="button" data-general-gallery-previous aria-label="Show previous gallery page" disabled>Previous</button>
        <span class="general-gallery__status" data-general-gallery-status aria-live="polite">Page 1</span>
        <button class="general-gallery__page" type="button" data-general-gallery-next aria-label="Show next gallery page">Next</button>
      </div>
      <dialog class="general-gallery__lightbox" data-general-gallery-lightbox aria-labelledby="general-gallery-lightbox-caption">
        <div class="general-gallery__lightbox-content">
          <div class="general-gallery__lightbox-top"><button class="general-gallery__lightbox-close" type="button" data-general-gallery-lightbox-close aria-label="Close image viewer">Close</button></div>
          <div class="general-gallery__lightbox-stage">
            <button class="general-gallery__lightbox-nav" type="button" data-general-gallery-lightbox-previous aria-label="Previous image">Previous</button>
            <figure class="general-gallery__lightbox-figure"><img class="general-gallery__lightbox-image" data-general-gallery-lightbox-image alt="" decoding="async"><figcaption id="general-gallery-lightbox-caption" class="general-gallery__lightbox-caption" data-general-gallery-lightbox-caption></figcaption><a class="general-gallery__lightbox-owner" data-general-gallery-lightbox-owner href="#">View service page</a></figure>
            <button class="general-gallery__lightbox-nav" type="button" data-general-gallery-lightbox-next aria-label="Next image">Next</button>
          </div>
        </div>
      </dialog>
    </section>
  </main>
  <footer></footer>
  <script src="script.js?v={script_version}"></script>
</body>
</html>
'''


def data_json(records: list[dict[str, object]]) -> str:
    return json.dumps(records, ensure_ascii=False, separators=(",", ":")) + "\n"


def write_or_check(path: Path, content: str, check: bool, stale: list[str]) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return
    if check:
        stale.append(path.relative_to(ROOT).as_posix())
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    records = build_records()
    components = build_component_records()
    gallery_records = combined_records(records, components) if components is not None else records
    stale: list[str] = []
    write_or_check(OUTPUT_DATA, data_json(records), args.check, stale)
    if components is not None:
        write_or_check(OUTPUT_COMPONENT_DATA, data_json(components), args.check, stale)
        write_or_check(OUTPUT_GENERAL_DATA, data_json(gallery_records), args.check, stale)
    write_or_check(OUTPUT_HTML, build_html(gallery_records, components is not None), args.check, stale)
    write_or_check(OUTPUT_CSS, CSS + CROP_FIX_CSS + (TYPE_FILTER_CSS if components is not None else "") + "\n", args.check, stale)
    if stale:
        print("General gallery outputs are stale: " + ", ".join(stale), file=sys.stderr)
        return 1
    print(f"General gallery is current: {len(gallery_records)} records, {PAGE_SIZE}-card pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
