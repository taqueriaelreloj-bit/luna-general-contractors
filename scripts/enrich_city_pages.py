from __future__ import annotations

from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

CITY_DATA = {
    "Waxahachie": {
        "profile": "Waxahachie combines older properties near the historic core, established neighborhoods, newer subdivisions and active commercial corridors. A useful project plan must account for the building age, previous repairs, access, drainage and how several trades will be sequenced.",
        "needs": ["Roof and exterior repairs after wind or hail", "Bathroom and kitchen updates in older or newer homes", "Drywall, flooring and paint after plumbing or water damage"],
        "planning": "Older homes may require careful demolition and compatibility checks, while newer properties often focus on layout, finishes and long-term durability. We inspect the actual work area before finalizing the scope.",
    },
    "Red Oak": {
        "profile": "Red Oak continues to grow along the I-35E corridor, with newer residential communities, established homes and local commercial properties. Projects often require coordination between interior finishes, exterior protection and practical scheduling for occupied buildings.",
        "needs": ["Storm-related roofing and siding work", "Whole-room remodeling and finish upgrades", "Fencing, carpentry and exterior property improvements"],
        "planning": "Newer construction can still have drainage, flashing, settlement or finish issues. A site-specific inspection helps separate cosmetic work from repairs that should be completed first.",
    },
    "Ovilla": {
        "profile": "Ovilla properties often include custom homes, larger lots and a mix of building ages. Access, long driveways, exterior exposure and the relationship between the house, drainage and surrounding land can affect project planning.",
        "needs": ["Exterior repairs and weather protection", "Custom bathroom and kitchen renovations", "Carpentry, fencing and property improvement projects"],
        "planning": "Larger residential properties benefit from clear staging, material delivery planning and protection of finished areas. We organize the work so trades do not interfere with one another.",
    },
    "Glenn Heights": {
        "profile": "Glenn Heights includes established neighborhoods and newer development near major transportation routes. Home improvement work frequently combines repairs, updated finishes and exterior maintenance.",
        "needs": ["Roofing and storm-damage repairs", "Bathroom, kitchen and flooring upgrades", "Drywall and paint following leaks or plumbing work"],
        "planning": "The best sequence usually starts with moisture, structure and exterior protection before moving to drywall, flooring, cabinets and paint.",
    },
    "DeSoto": {
        "profile": "DeSoto has mature neighborhoods, larger homes, newer residential areas and active commercial corridors. Property age and previous remodeling can change what is discovered once finishes are removed.",
        "needs": ["Roof, fascia, siding and exterior repairs", "Bathroom and kitchen modernization", "Insurance reconstruction and interior finish replacement"],
        "planning": "We document visible conditions, clarify allowances and identify decisions that must be made before demolition so the project can move with fewer interruptions.",
    },
    "Lancaster": {
        "profile": "Lancaster includes historic properties, established residential areas, newer developments and commercial spaces near major highways. Construction planning should account for the building's age, use and previous modifications.",
        "needs": ["Repairs for older homes and investment properties", "Roofing, siding and exterior maintenance", "Commercial repairs and tenant improvements"],
        "planning": "Older structures may contain multiple layers of finishes or earlier repairs. We keep concealed conditions separate from the visible base scope and discuss them when exposed.",
    },
    "Cedar Hill": {
        "profile": "Cedar Hill properties range from mature neighborhoods to hillside and lake-area homes. Elevation changes, drainage, trees and exterior exposure can influence roofing, foundations, siding and outdoor work.",
        "needs": ["Roofing and exterior protection", "Interior remodeling with coordinated trades", "Fencing, carpentry and drainage-related repairs"],
        "planning": "Site access and water movement around the property should be reviewed before replacing exterior finishes or repairing repeated interior moisture damage.",
    },
    "Duncanville": {
        "profile": "Duncanville contains established homes, investment properties and commercial buildings with convenient access to Dallas. Many projects involve updating older finishes while addressing deferred maintenance.",
        "needs": ["Bathroom and kitchen renovations", "Roof, siding and exterior trim repairs", "Drywall, flooring and painting for occupied properties"],
        "planning": "For occupied homes and rentals, sequencing, dust control and daily cleanup are important parts of the written project plan.",
    },
    "Grand Prairie": {
        "profile": "Grand Prairie spans diverse neighborhoods, retail centers, industrial areas and properties between Dallas and Fort Worth. The type of building and its daily use determine access, work hours and trade coordination.",
        "needs": ["Residential remodeling and repairs", "Commercial build-outs and property maintenance", "Water-damage reconstruction and insurance repairs"],
        "planning": "Commercial and occupied projects benefit from phased work, clear shutdown planning and early decisions on long-lead materials.",
    },
    "Mansfield": {
        "profile": "Mansfield includes established family neighborhoods, newer construction and growing commercial districts. Projects range from targeted repairs to complete interior transformations.",
        "needs": ["Bathroom and kitchen remodeling", "Roofing and storm restoration", "Flooring, painting and carpentry upgrades"],
        "planning": "We verify measurements, product compatibility and installation requirements before ordering major finish materials.",
    },
    "Arlington": {
        "profile": "Arlington combines mature residential neighborhoods, newer communities, entertainment districts and commercial properties. Access, parking and occupancy can be as important as the construction scope.",
        "needs": ["Home remodeling and exterior repairs", "Commercial construction and tenant improvements", "Insurance restoration after storms or water losses"],
        "planning": "A practical schedule separates noisy or disruptive work from finish work and identifies inspections, deliveries and customer decisions in advance.",
    },
    "Dallas": {
        "profile": "Dallas includes urban homes, historic neighborhoods, investment properties, multifamily buildings and commercial spaces. Building age, access, parking and local project requirements vary widely across the city.",
        "needs": ["Full interior remodeling and property updates", "Roofing, siding and exterior restoration", "Commercial build-outs and insurance reconstruction"],
        "planning": "Dense or occupied properties require careful delivery planning, protection of common areas and coordination with owners, tenants or property managers.",
    },
    "Fort Worth": {
        "profile": "Fort Worth includes historic districts, established suburbs, newer growth areas and a broad range of commercial properties. Construction methods and finish expectations vary by property type and age.",
        "needs": ["Renovations for older and newer homes", "Storm-related roof and exterior repairs", "Commercial improvements and reconstruction"],
        "planning": "We review the existing assembly and prior repairs so replacement materials and methods are appropriate for the building.",
    },
    "Irving": {
        "profile": "Irving includes established neighborhoods, centrally located homes, Las Colinas offices and commercial properties near major highways. Scheduling and access are key for active businesses and occupied residences.",
        "needs": ["Residential remodeling and repairs", "Office and commercial improvements", "Roofing, water-damage and insurance restoration"],
        "planning": "For business properties, we can organize work by area or phase to reduce interruption while maintaining a clear sequence between trades.",
    },
    "Keller": {
        "profile": "Keller has custom homes, family neighborhoods, established properties and maintained commercial spaces. Owners often prioritize durable materials, clean details and careful protection of occupied areas.",
        "needs": ["High-detail bathroom and kitchen remodeling", "Roof and exterior maintenance", "Custom carpentry, flooring and painting"],
        "planning": "Finish selections should be confirmed early because custom sizes, glass, cabinetry and specialty materials can affect the schedule.",
    },
    "Lewisville": {
        "profile": "Lewisville includes lake-area communities, mature neighborhoods, newer housing and busy business corridors. Exterior exposure and property use influence the most practical repair or remodeling approach.",
        "needs": ["Roof and siding repairs", "Interior remodeling and flooring", "Commercial repairs and water-damage reconstruction"],
        "planning": "Moisture sources and exterior openings should be corrected before replacing interior drywall, insulation, flooring or paint.",
    },
    "Mesquite": {
        "profile": "Mesquite includes established homes, rental and investment properties, newer communities and commercial areas east of Dallas. Many projects balance budget, durability and quick return to use.",
        "needs": ["Make-ready and property improvement work", "Roofing and exterior repairs", "Bathroom, kitchen and flooring updates"],
        "planning": "A clearly separated scope helps owners prioritize essential repairs, optional upgrades and items that depend on concealed conditions.",
    },
    "Garland": {
        "profile": "Garland has diverse housing, mature neighborhoods, industrial properties and active commercial corridors. Projects frequently involve older systems, previous repairs and multiple construction phases.",
        "needs": ["Interior renovation and repair", "Roofing, siding and storm restoration", "Commercial and light-industrial property improvements"],
        "planning": "We identify which existing materials can remain and which must be removed so new work has a sound, compatible base.",
    },
    "Richardson": {
        "profile": "Richardson includes established neighborhoods, technology corridors, offices and commercial properties. Owners often need well-organized remodeling that minimizes disruption and maintains a professional finished appearance.",
        "needs": ["Home remodeling and finish modernization", "Office and commercial improvements", "Roofing and water-damage repairs"],
        "planning": "Occupied projects require agreed work zones, access rules, protection and communication about temporary service interruptions.",
    },
    "Plano": {
        "profile": "Plano includes master-planned neighborhoods, executive homes, established communities and major commercial districts. Projects often involve coordinated finish selections and high expectations for consistency.",
        "needs": ["Complete bathroom and kitchen renovation", "Roofing and exterior maintenance", "Commercial remodeling and finish upgrades"],
        "planning": "We coordinate dimensions and product specifications among cabinets, countertops, plumbing, electrical, tile and finish carpentry before installation.",
    },
    "Carrollton": {
        "profile": "Carrollton has mature neighborhoods, newer developments and centrally located business corridors. Property improvement work ranges from repairs in older homes to modern finish upgrades.",
        "needs": ["Interior remodeling and repairs", "Roof and exterior improvements", "Commercial construction and maintenance"],
        "planning": "When several rooms or trades are involved, a shared sequence prevents finished work from being damaged by later rough work.",
    },
    "Farmers Branch": {
        "profile": "Farmers Branch includes established residential areas, redevelopment and business districts near major highways. Access, occupancy and building age are common planning factors.",
        "needs": ["Residential renovation and repair", "Commercial finish-outs and maintenance", "Roofing and insurance restoration"],
        "planning": "We review work-hour restrictions, access, debris handling and temporary protection before beginning active commercial projects.",
    },
    "Frisco": {
        "profile": "Frisco has newer homes, luxury communities and rapidly expanding commercial districts. Even newer properties may need layout changes, finish upgrades or repairs caused by weather and water.",
        "needs": ["Premium bathroom and kitchen upgrades", "Roofing and storm restoration", "Commercial and tenant improvement projects"],
        "planning": "Selections, lead times and installation specifications should be resolved before demolition when specialty finishes are involved.",
    },
    "McKinney": {
        "profile": "McKinney includes historic downtown properties, mature neighborhoods and extensive newer development. The building's age and construction type determine the right remodeling and repair approach.",
        "needs": ["Renovation of older and newer homes", "Roof and exterior repairs", "Commercial remodeling and restoration"],
        "planning": "Historic or older properties may require more investigation before exact repair quantities can be confirmed.",
    },
    "Allen": {
        "profile": "Allen includes established family neighborhoods, newer homes and commercial development along US-75. Projects often focus on improving function, finishes and long-term property maintenance.",
        "needs": ["Bathroom and kitchen remodeling", "Roofing, siding and exterior work", "Flooring, painting and carpentry updates"],
        "planning": "A coordinated scope helps avoid conflicts between cabinetry, countertops, tile, plumbing, electrical and flooring transitions.",
    },
    "Rockwall": {
        "profile": "Rockwall includes lake-area properties, newer neighborhoods and growing commercial corridors. Wind exposure, drainage and exterior maintenance can influence project priorities.",
        "needs": ["Roof and exterior weather protection", "Interior remodeling and finish upgrades", "Water-damage repair and insurance reconstruction"],
        "planning": "Exterior leaks should be traced to their source before interior repairs are closed and finished.",
    },
    "Rowlett": {
        "profile": "Rowlett has lakefront communities, established neighborhoods and expanding residential areas. Weather exposure and moisture management are frequent considerations for exterior and interior repairs.",
        "needs": ["Roofing and storm-damage work", "Bathroom, kitchen and flooring remodeling", "Drywall and reconstruction after water losses"],
        "planning": "We separate emergency protection, drying or source correction from permanent reconstruction so materials are installed under suitable conditions.",
    },
    "Bedford": {
        "profile": "Bedford is centrally located in the Mid-Cities with established neighborhoods and commercial properties. Many projects involve updating older finishes while keeping occupied spaces functional.",
        "needs": ["Interior remodeling and repairs", "Roofing and exterior maintenance", "Commercial improvements and restoration"],
        "planning": "Phased scheduling can keep part of a home or business available while work proceeds in another area.",
    },
    "Euless": {
        "profile": "Euless includes Mid-Cities neighborhoods, airport-area businesses and established communities. Access and scheduling are important for active commercial locations and occupied homes.",
        "needs": ["Residential remodeling", "Commercial repair and build-out work", "Roofing and water-damage restoration"],
        "planning": "Material deliveries, parking, disposal and noisy work should be planned around the property's daily use.",
    },
    "Hurst": {
        "profile": "Hurst has mature neighborhoods and commercial properties in the center of the Mid-Cities. Property updates often combine essential repairs with modern finishes.",
        "needs": ["Bathroom, kitchen and flooring renovation", "Roof and exterior repair", "Commercial construction and maintenance"],
        "planning": "We establish which work must occur first and which finish decisions can be made later without delaying the critical path.",
    },
    "North Richland Hills": {
        "profile": "North Richland Hills includes family neighborhoods, established homes and active retail corridors. Projects range from storm repairs to complete room remodeling and commercial improvements.",
        "needs": ["Residential remodeling and exterior work", "Roofing and insurance repairs", "Commercial tenant and maintenance projects"],
        "planning": "A written scope should identify protection, demolition, rough work, inspections, finishes and final cleanup as separate stages.",
    },
    "Grapevine": {
        "profile": "Grapevine includes historic homes, lake-area properties, established neighborhoods and hospitality-focused commercial spaces. Appearance, access and guest or customer impact are important planning concerns.",
        "needs": ["Renovation and repair of distinctive homes", "Roof and exterior maintenance", "Hospitality and commercial improvements"],
        "planning": "For customer-facing properties, we plan visible protection, work zones and phased completion to preserve a professional environment.",
    },
    "Colleyville": {
        "profile": "Colleyville features custom residences, larger lots and high-detail home improvement projects. Owners frequently prioritize finish quality, careful protection and coordinated specialty trades.",
        "needs": ["Custom bathroom and kitchen remodeling", "Exterior and roofing improvements", "Carpentry, flooring and detailed finish work"],
        "planning": "Custom materials require confirmed dimensions, samples and lead times before installation dates are committed.",
    },
    "Southlake": {
        "profile": "Southlake includes luxury homes, custom properties and premium commercial spaces. Projects often require detailed planning, finish coordination and careful work inside occupied buildings.",
        "needs": ["High-end interior remodeling", "Roofing and exterior property improvements", "Commercial finish upgrades"],
        "planning": "We organize approvals and product selections early so specialty fabrication does not interrupt the construction sequence.",
    },
    "Coppell": {
        "profile": "Coppell has well-maintained neighborhoods, executive homes and centrally located businesses. Projects commonly focus on functional updates, quality finishes and protecting existing improvements.",
        "needs": ["Bathroom and kitchen modernization", "Roof and exterior maintenance", "Commercial remodeling and repair"],
        "planning": "Protection of floors, cabinetry, landscaping and occupied areas is included in project planning rather than treated as an afterthought.",
    },
    "Midlothian": {
        "profile": "Midlothian combines fast-growing Ellis County neighborhoods, established homes, acreage properties and expanding commercial corridors. Construction planning must fit both newer development and older properties with previous repairs.",
        "needs": ["Roofing and storm-related exterior repairs", "Bathroom and kitchen remodeling", "Water-damage reconstruction and general property improvements"],
        "planning": "We review access, drainage, existing finishes and the required trade sequence before work begins, then separate the base scope from concealed conditions.",
    },
}


def slug(city: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", city.lower()).strip("-")


def section(city: str, data: dict[str, object]) -> str:
    needs = "".join(f"<li>{escape(item)}</li>" for item in data["needs"])
    return f'''<section class="local-content city-depth" data-city-depth="1"><div class="container">
<div class="local-grid"><article><p class="eyebrow gold">Built Around Local Property Conditions</p><h2>Planning Construction Work in {escape(city)}</h2><p>{escape(str(data["profile"]))}</p><p>{escape(str(data["planning"]))}</p></article>
<aside class="local-card"><h3>Common Project Priorities</h3><ul>{needs}</ul><p><strong>Estimate approach:</strong> visible conditions, measurements, access, requested materials and trade coordination are reviewed before the written scope is finalized.</p></aside></div>
<div class="local-grid city-depth-grid"><article><h2>How We Organize the Work</h2><p>Projects are divided into clear stages: site protection, demolition, structural or moisture corrections, rough mechanical work, inspections when required, finish installation and final cleanup. This sequence reduces rework and makes responsibilities easier to understand.</p><p>When hidden damage or an unexpected existing condition is uncovered, we document it and discuss the effect on price and schedule before adding work.</p></article>
<aside class="local-card"><h3>Useful Information to Send</h3><ul><li>Project address and preferred contact information</li><li>Photos of the work area and any visible damage</li><li>Approximate dimensions or plans, when available</li><li>Desired materials, finishes and target timing</li></ul></aside></div>
</div></section>'''


def main() -> int:
    changed = 0
    missing: list[str] = []
    for city, data in CITY_DATA.items():
        path = ROOT / f"{slug(city)}.html"
        if not path.exists():
            missing.append(path.name)
            continue
        html = path.read_text(encoding="utf-8")
        if 'data-city-depth="1"' in html:
            continue
        marker = '<div class="faq"><h2>Frequently Asked Questions</h2>'
        if marker not in html:
            missing.append(f"{path.name} (insertion marker)")
            continue
        html = html.replace(marker, section(city, data) + marker, 1)
        path.write_text(html, encoding="utf-8")
        changed += 1

    if missing:
        raise SystemExit("Could not enrich: " + ", ".join(missing))
    print(f"Enriched {changed} city pages with unique local content.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
