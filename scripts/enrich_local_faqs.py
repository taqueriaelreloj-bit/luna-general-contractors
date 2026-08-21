from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path

MANIFEST = Path("seo-generated-manifest.txt")
FAQ_CLASS = "seo-section seo-faq"

SERVICE_SUFFIXES = {
    "bathroom-remodeling": "Bathroom Remodeling",
    "carpentry": "Carpentry",
    "commercial-construction": "Commercial Construction",
    "drywall": "Drywall",
    "fencing": "Fencing",
    "flooring": "Flooring",
    "general-contractor": "General Contracting",
    "insurance-claims": "Insurance Claim Restoration",
    "kitchen-remodeling": "Kitchen Remodeling",
    "painting": "Painting",
    "roofing": "Roofing",
    "siding": "Siding",
    "water-damage-restoration": "Water Damage Restoration",
}

EXCLUDED = {
    "articles.html",
    "service-areas.html",
    "services-by-city.html",
    "bathroom-remodeling-cost-waxahachie.html",
    "best-general-contractor-midlothian.html",
    "commercial-construction-planning-dallas.html",
    "drywall-repair-after-water-damage-grand-prairie.html",
    "fence-replacement-cost-cedar-hill.html",
    "flooring-options-mansfield.html",
    "kitchen-remodeling-ideas-texas.html",
    "roof-replacement-cost-dallas.html",
    "roofing-insurance-claim-fort-worth.html",
    "water-damage-insurance-claims-arlington.html",
}

SERVICE_FAQS = {
    "Roofing": [
        ("How do I know whether my roof in {city} needs repair or replacement?", "The answer depends on the age of the roof, the number and location of damaged areas, prior repairs, shingle condition, flashing, decking, and whether the damage is isolated or widespread. We inspect the visible conditions first and explain the practical repair and replacement options."),
        ("Can hail damage be present even if my roof is not leaking?", "Yes. Hail can damage shingles, vents, flashing, soft metals, and other roofing components without causing an immediate interior leak. A post-storm inspection can document visible conditions before small problems become larger ones."),
        ("What should be checked before replacing a roof with solar panels?", "The roofing scope should account for safe solar-panel detach and reset, roof penetrations, flashing, access, scheduling, and responsibility for reconnecting the system. Those items should be coordinated before roofing work starts."),
        ("Does roof pitch affect the cost of a roofing project in {city}?", "It can. Steeper roofs may require additional labor, safety measures, staging, and material handling. Roof size, layers, access, decking condition, valleys, flashing, and ventilation also affect the final scope."),
        ("Should I repair storm damage before an insurance inspection?", "Emergency measures may be needed to prevent additional damage, but permanent repairs should be documented carefully. Photos, measurements, receipts, and a written scope can help preserve a clear record of the conditions that were observed."),
        ("What roofing details often get missed in a basic estimate?", "Commonly overlooked items can include steep or high charges, starter and ridge materials, flashing, vents, decking repairs, drip edge, disposal, protection, code-required items, and detach/reset work for roof-mounted equipment when applicable."),
    ],
    "Insurance Claim Restoration": [
        ("What documentation is useful for an insurance-related repair in {city}?", "Photos, measurements, room-by-room damage notes, emergency-service records, invoices, material information, and a written repair scope can all help organize the reconstruction portion of a property claim."),
        ("What is the difference between ACV and RCV on a property claim?", "Actual cash value generally reflects depreciation, while replacement cost value is based on the cost to repair or replace covered property subject to the policy terms. Whether depreciation is recoverable depends on the policy and claim settlement."),
        ("When can recoverable depreciation be released?", "Policies commonly require completed repairs and supporting documentation before recoverable depreciation is considered for release. The exact requirements depend on the policy, carrier, settlement, and whether the depreciation was identified as recoverable."),
        ("What is an insurance supplement?", "A supplement is a request to review additional repair items, quantities, pricing, or necessary work that was not included or was insufficiently addressed in the original estimate. Supporting photos, measurements, invoices, and scope notes are important."),
        ("Can overhead and profit be included in an insurance repair estimate?", "It may be appropriate when the repair reasonably requires coordination of multiple trades or general-contractor involvement. Whether it is allowed depends on the facts of the loss, the scope of work, policy terms, and carrier review."),
        ("Does the deductible disappear if the claim is approved?", "No. The deductible is generally the policyholder's contractual responsibility under the insurance policy. Approval of covered repairs does not automatically eliminate it."),
    ],
    "Bathroom Remodeling": [
        ("What should be inspected after bathroom demolition in {city}?", "Once finishes are removed, framing, plumbing, subfloor, wall conditions, moisture damage, and previous repairs can be evaluated more accurately before new waterproofing and finishes are installed."),
        ("What matters most before tile goes into a new shower?", "The substrate, drain, slope, waterproofing, corners, penetrations, niche details, and transitions should all be planned and completed correctly before the finish tile is installed."),
        ("Can a tub be replaced with a walk-in shower?", "Often yes, but the final scope depends on drain location, plumbing, framing, waterproofing, dimensions, glass, ventilation, and the layout of the bathroom."),
        ("Should fixtures be selected before rough-in work?", "Whenever possible, yes. Faucets, shower valves, tubs, vanities, lighting, mirrors, and glass can affect rough-in dimensions and blocking, so early selections can reduce rework."),
        ("How long does a bathroom remodel take?", "The schedule depends on demolition, hidden conditions, inspections, trade coordination, material availability, waterproofing, tile complexity, glass lead times, and finish selections."),
        ("Can you remodel a bathroom while the home is occupied?", "Yes. Work-zone protection, access, dust control, debris removal, scheduling, and keeping another bathroom available when possible can reduce disruption during construction."),
    ],
    "Kitchen Remodeling": [
        ("What should be finalized before ordering kitchen cabinets in {city}?", "Field measurements, appliance sizes, plumbing locations, electrical needs, cabinet layout, countertop dimensions, and flooring decisions should be coordinated before final cabinet ordering."),
        ("Can plumbing and electrical be moved for a new kitchen island?", "Often yes, depending on the existing structure and utilities. The island plan should account for circuits, outlets, dishwasher or disposal connections, plumbing, ventilation needs, and floor access."),
        ("Should flooring go under kitchen cabinets?", "The best sequence depends on the flooring product, cabinet design, appliance clearances, manufacturer requirements, and whether future cabinet changes are expected."),
        ("When should countertops be measured?", "Final countertop measurements are usually most reliable after base cabinets are installed, secured, leveled, and the final appliance and sink selections are confirmed."),
        ("Can existing cabinets be painted instead of replaced?", "Yes when the cabinet boxes and doors are in suitable condition. Preparation, cleaning, sanding or deglossing, repairs, primer, coating choice, and curing time all affect the result."),
        ("What causes kitchen remodel delays?", "Common causes include late material selections, cabinet or countertop lead times, hidden conditions after demolition, utility changes, inspection timing, and changes to the layout after work has started."),
    ],
    "Drywall": [
        ("Can drywall be replaced immediately after a water leak?", "The leak source and moisture condition should be addressed first. Framing, insulation, and cavities should be ready to close before new drywall is installed."),
        ("Why can a drywall patch still show after paint?", "Visible seams can result from narrow finishing, texture mismatch, inadequate sanding, skipped primer, or differences in paint sheen and lighting across the repaired area."),
        ("Do ceiling drywall repairs require different finishing?", "Ceilings often reveal surface irregularities more easily because light travels across them. Flatness, wide feathering, texture matching, primer, and paint blending are especially important."),
        ("How large should a drywall repair be?", "The repair should extend to sound, dry material with adequate backing. The final opening may need to be larger than the visible damage so the new board can be installed and finished properly."),
        ("Can texture be matched exactly?", "Many textures can be matched closely, but age, paint buildup, application method, and lighting can make perfect matching difficult. Test areas and broader blending can improve the result."),
        ("Should the whole wall be painted after a drywall repair?", "Sometimes. Repainting a larger wall or ceiling area can provide a more consistent sheen and color than touching up only the immediate patch."),
    ],
    "Flooring": [
        ("What should be checked before new flooring is installed in {city}?", "The substrate should be evaluated for flatness, movement, moisture, damage, old adhesive, height changes, and transitions to adjacent rooms."),
        ("Why do floor transitions need to be planned early?", "Different flooring thicknesses can affect doors, reducers, thresholds, baseboards, cabinets, appliances, and adjoining surfaces. Planning heights early helps avoid improvised finish details."),
        ("Can new flooring be installed over existing flooring?", "Sometimes, depending on the product, condition, flatness, moisture, height, manufacturer requirements, and whether the existing floor provides a suitable base."),
        ("How much extra flooring material should be ordered?", "Waste depends on room shape, layout, product size, pattern, defects, and future repair needs. A measured material plan should include a reasonable waste allowance for the specific installation."),
        ("What can be found after old flooring is removed?", "Removal may reveal uneven subfloor, cracks, moisture staining, old patches, damaged underlayment, adhesive, or height issues that should be addressed before the new floor is installed."),
        ("Which flooring works best for pets and heavy traffic?", "The best choice depends on water exposure, scratch resistance, cleaning, sunlight, comfort, repairability, and the specific room. Product performance should be matched to actual use rather than appearance alone."),
    ],
    "Painting": [
        ("What preparation matters before interior painting in {city}?", "Cleaning, patching, sanding, caulking, stain blocking, surface repairs, and protecting adjacent finishes all affect how the final paint looks and performs."),
        ("Do repaired drywall areas need primer before paint?", "Usually yes. Primer helps equalize absorption between joint compound and previously painted surfaces and can reduce flashing in the finish coat."),
        ("Why does paint sheen matter?", "Higher-sheen finishes can highlight surface imperfections but may be easier to clean. Lower-sheen finishes can hide some texture differences but may perform differently in high-use or moisture-prone areas."),
        ("Can exterior paint be applied over damaged wood?", "Damaged or deteriorated material should be evaluated and repaired first. Paint can protect properly prepared surfaces, but it does not correct rot, movement, or moisture entry by itself."),
        ("How many coats of paint are needed?", "Coverage depends on the existing color, new color, paint quality, surface porosity, primer, application method, and required finish. Some projects need more than one finish coat for consistent coverage."),
        ("Should cabinets be painted with wall paint?", "Cabinets typically benefit from coatings and preparation intended for harder, frequently touched surfaces. Cleaning, sanding or deglossing, primer, spray or brush technique, and curing time all matter."),
    ],
}

GENERIC_FAQS = [
    ("What should be included in a written {service} estimate in {city}?", "A useful estimate should describe the observed scope, quantities or areas when practical, major materials, labor categories, exclusions, and any conditions that still need to be confirmed after demolition or inspection."),
    ("Can hidden conditions change the final scope?", "Yes. Existing construction can conceal moisture damage, previous repairs, framing issues, utilities, substrate problems, or other conditions that are not visible until the work area is opened."),
    ("Why is trade sequencing important on a {service} project?", "Work performed in the wrong order can damage completed finishes or force rework. A clear sequence helps coordinate demolition, rough-ins, inspections, installation, finishing, and cleanup."),
    ("Should materials be ordered before field measurements are confirmed?", "Critical dimensions and selections should be confirmed first whenever possible. This reduces returns, delays, incompatible parts, and modifications after installation begins."),
    ("Can Luna General Contractors coordinate multiple trades in {city}?", "Yes. Multi-trade projects can be organized around one written scope so related work such as framing, drywall, paint, flooring, carpentry, roofing, and restoration can be sequenced more efficiently."),
    ("How do I request an estimate in {city}?", "Call Luna General Contractors at (817) 784-5998 or use the website estimate form with the project address, service needed, and a short description of the work."),
]


def stable_index(key: str, salt: str, size: int) -> int:
    digest = hashlib.sha256(f"{key}|{salt}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % size


def extract_city(page_html: str, filename: str) -> str:
    patterns = [
        r"Serving\s+([^<]+),\s*Texas",
        r"in\s+([^<]+),\s*TX",
        r"<h1>.*?\bin\s+([^<]+)</h1>",
    ]
    for pattern in patterns:
        match = re.search(pattern, page_html, re.I | re.S)
        if match:
            city = re.sub(r"<[^>]+>", "", match.group(1)).strip()
            city = re.sub(r"^Serving\s+", "", city, flags=re.I)
            if city:
                return city
    stem = Path(filename).stem
    for suffix in sorted(SERVICE_SUFFIXES, key=len, reverse=True):
        ending = f"-{suffix}"
        if stem.endswith(ending):
            stem = stem[: -len(ending)]
            break
    return stem.replace("-", " ").title()


def extract_service(filename: str, page_html: str) -> str:
    stem = Path(filename).stem
    for suffix, label in sorted(SERVICE_SUFFIXES.items(), key=lambda item: len(item[0]), reverse=True):
        if stem.endswith(f"-{suffix}"):
            return label
    h1 = re.search(r"<h1>(.*?)</h1>", page_html, re.S | re.I)
    if h1:
        visible = re.sub(r"<[^>]+>", "", h1.group(1)).strip()
        if " in " in visible:
            candidate = visible.split(" in ", 1)[0].strip()
            if candidate:
                return candidate
    return "General Contracting"


def faq_pool(service: str):
    return SERVICE_FAQS.get(service, GENERIC_FAQS)


def build_faqs(filename: str, city: str, service: str):
    pool = faq_pool(service)
    start = stable_index(filename.lower(), "faq-start", len(pool))
    ordered = [pool[(start + i) % len(pool)] for i in range(len(pool))]
    selected = ordered[:4]
    result = []
    for question, answer in selected:
        result.append((
            question.format(city=city, service=service),
            answer.format(city=city, service=service),
        ))
    if pool is not GENERIC_FAQS:
        generic = GENERIC_FAQS[stable_index(filename.lower(), "faq-generic", len(GENERIC_FAQS))]
        result[-1] = (
            generic[0].format(city=city, service=service),
            generic[1].format(city=city, service=service),
        )
    return result


def render_faq_section(city: str, service: str, faqs) -> str:
    details = "".join(
        f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>"
        for q, a in faqs
    )
    return (
        '<section class="seo-section seo-faq"><div class="container">'
        '<p class="eyebrow gold">Frequently Asked Questions</p>'
        f'<h2>{html.escape(city)} {html.escape(service)} FAQ</h2>'
        f"{details}</div></section>"
    )


def render_schema(faqs) -> str:
    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faqs
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + "</script>"


def replace_faq_section(page_html: str, block: str) -> str:
    pattern = re.compile(r'<section class="seo-section seo-faq">.*?</section>', re.S | re.I)
    if not pattern.search(page_html):
        return page_html
    return pattern.sub(block, page_html, count=1)


def replace_faq_schema(page_html: str, schema: str) -> str:
    pattern = re.compile(
        r'<script type="application/ld\+json">(?:(?!</script>).)*?"@type"\s*:\s*"FAQPage"(?:(?!</script>).)*?</script>',
        re.S | re.I,
    )
    if pattern.search(page_html):
        return pattern.sub(schema, page_html, count=1)
    return page_html.replace("</head>", schema + "</head>", 1)


def main() -> None:
    if not MANIFEST.exists():
        raise SystemExit("Missing seo-generated-manifest.txt")

    manifest_files = [
        line.strip()
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip().endswith(".html")
    ]

    updated = []
    validated = []
    fingerprints = {}

    for filename in manifest_files:
        if filename in EXCLUDED:
            continue
        path = Path(filename)
        if not path.exists():
            continue
        page_html = path.read_text(encoding="utf-8")
        if f'class="{FAQ_CLASS}"' not in page_html:
            continue

        city = extract_city(page_html, filename)
        service = extract_service(filename, page_html)
        faqs = build_faqs(filename, city, service)
        block = render_faq_section(city, service, faqs)
        schema = render_schema(faqs)

        fingerprint = hashlib.sha256((block + schema).encode("utf-8")).hexdigest()
        if fingerprint in fingerprints:
            raise SystemExit(f"Duplicate FAQ content generated for {fingerprints[fingerprint]} and {filename}")
        fingerprints[fingerprint] = filename

        new_html = replace_faq_section(page_html, block)
        new_html = replace_faq_schema(new_html, schema)
        if new_html.count(f'class="{FAQ_CLASS}"') != 1:
            raise SystemExit(f"FAQ section validation failed: {filename}")
        if new_html.count('"@type":"FAQPage"') != 1:
            raise SystemExit(f"FAQ schema validation failed: {filename}")

        validated.append(filename)
        if new_html != page_html:
            path.write_text(new_html, encoding="utf-8")
            updated.append(filename)

    print(f"Local FAQ pages checked: {len(validated)}")
    print(f"Local FAQ pages updated: {len(updated)}")
    print(f"Unique FAQ blocks validated: {len(fingerprints)}")


if __name__ == "__main__":
    main()
