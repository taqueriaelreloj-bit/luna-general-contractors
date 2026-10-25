import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "page_owned_builder", ROOT / "scripts" / "apply-page-owned-imagery.py"
)
BUILDER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(BUILDER)


class PageOwnedGalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "content" / "page-owned-imagery.json").read_text(encoding="utf-8"))

    def test_gallery_has_five_static_accessible_thumbnails(self):
        entry = self.manifest["dallas-roofing.html"]
        markup = BUILDER.render_gallery(entry, entry["images"])
        self.assertEqual(markup.count('data-page-owned-gallery-thumbnail="true"'), 5)
        self.assertEqual(markup.count('data-page-owned-gallery-image="true"'), 5)
        self.assertIn('data-page-owned-gallery-previous', markup)
        self.assertIn('data-page-owned-gallery-next', markup)
        self.assertIn('aria-live="polite"', markup)
        for slot in range(1, 6):
            self.assertIn(f'data-page-owned-slot="{slot:02}"', markup)

    def test_home_gallery_contains_all_five_owned_sources_and_is_idempotent(self):
        entry = self.manifest["index.html"]
        original = (ROOT / "index.html").read_text(encoding="utf-8")
        output = BUILDER.transform(original, entry, "index.html")
        self.assertEqual(BUILDER.transform(output, entry, "index.html"), output)
        self.assertNotIn('<!-- additional-services-imagery:start -->', output)
        self.assertEqual(output.count('data-page-owned-gallery="true"'), 1)
        for image in entry["images"]:
            self.assertIn(f'src="{image["src"]}"', output)

    def test_root_hero_is_kept_and_repeated_only_as_its_own_thumbnail(self):
        entry = self.manifest["roofing.html"]
        original = (ROOT / "roofing.html").read_text(encoding="utf-8")
        output = BUILDER.transform(original, entry, "roofing.html")
        hero = next(image for image in entry["images"] if image["slot"] == entry["hero_slot"])
        self.assertEqual(output.count('data-page-owned-hero="true"'), 1)
        self.assertEqual(output.count(hero["src"]), 2)
        self.assertEqual(output.count('data-page-owned-gallery-thumbnail="true"'), 5)


if __name__ == "__main__":
    unittest.main()
