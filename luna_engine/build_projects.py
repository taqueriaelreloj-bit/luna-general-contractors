from __future__ import annotations

import html
import json
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "luna_engine" / "content" / "projects"
DOMAIN = "https://lunageneralcontractors.com"
PHONE = "(817) 784-5998"
TODAY = date.today().isoformat()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_projects() -> list[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    projects: list[dict] = []
    for path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("status", "published") != "published":
            continue
        required = ["slug", "title", "city", "city_slug", "service", "service_slug", "summary", "problem", "solution"]
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise SystemExit(f"{path}: missing required fields: {', '.join(missing)}")
        projects.append(data)
    return projects


def schema(data: dict) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, separators=(",", ":")) + "</script>"


def render_project(project: dict) -> str:
    slug = project["slug"]
    url = f"{DOMAIN}/{slug}.html"
    title = project["title"]
    description = project.get("meta_description", project["summary"])
    city_url = f"{project['city_slug']}.html"
    service_url = f"{project['city_slug']}-{project['service_slug']}.html"
    images = project.get("images", [])
    materials = project.get("materials", [])
    duration = project.get("duration", "Project schedule varied by scope and site conditions")
    completed = project.get("date_completed", TODAY)

    image_schema = [
        {"@type": "ImageObject", "contentUrl": f"{DOMAIN}/{img['src']}", "caption": img.get("alt", title)}
        for img in images
    ]
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "datePublished": completed,
        "dateModified": TODAY,
        "mainEntityOfPage": url,
        "author": {"@type": "Organization", "name": "Luna General Contractors"},
        "publisher": {"@type": "Organization", "name": "Luna General Contractors", "url": f"{DOMAIN}/"},
        "about": [{"@type": "Service", "name": project["service"]}, {"@type": "City", "name": f"{project['city']}, Texas"}],
        "image": [item["contentUrl"] for item in image_schema],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Projects", "item": f"{DOMAIN}/projects.html"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url},
        ],
    }
    gallery_schema = {"@context": "https://schema.org", "@type": "ImageGallery", "name": f"{title} Gallery", "associatedMedia": image_schema}

    gallery = "".join(
        f'<figure><img src="{esc(img["src"])}" alt="{esc(img.get("alt", title))}" loading="lazy" width="1200" height="900"><figcaption>{esc(img.get("caption", ""))}</figcaption></figure>'
        for img in images
    ) or '<p>Project photos will be added after client approval.</p>'
    materials_html = "".join(f"<li>{esc(item)}</li>" for item in materials) or "<li>Materials selected for the actual project scope.</li>"

    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{esc(title)} | Luna General Contractors</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index, follow, max-image-preview:large"><link rel="canonical" href="{url}"><meta property="og:type" content="article"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{url}"><link rel="stylesheet" href="/styles.css">{schema(article_schema)}{schema(breadcrumb)}{schema(gallery_schema)}</head><body><header class="site-header"><div class="container header-inner"><a class="brand" href="index.html">Luna General Contractors</a><nav class="main-nav"><a href="index.html">Home</a><a href="projects.html">Projects</a><a href="service-areas.html">Service Areas</a><a href="articles.html">Resources</a></nav><div class="header-call"><a href="tel:+18177845998">☎ {PHONE}</a></div></div></header><main><section class="local-hero"><div class="container"><nav class="breadcrumbs"><a href="index.html">Home</a> / <a href="projects.html">Projects</a> / {esc(title)}</nav><p class="eyebrow gold">Real Project • {esc(project['city'])}, Texas</p><h1>{esc(title)}</h1><p>{esc(project['summary'])}</p><a class="btn btn-gold" href="tel:+18177845998">Call for a Free Estimate</a></div></section><section class="local-content"><div class="container"><div class="local-grid"><article><h2>Project Challenge</h2><p>{esc(project['problem'])}</p></article><article><h2>Our Solution</h2><p>{esc(project['solution'])}</p></article></div><h2>Materials and Work Included</h2><ul>{materials_html}</ul><p><strong>Project duration:</strong> {esc(duration)}</p><p><strong>Completed:</strong> {esc(completed)}</p><h2>Project Gallery</h2><div class="project-gallery">{gallery}</div><h2>Related Local Services</h2><p><a href="{city_url}">General contracting in {esc(project['city'])}</a> · <a href="{service_url}">{esc(project['service'])} in {esc(project['city'])}</a></p></div></section><section class="local-form" id="estimate-form"><div class="container"><h2>Request a Free Estimate</h2><form action="https://formspree.io/f/xzzvgpoy" method="POST" class="estimate-form"><input type="hidden" name="page" value="Project: {esc(title)}"><label>Full Name<input name="name" required></label><label>Phone Number<input name="phone" required></label><label>Email Address<input type="email" name="email" required></label><label>Project Details<textarea name="message" rows="5" required></textarea></label><button class="btn btn-gold" type="submit">Request Your Estimate</button></form></div></section></main></body></html>'''


def update_sitemap(names: list[str]) -> None:
    path = ROOT / "sitemap.xml"
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", ns)
    tree = ET.parse(path)
    root = tree.getroot()
    existing = {node.text for node in root.findall(f"{{{ns}}}url/{{{ns}}}loc") if node.text}
    for name in ["projects.html", *names]:
        url = f"{DOMAIN}/{name}"
        if url not in existing:
            node = ET.SubElement(root, f"{{{ns}}}url")
            ET.SubElement(node, f"{{{ns}}}loc").text = url
            ET.SubElement(node, f"{{{ns}}}lastmod").text = TODAY
    tree.write(path, encoding="utf-8", xml_declaration=True)


def render_index(projects: list[dict]) -> str:
    cards = "".join(f'<article class="seo-city-card"><p class="eyebrow gold">{esc(p["service"])} • {esc(p["city"])}</p><h2><a href="{esc(p["slug"])}.html">{esc(p["title"])}</a></h2><p>{esc(p["summary"])}</p><a class="seo-text-link" href="{esc(p["slug"])}.html">View project →</a></article>' for p in projects)
    if not cards:
        cards = '<article class="seo-city-card"><h2>Real project case studies are being organized</h2><p>We are preparing approved project photos and details. Visit our service pages or call for examples related to your project.</p><a class="seo-text-link" href="service-areas.html">Explore local services →</a></article>'
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Construction and Remodeling Projects | Luna General Contractors</title><meta name="description" content="Explore real Luna General Contractors roofing, remodeling, restoration and commercial construction projects across Dallas–Fort Worth."><meta name="robots" content="index, follow"><link rel="canonical" href="{DOMAIN}/projects.html"><meta property="og:title" content="Construction and Remodeling Projects | Luna General Contractors"><meta property="og:url" content="{DOMAIN}/projects.html"><link rel="stylesheet" href="/styles.css"></head><body><header class="site-header"><div class="container header-inner"><a class="brand" href="index.html">Luna General Contractors</a><nav class="main-nav"><a href="index.html">Home</a><a href="projects.html">Projects</a><a href="service-areas.html">Service Areas</a><a href="articles.html">Resources</a></nav></div></header><main><section class="local-hero"><div class="container"><p class="eyebrow gold">Dallas–Fort Worth Portfolio</p><h1>Construction and Remodeling Projects</h1><p>Real project case studies organized by city and service.</p></div></section><section class="seo-section"><div class="container"><div class="seo-city-grid">{cards}</div></div></section></main></body></html>'''


def main() -> None:
    projects = load_projects()
    names: list[str] = []
    for project in projects:
        name = f"{project['slug']}.html"
        (ROOT / name).write_text(render_project(project), encoding="utf-8")
        names.append(name)
    (ROOT / "projects.html").write_text(render_index(projects), encoding="utf-8")
    (ROOT / "luna_engine" / "project-manifest.txt").write_text("\n".join(names) + ("\n" if names else ""), encoding="utf-8")
    update_sitemap(names)
    print(f"Generated projects index and {len(names)} published project case studies")


if __name__ == "__main__":
    main()
