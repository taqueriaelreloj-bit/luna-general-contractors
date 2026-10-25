from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PageOwnedGeneralGalleryTests(unittest.TestCase):
    def test_generated_general_gallery_is_current_and_valid(self) -> None:
        check = subprocess.run(
            [sys.executable, "scripts/build-page-owned-general-gallery.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        validation = subprocess.run(
            [sys.executable, "scripts/validate-page-owned-general-gallery.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(validation.returncode, 0, validation.stdout + validation.stderr)
