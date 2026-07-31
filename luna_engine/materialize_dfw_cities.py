from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CITY_DIR = ROOT / "content" / "cities"

CITIES = [
    ("Irving", "Dallas County", ["Las Colinas", "Valley Ranch", "Hackberry Creek"], ["Dallas", "Grand Prairie", "Coppell", "Carrollton", "Farmers Branch"]),
    ("Keller", "Tarrant County", ["Hidden Lakes", "Marshall Ridge", "The Lakes"], ["Fort Worth", "Southlake", "Grapevine", "North Richland Hills", "Colleyville"]),
    ("Lewisville", "Denton County", ["Castle Hills", "Vista Ridge", "Old Town Lewisville"], ["Coppell", "Carrollton", "Frisco", "Grapevine", "Irving"]),
    ("Mesquite", "Dallas County", ["Creek Crossing", "Town East", "Paschall Park"], ["Dallas", "Garland", "Rowlett", "Rockwall", "Richardson"]),
    ("Garland", "Dallas County", ["Firewheel", "Duck Creek", "Lakewood"], ["Dallas", "Mesquite", "Rowlett", "Richardson", "Plano"]),
    ("Richardson", "Dallas and Collin Counties", ["Canyon Creek", "Cottonwood Heights", "Reservation"], ["Dallas", "Garland", "Plano", "Carrollton", "Farmers Branch"]),
    ("Plano", "Collin County", ["West Plano", "Legacy", "Willow Bend"], ["Richardson", "Frisco", "Allen", "Carrollton", "Garland"]),
    ("Carrollton", "Dallas, Denton and Collin Counties", ["Castle Hills", "Indian Creek", "Josey Ranch"], ["Irving", "Lewisville", "Farmers Branch", "Plano", "Coppell"]),
    ("Farmers Branch", "Dallas County", ["Brookhaven", "Valwood Park", "Mercer Crossing"], ["Dallas", "Irving", "Carrollton", "Coppell", "Richardson"]),
    ("Frisco", "Collin and Denton Counties", ["Starwood", "Phillips Creek Ranch", "Panther Creek"], ["Plano", "McKinney", "Allen", "Lewisville", "Carrollton"]),
    ("McKinney", "Collin County", ["Stonebridge Ranch", "Craig Ranch", "Historic Downtown"], ["Frisco", "Allen", "Plano", "Richardson", "Rockwall"]),
    ("Allen", "Collin County", ["Twin Creeks", "Watters Crossing", "Starcreek"], ["McKinney", "Plano", "Frisco", "Richardson", "Garland"]),
    ("Rockwall", "Rockwall County", ["The Shores", "Stone Creek", "Downtown Rockwall"], ["Rowlett", "Garland", "Mesquite", "Dallas", "McKinney"]),
    ("Rowlett", "Dallas and Rockwall Counties", ["Waterview", "Dalrock", "Lakeview"], ["Rockwall", "Garland", "Mesquite", "Dallas", "Richardson"]),
    ("Bedford", "Tarrant County", ["Bedford Heights", "Mayfair Hills", "Shady Brook"], ["Euless", "Hurst", "Grapevine", "Colleyville", "Fort Worth"]),
    ("Euless", "Tarrant County", ["Glade Parks", "Bear Creek", "Midway Park"], ["Bedford", "Hurst", "Grapevine", "Irving", "Arlington"]),
    ("Hurst", "Tarrant County", ["Mayfair", "Wintergreen", "Hurst Hills"], ["Bedford", "Euless", "North Richland Hills", "Fort Worth", "Arlington"]),
    ("North Richland Hills", "Tarrant County", ["HomeTown", "Forest Glenn", "Northfield Park"], ["Hurst", "Keller", "Fort Worth", "Bedford", "Colleyville"]),
    ("Grapevine", "Tarrant County", ["Silver Lake", "Dove Crossing", "Historic Main Street"], ["Southlake", "Colleyville", "Coppell", "Irving", "Euless"]),
    ("Colleyville", "Tarrant County", ["Timarron", "Montclair Parc", "Bridlewood"], ["Southlake", "Grapevine", "Keller", "Bedford", "North Richland Hills"]),
    ("Southlake", "Tarrant and Denton Counties", ["Timarron", "Carillon", "Southlake Town Square"], ["Grapevine", "Colleyville", "Keller", "Coppell", "Lewisville"]),
    ("Coppell", "Dallas and Denton Counties", ["Northlake Woodlands", "Old Town Coppell", "Cypress Waters"], ["Irving", "Lewisville", "Carrollton", "Grapevine", "Farmers Branch"]),
]


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-")


def city_record(name: str, county: str, neighborhoods: list[str], nearby: list[str]) -> dict:
    slug = slugify(name)
    neighborhood_text = ", ".join(neighborhoods)
    return {
        "name": name,
        "slug": slug,
        "state": "TX",
        "county": county,
        "title": f"General Contractor in {name}, TX | Luna General Contractors",
        "meta_description": f"Luna General Contractors provides roofing, remodeling, restoration and commercial construction in {name}, TX. Call (817) 784-5998 for a free estimate.",
        "hero": f"Professional roofing, remodeling, restoration and construction services for homeowners, investors and businesses in {name}.",
        "local_summary": f"{name} includes established neighborhoods, newer development and active commercial corridors. Properties around {neighborhood_text} may need coordinated roofing, remodeling, water-damage repair, exterior maintenance and interior improvements designed for North Texas heat, wind, hail and heavy rain.",
        "property_types": [
            f"Homes in {neighborhoods[0]}",
            f"Properties near {neighborhoods[1]}",
            "Established single-family homes",
            "Newer residential construction",
            "Retail, office and investment properties"
        ],
        "common_needs": [
            "Roof inspections and storm repairs",
            "Kitchen and bathroom remodeling",
            "Flooring, drywall and painting",
            "Water-damage restoration",
            "Siding, carpentry and fencing",
            "Commercial repairs and tenant improvements"
        ],
        "nearby_cities": nearby,
        "faqs": [
            {"question": f"Do you provide free estimates in {name}?", "answer": f"Yes. Luna General Contractors provides free estimates for most roofing, remodeling, restoration and commercial projects in {name}."},
            {"question": f"Can you repair storm damage in {name}?", "answer": "Yes. We inspect visible hail, wind and water damage, prepare a written scope and complete approved repairs."},
            {"question": f"Do you remodel occupied homes in {name}?", "answer": "Yes. We coordinate protection, access, scheduling and cleanup to reduce disruption while the property remains occupied."},
            {"question": f"Do you serve commercial properties in {name}?", "answer": "Yes. We provide repairs, tenant improvements, interior build-outs and coordinated commercial construction services."}
        ]
    }


def main() -> None:
    CITY_DIR.mkdir(parents=True, exist_ok=True)
    for name, county, neighborhoods, nearby in CITIES:
        path = CITY_DIR / f"{slugify(name)}.json"
        path.write_text(json.dumps(city_record(name, county, neighborhoods, nearby), indent=2), encoding="utf-8")
        print(f"Materialized {path.relative_to(ROOT)}")
    print(f"Materialized {len(CITIES)} DFW city data files")


if __name__ == "__main__":
    main()
