"""Repair the insurance-claims FAQ sections from the reviewed service source.

This intentionally selects only the 36 city insurance-claims pages recorded in the
service-guide manifest. It updates the visible FAQ details and the matching FAQPage
JSON-LD, leaving page imagery, galleries, local content, and other schema untouched.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.generate_seo_pages import INSURANCE_DISCLAIMER, faq_schema, insurance_claims_faqs

MANIFEST_PATH = ROOT / "content" / "service-guide-manifest.json"
FAQ_SCRIPT = re.compile(r'<script type="application/ld\+json">(?P<payload>.*?)</script>', re.DOTALL)
VISIBLE_FAQ = re.compile(
    r'(?s)(<div class="faq"><h2>Frequently Asked Questions</h2>)(.*?)(</div>)'
)


def target_files() -> list[Path]:
    assignments = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = [
        ROOT / item["file"]
        for item in assignments
        if item.get("key") == "insurance-claims" and item.get("slug") and not item.get("hub") and not item.get("article")
    ]
    if len(files) != 36 or len({path.name for path in files}) != 36:
        raise ValueError("Expected exactly 36 unique city insurance-claims pages in the service-guide manifest")
    missing = [path.name for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing insurance-claims page(s): {', '.join(missing)}")
    return files


def is_faq_page(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    kind = payload.get("@type")
    return kind == "FAQPage" or (isinstance(kind, list) and "FAQPage" in kind)


def replace_faq_schema(source: str, rendered_schema: str, path: Path) -> str:
    matches = []
    for match in FAQ_SCRIPT.finditer(source):
        try:
            payload = json.loads(match.group("payload"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON-LD in {path.name}: {error.msg}") from error
        if is_faq_page(payload):
            matches.append(match)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one FAQPage JSON-LD block in {path.name}, found {len(matches)}")
    match = matches[0]
    return source[:match.start()] + rendered_schema + source[match.end():]


def visible_faq_markup(faqs: list[tuple[str, str]]) -> str:
    return "".join(
        f"<details><summary>{escape(question)}</summary><p>{escape(answer)}</p></details>"
        for question, answer in faqs
    )


def replace_visible_faq(source: str, rendered_faq: str, path: Path) -> str:
    matches = list(VISIBLE_FAQ.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one visible FAQ block in {path.name}, found {len(matches)}")
    match = matches[0]
    return source[:match.start(2)] + rendered_faq + source[match.end(2):]


def updated_source(source: str, path: Path) -> str:
    faqs = insurance_claims_faqs()
    updated = replace_faq_schema(source, faq_schema(faqs), path)
    updated = replace_visible_faq(updated, visible_faq_markup(faqs), path)
    if INSURANCE_DISCLAIMER not in updated:
        raise ValueError(f"Insurance disclaimer did not render in {path.name}")
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair FAQPage and visible insurance FAQ content from the canonical service source.")
    parser.add_argument("--check", action="store_true", help="Fail if any target page differs from the canonical FAQ output.")
    args = parser.parse_args()

    stale: list[str] = []
    for path in target_files():
        source = path.read_text(encoding="utf-8")
        expected = updated_source(source, path)
        if source != expected:
            stale.append(path.name)
            if not args.check:
                path.write_text(expected, encoding="utf-8")

    if args.check and stale:
        raise SystemExit(
            f"Insurance FAQ repair is stale ({len(stale)} page(s)): {', '.join(stale[:8])}"
        )
    action = "Verified" if args.check else "Repaired"
    print(f"{action} insurance FAQ content for {len(target_files())} city pages")


if __name__ == "__main__":
    main()
