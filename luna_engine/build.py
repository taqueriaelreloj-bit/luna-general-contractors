from __future__ import annotations

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CITY_DIR = ROOT / "content" / "cities"
SERVICE_DIR = ROOT / "content" / "services"
DIST = ROOT / "dist"
DOMAIN = "https://lunageneralcontractors.com"
PHONE = "(817) 784-5998"
PHONE_LINK = "+18177845998"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_block(data: dict) -> str:
    return '<script type="application/ld+json">' + json.dumps(data, separators=(",", ":")) + "</script>"


def render_city(city: dict, services: list[dict]) -> str:
    city_name = city["name"]
    slug = city["slug"]
    url = f"{DOMAIN}/{slug}.html"

    local_business = {
        "@context": "https://schema.org",
        "@type": ["LocalBusiness", "GeneralContractor"],
        "@id": f"{DOMAIN}/#business",
        "name": "Luna General Contractors",
        "url": url,
        "telephone": "+18177845998",
        "email": "lunabestcontractors@gmail.com",
        "priceRange": "$$",
        "areaServed": {"@type": "City", "name": f"{city_name}, Texas"},
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Service Areas", "item": f"{DOMAIN}/service-areas.html"},
            {"@type": "ListItem", "position": 3, "name": city_name, "item": url},
        ],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
            for item in city["faqs"]
        ],
    }

    service_links = "".join(
        f'<a href="{slug}-{escape(service["slug"])}.html">{escape(service["name"])}</a>'
        for service in services
    )
    property_items = "".join(f"<li>{escape(item)}</li>" for item in city["property_types"])
    need_items = "".join(f"<li>{escape(item)}</li>" for item in city["common_needs"])
    nearby_links = "".join(
        f'<a href="{escape(name.lower().replace(" ", "-"))}.html">{escape(name)}</a>'
        for name in city["nearby_cities"]
    )
    faq_html = "".join(
        f'<details><summary>{escape(item["question"])}</summary><p>{escape(item["answer"])}</p></details>'
        for item in city["faqs"]
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(city["title"])}</title>
  <meta name="description" content="{escape(city["meta_description"])}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{escape(city["title"])}">
  <meta property="og:description" content="{escape(city["meta_description"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="Luna General Contractors">
  <link rel="stylesheet" href="../../styles.css">
  {schema_block(local_business)}
  {schema_block(breadcrumb)}
  {schema_block(faq)}
</head>
<body>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="../../index.html"><span class="brand-moon"></span><span class="brand-copy"><strong>LUNA</strong><small>GENERAL CONTRACTORS</small><em>Roofing • Remodeling • Restoration</em></span></a>
    <div class="header-call"><small>Call Now for a Free Estimate</small><a href="tel:{PHONE_LINK}">☎ {PHONE}</a><span>English &amp; Spanish</span></div>
  </div>
</header>
<main>
  <section class="local-hero"><div class="container">
    <p class="eyebrow gold">Serving {escape(city_name)}, Texas</p>
    <h1>General Contractor in {escape(city_name)}, TX</h1>
    <p>{escape(city["hero"])}</p>
    <div class="hero-actions"><a class="btn btn-gold" href="tel:{PHONE_LINK}">☎ Call for a Free Estimate</a><a class="btn btn-outline" href="#estimate-form">Request Online</a></div>
  </div></section>
  <section class="local-content"><div class="container">
    <h2>Construction and Remodeling for {escape(city_name)} Properties</h2>
    <p>{escape(city["local_summary"])}</p>
    <div class="local-grid">
      <article><h2>Property Types We Serve</h2><ul>{property_items}</ul></article>
      <article><h2>Common Project Needs</h2><ul>{need_items}</ul></article>
    </div>
    <h2>Services in {escape(city_name)}</h2><div class="local-services">{service_links}</div>
    <h2>Nearby Service Areas</h2><div class="local-near">{nearby_links}</div>
    <div class="faq"><h2>Frequently Asked Questions</h2>{faq_html}</div>
  </div></section>
  <section class="local-form" id="estimate-form"><div class="container">
    <h2>Request a Free Estimate in {escape(city_name)}</h2>
    <form action="https://formspree.io/f/xzzvgpoy" method="POST" class="estimate-form">
      <input type="hidden" name="page" value="{escape(city_name)} - Luna Engine Preview">
      <label>Full Name<input name="name" required autocomplete="name"></label>
      <label>Phone Number<input name="phone" required autocomplete="tel"></label>
      <label>Email Address<input type="email" name="email" required autocomplete="email"></label>
      <label>Project Address<input name="address" required autocomplete="street-address"></label>
      <label>Project Details<textarea name="message" rows="5" required></textarea></label>
      <button class="btn btn-gold" type="submit">Request Your Estimate</button>
    </form>
  </div></section>
</main>
</body>
</html>'''


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    cities = [load_json(path) for path in sorted(CITY_DIR.glob("*.json"))]
    services = [load_json(path) for path in sorted(SERVICE_DIR.glob("*.json"))]
    if not cities:
        raise SystemExit("No city data files found")
    if not services:
        raise SystemExit("No service data files found")

    for city in cities:
        output = DIST / f'{city["slug"]}.html'
        output.write_text(render_city(city, services), encoding="utf-8")
        print(f"Generated {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
