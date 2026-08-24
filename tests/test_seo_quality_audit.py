from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.enrich_all_local_pages import build_blog
from scripts.enrich_local_faqs import build_faqs, render_schema
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

    def test_indexable_root_page_outside_sitemap_is_reported(self):
        root = self.make_site(GOOD_PAGE)
        extra = GOOD_PAGE.replace(
            "https://lunageneralcontractors.com/",
            "https://lunageneralcontractors.com/extra.html",
        )
        extra = extra.replace(
            "Luna General Contractors in Dallas Fort Worth",
            "Roof Repair Planning in Arlington Texas",
        )
        extra = extra.replace(
            "Dallas Fort Worth General Contractor",
            "Arlington Roof Repair Planning",
        )
        (root / "extra.html").write_text(extra, encoding="utf-8")

        auditor = Auditor(root)
        auditor.run()
        messages = [
            item.message
            for item in auditor.findings
            if item.page == "extra.html" and item.severity == "warning"
        ]
        self.assertIn("Indexable root HTML is not listed in the sitemap", messages)

    def test_city_copy_is_grammatical_for_vowel_city_names(self):
        block = build_blog("allen-carpentry.html", "Allen", "Carpentry")
        self.assertNotIn("a Allen", block)
        self.assertIn("in Allen", block)

    def test_city_hub_and_general_contractor_faq_schemas_are_distinct(self):
        service_schema = render_schema(
            build_faqs(
                "arlington-general-contractor.html",
                "Arlington",
                "General Contracting",
            )
        )
        hub_schema = render_schema(
            build_faqs("arlington.html", "Arlington", "Construction & Remodeling")
        )
        self.assertNotEqual(service_schema, hub_schema)


    def test_directory_hubs_link_to_home_estimate_form(self):
        root = Path(__file__).resolve().parents[1]
        for page_name in ("articles.html", "service-areas.html", "services-by-city.html"):
            with self.subTest(page=page_name):
                page = (root / page_name).read_text(encoding="utf-8")
                self.assertNotIn('href="#estimate-form"', page)
                self.assertIn('href="index.html#estimate-form"', page)

if __name__ == "__main__":
    unittest.main()
