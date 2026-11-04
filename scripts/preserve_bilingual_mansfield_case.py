#!/usr/bin/env python3
"""Preserve the bilingual Mansfield pages after project regeneration."""

from __future__ import annotations

import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ENGLISH = ROOT / "gray-subway-kitchen-backsplash-mansfield.html"
SPANISH = ROOT / "proyecto-backsplash-cocina-mansfield.html"
PROJECTS = ROOT / "projects.html"
SITEMAP = ROOT / "sitemap.xml"
SPANISH_NAME = "proyecto-backsplash-cocina-mansfield.html"
SPANISH_URL = f"https://lunageneralcontractors.com/{SPANISH_NAME}"
OLD_TITLE = (
    "<title>Gray Subway Tile Kitchen Backsplash in Mansfield "
    "| Luna General Contractors</title>"
)
NEW_TITLE = "<title>Mansfield Gray Subway Tile Backsplash | Luna</title>"
CANONICAL = (
    '<link rel="canonical" '
    'href="https://lunageneralcontractors.com/'
    'gray-subway-kitchen-backsplash-mansfield.html">'
)
ALTERNATES = (
    CANONICAL
    + '<link rel="alternate" hreflang="en-US" '
    'href="https://lunageneralcontractors.com/'
    'gray-subway-kitchen-backsplash-mansfield.html">'
    + '<link rel="alternate" hreflang="es-US" '
    f'href="{SPANISH_URL}">'
    + '<link rel="alternate" hreflang="x-default" '
    'href="https://lunageneralcontractors.com/'
    'gray-subway-kitchen-backsplash-mansfield.html">'
)
SPANISH_INDEX_LINK = (
    '<a class="seo-text-link" '
    f'href="{SPANISH_NAME}" lang="es">Ver en español →</a>'
)

EVIDENCE_START = "<!-- VERIFIED_PROJECT_EVIDENCE_START -->"
EVIDENCE_END = "<!-- VERIFIED_PROJECT_EVIDENCE_END -->"
EVIDENCE_BLOCK = """<!-- VERIFIED_PROJECT_EVIDENCE_START --><div class="local-grid" data-project-evidence><article><p class="eyebrow gold">Evidence status</p><h2>What this project record verifies</h2><ul><li><strong>Location:</strong> Mansfield, Texas</li><li><strong>Work:</strong> gray subway-tile backsplash with cuts around cabinets, outlets and the range area</li><li><strong>Recorded duration:</strong> approximately two days</li><li><strong>Completion date:</strong> May 30, 2018</li><li><strong>Published evidence:</strong> one photograph showing tile installation and the protected work area</li></ul></article><article><p class="eyebrow gold">Transparent limits</p><h2>What is not claimed</h2><p>The published record does not contain the contract price, a project-specific customer review or a photograph from before work began. This page does not invent or imply those details.</p><p>A current price must be based on measured wall area, tile selection, layout, outlet count, substrate repair, edge treatment and site access.</p><p><a class="seo-text-link" href="#estimate-form">Request a measured Mansfield estimate →</a></p></article></div><!-- VERIFIED_PROJECT_EVIDENCE_END -->"""


def _legacy_project_patch_english() -> None:
    source = ENGLISH.read_text(encoding="utf-8")
    if OLD_TITLE in source:
        source = source.replace(OLD_TITLE, NEW_TITLE, 1)
    elif NEW_TITLE not in source:
        raise SystemExit("Mansfield English case title was not recognized")

    if 'hreflang="es-US"' not in source:
        if CANONICAL not in source:
            raise SystemExit("Mansfield English canonical was not found")
        source = source.replace(CANONICAL, ALTERNATES, 1)

    if f'href="{SPANISH_NAME}" lang="es"' not in source:
        match = re.search(r'<nav class="breadcrumbs">.*?</nav>', source, re.S)
        if not match:
            raise SystemExit("Mansfield English breadcrumb was not found")
        switcher = (
            '<p class="language-switch"><a '
            f'href="{SPANISH_NAME}" lang="es">'
            "Leer este caso en español →</a></p>"
        )
        source = source[: match.end()] + switcher + source[match.end() :]

    if 'property="og:image"' not in source:
        anchor = (
            '<meta property="og:url" '
            'content="https://lunageneralcontractors.com/'
            'gray-subway-kitchen-backsplash-mansfield.html">'
        )
        social = (
            anchor
            + '<meta property="og:image" '
            'content="https://lunageneralcontractors.com/20180530-181936.webp">'
            + '<meta property="og:image:width" content="720">'
            + '<meta property="og:image:height" content="405">'
            + '<meta property="og:image:alt" '
            'content="Gray subway tile kitchen backsplash installation '
            'in Mansfield Texas">'
            + '<meta name="twitter:card" content="summary_large_image">'
            + '<meta name="twitter:image" '
            'content="https://lunageneralcontractors.com/20180530-181936.webp">'
        )
        if anchor not in source:
            raise SystemExit("Mansfield English og:url was not found")
        source = source.replace(anchor, social, 1)

    source = source.replace(
        'loading="lazy" width="1200" height="900"',
        'loading="lazy" decoding="async" width="720" height="405"',
    )
    source = re.sub(
        re.escape(EVIDENCE_START) + r"[\\s\\S]*?" + re.escape(EVIDENCE_END),
        "",
        source,
    )
    evidence_anchor = '<p><strong>Completed:</strong> 2018-05-30</p>'
    if evidence_anchor not in source:
        raise SystemExit("Mansfield English evidence anchor was not found")
    source = source.replace(evidence_anchor, evidence_anchor + EVIDENCE_BLOCK, 1)
    source = re.sub(
        r'"dateModified":"[^"]+"',
        '"dateModified":"2026-09-06"',
        source,
        count=1,
    )

    ENGLISH.write_text(source, encoding="utf-8")


PAGE_URL = "https://lunageneralcontractors.com/gray-subway-kitchen-backsplash-mansfield.html"
PAGE_LABEL = "Kitchen Backsplash, Mansfield, Texas"
PAGE_DESCRIPTION = (
    "Kitchen backsplash services for Mansfield, Texas kitchens, with planning "
    "for tile selection, layout, outlets, cabinetry and range-wall details."
)
IMAGE_ALT = "Kitchen backsplash, Mansfield, Texas"
IMAGE_PATHS = tuple(
    "assets/images/illustrations/page-owned/"
    "gray-subway-kitchen-backsplash-mansfield/"
    f"gray-subway-kitchen-backsplash-mansfield-scene-0{slot}.webp"
    for slot in range(1, 6)
)


def _replace_once(source: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, source, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"Mansfield English page: expected one {label}")
    return updated


def _schema(data: dict) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, separators=(",", ":")) + "</script>"


def _neutral_page_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": PAGE_LABEL,
        "description": PAGE_DESCRIPTION,
        "url": PAGE_URL,
        "about": [
            {"@type": "Service", "name": "Kitchen Backsplash"},
            {"@type": "City", "name": "Mansfield, Texas"},
        ],
        "mainEntity": {
            "@type": "Service",
            "name": "Kitchen Backsplash",
            "areaServed": {"@type": "City", "name": "Mansfield, Texas"},
        },
    }


def _neutral_breadcrumb_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://lunageneralcontractors.com/"},
            {
                "@type": "ListItem",
                "position": 2,
                "name": "Kitchen Remodeling in Mansfield",
                "item": "https://lunageneralcontractors.com/mansfield-kitchen-remodeling.html",
            },
            {"@type": "ListItem", "position": 3, "name": PAGE_LABEL, "item": PAGE_URL},
        ],
    }


def _neutral_gallery_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": PAGE_LABEL,
        "associatedMedia": [
            {
                "@type": "ImageObject",
                "contentUrl": f"https://lunageneralcontractors.com/{image}",
                "caption": PAGE_LABEL,
            }
            for image in IMAGE_PATHS
        ],
    }


def _replace_structured_data(source: str) -> str:
    seen = {"page": 0, "breadcrumb": 0, "gallery": 0}

    def rewrite(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)
        if not isinstance(data, dict):
            return match.group(0)
        kind = data.get("@type")
        if kind in {"Article", "WebPage"} and data.get("mainEntityOfPage", data.get("url", PAGE_URL)) == PAGE_URL:
            seen["page"] += 1
            return _schema(_neutral_page_schema())
        if kind == "BreadcrumbList":
            seen["breadcrumb"] += 1
            return _schema(_neutral_breadcrumb_schema())
        if kind == "ImageGallery":
            seen["gallery"] += 1
            return _schema(_neutral_gallery_schema())
        return match.group(0)

    source = re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        rewrite,
        source,
        flags=re.S,
    )
    if seen != {"page": 1, "breadcrumb": 1, "gallery": 1}:
        raise SystemExit(f"Mansfield English page: unexpected structured-data blocks {seen}")
    return source


def _replace_gallery_copy(source: str) -> str:
    match = re.search(
        r"<!-- page-owned-imagery:start -->.*?<!-- page-owned-imagery:end -->",
        source,
        flags=re.S,
    )
    if not match:
        raise SystemExit("Mansfield English page: page-owned gallery was not found")
    gallery = match.group(0)
    gallery = _replace_once(
        gallery,
        r'<h2\b[^>]*id="page-owned-gallery-title"[^>]*>.*?</h2>',
        f'<h2 class="page-owned-gallery__heading" id="page-owned-gallery-title">{PAGE_LABEL}</h2>',
        "page-owned gallery heading",
    )
    gallery, labels = re.subn(
        r'aria-label="View [^"]*"',
        f'aria-label="View {PAGE_LABEL}"',
        gallery,
    )
    gallery, alts = re.subn(
        r'(<img\b[^>]*\balt=")[^"]*(")',
        lambda item: item.group(1) + IMAGE_ALT + item.group(2),
        gallery,
    )
    gallery, captions = re.subn(
        r"<figcaption>.*?</figcaption>",
        f"<figcaption>{PAGE_LABEL}</figcaption>",
        gallery,
        flags=re.S,
    )
    if (labels, alts, captions) != (5, 5, 5):
        raise SystemExit(
            "Mansfield English page: expected five gallery labels, alts, and captions"
        )
    return source[: match.start()] + gallery + source[match.end() :]


def patch_english() -> None:
    """Normalize only the English Mansfield page after the shared builders run."""
    source = ENGLISH.read_text(encoding="utf-8")
    if 'rel="canonical" href="' + PAGE_URL + '"' not in source:
        raise SystemExit("Mansfield English canonical was not found")
    if 'hreflang="es-US"' not in source:
        source = source.replace(CANONICAL, ALTERNATES, 1)

    source = _replace_once(
        source,
        r"<title>.*?</title>",
        f"<title>{PAGE_LABEL} | Luna General Contractors</title>",
        "title",
    )
    source = _replace_once(
        source,
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{PAGE_DESCRIPTION}">',
        "meta description",
    )
    source = _replace_once(
        source,
        r'<meta property="og:type" content="[^"]*">',
        '<meta property="og:type" content="website">',
        "Open Graph type",
    )
    source = _replace_once(
        source,
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{PAGE_LABEL}">',
        "Open Graph title",
    )
    source = _replace_once(
        source,
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{PAGE_DESCRIPTION}">',
        "Open Graph description",
    )
    source = _replace_structured_data(source)

    source = re.sub(
        r'<meta\b(?=[^>]*(?:property|name)=["\'](?:og:image(?::[^"\']*)?|twitter:image(?::[^"\']*)?|twitter:card)["\'])[^>]*>',
        "",
        source,
        flags=re.I,
    )
    social_image = f"https://lunageneralcontractors.com/{IMAGE_PATHS[0]}"
    social = (
        f'<meta property="og:image" content="{social_image}">'
        '<meta property="og:image:width" content="1280">'
        '<meta property="og:image:height" content="853">'
        f'<meta property="og:image:alt" content="{IMAGE_ALT}">'
        f'<meta name="twitter:image" content="{social_image}">'
        f'<meta name="twitter:image:alt" content="{IMAGE_ALT}">'
        '<meta name="twitter:card" content="summary_large_image">'
    )
    source = _replace_once(source, r"</head>", social + "</head>", "head close")

    hero = (
        '<section class="local-hero"><div class="container">'
        '<nav class="breadcrumbs"><a href="index.html">Home</a> / '
        '<a href="mansfield-kitchen-remodeling.html">Kitchen Remodeling in Mansfield</a> / '
        f"{PAGE_LABEL}</nav>"
        f'<p class="language-switch"><a href="{SPANISH_NAME}" lang="es">Ver en español</a></p>'
        '<p class="eyebrow gold">Kitchen Backsplash</p>'
        f"<h1>{PAGE_LABEL}</h1>"
        f"<p>{PAGE_DESCRIPTION}</p>"
        '<a class="btn btn-gold" href="tel:+18177845998">Call for a Free Estimate</a>'
        "</div></section>"
    )
    source = _replace_once(
        source,
        r'<section class="local-hero">.*?</section>',
        hero,
        "hero section",
    )
    source = _replace_once(
        source,
        r'<input type="hidden" name="page" value="[^"]*">',
        f'<input type="hidden" name="page" value="{PAGE_LABEL}">',
        "estimate form page value",
    )
    if "Kitchen Backsplash Details<textarea" not in source:
        source = _replace_once(
            source,
            r"<label>Project Details<textarea",
            "<label>Kitchen Backsplash Details<textarea",
            "estimate form label",
        )

    source = _replace_gallery_copy(source)
    content = (
        '<section class="local-content"><div class="container"><div class="local-grid">'
        "<article><h2>Backsplash Planning Considerations</h2>"
        "<p>Kitchen backsplash planning can consider tile selection, layout, cabinetry, "
        "countertops, outlets and range-wall details.</p></article>"
        "<article><h2>Tile and Layout Considerations</h2>"
        "<p>Tile size, pattern, grout color, edge treatment and wall conditions can help "
        "shape a backsplash plan for a Mansfield kitchen.</p></article></div>"
        "<h2>Materials to Consider</h2><ul><li>Gray subway tile</li>"
        "<li>Tile-setting materials</li><li>Grout</li><li>Edge trim</li>"
        "<li>Electrical finish plates</li></ul>"
        "<h2>Related Local Services</h2><p>"
        '<a href="mansfield.html">General contracting in Mansfield</a> &middot; '
        '<a href="mansfield-kitchen-remodeling.html">Kitchen Remodeling in Mansfield</a>'
        "</p></div></section>"
    )
    source = _replace_once(
        source,
        r'<section class="local-content">.*?</section>',
        content,
        "neutral service content",
    )
    contact = (
        '<section class="contact-section complete-contact" id="site-contact" '
        'aria-labelledby="site-contact-heading"><div class="container contact-grid"><div>'
        "<p class=\"eyebrow\">Plan Your Kitchen Backsplash</p>"
        '<h2 id="site-contact-heading">Request Your Free Estimate</h2>'
        "<p>Tell us about your kitchen backsplash plans. We can discuss layout, material "
        "selections, wall conditions and next steps.</p></div><div class=\"contact-actions\">"
        '<a class="btn btn-gold" href="tel:+18177845998">Call (817) 784-5998</a>'
        '<a class="btn btn-outline" href="mailto:lunabestcontractors@gmail.com">'
        "Email lunabestcontractors@gmail.com</a></div></div></section>"
    )
    source = _replace_once(
        source,
        r'<section class="contact-section complete-contact" id="site-contact".*?</section>',
        contact,
        "contact call to action",
    )

    forbidden = (
        "Real Project",
        "Project Challenge",
        "Our Solution",
        "Project duration:",
        "<strong>Completed:</strong>",
        "VERIFIED_PROJECT_EVIDENCE",
        "Published evidence:",
        "2018-05-30",
        "20180530-181936.webp",
        '"datePublished"',
        '"dateModified"',
        "data-project-evidence",
        "design concept",
    )
    lingering = [text for text in forbidden if text in source]
    if lingering:
        raise SystemExit(f"Mansfield English page: neutralization left {lingering[0]}")
    if source.count("data-page-owned-gallery-image") != 5:
        raise SystemExit("Mansfield English page: expected five page-owned images")
    ENGLISH.write_text(source, encoding="utf-8")


def patch_project_index() -> None:
    source = PROJECTS.read_text(encoding="utf-8")
    if f'href="{SPANISH_NAME}"' not in source:
        anchor = (
            '<a class="seo-text-link" '
            'href="gray-subway-kitchen-backsplash-mansfield.html">'
            "View project →</a>"
        )
        if anchor not in source:
            raise SystemExit("Mansfield project-index link was not found")
        source = source.replace(anchor, anchor + SPANISH_INDEX_LINK, 1)
        PROJECTS.write_text(source, encoding="utf-8")


def ensure_spanish_page() -> None:
    if not SPANISH.exists():
        raise SystemExit(f"Missing {SPANISH.name}")
    source = SPANISH.read_text(encoding="utf-8")
    required = (
        "<title>",
        "<h1>",
        'rel="canonical"',
        'hreflang="en-US"',
        '"@type":"Article"',
        '"@type":"BreadcrumbList"',
        '"@type":"ImageGallery"',
        "tel:+18177845998",
        "20180530-181936.webp",
    )
    missing = [token for token in required if token not in source]
    if missing:
        raise SystemExit(f"{SPANISH.name}: missing {missing[0]}")


def ensure_sitemap() -> None:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    document = ET.parse(SITEMAP)
    root = document.getroot()
    namespace = root.tag.split("}", 1)[0].lstrip("{") if "}" in root.tag else ""
    prefix = f"{{{namespace}}}" if namespace else ""
    urls = {
        loc.text.strip()
        for loc in root.findall(f"{prefix}url/{prefix}loc")
        if loc.text
    }
    if SPANISH_URL in urls:
        return
    node = ET.SubElement(root, f"{prefix}url")
    ET.SubElement(node, f"{prefix}loc").text = SPANISH_URL
    ET.SubElement(node, f"{prefix}lastmod").text = "2026-09-05"
    ET.SubElement(node, f"{prefix}changefreq").text = "monthly"
    ET.SubElement(node, f"{prefix}priority").text = "0.6"
    document.write(SITEMAP, encoding="utf-8", xml_declaration=True)


def main() -> None:
    ensure_spanish_page()
    patch_english()
    patch_project_index()
    ensure_sitemap()
    print("Preserved the bilingual verified Mansfield kitchen case.")


if __name__ == "__main__":
    main()
