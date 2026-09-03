from __future__ import annotations

from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lunageneralcontractors.com"
INDEX_PAGES = {"service-areas.html", "services-by-city.html", "articles.html"}
ARTICLE_PAGES = {
    "commercial-construction-planning-dallas.html",
    "drywall-repair-after-water-damage-grand-prairie.html",
    "fence-replacement-cost-cedar-hill.html",
    "flooring-options-mansfield.html",
    "roofing-insurance-claim-fort-worth.html",
}
PRIMARY_SERVICE_PAGES = {
    "roofing.html",
    "mitigation.html",
    "insurance-claims.html",
    "kitchens.html",
    "bathrooms.html",
    "flooring.html",
    "painting.html",
    "drywall.html",
    "siding.html",
    "carpentry.html",
    "fencing.html",
    "commercial.html",
}
PRIMARY_PAGES = {"index.html", "es.html", "projects.html"} | PRIMARY_SERVICE_PAGES


def common_errors(path: Path, expected_canonical: str) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    for marker in (
        "<title>",
        'name="description"',
        'name="robots"',
        'rel="canonical"',
        "<h1",
        "application/ld+json",
    ):
        if marker not in text:
            errors.append(f"missing {marker}")
    if text.count("<h1") != 1:
        errors.append(f"expected one H1, found {text.count('<h1')}")
    canonical = re.search(r'rel="canonical" href="([^"]+)"', text)
    if canonical and canonical.group(1) != expected_canonical:
        errors.append(f"canonical mismatch: {canonical.group(1)}")
    return errors


def parsed_schema_types(text: str) -> tuple[set[str], list[str]]:
    types: set[str] = set()
    errors: list[str] = []
    blocks = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        text,
        re.I | re.S,
    )

    def collect(value: object) -> None:
        if isinstance(value, dict):
            schema_type = value.get("@type")
            if isinstance(schema_type, str):
                types.add(schema_type)
            elif isinstance(schema_type, list):
                types.update(item for item in schema_type if isinstance(item, str))
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    for number, block in enumerate(blocks, start=1):
        try:
            collect(json.loads(block))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON-LD block {number}: {exc.msg}")
    return types, errors


def validate_generated(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors = common_errors(path, f"{DOMAIN}/{path.name}")
    if 'tel:+18177845998' not in text:
        errors.append("missing telephone link")
    if path.name not in INDEX_PAGES:
        for schema in ("BreadcrumbList", "LocalBusiness", "GeneralContractor"):
            if schema not in text:
                errors.append(f"missing {schema} schema")
    if path.name not in INDEX_PAGES | ARTICLE_PAGES and "FAQPage" not in text:
        errors.append("missing FAQPage schema")
    if "noindex" in text.lower():
        errors.append("unexpected noindex")
    _, schema_errors = parsed_schema_types(text)
    return errors + schema_errors


def validate_primary(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    canonical = DOMAIN + "/" if path.name == "index.html" else f"{DOMAIN}/{path.name}"
    errors = common_errors(path, canonical)
    for marker in ('property="og:image"', 'name="twitter:card"'):
        if marker not in text:
            errors.append(f"missing {marker}")
    types, schema_errors = parsed_schema_types(text)
    errors.extend(schema_errors)
    if path.name in PRIMARY_SERVICE_PAGES:
        for schema_type in ("Service", "BreadcrumbList"):
            if schema_type not in types:
                errors.append(f"missing {schema_type} schema")
    elif path.name == "projects.html" and "ImageGallery" not in types:
        errors.append("missing ImageGallery schema")
    elif path.name == "index.html":
        for schema_type in ("LocalBusiness", "GeneralContractor", "FAQPage"):
            if schema_type not in types:
                errors.append(f"missing {schema_type} schema")
    elif path.name == "es.html":
        for schema_type in ("LocalBusiness", "GeneralContractor", "WebPage"):
            if schema_type not in types:
                errors.append(f"missing {schema_type} schema")
    return errors


def main() -> int:
    manifest = ROOT / "seo-generated-manifest.txt"
    if not manifest.exists():
        print("SEO validation failed:\n- missing seo-generated-manifest.txt")
        return 1
    generated = [
        line.strip()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip().endswith(".html")
    ]
    failures: list[str] = []
    for filename in generated:
        path = ROOT / filename
        if not path.exists():
            failures.append(f"{filename}: file not found")
            continue
        errors = validate_generated(path)
        if errors:
            failures.append(f"{filename}: " + "; ".join(errors))
    for filename in sorted(PRIMARY_PAGES):
        path = ROOT / filename
        if not path.exists():
            failures.append(f"{filename}: file not found")
            continue
        errors = validate_primary(path)
        if errors:
            failures.append(f"{filename}: " + "; ".join(errors))
    try:
        tree = ET.parse(ROOT / "sitemap.xml")
        locs = [
            node.text
            for node in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if node.text
        ]
        if len(locs) != len(set(locs)):
            failures.append("sitemap.xml: duplicate URLs found")
        for filename in generated:
            if f"{DOMAIN}/{filename}" not in locs:
                failures.append(f"{filename}: missing from sitemap.xml")
        for filename in PRIMARY_PAGES:
            url = DOMAIN + "/" if filename == "index.html" else f"{DOMAIN}/{filename}"
            if url not in locs:
                failures.append(f"{filename}: missing from sitemap.xml")
    except Exception as exc:
        failures.append(f"sitemap.xml: {exc}")
    if failures:
        print("SEO validation failed:")
        for failure in failures:
            print("-", failure)
        print(
            f"Checked {len(generated)} generated local SEO pages and "
            f"{len(PRIMARY_PAGES)} primary pages."
        )
        return 1
    print(
        f"SEO validation passed for {len(generated)} generated local SEO pages and "
        f"{len(PRIMARY_PAGES)} primary pages."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
