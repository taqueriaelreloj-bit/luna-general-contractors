from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def main() -> None:
    changed = 0
    for page in sorted(DIST.glob("*-general-contractor.html")):
        html = page.read_text(encoding="utf-8")
        start = html.find("<title>")
        end = html.find("</title>")
        if start == -1 or end == -1:
            raise SystemExit(f"Missing title in {page}")

        old_title = html[start + 7:end]
        if not old_title.startswith("General Contractor in "):
            continue

        new_title = old_title.replace("General Contractor in ", "General Contractor Services in ", 1)
        html = html.replace(f"<title>{old_title}</title>", f"<title>{new_title}</title>", 1)
        html = html.replace(f'property="og:title" content="{old_title}"', f'property="og:title" content="{new_title}"', 1)
        html = html.replace(f'"name":"{old_title}"', f'"name":"{new_title}"', 1)
        page.write_text(html, encoding="utf-8")
        changed += 1

    print(f"Updated {changed} general-contractor page titles")


if __name__ == "__main__":
    main()
