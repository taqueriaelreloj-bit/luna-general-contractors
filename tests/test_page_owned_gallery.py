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

    def test_transform_removes_legacy_additional_imagery_and_duplicate_anchor(self):
        entry = self.manifest["kitchens.html"]
        original = (ROOT / "kitchens.html").read_text(encoding="utf-8")
        legacy = (
            '<span id="gallery" class="poi-gallery-anchor" aria-hidden="true"></span>'
            '<!-- additional-test-imagery:start -->'
            '<section id="legacy-planning-scene">legacy planning scene</section>'
            '<!-- additional-test-imagery:end -->'
        )
        fixture = original.replace('<!-- page-owned-imagery:end -->', '<!-- page-owned-imagery:end -->' + legacy, 1)
        output = BUILDER.transform(fixture, entry, "kitchens.html")
        self.assertNotIn('additional-test-imagery', output)
        self.assertNotIn('legacy-planning-scene', output)
        self.assertEqual(output.count('id="gallery"'), 1)
        self.assertEqual(BUILDER.transform(output, entry, "kitchens.html"), output)

    def test_hub_pages_have_only_the_owned_five_image_gallery(self):
        for page in ("kitchens.html", "bathrooms.html", "carpentry.html", "painting.html", "siding.html", "fencing.html"):
            output = (ROOT / page).read_text(encoding="utf-8")
            self.assertNotRegex(output, r"additional-[a-z0-9-]+-imagery")
            self.assertEqual(output.count('data-page-owned-slot="'), 5, page)
            self.assertEqual(output.count('id="gallery"'), 1, page)

    def test_root_hero_is_kept_and_repeated_only_as_its_own_thumbnail(self):
        entry = self.manifest["roofing.html"]
        original = (ROOT / "roofing.html").read_text(encoding="utf-8")
        output = BUILDER.transform(original, entry, "roofing.html")
        hero = next(image for image in entry["images"] if image["slot"] == entry["hero_slot"])
        self.assertEqual(output.count('data-page-owned-hero="true"'), 1)
        self.assertEqual(output.count(hero["src"]), 2)
        self.assertEqual(output.count('data-page-owned-gallery-thumbnail="true"'), 5)

    def test_normal_page_places_full_width_gallery_after_compact_form_reviews_row(self):
        entry = self.manifest["dallas-roofing.html"]
        original = (ROOT / "dallas-roofing.html").read_text(encoding="utf-8")
        output = BUILDER.transform(original, entry, "dallas-roofing.html")
        self.assertEqual(BUILDER.transform(output, entry, "dallas-roofing.html"), output)
        lead = output.split(BUILDER.LEAD_START, 1)[1].split(BUILDER.LEAD_END, 1)[0]
        self.assertIn('<div class="container estimate-reviews-layout">', lead)
        self.assertIn('<div class="page-estimate-reviews__reviews">', lead)
        self.assertIn('<div class="page-estimate-reviews__gallery">', lead)
        self.assertNotIn('page-estimate-reviews__content', lead)
        self.assertLess(lead.index('id="estimate-form"'), lead.index(BUILDER.REVIEW_START))
        self.assertLess(lead.index(BUILDER.REVIEW_START), lead.index('<div class="page-estimate-reviews__gallery">'))
        self.assertEqual(lead.count('data-page-owned-gallery-thumbnail="true"'), 5)


if __name__ == "__main__":
    unittest.main()
