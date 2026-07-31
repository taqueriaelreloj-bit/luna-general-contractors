from __future__ import annotations

from datetime import date
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lunageneralcontractors.com"
MANIFEST = ROOT / "seo-generated-manifest.txt"
SITEMAP = ROOT / "sitemap.xml"

INDEX_PAGES = {"service-areas.html", "services-by-city.html", "articles.html"}


def title_from_html(html: str, fallback: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    if not match:
        return fallback
    return re.sub(r"\s+", " ", match.group(1)).strip()


def description_from_html(html: str) -> str:
    match = re.search(r'name="description"\s+content="([^"]+)"', html, re.I)
    return match.group(1).strip() if match else "Construction, remodeling and restoration services from Luna General Contractors."


def page_name(filename: str) -> str:
    return filename.removesuffix(".html").replace("-", " ").title()


def schema_block(filename: str, html: str) -> str:
    url = f"{DOMAIN}/{filename}"
    title = title_from_html(html, page_name(filename))
    description = description_from_html(html)
    name = page_name(filename)

    local_business = {
        "@context": "https://schema.org",
        "@type": ["LocalBusiness", "GeneralContractor"],
        "@id": f"{DOMAIN}/#business",
        "name": "Luna General Contractors",
        "url": url,
        "telephone": "+18177845998",
        "email": "lunabestcontractors@gmail.com",
        "priceRange": "$$",
        "areaServed": {"@type": "AdministrativeArea", "name": "Dallas-Fort Worth, Texas"},
        "description": description,
    }

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": name, "item": url},
        ],
    }

    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"How can I request an estimate for {name}?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Call Luna General Contractors at (817) 784-5998 or use the estimate form on the website.",
                },
            },
            {
                "@type": "Question",
                "name": "Does Luna General Contractors serve the Dallas-Fort Worth area?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. Luna General Contractors provides construction, remodeling, roofing and restoration services across Dallas-Fort Worth and nearby communities.",
                },
            },
        ],
    }

    blocks = []
    if "LocalBusiness" not in html or "GeneralContractor" not in html:
        blocks.append(local_business)
    if filename not in INDEX_PAGES and "BreadcrumbList" not in html:
        blocks.append(breadcrumb)
    if filename not in INDEX_PAGES and "FAQPage" not in html:
        blocks.append(faq)

    return "".join(
        '<script type="application/ld+json">' + json.dumps(block, separators=(",", ":")) + "</script>"
        for block in blocks
    )


def patch_pages(files: list[str]) -> None:
    for filename in files:
        path = ROOT / filename
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        addition = schema_block(filename, html)
        if addition:
            if "</head>" not in html:
                raise RuntimeError(f"{filename} has no </head> tag")
            html = html.replace("</head>", addition + "</head>", 1)
            path.write_text(html, encoding="utf-8")


def patch_sitemap(files: list[str]) -> None:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    tree = ET.parse(SITEMAP)
    root = tree.getroot()
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    existing = {node.text for node in root.findall(f"{ns}url/{ns}loc") if node.text}
    today = date.today().isoformat()

    for filename in files:
        url = f"{DOMAIN}/{filename}"
        if url in existing:
            continue
        entry = ET.SubElement(root, f"{ns}url")
        loc = ET.SubElement(entry, f"{ns}loc")
        loc.text = url
        lastmod = ET.SubElement(entry, f"{ns}lastmod")
        lastmod.text = today

    tree.write(SITEMAP, encoding="utf-8", xml_declaration=True)


def main() -> None:
    files = [
        line.strip()
        for line in MANIFEST.read_text(encoding="utf-8").splitlines()
        if line.strip().endswith(".html")
    ]
    patch_pages(files)
    patch_sitemap(files)
    print(f"Patched structured data and sitemap coverage for {len(files)} generated pages.")


if __name__ == "__main__":
    main()
