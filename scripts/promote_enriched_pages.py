#!/usr/bin/env python3
"""Promote the final 17 enriched pages into the public sitemap.

The site generators can rebuild these pages. This idempotent post-processing
step restores verified-work context, complete social metadata and sitemap
coverage without claiming that a DFW portfolio image came from a specific city.
"""

from __future__ import annotations

import csv
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lunageneralcontractors.com"
LASTMOD = "2026-09-06"
START = "<!-- READY_PAGE_ENRICHMENT_START -->"
END = "<!-- READY_PAGE_ENRICHMENT_END -->"

CITY_PAGES = {
    "addison.html": {
        "city": "Addison",
        "title": "Addison, TX Roofing & General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Addison, TX, with written scopes and coordinated trades. Call Luna at (817) 784-5998 for a free estimate.",
        "planning": "Addison projects may combine occupied homes, townhomes and commercial spaces. Before pricing the work, we separate access requirements, protection, trade sequencing and any urgent weather-exposure items from the planned improvements.",
        "checks": [
            "Confirm residential or commercial access and allowable working areas.",
            "Inspect roof penetrations, flashing, transitions and drainage before selecting a repair.",
            "Identify interior protection when exterior damage has reached ceilings or walls.",
            "Write exclusions and concealed-condition allowances into the scope.",
        ],
    },
    "aledo.html": {
        "city": "Aledo",
        "title": "Aledo, TX Roofing & General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Aledo, TX, with site-specific scopes and coordinated trades. Call (817) 784-5998 for a free estimate.",
        "planning": "Aledo estimates should account for the actual lot, building access and connections between roofing, drainage and exterior finishes. Material matching and delivery planning are confirmed before the scope is finalized.",
        "checks": [
            "Confirm delivery access, work-area protection and material staging.",
            "Review roof slopes, penetrations, flashing and runoff at the property.",
            "Compare existing exterior materials before promising a visual match.",
            "Sequence roofing, carpentry, siding, drywall and paint where scopes overlap.",
        ],
    },
    "benbrook.html": {
        "city": "Benbrook",
        "title": "Benbrook, TX Roofing & General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Benbrook, TX, based on the property's visible conditions. Call Luna at (817) 784-5998 for a free estimate.",
        "planning": "For Benbrook repairs, the first visible stain or damaged shingle may not define the full scope. We trace likely entry points, examine roof-to-wall details and document connected interior finishes before recommending work.",
        "checks": [
            "Examine roof edges, wall transitions, chimneys, vents and drainage paths.",
            "Photograph visible wind or hail conditions before temporary or permanent repairs.",
            "Trace interior staining to the likely exterior source instead of patching only the finish.",
            "Confirm cleanup, access and protection requirements in writing.",
        ],
    },
    "denton.html": {
        "city": "Denton",
        "title": "Denton, TX Roofing & General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Denton, TX, with clear scopes for homes, rentals and businesses. Call (817) 784-5998 for an estimate.",
        "planning": "Denton work can involve established buildings, newer additions, rentals and occupied commercial areas. A useful inspection separates existing repairs from new damage and confirms which trades must be completed first.",
        "checks": [
            "Document previous repairs and the condition of adjoining materials.",
            "Review ventilation, roof penetrations, flashing and drainage together.",
            "Plan access and working hours around occupants or business operations.",
            "Verify finish matching before drywall, flooring or paint work begins.",
        ],
    },
    "flower-mound.html": {
        "city": "Flower Mound",
        "title": "Flower Mound, TX General Contractor | Luna",
        "description": "Roofing, remodeling, restoration and commercial construction in Flower Mound, TX. Call Luna at (817) 784-5998 for a free project estimate.",
        "planning": "Flower Mound projects often connect exterior protection with interior finish work. We document roof and wall tie-ins, confirm material lead times and organize the trade sequence around the occupied property.",
        "checks": [
            "Review roofing, drainage and exterior-envelope details as one system.",
            "Confirm how new materials will connect to existing finishes.",
            "Identify owner, property-management or association requirements before scheduling.",
            "Plan protection and daily access for occupied spaces.",
        ],
    },
    "highland-village.html": {
        "city": "Highland Village",
        "title": "Highland Village, TX General Contractor | Luna",
        "description": "Roofing, remodeling and restoration in Highland Village, TX, with coordinated trades and written scopes. Call (817) 784-5998 for an estimate.",
        "planning": "Highland Village scopes should connect roof protection, exterior details and any affected interior finishes. We document existing materials and access needs before recommending repair, replacement or coordinated remodeling.",
        "checks": [
            "Inspect roof edges, penetrations, ventilation, flashing and visible drainage conditions.",
            "Protect landscaping, entries and interior traffic paths during the work.",
            "Record material and finish selections before ordering.",
            "Sequence roofing, carpentry, drywall and painting when more than one trade is involved.",
        ],
    },
}

ARTICLE_PAGES = {
    "best-flooring-for-pets-grand-prairie.html": {
        "title": "Pet-Friendly Flooring in Grand Prairie, TX | Luna",
        "description": "Compare pet-friendly flooring for Grand Prairie homes by scratch resistance, moisture, traction, cleanup and subfloor needs. Request a free estimate.",
        "image": "dfw-gray-plank-flooring-installation-2018.jpg", "width": 669, "height": 891,
        "alt": "Finished gray wood-look plank flooring installed by Luna General Contractors in DFW",
        "caption": "Completed plank-flooring work from Luna's documented DFW project portfolio.",
        "heading": "Pet-friendly flooring inspection checklist",
        "checks": ["Pet size, activity level and traction needs", "Likely water-bowl and accident exposure", "Direct sunlight and room temperature changes", "Subfloor flatness, moisture and damaged areas", "Transitions, stairs, doors and adjoining floor heights"],
        "proof": "The portfolio photo shows completed Luna flooring work. It demonstrates installation quality but is not presented as the exact Grand Prairie home discussed in this guide.",
        "proof_link": "flooring.html", "proof_label": "View verified flooring photos",
    },
    "commercial-tenant-improvement-planning-irving.html": {
        "title": "Commercial Tenant Improvements in Irving, TX | Luna",
        "description": "Plan an Irving tenant improvement around permits, existing systems, access, trade sequencing, inspections and turnover. Request a written project scope.",
        "image": "dfw-commercial-deli-finish-out-2019.jpg", "width": 669, "height": 891,
        "alt": "Completed commercial deli finish-out with service counter, cabinets, flooring and lighting",
        "caption": "Completed commercial finish-out from Luna's documented DFW project portfolio.",
        "heading": "Tenant-improvement preconstruction checklist",
        "checks": ["Lease and landlord construction requirements", "Permit, plan-review and inspection responsibilities", "Existing electrical, plumbing and HVAC capacity", "Occupied-hours, deliveries, dust control and public access", "Long-lead finishes, final cleaning and turnover documentation"],
        "proof": "This completed DFW finish-out demonstrates coordinated cabinets, counter, flooring and lighting. It is included as workmanship evidence and is not represented as the specific Irving property.",
        "proof_link": "commercial.html", "proof_label": "View commercial project photos",
    },
    "drywall-texture-matching-desoto.html": {
        "title": "Drywall Texture Matching in DeSoto, TX | Luna",
        "description": "Learn how DeSoto drywall patches are blended by identifying texture, widening the repair, priming and matching paint sheen. Request a free estimate.",
        "image": "drywall-commercial-project.jpg", "width": 1600, "height": 900,
        "alt": "Commercial drywall construction in progress by Luna General Contractors",
        "caption": "Documented drywall construction in progress from Luna's DFW portfolio.",
        "heading": "What to record before matching texture",
        "checks": ["Texture pattern under direct and side lighting", "Patch dimensions and nearby joints or corners", "Whether the leak or movement that caused damage is corrected", "Existing primer, paint color and sheen", "A dry sample area before coating the full repair"],
        "proof": "The project image verifies Luna's drywall experience. Texture matching still requires an on-site sample because lighting, previous paint and application technique change the final appearance.",
        "proof_link": "drywall.html", "proof_label": "View drywall project photos",
    },
    "exterior-paint-preparation-cedar-hill.html": {
        "title": "Exterior Paint Preparation in Cedar Hill, TX | Luna",
        "description": "Prepare a Cedar Hill exterior with cleaning, scraping, repairs, caulk and spot primer before paint. See the checklist and request an estimate.",
        "image": "siding-after.jpg", "width": 1600, "height": 1200,
        "alt": "Completed residential siding and exterior finish project by Luna General Contractors",
        "caption": "Completed siding and exterior-finish work from Luna's documented DFW portfolio.",
        "heading": "Exterior preparation walk-through checklist",
        "checks": ["Loose coating, chalking, mildew and surface contamination", "Rot, open joints and damaged siding or trim", "Failed caulk around openings and penetrations", "Bare areas that require the correct primer", "Weather window, masking, landscaping protection and cure time"],
        "proof": "The photograph documents completed Luna exterior work. Paint cannot correct rot, movement or failed weather details, so those conditions belong in the repair scope before coating.",
        "proof_link": "painting.html", "proof_label": "Review Luna's painting process",
    },
    "kitchen-remodel-planning-mansfield.html": {
        "title": "Mansfield Kitchen Remodel Planning | Luna",
        "description": "Plan a Mansfield kitchen remodel around layout, cabinets, countertops, appliances, lighting, plumbing and construction sequence. Request an estimate.",
        "image": "dfw-kitchen-remodel-quartz-island-2018.jpg", "width": 669, "height": 891,
        "alt": "Completed white and gray kitchen remodel with quartz island by Luna General Contractors",
        "caption": "Completed kitchen remodeling work from Luna's documented DFW project portfolio.",
        "heading": "Decisions to confirm before demolition",
        "checks": ["Final cabinet plan and appliance specifications", "Countertop overhangs, sink, faucet and backsplash dimensions", "Electrical, lighting, ventilation and plumbing changes", "Flooring transitions and finished floor height", "Material lead times and the order of inspections and trades"],
        "proof": "For a Mansfield-specific example, Luna's documented gray subway-tile backsplash case records the materials, detailed cuts and approximately two-day installation without adding undocumented claims.",
        "proof_link": "gray-subway-kitchen-backsplash-mansfield.html", "proof_label": "See the verified Mansfield kitchen case",
    },
    "roof-repair-vs-replacement-arlington.html": {
        "title": "Roof Repair or Replacement in Arlington, TX | Luna",
        "description": "Compare roof repair and replacement in Arlington using age, damage extent, flashing, decking and leak history. Request a documented inspection.",
        "image": "dfw-roof-replacement-brick-home-2019.jpg", "width": 1188, "height": 891,
        "alt": "Completed architectural shingle roof on a brick home by Luna General Contractors",
        "caption": "Completed shingle-roof work from Luna's documented DFW project portfolio.",
        "heading": "Information needed for a repair-or-replace decision",
        "checks": ["Roof age, material and available matching products", "Number and location of leaks or impact areas", "Flashing, penetrations, valleys, edges and ventilation", "Decking condition visible from accessible areas", "Prior repairs, warranties and the owner's expected time in the property"],
        "proof": "The image documents completed Luna roofing work in DFW. A photograph alone cannot determine the correct Arlington scope; the decision requires inspection of the actual roof.",
        "proof_link": "roofing.html", "proof_label": "View verified roofing photos",
    },
    "storm-damage-documentation-fort-worth.html": {
        "title": "Documenting Storm Damage in Fort Worth, TX | Luna",
        "description": "Document Fort Worth storm damage safely with dated photos, affected rooms, temporary repairs, estimates and receipts. Request a construction scope.",
        "image": "dfw-commercial-ceiling-damage-documentation-2024.jpg", "width": 669, "height": 891,
        "alt": "Commercial ceiling damage documented for a construction repair scope in DFW",
        "caption": "Visible ceiling damage documented during development of a DFW construction repair scope.",
        "heading": "Storm file checklist",
        "checks": ["Storm date and when each condition was first observed", "Wide and close photos taken from safe accessible locations", "Room-by-room list of stains, openings and damaged finishes", "Temporary protection invoices, receipts and photographs", "Contractor scopes, carrier correspondence and revision dates"],
        "proof": "Luna can document visible construction conditions and prepare a repair scope. The insurance carrier and policy determine coverage; documentation should describe observed damage without promising a claim outcome.",
        "proof_link": "insurance-claims.html", "proof_label": "Review claim-documentation services",
    },
    "walk-in-shower-cost-midlothian.html": {
        "title": "Midlothian Walk-In Shower Cost Factors | Luna",
        "description": "Understand Midlothian walk-in shower cost factors: demolition, plumbing, waterproofing, tile, glass and hidden conditions. Request an estimate.",
        "image": "dfw-bathroom-remodel-glass-shower-2020.jpg", "width": 1188, "height": 891,
        "alt": "Finished bathroom remodel with glass shower by Luna General Contractors",
        "caption": "Completed glass-shower remodel from Luna's documented DFW project portfolio.",
        "heading": "Measurements and selections that affect the scope",
        "checks": ["Existing shower or tub dimensions and demolition limits", "Drain location, plumbing changes and subfloor condition", "Waterproofing system, niches, benches and curb design", "Tile size, pattern, edge details and grout selection", "Glass configuration, fixtures, ventilation and accessories"],
        "proof": "Luna's Midlothian master-bathroom case provides location-specific project evidence. Every new shower still needs its own measurements and concealed-condition allowance.",
        "proof_link": "luxury-master-bathroom-remodel-midlothian.html", "proof_label": "See the verified Midlothian bathroom case",
    },
    "water-damage-rebuild-process-dallas.html": {
        "title": "Dallas Water-Damage Rebuild Process | Luna",
        "description": "Follow the Dallas water-damage rebuild sequence from source correction and drying through framing, drywall, paint, flooring and final inspection.",
        "image": "dfw-interior-rebuild-framing-2018.jpg", "width": 1188, "height": 891,
        "alt": "Interior framing exposed during reconstruction work by Luna General Contractors",
        "caption": "Documented interior reconstruction work from Luna's DFW project portfolio.",
        "heading": "Rebuild readiness checklist",
        "checks": ["Water source corrected and affected areas released for reconstruction", "Damaged materials and repair boundaries documented", "Framing, insulation and mechanical conditions reviewed", "Cabinet, drywall, texture, paint and flooring matches confirmed", "Trade sequence, inspections and final cleaning included in the scope"],
        "proof": "The photograph documents Luna reconstruction work with framing exposed. It is evidence of field experience, not a claim that every Dallas loss needs the same demolition or repair sequence.",
        "proof_link": "mitigation.html", "proof_label": "Review restoration and rebuild services",
    },
    "wood-fence-repair-vs-replacement-waxahachie.html": {
        "title": "Fence Repair or Replacement in Waxahachie, TX | Luna",
        "description": "Compare wood fence repair and replacement in Waxahachie by post condition, alignment, damaged sections, gates and finish. Request an estimate.",
        "image": "fencing-project-two.jpg", "width": 1600, "height": 1200,
        "alt": "Completed stained wood privacy fence by Luna General Contractors",
        "caption": "Completed stained privacy-fence work from Luna's documented DFW project portfolio.",
        "heading": "Fence condition checklist",
        "checks": ["Loose, leaning or rotted posts and their spacing", "Rail condition and the number of damaged pickets", "Gate frame, hinges, latch and ground clearance", "Property access, utilities and drainage near the fence line", "Desired stain or sealer and replacement-material match"],
        "proof": "The image verifies completed Luna fence work. The repair-or-replacement recommendation for a Waxahachie property depends on the percentage of reusable posts, rails and sections observed on site.",
        "proof_link": "fencing.html", "proof_label": "View verified fencing photos",
    },
}

REVIEWS = {
    "reviews.html": {
        "title": "Customer Reviews | Luna General Contractors",
        "description": "Read sourced Google, Yelp and Nextdoor feedback for Luna General Contractors, then compare documented DFW projects and request a free estimate.",
        "image": "dfw-bathroom-remodel-glass-shower-2020.jpg", "width": 1188, "height": 891,
        "alt": "Finished bathroom remodel with glass shower by Luna General Contractors",
    }
}

PROMOTED = set(CITY_PAGES) | set(ARTICLE_PAGES) | set(REVIEWS)
HUB_PAGES = {"service-areas.html", "articles.html"}


def replace_tag_value(source: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, source, count=1, flags=re.I | re.S)
    if count != 1:
        raise SystemExit(f"Unable to update {label}")
    return updated


def social_metadata(config: dict[str, object], canonical: str, og_type: str) -> str:
    title = html.escape(str(config["title"]), quote=True)
    description = html.escape(str(config["description"]), quote=True)
    image_url = f'{DOMAIN}/{config["image"]}'
    alt = html.escape(str(config["alt"]), quote=True)
    return (
        f'<meta property="og:type" content="{html.escape(og_type, quote=True)}">'
        f'<meta property="og:title" content="{title}">'
        f'<meta property="og:description" content="{description}">'
        f'<meta property="og:url" content="{html.escape(canonical, quote=True)}">'
        f'<meta property="og:image" content="{image_url}">'
        f'<meta property="og:image:width" content="{config["width"]}">'
        f'<meta property="og:image:height" content="{config["height"]}">'
        f'<meta property="og:image:alt" content="{alt}">'
        '<meta property="og:site_name" content="Luna General Contractors">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{title}">'
        f'<meta name="twitter:description" content="{description}">'
        f'<meta name="twitter:image" content="{image_url}">'
        f'<meta name="twitter:image:alt" content="{alt}">'
    )


def update_head(source: str, config: dict[str, object]) -> str:
    title = html.escape(str(config["title"]), quote=False)
    description = html.escape(str(config["description"]), quote=True)
    source = replace_tag_value(source, r"<title>[\s\S]*?</title>", f"<title>{title}</title>", "title")
    source = replace_tag_value(source, r'<meta\b[^>]*\bname=["\']description["\'][^>]*>', f'<meta name="description" content="{description}">', "description")
    canonical_match = re.search(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*\bhref=["\']([^"\']+)', source, re.I)
    if not canonical_match:
        raise SystemExit("Missing canonical insertion point")
    canonical = html.unescape(canonical_match.group(1))
    type_match = re.search(r'<meta\b[^>]*\bproperty=["\']og:type["\'][^>]*\bcontent=["\']([^"\']+)', source, re.I)
    og_type = html.unescape(type_match.group(1)) if type_match else "website"
    for key in ("og:type", "og:title", "og:description", "og:url", "og:image", "og:image:width", "og:image:height", "og:image:alt", "og:site_name"):
        source = re.sub(rf'<meta\b[^>]*\bproperty=["\']{re.escape(key)}["\'][^>]*>\s*', "", source, flags=re.I)
    for key in ("twitter:card", "twitter:title", "twitter:description", "twitter:image", "twitter:image:alt"):
        source = re.sub(rf'<meta\b[^>]*\bname=["\']{re.escape(key)}["\'][^>]*>\s*', "", source, flags=re.I)
    marker = re.search(r'<link\b[^>]*\brel=["\']canonical["\'][^>]*>', source, re.I)
    if not marker:
        raise SystemExit("Missing canonical insertion point")
    return source[: marker.end()] + social_metadata(config, canonical, og_type) + source[marker.end() :]


def update_schema(source: str, config: dict[str, object], page_kind: str) -> str:
    image_url = f'{DOMAIN}/{config["image"]}'

    def transform(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)
        schema_type = data.get("@type")
        types = set(schema_type if isinstance(schema_type, list) else [schema_type])
        target = page_kind == "article" and "Article" in types
        target = target or page_kind == "city" and bool(types & {"LocalBusiness", "GeneralContractor", "RoofingContractor"})
        target = target or page_kind == "reviews" and "GeneralContractor" in types
        if not target:
            return match.group(0)
        data["image"] = image_url
        if page_kind == "article":
            data["dateModified"] = LASTMOD
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    pattern = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)', re.I)
    updated, count = pattern.subn(transform, source)
    if count == 0:
        raise SystemExit("No JSON-LD blocks found")
    return updated


def clear_block(source: str) -> str:
    return re.sub(re.escape(START) + r"[\s\S]*?" + re.escape(END), "", source)


def city_block(config: dict[str, object]) -> str:
    city = html.escape(str(config["city"]))
    checks = "".join(f"<li>{html.escape(item)}</li>" for item in config["checks"])
    return (
        f'{START}<section data-ready-page-enrichment><div class="local-grid" style="margin:48px 0">'
        '<div><p class="eyebrow gold">Site-Specific Planning</p>'
        f'<h2>What We Verify Before an Estimate in {city}</h2><p>{html.escape(str(config["planning"]))}</p>'
        f'<ul>{checks}</ul><p><a href="projects.html"><strong>View documented DFW projects →</strong></a> '
        '<a href="reviews.html"><strong>Read sourced customer reviews →</strong></a></p></div>'
        '<figure class="local-card" style="margin:0"><img src="dfw-roof-replacement-brick-home-2019.jpg" '
        'alt="Completed shingle roof on a brick home by Luna General Contractors in DFW" width="1188" height="891" '
        'loading="lazy" decoding="async" style="display:block;width:100%;height:auto">'
        f'<figcaption style="margin-top:12px">Verified Luna roofing work from the DFW portfolio. This photograph is not represented as a project completed in {city}.</figcaption>'
        f'</figure></div></section>{END}'
    )


def article_block(config: dict[str, object]) -> str:
    checks = "".join(f"<li>{html.escape(item)}</li>" for item in config["checks"])
    return (
        f'{START}<figure class="seo-article-photo">'
        f'<img src="{config["image"]}" alt="{html.escape(str(config["alt"]), quote=True)}" width="{config["width"]}" height="{config["height"]}" loading="lazy" decoding="async">'
        f'<figcaption>{html.escape(str(config["caption"]))}</figcaption></figure>'
        f'<section data-ready-page-enrichment><h2>{html.escape(str(config["heading"]))}</h2><ul class="seo-checklist">{checks}</ul>'
        f'<p>{html.escape(str(config["proof"]))}</p><p><a class="seo-text-link" href="{config["proof_link"]}">{html.escape(str(config["proof_label"]))} →</a></p></section>{END}'
    )


def reviews_block() -> str:
    config = REVIEWS["reviews.html"]
    return (
        f'{START}<section class="source-box" data-ready-page-enrichment><h2>Compare Reviews With Documented Work</h2>'
        '<p>The review summaries identify their public sources. The project pages separately document photographs, city, scope, materials and dates when those facts are available.</p>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px;align-items:center">'
        f'<img src="{config["image"]}" alt="{html.escape(str(config["alt"]), quote=True)}" width="{config["width"]}" height="{config["height"]}" loading="lazy" decoding="async" style="display:block;width:100%;height:auto;border-radius:12px">'
        '<div><p><strong>Check both forms of evidence:</strong> read the original review source, then compare Luna\'s documented project records and photographs.</p>'
        '<p><a class="source-link gold" href="projects.html">View documented projects →</a> '
        '<a class="source-link" href="proyecto-backsplash-cocina-mansfield.html">Caso en español →</a></p></div></div></section>'
        f'{END}'
    )


def service_area_links_block() -> str:
    cards = "".join(
        f'<article class="seo-city-card"><h2><a href="{name}">{html.escape(str(config["city"]))}</a></h2>'
        f'<p>{html.escape(str(config["planning"]))}</p>'
        f'<a class="seo-text-link" href="{name}">View {html.escape(str(config["city"]))} services →</a></article>'
        for name, config in CITY_PAGES.items()
    )
    return (
        f'{START}<section class="seo-section" data-ready-page-enrichment><div class="container">'
        '<div class="section-heading"><p class="eyebrow gold">Additional Service Areas</p>'
        '<h2>Property-Specific Planning Across DFW</h2>'
        '<p>These city pages explain what Luna reviews before preparing a roofing, remodeling or restoration scope.</p></div>'
        f'<div class="seo-city-grid">{cards}</div></div></section>{END}'
    )


def article_links_block() -> str:
    cards = "".join(
        f'<article class="seo-city-card"><p class="eyebrow gold">Local Planning Guide</p>'
        f'<h2><a href="{name}">{html.escape(str(config["title"]).split(" | Luna")[0])}</a></h2>'
        f'<p>{html.escape(str(config["description"]))}</p>'
        f'<a class="seo-text-link" href="{name}">Read guide →</a></article>'
        for name, config in ARTICLE_PAGES.items()
    )
    return (
        f'{START}<section class="seo-section" data-ready-page-enrichment><div class="container">'
        '<div class="section-heading"><p class="eyebrow gold">More Local Resources</p>'
        '<h2>Inspection and Project-Planning Guides</h2>'
        '<p>Use these checklists to prepare for a site visit and compare options before requesting a written scope.</p></div>'
        f'<div class="seo-city-grid">{cards}</div></div></section>{END}'
    )


def enrich_city(path: Path, config: dict[str, object]) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    image_config = {**config, "image": "dfw-roof-replacement-brick-home-2019.jpg", "width": 1188, "height": 891, "alt": "Completed shingle roof on a brick home by Luna General Contractors in DFW"}
    source = update_head(source, image_config)
    source = update_schema(source, image_config, "city")
    anchor = f'<h2>Services Available in {config["city"]}</h2>'
    if anchor not in source:
        raise SystemExit(f"{path.name}: city insertion point not found")
    source = source.replace(anchor, city_block(config) + anchor, 1)
    path.write_text(source, encoding="utf-8")


def enrich_article(path: Path, config: dict[str, object]) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    source = update_head(source, config)
    source = update_schema(source, config, "article")
    lead = re.search(r'<p class="seo-lead">[\s\S]*?</p>', source, re.I)
    if not lead:
        raise SystemExit(f"{path.name}: article lead insertion point not found")
    block = article_block(config)
    source = source[: lead.end()] + block + source[lead.end() :]
    path.write_text(source, encoding="utf-8")


def enrich_reviews(path: Path, config: dict[str, object]) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    source = update_head(source, config)
    source = update_schema(source, config, "reviews")
    anchor = '<div class="review-list">'
    if anchor not in source:
        raise SystemExit("reviews.html: review-list insertion point not found")
    source = source.replace(anchor, reviews_block() + anchor, 1)
    path.write_text(source, encoding="utf-8")


def enrich_hub(path: Path, block: str) -> None:
    source = clear_block(path.read_text(encoding="utf-8"))
    anchor = "</main>"
    if anchor not in source:
        raise SystemExit(f"{path.name}: main insertion point not found")
    source = source.replace(anchor, block + anchor, 1)
    path.write_text(source, encoding="utf-8")


def remove_promoted_classifications() -> None:
    inventory = ROOT / "seo" / "sitemap-exclusions.csv"
    with inventory.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [row for row in reader if row["path"].strip() not in PROMOTED]
        fields = reader.fieldnames
    if not fields:
        raise SystemExit("Classification inventory has no header")
    with inventory.open("w", newline="", encoding="utf-8") as handle:
        handle.write(",".join(fields) + "\n")
        writer = csv.DictWriter(handle, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(rows)


def update_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    source = path.read_text(encoding="utf-8")
    priorities = {name: "0.9" for name in CITY_PAGES}
    priorities.update({name: "0.7" for name in ARTICLE_PAGES})
    priorities["reviews.html"] = "0.8"
    additions = []
    for name in sorted(PROMOTED):
        url = f"{DOMAIN}/{name}"
        block_re = re.compile(rf'<url><loc>{re.escape(url)}</loc>[\s\S]*?</url>')
        match = block_re.search(source)
        entry = f'<url><loc>{url}</loc><lastmod>{LASTMOD}</lastmod><changefreq>monthly</changefreq><priority>{priorities[name]}</priority></url>'
        if match:
            source = source[: match.start()] + entry + source[match.end() :]
        else:
            additions.append("  " + entry + "\n")
    if additions:
        source = source.replace("</urlset>", "".join(additions) + "</urlset>", 1)
    for name in sorted(HUB_PAGES):
        url = f"{DOMAIN}/{name}"
        block_re = re.compile(rf'(<url><loc>{re.escape(url)}</loc>)([\s\S]*?)(</url>)')
        match = block_re.search(source)
        if not match:
            raise SystemExit(f"{name}: existing sitemap entry not found")
        middle = re.sub(r'<lastmod>[^<]+</lastmod>', f'<lastmod>{LASTMOD}</lastmod>', match.group(2), count=1)
        source = source[: match.start()] + match.group(1) + middle + match.group(3) + source[match.end() :]
    path.write_text(source, encoding="utf-8")


def validate() -> None:
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    inventory = (ROOT / "seo" / "sitemap-exclusions.csv").read_text(encoding="utf-8")
    for name in sorted(PROMOTED):
        source = (ROOT / name).read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", source, re.I | re.S)
        description = re.search(r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)', source, re.I)
        if not title or len(html.unescape(title.group(1))) > 60:
            raise SystemExit(f"{name}: title missing or exceeds 60 characters")
        if not description or len(html.unescape(description.group(1))) > 160:
            raise SystemExit(f"{name}: description missing or exceeds 160 characters")
        for token in (START, 'property="og:image"', 'name="twitter:image"', 'width="', 'height="'):
            if token not in source:
                raise SystemExit(f"{name}: missing {token}")
        if source.count("<h1") != 1:
            raise SystemExit(f"{name}: expected one H1")
        for raw in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', source, re.I):
            json.loads(raw)
        if f"{DOMAIN}/{name}" not in sitemap:
            raise SystemExit(f"{name}: missing from sitemap")
        if re.search(rf'^"?{re.escape(name)}"?,', inventory, re.M):
            raise SystemExit(f"{name}: stale sitemap-exclusion row")
    service_areas = (ROOT / "service-areas.html").read_text(encoding="utf-8")
    articles = (ROOT / "articles.html").read_text(encoding="utf-8")
    if any(f'href="{name}"' not in service_areas for name in CITY_PAGES):
        raise SystemExit("service-areas.html: missing promoted city link")
    if any(f'href="{name}"' not in articles for name in ARTICLE_PAGES):
        raise SystemExit("articles.html: missing promoted article link")
    for name, source in (("service-areas.html", service_areas), ("articles.html", articles)):
        if source.count(START) != 1 or source.count(END) != 1:
            raise SystemExit(f"{name}: expected one enrichment block")


def main() -> None:
    for name, config in CITY_PAGES.items():
        enrich_city(ROOT / name, config)
    for name, config in ARTICLE_PAGES.items():
        enrich_article(ROOT / name, config)
    for name, config in REVIEWS.items():
        enrich_reviews(ROOT / name, config)
    enrich_hub(ROOT / "service-areas.html", service_area_links_block())
    enrich_hub(ROOT / "articles.html", article_links_block())
    remove_promoted_classifications()
    update_sitemap()
    validate()
    print(f"Promoted {len(PROMOTED)} enriched pages into sitemap.xml.")


if __name__ == "__main__":
    main()
