from __future__ import annotations

import html
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://lunageneralcontractors.com"
TODAY = date.today().isoformat()
PHONE = "(817) 784-5998"

ARTICLES = [
    ("roof-ventilation-plano", "Roofing", "Roof Ventilation Planning in Plano, TX", "Plano", "roofing", "Roofing", "Proper roof ventilation can help control attic heat and moisture when intake and exhaust are balanced for the roof design.", ["Review soffit intake, ridge or roof exhaust, blocked air paths and attic insulation before selecting a correction.", "Ventilation should be coordinated with roofing, decking, insulation and bathroom exhaust systems rather than treated as an isolated product.", "A site inspection is needed because roof shape, attic layout and existing penetrations affect the practical solution."]),
    ("bathroom-waterproofing-frisco", "Bathroom Remodeling", "Bathroom Waterproofing Details in Frisco, TX", "Frisco", "bathroom-remodeling", "Bathroom Remodeling", "Waterproofing must form a continuous system behind tile, around penetrations and across changes of plane.", ["Confirm the approved substrate and waterproofing method before tile installation begins.", "Corners, niches, benches, curbs, valves and drain transitions deserve special attention because small gaps can create hidden damage.", "Flood testing or manufacturer-required checks should happen before finish materials cover the assembly."]),
    ("kitchen-island-layout-mckinney", "Kitchen Remodeling", "Kitchen Island Layout Tips in McKinney, TX", "McKinney", "kitchen-remodeling", "Kitchen Remodeling", "A useful kitchen island supports traffic, storage and work zones without crowding appliances or door swings.", ["Measure clearances around the island with appliance doors and drawers open.", "Plan electrical, seating overhang, lighting and any plumbing before cabinets and countertops are ordered.", "The island size should fit the room rather than forcing an oversized feature into a limited walkway."]),
    ("flooring-subfloor-preparation-allen", "Flooring", "Subfloor Preparation for Flooring in Allen, TX", "Allen", "flooring", "Flooring", "Flooring performance depends on a clean, dry, flat and structurally suitable subfloor.", ["Check slab moisture, wood movement, damaged areas, height changes and flatness before installation.", "High spots, low areas and loose panels should be corrected using methods compatible with the selected flooring.", "Transitions, door clearances and adjoining rooms should be reviewed before final material quantities are ordered."]),
    ("exterior-paint-southlake", "Painting", "Exterior Paint Selection in Southlake, TX", "Southlake", "painting", "Painting", "Exterior coatings should match the substrate and withstand North Texas sun, heat, wind and rain.", ["Identify whether surfaces are wood, fiber cement, masonry, metal or previously coated material.", "Use compatible primer where bare, repaired or stained areas require it.", "Sheen, color, joint movement and moisture sources should be considered before the finish coat is applied."]),
    ("ceiling-drywall-repair-garland", "Drywall", "Ceiling Drywall Repair in Garland, TX", "Garland", "drywall", "Drywall", "Ceiling repairs should begin only after the leak, movement or impact source has been corrected.", ["Inspect framing, insulation and surrounding material before closing the opening.", "Patch support, fastener spacing, tape, compound and texture blending affect how visible the repair remains.", "Primer and repainting to natural breaks can reduce flashing and sheen differences."]),
    ("siding-repair-rowlett", "Siding", "Siding Repair After Storm Damage in Rowlett, TX", "Rowlett", "siding", "Siding", "Storm-damaged siding should be evaluated for impact marks, loose panels, moisture entry and damage around openings.", ["Inspect corners, trim, flashing and wall penetrations in addition to the visible siding surface.", "Matching older profiles and colors may require replacing a larger section when exact material is unavailable.", "Repairs should restore drainage and weather resistance, not only appearance."]),
    ("exterior-trim-carpentry-keller", "Carpentry", "Exterior Trim Carpentry in Keller, TX", "Keller", "carpentry", "Carpentry", "Exterior trim repairs protect roof edges, openings and transitions while restoring a finished appearance.", ["Determine whether damage is limited to trim or extends into sheathing, framing or flashing.", "Replacement material should be selected for exposure, movement and paint compatibility.", "Joints, fasteners, caulk and primer must work together to reduce future water entry."]),
    ("fence-post-replacement-mesquite", "Fencing", "Fence Post Replacement in Mesquite, TX", "Mesquite", "fencing", "Fencing", "A leaning fence often begins with failed posts, inadequate depth, soil movement or trapped moisture.", ["Inspect rails and panels before deciding whether posts can be replaced individually.", "Post depth, spacing, concrete placement and grade conditions affect stability.", "Gates need additional support and should be checked for sagging, latch alignment and clearance."]),
    ("commercial-office-remodel-richardson", "Commercial Construction", "Office Remodeling Planning in Richardson, TX", "Richardson", "commercial-construction", "Commercial Construction", "Office remodeling requires coordination between layout, accessibility, electrical, data, HVAC, finishes and business operations.", ["Document the existing space and intended occupancy before finalizing partitions and rooms.", "Review permits, landlord requirements, inspections and long-lead materials early.", "Plan dust control, deliveries, work hours and phased turnover when adjacent areas remain occupied."]),
    ("water-damage-cabinet-repair-lewisville", "Water Damage Restoration", "Cabinet Repair After Water Damage in Lewisville, TX", "Lewisville", "water-damage-restoration", "Water Damage Restoration", "Water-damaged cabinets should be evaluated for swelling, delamination, contamination and hidden moisture behind the boxes.", ["Confirm the water source is corrected and surrounding cavities are ready for reconstruction.", "Face frames, doors and finishes may sometimes be saved even when cabinet boxes require replacement.", "Countertops, plumbing and flooring connections should be included in the repair sequence."]),
    ("insurance-scope-review-rockwall", "Insurance Claims", "Reviewing an Insurance Repair Scope in Rockwall, TX", "Rockwall", "insurance-claims", "Insurance Claims", "A repair scope should clearly connect observed damage with the labor, materials and access needed to restore the property.", ["Compare room dimensions, quantities, finish descriptions and affected components with actual site conditions.", "Document hidden conditions or additional damage discovered after approved work begins.", "Coverage decisions remain with the carrier, while the contractor prepares and completes the construction scope."]),
    ("contractor-estimate-comparison-carrollton", "General Contractor", "How to Compare Contractor Estimates in Carrollton, TX", "Carrollton", "general-contractor", "General Contractor", "The lowest total is not always the lowest final cost when estimates describe different scopes, materials or exclusions.", ["Compare demolition, preparation, materials, permits, cleanup and finish details line by line.", "Confirm allowances, change-order rules, payment schedule and who coordinates each trade.", "A clear written scope makes it easier to identify genuine price differences and missing work."]),
    ("roof-flashing-grapevine", "Roofing", "Roof Flashing Problems in Grapevine, TX", "Grapevine", "roofing", "Roofing", "Flashing directs water away from roof intersections, walls, chimneys, valleys and penetrations.", ["Look for lifted metal, failed sealant, improper overlaps and staining below the transition.", "A surface patch may not solve the problem when flashing was installed incorrectly beneath the roofing.", "Repairs should follow the water path and restore layered drainage rather than rely only on exposed caulk."]),
    ("bathroom-ventilation-bedford", "Bathroom Remodeling", "Bathroom Ventilation Improvements in Bedford, TX", "Bedford", "bathroom-remodeling", "Bathroom Remodeling", "Bathroom ventilation helps remove moisture when the fan is correctly sized, ducted and used long enough.", ["Confirm the fan exhausts outdoors instead of into the attic or another enclosed space.", "Review duct length, bends, termination, backdraft damper and replacement-air path.", "Ventilation improvements should accompany repairs to recurring peeling paint, mildew or moisture damage."]),
]


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def render_article(item: tuple) -> str:
    slug, category, title, city, service_slug, service_name, intro, sections = item
    filename = f"{slug}.html"
    url = f"{DOMAIN}/{filename}"
    related = f"{city.lower().replace(' ', '-')}-{service_slug}.html"
    description = f"Practical guidance about {title.lower()} from Luna General Contractors. Call {PHONE} for a project estimate."
    section_html = ''.join(f'<section><h2>{esc(["What to inspect", "Planning the work", "Avoiding repeat problems"][i])}</h2><p>{esc(text)}</p></section>' for i, text in enumerate(sections))
    schema = f'''<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":"{esc(title)}","description":"{esc(description)}","mainEntityOfPage":"{url}","author":{{"@type":"Organization","name":"Luna General Contractors"}},"publisher":{{"@type":"Organization","name":"Luna General Contractors"}},"datePublished":"{TODAY}","dateModified":"{TODAY}"}}</script><script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"{DOMAIN}/"}},{{"@type":"ListItem","position":2,"name":"Articles","item":"{DOMAIN}/articles.html"}},{{"@type":"ListItem","position":3,"name":"{esc(title)}","item":"{url}"}}]}}</script><script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{{"@type":"Question","name":"Should this work be inspected in person?","acceptedAnswer":{{"@type":"Answer","text":"Yes. Site conditions, access, materials and hidden damage can change the correct scope."}}}},{{"@type":"Question","name":"Does Luna General Contractors provide estimates in {esc(city)}?","acceptedAnswer":{{"@type":"Answer","text":"Yes. Call {PHONE} to discuss a project in {esc(city)} and nearby areas."}}}}]}}</script>'''
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Luna General Contractors</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index, follow, max-image-preview:large"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{url}"><link rel="stylesheet" href="/styles.css">{schema}</head><body><header class="site-header"><div class="container header-inner"><a class="brand" href="index.html"><strong>LUNA GENERAL CONTRACTORS</strong></a><nav class="main-nav"><a href="index.html">Home</a><a href="service-areas.html">Service Areas</a><a href="articles.html">Resources</a></nav><div class="header-call"><a href="tel:+18177845998">☎ {PHONE}</a></div></div></header><main><section class="local-hero"><div class="container"><p class="eyebrow gold">{esc(category)} • {esc(city)}, Texas</p><h1>{esc(title)}</h1><p>{esc(intro)}</p></div></section><article class="local-content"><div class="container">{section_html}<section><h2>Related Local Service</h2><p><a href="{related}">{esc(service_name)} in {esc(city)}, TX</a></p></section><section class="faq"><h2>Frequently Asked Questions</h2><details><summary>Should this work be inspected in person?</summary><p>Yes. Site conditions, access, materials and hidden damage can change the correct scope.</p></details><details><summary>Do you provide estimates in {esc(city)}?</summary><p>Yes. Call {PHONE} to discuss the project.</p></details></section></div></article></main></body></html>'''


def main() -> None:
    generated = []
    cards = []
    for item in ARTICLES:
        slug, category, title, city, service_slug, service_name, intro, sections = item
        filename = f"{slug}.html"
        (ROOT / filename).write_text(render_article(item), encoding="utf-8")
        generated.append(filename)
        cards.append(f'<article class="seo-city-card"><p class="eyebrow gold">{esc(category)}</p><h2><a href="{filename}">{esc(title)}</a></h2><p>{esc(intro)}</p><a class="seo-text-link" href="{filename}">Read article →</a></article>')

    index_path = ROOT / "articles.html"
    index = index_path.read_text(encoding="utf-8")
    start, end = '<!-- LUNA_BATCH3_START -->', '<!-- LUNA_BATCH3_END -->'
    block = start + ''.join(cards) + end
    if start in index and end in index:
        before = index.split(start, 1)[0]
        after = index.split(end, 1)[1]
        index = before + block + after
    else:
        marker = '</div></div></section></main>'
        if marker not in index:
            raise SystemExit('Article index insertion marker not found')
        index = index.replace(marker, block + marker, 1)
    index_path.write_text(index, encoding="utf-8")

    sitemap = ROOT / "sitemap.xml"
    tree = ET.parse(sitemap)
    root = tree.getroot()
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    existing = {node.text for node in root.findall(f'{{{ns}}}url/{{{ns}}}loc') if node.text}
    for filename in generated:
        url = f"{DOMAIN}/{filename}"
        if url not in existing:
            node = ET.SubElement(root, f'{{{ns}}}url')
            ET.SubElement(node, f'{{{ns}}}loc').text = url
            ET.SubElement(node, f'{{{ns}}}lastmod').text = TODAY
    ET.register_namespace('', ns)
    tree.write(sitemap, encoding='utf-8', xml_declaration=True)

    manifest_path = ROOT / 'luna_engine/article-manifest.txt'
    existing_manifest = [line.strip() for line in manifest_path.read_text(encoding='utf-8').splitlines() if line.strip()] if manifest_path.exists() else []
    combined = list(dict.fromkeys(existing_manifest + generated))
    manifest_path.write_text('\n'.join(combined) + '\n', encoding='utf-8')
    print(f"Generated {len(generated)} third-batch articles; manifest now has {len(combined)} articles")


if __name__ == '__main__':
    main()
