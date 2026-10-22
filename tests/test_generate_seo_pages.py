import unittest

from tools.generate_seo_pages import PRESERVED_INDEXABLE_SITEMAP_PATHS, sitemap_paths


class SitemapGenerationTests(unittest.TestCase):
    def test_preserves_reviewed_indexable_routes_without_duplicates(self):
        paths = sitemap_paths(["roofing.html", "projects.html", "new-city-guide.html"])

        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(18, len(PRESERVED_INDEXABLE_SITEMAP_PATHS))
        self.assertTrue(set(PRESERVED_INDEXABLE_SITEMAP_PATHS).issubset(paths))
        self.assertIn("new-city-guide.html", paths)


if __name__ == "__main__":
    unittest.main()
