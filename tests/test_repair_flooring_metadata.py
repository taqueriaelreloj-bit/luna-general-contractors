import unittest
from pathlib import Path

from scripts.repair_flooring_metadata import DESCRIPTIONS, ROOT, updated_source


class FlooringMetadataRepairTests(unittest.TestCase):
    def test_reviewed_guides_are_already_in_their_expected_state(self):
        for name, description in DESCRIPTIONS.items():
            with self.subTest(page=name):
                source = (ROOT / name).read_text(encoding="utf-8")
                self.assertEqual(source, updated_source(source, description))

    def test_repair_scope_is_exactly_the_three_reviewed_guides(self):
        self.assertEqual(
            {
                "flooring-subfloor-preparation-allen.html",
                "best-flooring-for-pets-grand-prairie.html",
                "flooring-options-mansfield.html",
            },
            set(DESCRIPTIONS),
        )
        self.assertTrue(all((ROOT / name).is_file() for name in DESCRIPTIONS))


if __name__ == "__main__":
    unittest.main()
