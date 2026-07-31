from __future__ import annotations

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    '<title>',
    'name="description"',
    'rel="canonical"',
    '<h1',
    'application/ld+json',
    'tel:+18177845998',
)


def validate_html(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    for marker in REQUIRED:
        if marker not in text:
            errors.append(f"missing {marker}")
    if text.count('<h1') != 1:
        errors.append(f"expected one H1, found {text.count('<h1')}")
    canonical = re.search(r'rel="canonical" href="([^"]+)"', text)
    if canonical and not canonical.group(1).endswith('/' + path.name):
        if path.name != 'index.html' or canonical.group(1) != 'https://lunageneralcontractors.com/':
            errors.append(f"canonical mismatch: {canonical.group(1)}")
    return errors


def main() -> int:
    failures: list[str] = []
    html_files = sorted(ROOT.glob('*.html'))
    for path in html_files:
        errors = validate_html(path)
        if errors:
            failures.append(f"{path.name}: " + '; '.join(errors))

    sitemap = ROOT / 'sitemap.xml'
    try:
        tree = ET.parse(sitemap)
        locs = {node.text for node in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc') if node.text}
        for path in html_files:
            if path.name == '404.html':
                continue
            url = 'https://lunageneralcontractors.com/' if path.name == 'index.html' else f'https://lunageneralcontractors.com/{path.name}'
            if url not in locs:
                failures.append(f"{path.name}: missing from sitemap.xml")
    except Exception as exc:
        failures.append(f"sitemap.xml: {exc}")

    if failures:
        print('SEO validation failed:')
        for failure in failures:
            print('-', failure)
        return 1

    print(f'SEO validation passed for {len(html_files)} HTML pages.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
