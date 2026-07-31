from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CITY_DIR = ROOT / "content" / "cities"
SERVICE_DIR = ROOT / "content" / "services"
DIST = ROOT / "dist"
DOMAIN = "https://lunageneralcontractors.com"
PHONE = "(817) 784-5998"
PHONE_LINK = "+18177845998"
EMAIL = "lunabestcontractors@gmail.com"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_block(data: dict) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, separators=(",", ":")) + "</script>"


def city_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def page_head(title: str, description: str, url: str, schemas: list[dict]) -> str:
    schema_html = "\n".join(schema_block(item) for item in schemas)
    return f'''<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Luna General Contractors">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="../../styles.css">
  {schema_html}
</head>'''


def header() -> str:
    return f'''<header class="site-header"><div class="container header-inner">
<a class="brand" href="../../index.html" aria-label="Luna General Contractors home"><span class="brand-moon"></span><span class="brand-copy"><strong>LUNA</strong><small>GENERAL CONTRACTORS</small><em>Roofing • Remodeling • Restoration</em></span></a>
<nav class="main-nav"><a href="../../index.html">Home</a><a href="../../service-areas.html">Service Areas</a><a href="../../articles.html">Resources</a><a href="#estimate-form">Contact</a></nav>
<div class="header-call"><small>Call Now for a Free Estimate</small><a href="tel:{PHONE_LINK}">☎ {PHONE}</a><span>English &amp; Spanish</span></div>
</div></header>'''


def estimate_form(city: str, service: str) -> str:
    return f'''<section class="local-form" id="estimate-form"><div class="container"><h2>Request a Free {escape(service)} Estimate in {escape(city)}</h2>
<form action="https://formspree.io/f/xzzvgpoy" method="POST" class="estimate-form">
<input type="hidden" name="page" value="{escape(city)} - {escape(service)}">
<label>Full Name<input name="name" required autocomplete="name"></label>
<label>Phone Number<input name="phone" required autocomplete="tel"></label>
<label>Email Address<input type="email" name="email" required autocomplete="email"></label>
<label>Project Address<input name="address" required autocomplete="street-address"></label>
<label>Project Details<textarea name="message" rows="5" required></textarea></label>
<button class="btn btn-gold" type="submit">Request Your Estimate</button>
</form></div></section>'''


def base_business(url: str, city: str) -> dict:
    return {"@context":"https://schema.org","@type":["LocalBusiness","GeneralContractor"],"@id":f"{DOMAIN}/#business","name":"Luna General Contractors","url":url,"telephone":"+18177845998","email":EMAIL,"priceRange":"$$","areaServed":{"@type":"City","name":f"{city}, Texas"}}


def organization_schema() -> dict:
    return {"@context":"https://schema.org","@type":"Organization","@id":f"{DOMAIN}/#organization","name":"Luna General Contractors","url":f"{DOMAIN}/","telephone":"+18177845998","email":EMAIL}


def webpage_schema(url: str, title: str, description: str) -> dict:
    return {"@context":"https://schema.org","@type":"WebPage","@id":f"{url}#webpage","url":url,"name":title,"description":description,"isPartOf":{"@id":f"{DOMAIN}/#website"},"about":{"@id":f"{DOMAIN}/#business"}}


def render_city(city: dict, services: list[dict]) -> str:
    name, slug = city["name"], city["slug"]
    url = f"{DOMAIN}/{slug}.html"
    title = city["title"]
    description = city["meta_description"]
    city_service = {"@context":"https://schema.org","@type":"Service","name":f"General Contractor Services in {name}, TX","serviceType":"General Contractor","url":url,"description":description,"provider":{"@id":f"{DOMAIN}/#business"},"areaServed":{"@type":"City","name":f"{name}, Texas"}}
    breadcrumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":f"{DOMAIN}/"},{"@type":"ListItem","position":2,"name":"Service Areas","item":f"{DOMAIN}/service-areas.html"},{"@type":"ListItem","position":3,"name":name,"item":url}]}
    faq = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":item["question"],"acceptedAnswer":{"@type":"Answer","text":item["answer"]}} for item in city["faqs"]]}
    service_links = "".join(f'<a href="{slug}-{escape(s["slug"])}.html">{escape(s["name"])}</a>' for s in services)
    property_items = "".join(f"<li>{escape(item)}</li>" for item in city["property_types"])
    need_items = "".join(f"<li>{escape(item)}</li>" for item in city["common_needs"])
    nearby = "".join(f'<a href="{city_slug(n)}.html">{escape(n)}</a>' for n in city["nearby_cities"])
    faq_html = "".join(f'<details><summary>{escape(x["question"])}</summary><p>{escape(x["answer"])}</p></details>' for x in city["faqs"])
    schemas = [organization_schema(),base_business(url,name),city_service,webpage_schema(url,title,description),breadcrumb,faq]
    return f'''<!DOCTYPE html><html lang="en">{page_head(title,description,url,schemas)}<body>{header()}<main>
<section class="local-hero"><div class="container"><p class="eyebrow gold">Serving {escape(name)}, Texas</p><h1>General Contractor in {escape(name)}, TX</h1><p>{escape(city["hero"])}</p><div class="hero-actions"><a class="btn btn-gold" href="tel:{PHONE_LINK}">☎ Call for a Free Estimate</a><a class="btn btn-outline" href="#estimate-form">Request Online</a></div></div></section>
<section class="local-content"><div class="container"><h2>Construction and Remodeling for {escape(name)} Properties</h2><p>{escape(city["local_summary"])}</p><div class="local-grid"><article><h2>Property Types We Serve</h2><ul>{property_items}</ul></article><article><h2>Common Project Needs</h2><ul>{need_items}</ul></article></div><h2>Services in {escape(name)}</h2><div class="local-services">{service_links}</div><h2>Nearby Service Areas</h2><div class="local-near">{nearby}</div><div class="faq"><h2>Frequently Asked Questions</h2>{faq_html}</div></div></section>{estimate_form(name,"General Contractor")}</main></body></html>'''


def render_city_service(city: dict, service: dict, all_services: list[dict]) -> str:
    name, cslug = city["name"], city["slug"]
    sname, sslug = service["name"], service["slug"]
    filename = f"{cslug}-{sslug}.html"
    url = f"{DOMAIN}/{filename}"
    title = f"{sname} in {name}, TX | Luna General Contractors"
    description = f"Professional {sname.lower()} in {name}, TX. {service['summary']} Call {PHONE} for a free estimate."
    service_schema = {"@context":"https://schema.org","@type":"Service","name":f"{sname} in {name}, TX","serviceType":sname,"url":url,"description":description,"provider":{"@id":f"{DOMAIN}/#business"},"areaServed":{"@type":"City","name":f"{name}, Texas"}}
    breadcrumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":f"{DOMAIN}/"},{"@type":"ListItem","position":2,"name":"Service Areas","item":f"{DOMAIN}/service-areas.html"},{"@type":"ListItem","position":3,"name":name,"item":f"{DOMAIN}/{cslug}.html"},{"@type":"ListItem","position":4,"name":sname,"item":url}]}
    faq_items = service.get("faqs", []) + [{"question":f"Do you provide {sname.lower()} in {name}?","answer":f"Yes. Luna General Contractors serves homes and businesses throughout {name} and nearby communities."}]
    faq_schema = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":x["question"],"acceptedAnswer":{"@type":"Answer","text":x["answer"]}} for x in faq_items]}
    features = "".join(f"<li>{escape(x)}</li>" for x in service.get("features", []))
    related = "".join(f'<a href="{cslug}-{escape(s["slug"])}.html">{escape(s["name"])}</a>' for s in all_services if s["slug"] != sslug)
    nearby = "".join(f'<a href="{city_slug(n)}-{sslug}.html">{escape(n)}</a>' for n in city["nearby_cities"][:5])
    faq_html = "".join(f'<details><summary>{escape(x["question"])}</summary><p>{escape(x["answer"])}</p></details>' for x in faq_items)
    schemas = [organization_schema(),base_business(url,name),service_schema,webpage_schema(url,title,description),breadcrumb,faq_schema]
    return f'''<!DOCTYPE html><html lang="en">{page_head(title,description,url,schemas)}<body>{header()}<main>
<section class="local-hero"><div class="container"><nav class="breadcrumbs"><a href="../../index.html">Home</a> / <a href="{cslug}.html">{escape(name)}</a> / {escape(sname)}</nav><p class="eyebrow gold">{escape(name)}, Texas</p><h1>{escape(sname)} in {escape(name)}, TX</h1><p>{escape(service["summary"])}</p><div class="hero-actions"><a class="btn btn-gold" href="tel:{PHONE_LINK}">☎ Call {PHONE}</a><a class="btn btn-outline" href="#estimate-form">Request an Estimate</a></div></div></section>
<section class="local-content"><div class="container"><h2>Local {escape(sname)} Services</h2><p>{escape(city["local_summary"])}</p><p>We evaluate the property, discuss priorities, document the scope and coordinate the work so the project is based on actual site conditions rather than a generic online estimate.</p><div class="local-grid"><article><h2>What the Service May Include</h2><ul>{features}</ul></article><article><h2>Planning the Project</h2><p>Scheduling, access, protection, materials, trade coordination, cleanup and any hidden conditions are reviewed before work begins.</p></article></div><h2>Other Services in {escape(name)}</h2><div class="local-services">{related}</div><h2>{escape(sname)} Near {escape(name)}</h2><div class="local-near">{nearby}</div><div class="faq"><h2>{escape(sname)} FAQ</h2>{faq_html}</div></div></section>{estimate_form(name,sname)}</main></body></html>'''


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    for stale in DIST.glob("*.html"):
        stale.unlink()
    manifest = DIST / "manifest.json"
    if manifest.exists():
        manifest.unlink()

    cities = [load_json(p) for p in sorted(CITY_DIR.glob("*.json"))]
    services = [load_json(p) for p in sorted(SERVICE_DIR.glob("*.json"))]
    if not cities or not services:
        raise SystemExit("City and service data are required")

    generated: list[str] = []
    for city in cities:
        city_path = DIST / f'{city["slug"]}.html'
        city_path.write_text(render_city(city, services), encoding="utf-8")
        generated.append(city_path.name)
        for service in services:
            path = DIST / f'{city["slug"]}-{service["slug"]}.html'
            path.write_text(render_city_service(city, service, services), encoding="utf-8")
            generated.append(path.name)

    (DIST / "manifest.json").write_text(json.dumps({"cities":len(cities),"services":len(services),"pages":generated}, indent=2), encoding="utf-8")
    print(f"Generated {len(generated)} pages from {len(cities)} cities and {len(services)} services")


if __name__ == "__main__":
    main()
