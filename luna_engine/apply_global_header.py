from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEADER = '''<header class="site-header" id="page-top">
  <div class="topbar container">
    <a class="brand" href="index.html" aria-label="Luna General Contractors home">
      <span class="brand-moon" aria-hidden="true"></span>
      <span class="brand-copy">
        <strong>LUNA</strong>
        <small>GENERAL CONTRACTORS</small>
        <em>Roofing • Remodeling • Restoration</em>
      </span>
    </a>

    <button class="menu-toggle" aria-label="Open navigation menu" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>

    <nav class="main-nav" aria-label="Main navigation">
      <a href="index.html">Home</a>
      <a href="index.html#services">Services</a>
      <a href="projects.html">Projects</a>
      <a href="reviews.html">Reviews</a>
      <a href="index.html#about">About</a>
      <a href="service-areas.html">Service Areas</a>
      <a href="articles.html">Resources</a>
      <a href="index.html#estimate-form">Contact</a>
    </nav>

    <div class="header-call">
      <small>Call Now for a Free Estimate</small>
      <a href="tel:+18177845998">☎ (817) 784-5998</a>
      <span>English &amp; Spanish</span>
    </div>
  </div>

  <nav class="trade-bar" aria-label="Trade pages">
    <div class="trade-bar-inner">
      <a href="roofing.html">Roofing</a>
      <a href="mitigation.html">Mitigation</a>
      <a href="insurance-claims.html">Insurance Claims</a>
      <a href="kitchens.html">Kitchen</a>
      <a href="bathrooms.html">Bathroom</a>
      <a href="flooring.html">Flooring</a>
      <a href="painting.html">Painting</a>
      <a href="drywall.html">Drywall</a>
      <a href="siding.html">Siding</a>
      <a href="carpentry.html">Carpentry</a>
      <a href="fencing.html">Fencing</a>
      <a href="commercial.html">Commercial</a>
    </div>
  </nav>
</header>'''

HEADER_RE = re.compile(r"<header\b[^>]*>.*?</header>", re.IGNORECASE | re.DOTALL)


def normalize_root_asset_paths(html: str) -> str:
    html = html.replace('href="../../styles.css"', 'href="styles.css"')
    html = html.replace('href="../styles.css"', 'href="styles.css"')
    html = html.replace('src="../../script.js"', 'src="script.js"')
    html = html.replace('src="../script.js"', 'src="script.js"')
    html = html.replace('href="../../', 'href="')
    html = html.replace('href="../', 'href="')
    return html


def apply_header_to_page(page: Path) -> bool:
    if page.name == "index.html":
        return False

    html = normalize_root_asset_paths(page.read_text(encoding="utf-8"))
    original = html

    if HEADER_RE.search(html):
        html = HEADER_RE.sub(HEADER, html, count=1)
    else:
        body_match = re.search(r"<body\b[^>]*>", html, re.IGNORECASE)
        if not body_match:
            return False
        html = html[: body_match.end()] + "\n" + HEADER + html[body_match.end() :]

    if 'href="styles.css"' not in html and "</head>" in html:
        html = html.replace("</head>", '  <link rel="stylesheet" href="styles.css">\n</head>', 1)

    if 'src="script.js"' not in html and "</body>" in html:
        html = html.replace("</body>", '  <script src="script.js" defer></script>\n</body>', 1)

    if html != original:
        page.write_text(html, encoding="utf-8")
        return True
    return False


def apply_headers() -> int:
    changed = 0
    for page in sorted(ROOT.glob("*.html")):
        if apply_header_to_page(page):
            changed += 1
    print(f"Applied the complete Luna header to {changed} HTML pages.")
    return changed


if __name__ == "__main__":
    apply_headers()
