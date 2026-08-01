from __future__ import annotations

import html
import re
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://lunageneralcontractors.com"
PHONE = "(817) 784-5998"
PHONE_LINK = "+18177845998"
TODAY = date.today().isoformat()

ARTICLES = [
    {
        "slug": "roof-repair-vs-replacement-arlington",
        "category": "Roofing",
        "title": "Roof Repair vs. Replacement in Arlington, TX",
        "description": "Learn when an Arlington roof may need a focused repair and when full replacement is the more practical long-term option.",
        "city": "Arlington",
        "service_slug": "roofing",
        "service_name": "Roofing",
        "intro": "Choosing between roof repair and full replacement should be based on the roof’s condition, age, leak history, storm damage, decking, flashing and the cost of repeated repairs.",
        "sections": [
            ("When a roof repair may be enough", "A localized repair may be appropriate when damage is limited, surrounding shingles remain serviceable, the decking is sound and the leak source can be identified and corrected without disturbing a large area."),
            ("When replacement deserves consideration", "Replacement becomes more practical when shingles are brittle or widely damaged, leaks appear in several areas, prior repairs are failing, ventilation is poor or the roof is near the end of its expected service life."),
            ("What should be inspected", "A useful inspection reviews shingles, penetrations, flashing, valleys, ridge, ventilation, gutters, visible decking conditions and interior signs of moisture before recommending the scope."),
        ],
        "faqs": [("Can one missing shingle be repaired?", "Often yes, provided matching material is available and the surrounding roof is still in good condition."), ("Does a roof leak always mean replacement?", "No. The correct solution depends on the source, extent of damage and overall roof condition.")],
    },
    {
        "slug": "walk-in-shower-cost-midlothian",
        "category": "Bathroom Remodeling",
        "title": "Walk-In Shower Cost Factors in Midlothian, TX",
        "description": "Understand the main cost drivers for a walk-in shower in Midlothian, including demolition, plumbing, waterproofing, tile and glass.",
        "city": "Midlothian",
        "service_slug": "bathroom-remodeling",
        "service_name": "Bathroom Remodeling",
        "intro": "A walk-in shower estimate depends on the existing bathroom, shower dimensions, plumbing changes, drain location, waterproofing system, tile design, niches, bench, glass and finish selections.",
        "sections": [
            ("Demolition and hidden conditions", "Removing a tub or old shower can reveal damaged framing, moisture, unsuitable wallboard or an uneven slab. Those conditions must be addressed before new finishes are installed."),
            ("Plumbing and slope", "Relocating the valve, drain or supply lines adds labor. The shower floor must also be prepared with the correct slope so water reaches the drain."),
            ("Waterproofing, tile and glass", "The waterproofing method, tile size, pattern, grout, niches, bench details and custom glass dimensions have a major effect on the final scope and price."),
        ],
        "faqs": [("Can a bathtub be converted to a walk-in shower?", "Yes. The scope may include demolition, plumbing changes, slope preparation, waterproofing, tile and glass."), ("How long does a walk-in shower project take?", "Timing varies with demolition, inspections, curing time, tile complexity, glass measurement and material availability.")],
    },
    {
        "slug": "kitchen-remodel-planning-mansfield",
        "category": "Kitchen Remodeling",
        "title": "Kitchen Remodel Planning in Mansfield, TX",
        "description": "Plan a Mansfield kitchen remodel around layout, cabinets, countertops, lighting, plumbing, appliances and project sequencing.",
        "city": "Mansfield",
        "service_slug": "kitchen-remodeling",
        "service_name": "Kitchen Remodeling",
        "intro": "A successful kitchen remodel starts with the layout and daily use of the room, then coordinates cabinets, appliances, plumbing, electrical, lighting, countertops, backsplash and finishes.",
        "sections": [
            ("Start with the layout", "Confirm traffic paths, door swings, appliance clearances, landing space, island dimensions and storage needs before ordering cabinets or countertops."),
            ("Coordinate materials and lead times", "Cabinets, specialty hardware, appliances and countertop fabrication can control the schedule. Selections should be confirmed early enough to avoid unnecessary delays."),
            ("Plan the construction sequence", "Demolition, framing, rough plumbing, electrical, drywall, cabinets, countertops, backsplash, paint and finish work must happen in a practical order."),
        ],
        "faqs": [("Should cabinets or flooring be installed first?", "The answer depends on the flooring system, cabinet plan and manufacturer requirements, so the sequence should be decided before installation."), ("Can a kitchen stay usable during remodeling?", "Sometimes partially, but major projects often require a temporary food-preparation area elsewhere in the home.")],
    },
    {
        "slug": "storm-damage-documentation-fort-worth",
        "category": "Insurance Claims",
        "title": "How to Document Storm Damage in Fort Worth, TX",
        "description": "Practical steps for documenting visible hail, wind and water damage after a Fort Worth storm before repairs begin.",
        "city": "Fort Worth",
        "service_slug": "insurance-claims",
        "service_name": "Insurance Claims",
        "intro": "Good storm documentation creates a clear record of what happened, what areas were affected and what temporary measures or repairs were necessary.",
        "sections": [
            ("Photograph conditions safely", "Document visible roof-edge, gutter, siding, fence, window and interior water damage from safe locations. Do not climb onto a wet, steep or damaged roof."),
            ("Record dates and affected rooms", "Note the storm date, when leaks were discovered, which rooms were affected and what was done to prevent additional damage."),
            ("Keep estimates and receipts", "Save inspection reports, written scopes, temporary protection invoices, drying records and repair estimates so the documentation remains organized."),
        ],
        "faqs": [("Should emergency damage be protected before inspection?", "Reasonable temporary steps may be needed to prevent additional damage, but conditions should be documented first when safely possible."), ("Can a contractor decide what insurance covers?", "Coverage decisions belong to the insurance carrier and policy. A contractor can document damage and prepare a construction scope.")],
    },
    {
        "slug": "water-damage-rebuild-process-dallas",
        "category": "Water Damage Restoration",
        "title": "Water Damage Rebuild Process in Dallas, TX",
        "description": "See how a Dallas water-damage rebuild moves from source correction and drying to drywall, texture, paint, flooring and finish work.",
        "city": "Dallas",
        "service_slug": "water-damage-restoration",
        "service_name": "Water Damage Restoration",
        "intro": "Reconstruction should begin only after the water source is corrected, affected materials are evaluated and the structure is ready to be closed back up.",
        "sections": [
            ("Confirm the building is ready", "Before rebuild, verify that the source is corrected, required removal is complete and framing or cavities are sufficiently dry for reconstruction."),
            ("Rebuild in the right order", "Framing repairs, insulation, drywall, tape and float, texture, primer, paint, trim, doors, cabinets and flooring must be sequenced to avoid damaging completed work."),
            ("Match existing finishes", "Texture, paint sheen, trim profiles and flooring transitions should be reviewed carefully because exact matches may depend on age and material availability."),
        ],
        "faqs": [("Can drywall be installed before everything is dry?", "No. Closing damp cavities can trap moisture and create additional problems."), ("Is mitigation the same as reconstruction?", "No. Mitigation focuses on stopping and drying the loss; reconstruction restores removed or damaged building materials.")],
    },
    {
        "slug": "best-flooring-for-pets-grand-prairie",
        "category": "Flooring",
        "title": "Best Flooring Considerations for Pets in Grand Prairie, TX",
        "description": "Compare practical flooring factors for Grand Prairie homes with pets, including scratch resistance, moisture, cleanup and comfort.",
        "city": "Grand Prairie",
        "service_slug": "flooring",
        "service_name": "Flooring",
        "intro": "Pet-friendly flooring should balance scratch resistance, moisture tolerance, traction, comfort, cleaning and compatibility with the existing subfloor.",
        "sections": [
            ("Luxury vinyl plank", "Quality LVP can offer moisture resistance and easy cleanup, but the wear layer, locking system, subfloor flatness and direct sunlight conditions should be reviewed."),
            ("Tile and engineered wood", "Tile is durable and easy to clean but can feel hard and cool. Engineered wood offers a warmer appearance but needs careful product selection and moisture control."),
            ("Installation matters", "Even a durable product can fail when installed over an uneven or damp subfloor. Preparation, transitions and expansion requirements remain important."),
        ],
        "faqs": [("Is waterproof flooring completely protected from pet accidents?", "The flooring surface may resist moisture, but liquid can still reach seams, edges, walls or the subfloor."), ("What flooring hides scratches best?", "Matte finishes, textured surfaces and varied patterns often make minor wear less noticeable.")],
    },
    {
        "slug": "exterior-paint-preparation-cedar-hill",
        "category": "Painting",
        "title": "Exterior Paint Preparation in Cedar Hill, TX",
        "description": "Learn why washing, scraping, caulking, priming and surface repair matter before exterior painting in Cedar Hill.",
        "city": "Cedar Hill",
        "service_slug": "painting",
        "service_name": "Painting",
        "intro": "Exterior paint performance depends heavily on preparation. New paint will not correct loose coatings, rotten trim, failed caulk or moisture problems underneath.",
        "sections": [
            ("Clean and inspect", "Dirt, mildew, chalking and loose coatings should be removed so the condition of siding, fascia, soffit and trim can be evaluated."),
            ("Repair before coating", "Damaged wood, open joints, failed caulk and exposed fasteners should be addressed before primer and finish paint are applied."),
            ("Choose products for the surface", "Primer and paint should be compatible with the existing substrate and selected for North Texas sun, heat, rain and seasonal movement."),
        ],
        "faqs": [("Can exterior paint cover rotten wood?", "No. Deteriorated material should be repaired or replaced before painting."), ("Is pressure washing always required?", "Cleaning is important, but the safest method and pressure depend on the surface and its condition.")],
    },
    {
        "slug": "drywall-texture-matching-desoto",
        "category": "Drywall",
        "title": "Drywall Texture Matching in DeSoto, TX",
        "description": "Understand the process and limitations of matching orange peel, knockdown and other drywall textures in DeSoto homes.",
        "city": "DeSoto",
        "service_slug": "drywall",
        "service_name": "Drywall",
        "intro": "Texture matching requires more than spraying new material over a patch. The surrounding texture, thickness, pattern, paint layers and lighting all affect the final appearance.",
        "sections": [
            ("Identify the existing texture", "Orange peel, knockdown, skip trowel and hand-applied textures each require different materials, tools and application methods."),
            ("Blend beyond the patch", "A repair often needs feathering and texture blending outside the exact cut area so the transition is less visible."),
            ("Prime and paint consistently", "Fresh texture absorbs paint differently. Primer and repainting to natural breaks can improve uniformity, though aged surfaces may still vary slightly."),
        ],
        "faqs": [("Can drywall texture be matched perfectly?", "A close match is often possible, but age, prior paint and hand-applied patterns can make an exact match difficult."), ("Why does a patch flash after painting?", "Different porosity, sheen, application method or lighting can make repaired areas reflect light differently.")],
    },
    {
        "slug": "wood-fence-repair-vs-replacement-waxahachie",
        "category": "Fencing",
        "title": "Wood Fence Repair vs. Replacement in Waxahachie, TX",
        "description": "Decide whether a Waxahachie wood fence needs targeted repairs, new posts and sections, or complete replacement.",
        "city": "Waxahachie",
        "service_slug": "fencing",
        "service_name": "Fencing",
        "intro": "Fence decisions should consider post condition, leaning, rot, rail damage, picket life, gate operation, storm damage and how much of the fence is affected.",
        "sections": [
            ("When repair may make sense", "Repair can be practical when damage is limited to a few posts, rails, pickets or a gate and the remaining fence is structurally sound."),
            ("When replacement may be better", "Replacement deserves consideration when many posts are failing, long sections lean, widespread rot is present or repeated repairs would approach the cost of a new fence."),
            ("Plan posts, gates and finish", "Post depth, spacing, rail layout, picket style, grade changes, gate hardware, staining and access all affect the scope."),
        ],
        "faqs": [("Can fence posts be replaced without replacing every panel?", "Often yes, depending on panel condition and access."), ("Should a new fence be stained immediately?", "Timing depends on moisture content and the stain manufacturer’s requirements.")],
    },
    {
        "slug": "commercial-tenant-improvement-planning-irving",
        "category": "Commercial Construction",
        "title": "Commercial Tenant Improvement Planning in Irving, TX",
        "description": "Plan an Irving commercial tenant improvement around scope, permits, access, schedule, trades, inspections and turnover.",
        "city": "Irving",
        "service_slug": "commercial-construction",
        "service_name": "Commercial Construction",
        "intro": "Tenant improvements require clear decisions about the intended use, existing conditions, code requirements, building access, landlord standards and business opening date.",
        "sections": [
            ("Define the complete scope", "Partitions, doors, ceilings, flooring, paint, millwork, plumbing, electrical, HVAC, fire protection and accessibility should be coordinated before construction starts."),
            ("Review approvals and lead times", "Permits, landlord approvals, utility coordination, inspections and long-lead materials can control the schedule."),
            ("Plan occupied-building logistics", "Delivery routes, work hours, dust control, noise, security, elevators, parking and protection of neighboring spaces should be addressed in advance."),
        ],
        "faqs": [("Do all tenant improvements require permits?", "Requirements depend on the jurisdiction and scope. Structural, electrical, plumbing, mechanical and occupancy changes commonly require review."), ("Can work be completed while a business remains open?", "Sometimes, with phased scheduling and protection, but safety, access and code requirements must be considered.")],
    },
]

HEADER = '''<header class="site-header"><div class="container header-inner"><a class="brand" href="index.html" aria-label="Luna General Contractors home"><span class="brand-moon"></span><span class="brand-copy"><strong>LUNA</strong><small>GENERAL CONTRACTORS</small><em>Roofing • Remodeling • Restoration</em></span></a><nav class="main-nav"><a href="index.html">Home</a><a href="service-areas.html">Service Areas</a><a href="articles.html">Resources</a><a href="#estimate-form">Contact</a></nav><div class="header-call"><small>Call Now for a Free Estimate</small><a href="tel:+18177845998">☎ (817) 784-5998</a><span>English &amp; Spanish</span></div></div></header>'''

FORM = '''<section class="local-form" id="estimate-form"><div class="container"><h2>Request a Free Estimate</h2><form action="https://formspree.io/f/xzzvgpoy" method="POST" class="estimate-form"><label>Full Name<input name="name" required autocomplete="name"></label><label>Phone Number<input name="phone" required autocomplete="tel"></label><label>Email Address<input type="email" name="email" required autocomplete="email"></label><label>Project Address<input name="address" required autocomplete="street-address"></label><label>Project Details<textarea name="message" rows="5" required></textarea></label><button class="btn btn-gold" type="submit">Request Your Estimate</button></form></div></section>'''


def schema(data: dict) -> str:
    import json
    return '<script type="application/ld+json">' + json.dumps(data, separators=(",", ":")) + '</script>'


def render_article(item: dict) -> str:
    url = f"{DOMAIN}/{item['slug']}.html"
    service_url = f"{DOMAIN}/{item['city'].lower().replace(' ', '-')}-{item['service_slug']}.html"
    article_schema = {"@context":"https://schema.org","@type":"Article","headline":item["title"],"description":item["description"],"datePublished":TODAY,"dateModified":TODAY,"author":{"@type":"Organization","name":"Luna General Contractors"},"publisher":{"@type":"Organization","name":"Luna General Contractors"},"mainEntityOfPage":url}
    breadcrumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":f"{DOMAIN}/"},{"@type":"ListItem","position":2,"name":"Articles","item":f"{DOMAIN}/articles.html"},{"@type":"ListItem","position":3,"name":item["title"],"item":url}]}
    faq = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in item["faqs"]]}
    section_html = ''.join(f'<section><h2>{html.escape(h)}</h2><p>{html.escape(p)}</p></section>' for h,p in item["sections"])
    faq_html = ''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q,a in item["faqs"])
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{html.escape(item['title'])} | Luna General Contractors</title><meta name="description" content="{html.escape(item['description'])}"><meta name="robots" content="index, follow, max-image-preview:large"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{html.escape(item['title'])}"><meta property="og:description" content="{html.escape(item['description'])}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/local-seo.css">{schema(article_schema)}{schema(breadcrumb)}{schema(faq)}</head><body>{HEADER}<main><article class="seo-section"><div class="container"><nav class="seo-breadcrumbs"><a href="index.html">Home</a> › <a href="articles.html">Articles</a> › <span>{html.escape(item['category'])}</span></nav><p class="eyebrow gold">{html.escape(item['category'])} · {html.escape(item['city'])}, Texas</p><h1>{html.escape(item['title'])}</h1><p class="seo-lead">{html.escape(item['intro'])}</p>{section_html}<section><h2>Talk With a Local Contractor</h2><p>For a site-specific scope, request an inspection and written estimate based on the actual property conditions.</p><p><a class="btn btn-gold" href="{item['city'].lower().replace(' ', '-')}-{item['service_slug']}.html">View {html.escape(item['service_name'])} in {html.escape(item['city'])}</a> <a class="btn btn-outline" href="tel:{PHONE_LINK}">Call {PHONE}</a></p></section><section class="faq"><h2>Frequently Asked Questions</h2>{faq_html}</section></div></article>{FORM}</main></body></html>'''


def update_index() -> None:
    path = ROOT / "articles.html"
    text = path.read_text(encoding="utf-8")
    cards = []
    for item in ARTICLES:
        if f'href="{item["slug"]}.html"' in text:
            continue
        cards.append(f'<article class="seo-city-card"><p class="eyebrow gold">{html.escape(item["category"])}</p><h2><a href="{item["slug"]}.html">{html.escape(item["title"])}</a></h2><p>{html.escape(item["description"])}</p><a class="seo-text-link" href="{item["slug"]}.html">Read article →</a></article>')
    if cards:
        marker = '</div></div></section></main>'
        text = text.replace(marker, ''.join(cards) + marker, 1)
        path.write_text(text, encoding="utf-8")


def update_sitemap() -> None:
    path = ROOT / "sitemap.xml"
    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    tree = ET.parse(path)
    root = tree.getroot()
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    existing = {loc.text for loc in root.findall(f'{ns}url/{ns}loc')}
    for item in ARTICLES:
        url = f"{DOMAIN}/{item['slug']}.html"
        if url not in existing:
            node = ET.SubElement(root, f'{ns}url')
            ET.SubElement(node, f'{ns}loc').text = url
            ET.SubElement(node, f'{ns}lastmod').text = TODAY
    tree.write(path, encoding='utf-8', xml_declaration=True)


def main() -> None:
    for item in ARTICLES:
        (ROOT / f"{item['slug']}.html").write_text(render_article(item), encoding="utf-8")
    update_index()
    update_sitemap()
    (ROOT / "luna_engine" / "article-manifest.txt").write_text('\n'.join(f"{item['slug']}.html" for item in ARTICLES) + '\n', encoding='utf-8')
    print(f"Generated {len(ARTICLES)} local SEO articles")


if __name__ == "__main__":
    main()
