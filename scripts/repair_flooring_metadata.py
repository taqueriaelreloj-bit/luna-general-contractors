#!/usr/bin/env python3
"""Keep three published flooring guides' description metadata distinct and aligned.

The routine is deliberately narrow: it changes only the normal, Open Graph,
Twitter, and Article JSON-LD description fields for the reviewed guide pages.
"""

from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DESCRIPTIONS = {
    "flooring-subfloor-preparation-allen.html": (
        "Plan Allen flooring preparation by checking flatness, moisture, movement, "
        "damaged areas, underlayment, transitions and manufacturer requirements."
    ),
    "best-flooring-for-pets-grand-prairie.html": (
        "Compare pet-friendly flooring for Grand Prairie homes by scratch resistance, "
        "moisture, traction, cleanup and subfloor needs. Request a free estimate."
    ),
    "flooring-options-mansfield.html": (
        "The right flooring for a Mansfield home depends on moisture, subfloor condition, "
        "traffic, pets, maintenance preferences, and room connections."
    ),
}


def meta_pattern(attribute: str, key: str) -> re.Pattern[str]:
    return re.compile(
        rf'<meta\b(?=[^>]*\b{re.escape(attribute)}=["\']{re.escape(key)}["\'])[^>]*>',
        re.IGNORECASE,
    )


def upsert_meta(source: str, attribute: str, key: str, description: str) -> str:
    tag = f'<meta {attribute}="{key}" content="{escape(description, quote=True)}">'
    pattern = meta_pattern(attribute, key)
    matches = list(pattern.finditer(source))
    if len(matches) == 1:
        return source[: matches[0].start()] + tag + source[matches[0].end() :]
    if len(matches) > 1:
        raise ValueError(f"expected one {key} meta tag, found {len(matches)}")
    if key != "twitter:description":
        raise ValueError(f"missing required {key} meta tag")

    anchor_matches = list(meta_pattern("name", "twitter:card").finditer(source))
    if len(anchor_matches) != 1:
        raise ValueError("missing unique twitter:card insertion point")
    anchor = anchor_matches[0]
    return source[: anchor.end()] + tag + source[anchor.end() :]


def update_article_jsonld(source: str, description: str) -> str:
    pattern = re.compile(
        r'(<script\b[^>]*\btype=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)',
        re.IGNORECASE,
    )
    updates = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal updates
        data = json.loads(match.group(2))
        types = data.get("@type")
        is_article = types == "Article" or (isinstance(types, list) and "Article" in types)
        if not is_article:
            return match.group(0)
        updates += 1
        data["description"] = description
        return match.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + match.group(3)

    updated = pattern.sub(replace, source)
    if updates != 1:
        raise ValueError(f"expected one Article JSON-LD block, updated {updates}")
    return updated


def updated_source(source: str, description: str) -> str:
    source = upsert_meta(source, "name", "description", description)
    source = upsert_meta(source, "property", "og:description", description)
    source = upsert_meta(source, "name", "twitter:description", description)
    return update_article_jsonld(source, description)


def main() -> None:
    if set(sys.argv[1:]) - {"--check"}:
        raise SystemExit("Usage: repair_flooring_metadata.py [--check]")
    check = "--check" in sys.argv[1:]
    stale: list[str] = []
    for name, description in DESCRIPTIONS.items():
        path = ROOT / name
        source = path.read_text(encoding="utf-8")
        updated = updated_source(source, description)
        if source == updated:
            continue
        if check:
            stale.append(name)
        else:
            path.write_text(updated, encoding="utf-8")
    if stale:
        raise SystemExit("Flooring metadata is stale: " + ", ".join(stale))
    print(f"{'Verified' if check else 'Updated'} distinct description metadata for {len(DESCRIPTIONS)} flooring guides.")


if __name__ == "__main__":
    main()
