from __future__ import annotations

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lunageneralcontractors.com"

# The validator focuses on pages produced by the local SEO generator. Older
# hand-built pages use a different template and are checked separately by the
# normal site review instead of being treated as generator failures.
GENERATED_MARKERS = (
    'local-seo.css',
    'data-seo-footer',
    'seo-pages.js',
)

REQUIRED = (
    '<title>',
    'name="description"',
    'name="robots"',
    'rel="canonical"',
    '<h1',
    'application/ld+json',
    'tel:+18177845998',
)


def is_generated_page(text: str) -> bool:
    return any(marker in text for marker in GENERATED_MARKERS)


def validate_html(path: Path, text: str) -> list[str]:
    errors: list[str] = []

    for marker in REQUIRED:
        if marker not in text:
            errors.append(f"missing {marker}")

    h1_count = len(re.findall(r'<h1(?:\s|>)', text, flags=re.IGNORECASE))
    if h1_count != 1:
        errors.append(f"expected one H1, found {h1_count}")

    canonical = re.search(
        r'rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
        text,
        flags=re.IGNORECASE,
    )
    expected = f"{DOMAIN}/{path.name}"
    if canonical and canonical.group(1) != expected:
        errors.append(f"canonical mismatch: {canonical.group(1)}")

    if text.count('application/ld+json') < 2:
        errors.append('expected at least two JSON-LD schema blocks')

    if 'FAQPage' not in text:
        errors.append('missing FAQPage schema')

    if 'BreadcrumbList' not in text:
        errors.append('missing BreadcrumbList schema')

    if 'LocalBusiness' not in text and 'GeneralContractor' not in text:
        errors.append('missing LocalBusiness/GeneralContractor schema')

    return errors


def load_sitemap() -> set[str]:
    sitemap = ROOT / 'sitemap.xml'
    tree = ET.parse(sitemap)
    return {
        node.text.strip()
        for node in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        if node.text and node.text.strip()
    }


def main() -> int:
    failures: list[str] = []
    generated: list[Path] = []

    for path in sorted(ROOT.glob('*.html')):
        text = path.read_text(encoding='utf-8', errors='replace')
        if not is_generated_page(text):
            continue
        generated.append(path)
        errors = validate_html(path, text)
        if errors:
            failures.append(f"{path.name}: " + '; '.join(errors))

    if not generated:
        failures.append('No generated local SEO pages were detected.')

    try:
        locs = load_sitemap()
        for path in generated:
            expected_url = f"{DOMAIN}/{path.name}"
            if expected_url not in locs:
                failures.append(f"{path.name}: missing from sitemap.xml")
    except Exception as exc:
        failures.append(f"sitemap.xml: {exc}")

    if failures:
        print('SEO validation failed:')
        for failure in failures:
            print('-', failure)
        print(f'Checked {len(generated)} generated local SEO pages.')
        return 1

    print(f'SEO validation passed for {len(generated)} generated local SEO pages.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
