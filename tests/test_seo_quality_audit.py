from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.seo_quality_audit import Auditor
from scripts.update_sitemap_lastmod import update_sitemap


GOOD_PAGE = """<!doctype html>
<html lang="en"><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Luna General Contractors provides detailed construction planning and dependable project coordination throughout Dallas Fort Worth.">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:title" content="Luna General Contractors">
<meta property="og:description" content="Construction services across Dallas Fort Worth.">
<meta property="og:url" content="https://lunageneralcontractors.com/">
<meta property="og:image" content="https://lunageneralcontractors.com/project.webp">
<meta name="twitter:card" content="summary_large_image">
<title>Luna General Contractors in Dallas Fort Worth</title>
<link rel="canonical" href="https://lunageneralcontractors.com/">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite"}</script>
</head><body><main><h1>Dallas Fort Worth General Contractor</h1>
<h2>Construction Services</h2><p>{copy}</p>
<a href="#contact">Request an estimate</a><a href="tel:+18177845998">Call</a>
<a href="mailto:test@example.com">Email</a><div id="contact">Contact</div></main></body></html>"""


class SEOAuditTests(unittest.TestCase):
    def make_site(self, page: str) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        copy = " ".join(["Field-based planning protects quality, schedule, and completed finishes."] * 35)
        (root / "index.html").write_text(page.replace("{copy}", copy), encoding="utf-8")
        (root / "sitemap.xml").write_text(
            '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            '<url><loc>https://lunageneralcontractors.com/</loc><lastmod>2026-08-01</lastmod></url>'
            "</urlset>",
            encoding="utf-8",
        )
        return root

    def test_good_page_has_no_critical_findings(self):
        auditor = Auditor(self.make_site(GOOD_PAGE))
        auditor.run()
        critical = [item for item in auditor.findings if item.severity == "critical"]
        self.assertEqual([], critical)

    def test_bad_heading_and_copy_are_critical(self):
        bad = GOOD_PAGE.replace("<h1>Dallas Fort Worth General Contractor</h1>", "")
        bad = bad.replace("Construction Services", "Construction Services in Serving Dallas")
        auditor = Auditor(self.make_site(bad))
        auditor.run()
        messages = [item.message for item in auditor.findings if item.severity == "critical"]
        self.assertTrue(any("exactly one H1" in message for message in messages))
        self.assertTrue(any("awkward city phrase" in message for message in messages))

    def test_sitemap_updates_only_changed_page(self):
        root = self.make_site(GOOD_PAGE)
        count = update_sitemap(root / "sitemap.xml", {"index.html"}, "2026-08-21")
        text = (root / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(1, count)
        self.assertIn("<lastmod>2026-08-21</lastmod>", text)


if __name__ == "__main__":
    unittest.main()
