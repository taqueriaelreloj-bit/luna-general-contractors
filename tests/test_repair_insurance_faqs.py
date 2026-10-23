import unittest

from scripts.repair_insurance_faqs import INSURANCE_DISCLAIMER, target_files, updated_source
from tools.generate_seo_pages import SERVICES, insurance_claims_faqs, service_page


class InsuranceFaqRepairTests(unittest.TestCase):
    def test_scope_is_exactly_the_36_city_insurance_pages(self):
        files = target_files()
        self.assertEqual(36, len(files))
        self.assertEqual(36, len({path.name for path in files}))
        self.assertTrue(all(path.name.endswith("-insurance-claims.html") for path in files))

    def test_canonical_faq_renders_in_generator_and_repair_output(self):
        source = target_files()[0].read_text(encoding="utf-8")
        repaired = updated_source(source, target_files()[0])
        generated = service_page(
            "Dallas",
            "insurance-claims",
            SERVICES["insurance-claims"][0],
            SERVICES["insurance-claims"][1],
        )
        self.assertIn(INSURANCE_DISCLAIMER, repaired)
        self.assertIn(INSURANCE_DISCLAIMER, generated)
        self.assertEqual(4, len(insurance_claims_faqs()))


if __name__ == "__main__":
    unittest.main()
