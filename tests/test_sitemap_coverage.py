from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.reconcile_sitemap import DOMAIN, NS, Metadata, page_url, reconcile
from tools.generate_seo_pages import sitemap_paths

ROOT = Path(__file__).resolve().parents[1]


class SitemapCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "seo").mkdir()
        (self.root / "seo/sitemap-exclusions.csv").write_text(
            "path,classification,next_action,rationale\n"
            "home-v2-preview.html,exclude-preview,keep-noindex,Duplicate preview\n"
        )
        for name in ["index.html", "service.html", "privacy.html", "gallery.html", "home-v2-preview.html"]:
            canonical = page_url("index.html" if name == "home-v2-preview.html" else name)
            robots = "noindex, nofollow" if name != "index.html" else "index, follow"
            (self.root / name).write_text(
                f'<html><head><link rel="canonical" href="{canonical}">'
                f'<meta name="robots" content="{robots}"></head>'
                '<body>Preserve content and <img src="photo.jpg"></body></html>'
            )
        (self.root / "sitemap.xml").write_text(
            f'<urlset xmlns="{NS}"><url><loc>{DOMAIN}/</loc>'
            '<lastmod>2026-09-01</lastmod></url></urlset>'
        )

    def test_promotes_all_public_pages_and_preserves_preview(self):
        preview = (self.root / "home-v2-preview.html").read_bytes()
        self.assertEqual(reconcile(self.root, apply=True), (4, 1))
        self.assertEqual(reconcile(self.root), (4, 1))
        self.assertEqual(preview, (self.root / "home-v2-preview.html").read_bytes())
        for name in ["service.html", "privacy.html", "gallery.html"]:
            source = (self.root / name).read_text()
            self.assertNotIn("noindex", Metadata(source).robots[0])
            self.assertIn('<body>Preserve content and <img src="photo.jpg"></body>', source)

    def test_preserves_old_dates_without_inventing_new_dates(self):
        reconcile(self.root, apply=True)
        tree = ET.parse(self.root / "sitemap.xml")
        self.assertEqual([node.text for node in tree.findall(f".//{{{NS}}}lastmod")], ["2026-09-01"])

    def test_second_apply_is_byte_identical(self):
        reconcile(self.root, apply=True)
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        reconcile(self.root, apply=True)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_check_never_writes(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(ValueError, "Coverage mismatch"):
            reconcile(self.root)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_removes_accidentally_included_preview(self):
        p = self.root / "sitemap.xml"
        p.write_text(p.read_text().replace("</urlset>", f"<url><loc>{page_url('home-v2-preview.html')}</loc></url></urlset>"))
        reconcile(self.root, apply=True)
        self.assertNotIn("home-v2-preview.html", p.read_text())
        self.assertEqual(reconcile(self.root), (4, 1))

    def test_rejects_canonical_conflict_before_writing(self):
        p = self.root / "service.html"
        p.write_text(p.read_text().replace(page_url("service.html"), page_url("index.html")))
        with self.assertRaisesRegex(ValueError, "self-referencing canonical"):
            reconcile(self.root, apply=True)
        self.assertIn("noindex", (self.root / "gallery.html").read_text())

    def test_rejects_duplicate_sitemap_urls(self):
        p = self.root / "sitemap.xml"
        p.write_text(p.read_text().replace("</urlset>", f"<url><loc>{DOMAIN}/</loc></url></urlset>"))
        with self.assertRaisesRegex(ValueError, "duplicate loc"):
            reconcile(self.root, apply=True)

    def test_rejects_noncanonical_index_alias(self):
        p = self.root / "sitemap.xml"
        p.write_text(p.read_text().replace(f"{DOMAIN}/</loc>", f"{DOMAIN}/index.html</loc>"))
        with self.assertRaisesRegex(ValueError, "non-canonical"):
            reconcile(self.root, apply=True)

    def test_preview_cannot_silently_become_indexable(self):
        p = self.root / "home-v2-preview.html"
        p.write_text(p.read_text().replace("noindex, nofollow", "index, follow"))
        with self.assertRaisesRegex(ValueError, "must remain noindex"):
            reconcile(self.root, apply=True)

    def test_real_generator_retains_all_1009_approved_urls(self):
        paths = sitemap_paths(["index.html", "gallery.html", "home-v2-preview.html"])
        expected = {"" if p.name == "index.html" else p.name for p in ROOT.glob("*.html") if p.name != "home-v2-preview.html"}
        self.assertEqual(len(expected), 1009)
        self.assertEqual(set(paths), expected)
        self.assertEqual(len(paths), len(expected))

    def test_gallery_builder_remains_indexable(self):
        spec = importlib.util.spec_from_file_location("gallery_builder", ROOT / "scripts/build-page-owned-general-gallery.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(Metadata(module.build_html([], False)).robots, ["index, follow, max-image-preview:large"])


if __name__ == "__main__":
    unittest.main()
