from __future__ import annotations

from datetime import date
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://lunageneralcontractors.com"
PHONE = "(817) 784-5998"
PHONE_LINK = "+18177845998"
EMAIL = "lunabestcontractors@gmail.com"
TODAY = date.today().isoformat()

CITIES = [
    "Waxahachie", "Red Oak", "Ovilla", "Glenn Heights", "DeSoto", "Lancaster",
    "Cedar Hill", "Duncanville", "Grand Prairie", "Mansfield", "Arlington", "Dallas",
    "Fort Worth", "Irving", "Keller", "Lewisville", "Mesquite", "Garland", "Richardson",
    "Plano", "Carrollton", "Farmers Branch", "Frisco", "McKinney", "Allen", "Rockwall",
    "Rowlett", "Bedford", "Euless", "Hurst", "North Richland Hills", "Grapevine",
    "Colleyville", "Southlake", "Coppell", "Midlothian"
]

SERVICES = {
    "roofing": ("Roofing", "roof repair, roof replacement, storm-damage inspections and emergency protection"),
    "bathroom-remodeling": ("Bathroom Remodeling", "showers, tile, vanities, lighting, flooring and complete bathroom renovations"),
    "kitchen-remodeling": ("Kitchen Remodeling", "cabinets, countertops, backsplashes, flooring, lighting and layout improvements"),
    "flooring": ("Flooring", "luxury vinyl plank, engineered wood, laminate, tile and flooring repairs"),
    "painting": ("Painting", "interior painting, exterior painting, trim, doors and surface preparation"),
    "drywall": ("Drywall", "drywall installation, repairs, tape, texture matching and ceiling work"),
    "siding": ("Siding", "siding repair, replacement, soffit, fascia and exterior trim"),
    "carpentry": ("Carpentry", "trim, doors, framing, cabinets, built-ins and custom wood repairs"),
    "fencing": ("Fencing", "wood fencing, gates, fence repairs, replacement and hauling"),
    "commercial-construction": ("Commercial Construction", "tenant improvements, build-outs, repairs and coordinated commercial trades"),
    "water-damage-restoration": ("Water Damage Restoration", "dry-out coordination, damaged-material removal and reconstruction after water losses"),
    "insurance-claims": ("Insurance Claims", "insurance restoration scopes, documentation, repairs and reconstruction"),
    "general-contractor": ("General Contractor", "remodeling, repairs, additions, exterior work and coordinated construction services"),
}

CITY_GROUPS = {
    "south": ["Midlothian", "Waxahachie", "Red Oak", "Ovilla", "Glenn Heights", "DeSoto", "Lancaster", "Cedar Hill", "Duncanville", "Mansfield"],
    "central": ["Dallas", "Grand Prairie", "Arlington", "Irving", "Mesquite", "Garland", "Richardson", "Farmers Branch", "Carrollton", "Coppell"],
    "north": ["Plano", "Frisco", "McKinney", "Allen", "Lewisville", "Keller", "Grapevine", "Colleyville", "Southlake"],
    "east": ["Rockwall", "Rowlett", "Mesquite", "Garland", "Dallas"],
    "west": ["Fort Worth", "Bedford", "Euless", "Hurst", "North Richland Hills", "Keller", "Grapevine", "Arlington"],
}

CITY_DETAILS = {
    "Midlothian": "fast-growing Ellis County neighborhoods, established homes and expanding commercial corridors",
    "Waxahachie": "historic homes, newer subdivisions and busy commercial properties across Ellis County",
    "Red Oak": "growing residential communities and local businesses along the I-35E corridor",
    "Ovilla": "custom homes, larger residential lots and properties near the Ellis–Dallas county line",
    "Glenn Heights": "newer neighborhoods, established homes and properties near I-35E",
    "DeSoto": "established neighborhoods, larger homes and active commercial corridors",
    "Lancaster": "historic properties, newer developments and commercial spaces near I-20",
    "Cedar Hill": "hillside homes, mature neighborhoods and properties near Joe Pool Lake",
    "Duncanville": "established homes and commercial properties with convenient access to Dallas",
    "Grand Prairie": "diverse neighborhoods, retail centers and properties between Dallas and Fort Worth",
    "Mansfield": "family neighborhoods, newer construction and growing commercial districts",
    "Arlington": "established neighborhoods, entertainment districts and commercial properties",
    "Dallas": "urban homes, established neighborhoods, investment properties and commercial spaces",
    "Fort Worth": "historic districts, suburban communities and expanding commercial areas",
    "Irving": "Las Colinas offices, established neighborhoods and centrally located properties",
    "Keller": "custom homes, family neighborhoods and well-maintained commercial properties",
    "Lewisville": "lake-area communities, established neighborhoods and busy business corridors",
    "Mesquite": "established homes, investment properties and commercial areas east of Dallas",
    "Garland": "diverse housing, mature neighborhoods and active industrial and commercial areas",
    "Richardson": "well-established neighborhoods, technology corridors and commercial properties",
    "Plano": "master-planned neighborhoods, executive homes and major commercial districts",
    "Carrollton": "mature neighborhoods, newer developments and central DFW commercial corridors",
    "Farmers Branch": "established residential areas and business districts near major highways",
    "Frisco": "newer homes, luxury communities and rapidly growing commercial districts",
    "McKinney": "historic downtown properties, newer communities and expanding neighborhoods",
    "Allen": "family neighborhoods, newer homes and commercial development along US-75",
    "Rockwall": "lake-area properties, newer neighborhoods and growing commercial corridors",
    "Rowlett": "lakefront communities, established homes and expanding residential areas",
    "Bedford": "central Mid-Cities neighborhoods and conveniently located commercial properties",
    "Euless": "Mid-Cities homes, airport-area businesses and established communities",
    "Hurst": "mature neighborhoods and commercial properties in the heart of the Mid-Cities",
    "North Richland Hills": "family neighborhoods, established homes and active retail corridors",
    "Grapevine": "historic homes, lake-area properties and hospitality-focused commercial spaces",
    "Colleyville": "custom residences, larger lots and high-end home improvement projects",
    "Southlake": "luxury homes, custom properties and premium commercial spaces",
    "Coppell": "well-maintained neighborhoods, executive homes and centrally located businesses",
}


def slug(value: str) -> str:
    value = value.lower().replace("desoto", "desoto")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def nearby(city: str) -> list[str]:
    for group in CITY_GROUPS.values():
        if city in group:
            result = [c for c in group if c != city]
            return result[:5]
    return [c for c in CITIES if c != city][:5]


def nav() -> str:
    return '''<header class="site-header" id="home"><div class="container header-inner">
<a class="brand" href="index.html" aria-label="Luna General Contractors home"><span class="brand-moon" aria-hidden="true"></span><span class="brand-copy"><strong>LUNA</strong><small>GENERAL CONTRACTORS</small><em>Roofing • Remodeling • Restoration</em></span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="main-nav" aria-label="Open navigation"><span></span><span></span><span></span></button>
<nav class="main-nav" id="main-nav"><a href="index.html">Home</a><a href="index.html#services">Services</a><a href="index.html#projects">Projects</a><a href="index.html#reviews">Reviews</a><a href="index.html#about">About</a><a href="#estimate-form">Contact</a></nav>
<div class="header-call"><small>Call Now for a Free Estimate</small><a href="tel:+18177845998">☎ (817) 784-5998</a><span>English & Spanish</span></div></div></header>
<nav class="trade-bar" aria-label="Services"><a href="roofing.html">Roofing</a><a href="kitchens.html">Kitchen</a><a href="bathrooms.html">Bathroom</a><a href="flooring.html">Flooring</a><a href="painting.html">Painting</a><a href="drywall.html">Drywall</a><a href="siding.html">Siding</a><a href="carpentry.html">Carpentry</a><a href="fencing.html">Fencing</a><a href="commercial.html">Commercial</a></nav>'''


def form(city: str, service: str = "General Contractor") -> str:
    return f'''<section class="local-form" id="estimate-form"><div class="container"><div class="local-grid"><div><p class="eyebrow gold">Free Estimate</p><h2>Tell Us About Your {escape(service)} Project in {escape(city)}</h2><p>Share the project address, service needed and a short description. Our team will contact you to discuss the next step.</p><p><a class="btn btn-gold" href="tel:{PHONE_LINK}">☎ Call {PHONE}</a></p></div>
<form action="https://formspree.io/f/xzzvgpoy" method="POST" class="estimate-form"><input type="hidden" name="page" value="{escape(city)} - {escape(service)}"><label>Full Name<input name="name" required autocomplete="name"></label><label>Phone Number<input name="phone" required autocomplete="tel"></label><label>Email Address<input type="email" name="email" required autocomplete="email"></label><label>Project Address<input name="address" required autocomplete="street-address"></label><label>Service Needed<select name="service" required><option>{escape(service)}</option><option>Roofing</option><option>Bathroom Remodeling</option><option>Kitchen Remodeling</option><option>Water Damage Restoration</option><option>Insurance Claims</option><option>Other</option></select></label><label>Project Details<textarea name="message" rows="5" required></textarea></label><button class="btn btn-gold" type="submit">Request Your Estimate</button></form></div></div></section>'''


def footer() -> str:
    city_links = ''.join(f'<a href="{slug(c)}.html">{escape(c)}</a>' for c in ["Midlothian", "Waxahachie", "Dallas", "Fort Worth", "Arlington", "Mansfield"])
    return f'''<footer class="site-footer"><div class="container footer-grid"><div class="footer-brand"><a class="brand" href="index.html"><span class="brand-moon"></span><span class="brand-copy"><strong>LUNA</strong><small>GENERAL CONTRACTORS</small><em>Roofing • Remodeling • Restoration</em></span></a><p>Quality construction and restoration across Dallas–Fort Worth.</p><small>© <span id="year"></span> Luna General Contractors.</small></div><div><h3>Services</h3><a href="roofing.html">Roofing</a><a href="kitchens.html">Kitchens</a><a href="bathrooms.html">Bathrooms</a><a href="mitigation.html">Water Damage</a><a href="commercial.html">Commercial</a></div><div><h3>Service Areas</h3>{city_links}</div><div><h3>Contact</h3><a href="tel:{PHONE_LINK}">☎ {PHONE}</a><a href="mailto:{EMAIL}">✉ {EMAIL}</a><span>English & Spanish</span></div></div></footer><a class="floating-call" href="tel:{PHONE_LINK}" aria-label="Call Luna General Contractors">☎</a><script src="script.js"></script>'''


def schemas(city: str, title: str, url: str, description: str, service_name: str | None = None) -> str:
    local = {
        "@context": "https://schema.org", "@type": ["LocalBusiness", "GeneralContractor"],
        "name": "Luna General Contractors", "url": url, "telephone": "+1-817-784-5998",
        "email": EMAIL, "priceRange": "$$", "areaServed": {"@type": "City", "name": f"{city}, Texas"},
        "description": description
    }
    breadcrumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":DOMAIN+"/"},
        {"@type":"ListItem","position":2,"name":city,"item":DOMAIN+f"/{slug(city)}.html"}
    ]}
    blocks = [local, breadcrumb]
    if service_name:
        blocks.append({"@context":"https://schema.org","@type":"Service","name":f"{service_name} in {city}, TX","serviceType":service_name,"provider":{"@type":"GeneralContractor","name":"Luna General Contractors","telephone":"+1-817-784-5998"},"areaServed":{"@type":"City","name":city},"url":url,"description":description})
    return ''.join('<script type="application/ld+json">'+json.dumps(x, separators=(",", ":"))+'</script>' for x in blocks)


def faq_schema(items: list[tuple[str,str]]) -> str:
    data = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in items]}
    return '<script type="application/ld+json">'+json.dumps(data, separators=(",", ":"))+'</script>'


def head(title: str, description: str, url: str, city: str, schema_html: str) -> str:
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{escape(title)}</title><meta name="description" content="{escape(description)}"><meta name="robots" content="index, follow"><link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Luna General Contractors"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="styles.css">{schema_html}<style>
.local-hero{{min-height:520px;display:grid;align-items:center;background:radial-gradient(circle at 80% 25%,rgba(229,160,0,.18),transparent 32%),linear-gradient(120deg,#05080a 15%,#111820 70%,#05080a);color:#fff}}.local-hero .container{{padding-top:80px;padding-bottom:80px}}.local-hero h1{{font-size:clamp(2.8rem,7vw,6.5rem);line-height:.94;max-width:1050px;margin:.2em 0}}.local-hero p{{font-size:1.18rem;max-width:800px}}.breadcrumbs{{font-size:.9rem;margin-bottom:20px}}.breadcrumbs a{{color:#e5a000}}.local-content,.local-form{{padding:72px 0;background:#fff;color:#17191c}}.local-content h2,.local-form h2{{font-size:clamp(2rem,4vw,3.4rem)}}.local-grid{{display:grid;grid-template-columns:1.15fr .85fr;gap:42px}}.local-card{{background:#f3f4f5;border-left:5px solid #e5a000;padding:30px}}.local-services{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin:28px 0}}.local-services a{{display:block;padding:18px;background:#111820;color:#fff;text-decoration:none;font-weight:800;border-bottom:3px solid #e5a000}}.local-near a{{display:inline-block;margin:5px 10px 5px 0;color:#9a6200;font-weight:800}}.faq details{{border-bottom:1px solid #ddd;padding:16px 0}}.faq summary{{font-weight:800;cursor:pointer}}.estimate-form{{display:grid;gap:13px;background:#f3f4f5;padding:25px}}.estimate-form label{{font-weight:700;display:grid;gap:6px}}.estimate-form input,.estimate-form select,.estimate-form textarea{{width:100%;padding:13px;border:1px solid #bbb;background:#fff}}@media(max-width:800px){{.local-grid{{grid-template-columns:1fr}}.local-services{{grid-template-columns:1fr 1fr}}}}@media(max-width:520px){{.local-services{{grid-template-columns:1fr}}}}
</style></head><body>'''


def city_page(city: str) -> str:
    cslug = slug(city)
    url = f"{DOMAIN}/{cslug}.html"
    detail = CITY_DETAILS.get(city, "residential neighborhoods, investment properties and commercial buildings across the Dallas–Fort Worth area")
    title = f"General Contractor in {city}, TX | Luna General Contractors"
    description = f"Trusted general contractor serving {city}, TX with roofing, remodeling, restoration and commercial construction. Call {PHONE} for a free estimate."
    faqs = [
        (f"Does Luna General Contractors serve {city}, Texas?", f"Yes. We provide roofing, remodeling, restoration and general construction services throughout {city} and nearby DFW communities."),
        (f"What types of projects do you complete in {city}?", "Our team handles roofing, bathrooms, kitchens, flooring, painting, drywall, siding, carpentry, fencing, commercial work and insurance restoration."),
        ("How do I request an estimate?", f"Call {PHONE} or submit the project form on this page with your address and a description of the work."),
    ]
    schema_html = schemas(city,title,url,description,"General Contractor") + faq_schema(faqs)
    service_links = ''.join(f'<a href="{cslug}-{s}.html">{escape(name)}</a>' for s,(name,_) in SERVICES.items())
    near_links = ''.join(f'<a href="{slug(n)}.html">{escape(n)}</a>' for n in nearby(city))
    faq_html = ''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q,a in faqs)
    return head(title,description,url,city,schema_html)+nav()+f'''<main><section class="local-hero"><div class="container"><div class="breadcrumbs"><a href="index.html">Home</a> / Service Areas / {escape(city)}</div><p class="eyebrow gold">Serving {escape(city)}, Texas</p><h1>{escape(city)} General Contractor</h1><p>Roofing, remodeling, restoration and coordinated construction for homeowners, property managers and businesses in {escape(city)}.</p><div class="hero-actions"><a class="btn btn-gold" href="tel:{PHONE_LINK}">☎ Call for a Free Estimate</a><a class="btn btn-outline" href="#estimate-form">Request Online</a></div></div></section><section class="local-content"><div class="container"><div class="local-grid"><div><p class="eyebrow gold">Local Construction Services</p><h2>Practical Project Management for {escape(city)} Properties</h2><p>{escape(city)} includes {escape(detail)}. Those properties need different solutions, from targeted repairs to complete renovations.</p><p>Luna General Contractors coordinates the work, communicates the scope clearly and keeps the project focused on durable results. We can help with interior upgrades, exterior protection, storm repairs and reconstruction after covered property losses.</p><p>Because every property is different, we inspect the work area, discuss priorities and prepare an estimate based on the actual project conditions.</p></div><aside class="local-card"><h3>Why property owners call Luna</h3><p>One point of contact, coordinated trades, realistic recommendations and workmanship focused on long-term use.</p><p><strong>Serving:</strong> {escape(city)} and nearby DFW communities.</p><a class="btn btn-gold" href="tel:{PHONE_LINK}">{PHONE}</a></aside></div><h2>Services Available in {escape(city)}</h2><div class="local-services">{service_links}</div><div class="local-near"><h2>Nearby Service Areas</h2>{near_links}</div><div class="faq"><h2>Frequently Asked Questions</h2>{faq_html}</div></div></section>{form(city)}</main>'''+footer()+"</body></html>"


def service_page(city: str, service_slug: str, service_name: str, scope: str) -> str:
    cslug = slug(city)
    filename = f"{cslug}-{service_slug}.html"
    url = f"{DOMAIN}/{filename}"
    title = f"{service_name} in {city}, TX | Free Estimate"
    description = f"Professional {service_name.lower()} in {city}, TX for {scope}. Call Luna General Contractors at {PHONE}."
    detail = CITY_DETAILS.get(city, "residential and commercial properties throughout the DFW area")
    faqs = [
        (f"Do you provide {service_name.lower()} in {city}?", f"Yes. Luna General Contractors provides {service_name.lower()} for residential and commercial properties in {city} and nearby communities."),
        (f"What is included in a {service_name.lower()} estimate?", "The estimate is based on the visible scope, access, measurements, selected finishes and any related repairs needed to complete the work properly."),
        ("How quickly can I schedule an inspection?", f"Call {PHONE} or submit the form. Scheduling depends on current project volume and the urgency of the work."),
    ]
    schema_html = schemas(city,title,url,description,service_name)+faq_schema(faqs)
    other_services = ''.join(f'<a href="{cslug}-{s}.html">{escape(n)}</a>' for s,(n,_) in SERVICES.items() if s != service_slug)[:4000]
    near_links = ''.join(f'<a href="{slug(n)}-{service_slug}.html">{escape(service_name)} in {escape(n)}</a>' for n in nearby(city))
    faq_html = ''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q,a in faqs)
    image = '<img src="roofing-project-one.jpg" loading="lazy" width="1200" height="800" alt="Roofing project completed by Luna General Contractors">' if service_slug == "roofing" else ''
    return head(title,description,url,city,schema_html)+nav()+f'''<main><section class="local-hero"><div class="container"><div class="breadcrumbs"><a href="index.html">Home</a> / <a href="{cslug}.html">{escape(city)}</a> / {escape(service_name)}</div><p class="eyebrow gold">{escape(city)}, Texas</p><h1>{escape(service_name)} in {escape(city)}</h1><p>Local help with {escape(scope)} for properties throughout {escape(city)}.</p><div class="hero-actions"><a class="btn btn-gold" href="tel:{PHONE_LINK}">☎ Call for a Free Estimate</a><a class="btn btn-outline" href="#estimate-form">Request Online</a></div></div></section><section class="local-content"><div class="container"><div class="local-grid"><div><p class="eyebrow gold">Professional {escape(service_name)}</p><h2>A Clear Plan for Your {escape(city)} Property</h2><p>Properties in {escape(city)} include {escape(detail)}. Our approach begins with the actual conditions at the property rather than a one-size-fits-all scope.</p><p>For {escape(service_name.lower())}, we review access, measurements, affected materials, desired finishes and any related work needed for a complete result. You receive practical recommendations and a defined project scope before work begins.</p><p>Luna General Contractors coordinates the necessary trades and keeps communication centered on schedule, quality and the agreed scope.</p>{image}</div><aside class="local-card"><h3>Service overview</h3><p><strong>{escape(service_name)}:</strong> {escape(scope)}.</p><p><strong>Area:</strong> {escape(city)}, Texas and nearby DFW communities.</p><a class="btn btn-gold" href="tel:{PHONE_LINK}">{PHONE}</a></aside></div><h2>Related Services in {escape(city)}</h2><div class="local-services">{other_services}</div><div class="local-near"><h2>{escape(service_name)} Near {escape(city)}</h2>{near_links}</div><div class="faq"><h2>Frequently Asked Questions</h2>{faq_html}</div></div></section>{form(city,service_name)}</main>'''+footer()+"</body></html>"


def article_page(filename: str, title: str, city: str, intro: str, sections: list[tuple[str,str]]) -> str:
    url=f"{DOMAIN}/{filename}"
    description=intro[:155]
    schema={"@context":"https://schema.org","@type":"Article","headline":title,"description":description,"datePublished":TODAY,"dateModified":TODAY,"author":{"@type":"Organization","name":"Luna General Contractors"},"publisher":{"@type":"Organization","name":"Luna General Contractors"},"mainEntityOfPage":url}
    section_html=''.join(f'<h2>{escape(h)}</h2><p>{escape(p)}</p>' for h,p in sections)
    return head(title,description,url,city,'<script type="application/ld+json">'+json.dumps(schema,separators=(",",":"))+'</script>')+nav()+f'''<main><section class="local-hero"><div class="container"><div class="breadcrumbs"><a href="index.html">Home</a> / Resources / {escape(title)}</div><p class="eyebrow gold">DFW Construction Guide</p><h1>{escape(title)}</h1><p>{escape(intro)}</p></div></section><article class="local-content"><div class="container" style="max-width:900px"><p>{escape(intro)}</p>{section_html}<p><strong>Planning a project?</strong> Call <a href="tel:{PHONE_LINK}">{PHONE}</a> for a free estimate.</p></div></article>{form(city)}</main>'''+footer()+"</body></html>"


def write(path: str, content: str) -> None:
    (ROOT/path).write_text(content, encoding="utf-8")


def main() -> None:
    generated=[]
    for city in CITIES:
        city_file=f"{slug(city)}.html"
        write(city_file,city_page(city)); generated.append(city_file)
        for s,(name,scope) in SERVICES.items():
            f=f"{slug(city)}-{s}.html"
            write(f,service_page(city,s,name,scope)); generated.append(f)
    articles=[
        ("roof-replacement-cost-dallas.html","Roof Replacement Cost in Dallas","Dallas","Roof replacement prices in Dallas depend on roof size, pitch, materials, access, decking condition and storm-related damage.",[("Main cost factors","Square count, roof complexity, shingle selection, ventilation, flashing and damaged decking have the largest effect on price."),("Insurance versus retail work","Storm-related projects may involve an insurance scope, while age-related replacement is usually a direct retail project."),("Getting an accurate estimate","A site inspection and measurements are necessary before a reliable price can be prepared.")]),
        ("bathroom-remodeling-cost-waxahachie.html","Bathroom Remodeling Cost in Waxahachie","Waxahachie","Bathroom remodeling cost in Waxahachie changes with shower design, tile, plumbing moves, cabinetry, glass and finish selections.",[("Budget drivers","Custom showers, plumbing relocation, large-format tile, cabinetry and glass are common cost drivers."),("Plan the scope first","Define what stays, what moves and which finishes are selected before comparing estimates."),("Allow for hidden conditions","Older bathrooms can reveal water damage, framing issues or outdated plumbing after demolition.")]),
        ("water-damage-insurance-claims-arlington.html","Water Damage Insurance Claims in Arlington","Arlington","Water losses in Arlington require quick documentation, damage control and a clear reconstruction scope.",[("Document the loss","Photos, moisture readings and a record of damaged materials help establish the condition after the event."),("Mitigation and reconstruction","Dry-out work stops further damage; reconstruction replaces the materials removed or damaged."),("Review the scope carefully","Confirm that finishes, labor steps and affected areas are included before reconstruction begins.")]),
        ("best-general-contractor-midlothian.html","How to Choose a General Contractor in Midlothian","Midlothian","The best contractor for a Midlothian project is the one who defines the scope, communicates clearly and coordinates the work responsibly.",[("Compare complete scopes","A low number can omit preparation, related repairs, cleanup or finish work."),("Ask about communication","Know who manages the project, how changes are approved and how progress is reported."),("Review relevant work","Look for experience with the same type of property and project rather than unrelated work.")]),
        ("kitchen-remodeling-ideas-texas.html","Kitchen Remodeling Ideas for Texas Homes","Dallas","Texas kitchens benefit from durable finishes, practical storage, efficient lighting and layouts designed for everyday use.",[("Improve task lighting","Use layered ceiling, under-cabinet and decorative lighting for a more useful workspace."),("Choose durable surfaces","Quartz, quality tile and water-resistant flooring perform well in active households."),("Plan storage around routines","Deep drawers, pantry pullouts and organized cabinet zones reduce clutter and improve workflow.")]),
    ]
    for args in articles:
        write(args[0],article_page(*args)); generated.append(args[0])
    static=["","roofing.html","mitigation.html","insurance-claims.html","kitchens.html","bathrooms.html","flooring.html","painting.html","drywall.html","siding.html","carpentry.html","fencing.html","commercial.html"]
    urls=[DOMAIN+("/" if not x else "/"+x) for x in static+generated]
    sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>\n' for u in urls)+'</urlset>\n'
    write("sitemap.xml",sitemap)
    write("robots.txt",f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    print(f"Generated {len(generated)} SEO pages and sitemap with {len(urls)} URLs")

if __name__ == "__main__":
    main()
