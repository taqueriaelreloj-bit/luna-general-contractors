from __future__ import annotations

from pathlib import Path
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


def validate_html(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    for marker in ('<title>', 'name="description"', 'name="robots"', 'rel="canonical"', '<h1', 'application/ld+json', 'tel:+18177845998'):
        if marker not in text:
            errors.append(f"missing {marker}")
    if text.count('<h1') != 1:
        errors.append(f"expected one H1, found {text.count('<h1')}")
    canonical = re.search(r'rel="canonical" href="([^"]+)"', text)
    expected = f"{DOMAIN}/{path.name}"
    if canonical and canonical.group(1) != expected:
        errors.append(f"canonical mismatch: {canonical.group(1)}")
    if path.name not in INDEX_PAGES:
        for schema in ("BreadcrumbList", "LocalBusiness", "GeneralContractor"):
            if schema not in text:
                errors.append(f"missing {schema} schema")
    if path.name not in INDEX_PAGES | ARTICLE_PAGES and "FAQPage" not in text:
        errors.append("missing FAQPage schema")
    if "noindex" in text.lower():
        errors.append("unexpected noindex")
    return errors


def main() -> int:
    manifest = ROOT / "seo-generated-manifest.txt"
    if not manifest.exists():
        print("SEO validation failed:\n- missing seo-generated-manifest.txt")
        return 1
    generated = [line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip().endswith(".html")]
    failures: list[str] = []
    for filename in generated:
        path = ROOT / filename
        if not path.exists():
            failures.append(f"{filename}: file not found")
            continue
        errors = validate_html(path)
        if errors:
            failures.append(f"{filename}: " + "; ".join(errors))
    try:
        tree = ET.parse(ROOT / "sitemap.xml")
        locs = {node.text for node in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc') if node.text}
        for filename in generated:
            if f"{DOMAIN}/{filename}" not in locs:
                failures.append(f"{filename}: missing from sitemap.xml")
    except Exception as exc:
        failures.append(f"sitemap.xml: {exc}")
    if failures:
        print("SEO validation failed:")
        for failure in failures:
            print("-", failure)
        print(f"Checked {len(generated)} generated local SEO pages.")
        return 1
    print(f"SEO validation passed for {len(generated)} generated local SEO pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
