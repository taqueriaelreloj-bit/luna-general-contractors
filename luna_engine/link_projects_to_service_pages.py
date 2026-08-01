from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "luna_engine" / "content" / "projects"
START = "<!-- LUNA_PROJECTS_START -->"
END = "<!-- LUNA_PROJECTS_END -->"


def published_projects() -> list[dict]:
    projects: list[dict] = []
    for path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("status") == "published":
            projects.append(data)
    return projects


def project_block(items: list[dict]) -> str:
    cards = "".join(
        f'<article class="seo-city-card"><p class="eyebrow gold">Real Project</p>'
        f'<h3><a href="{p["slug"]}.html">{p["title"]}</a></h3>'
        f'<p>{p["summary"]}</p><a class="seo-text-link" href="{p["slug"]}.html">View project →</a></article>'
        for p in items
    )
    return (
        f'{START}<section class="seo-section related-projects"><div class="container">'
        f'<h2>Related Projects in This Area</h2><div class="seo-city-grid">{cards}</div>'
        f'</div></section>{END}'
    )


def inject(path: Path, block: str) -> None:
    html = path.read_text(encoding="utf-8")
    if START in html and END in html:
        before, rest = html.split(START, 1)
        _, after = rest.split(END, 1)
        html = before + block + after
    elif "</main>" in html:
        html = html.replace("</main>", block + "</main>", 1)
    else:
        raise SystemExit(f"{path}: missing </main>")
    path.write_text(html, encoding="utf-8")


def main() -> None:
    grouped: dict[tuple[str, str], list[dict]] = {}
    for project in published_projects():
        key = (project["city_slug"], project["service_slug"])
        grouped.setdefault(key, []).append(project)

    changed: list[str] = []
    for (city_slug, service_slug), projects in sorted(grouped.items()):
        page = ROOT / f"{city_slug}-{service_slug}.html"
        if not page.exists():
            raise SystemExit(f"Missing related service page: {page.name}")
        inject(page, project_block(projects))
        changed.append(page.name)

    manifest = ROOT / "luna_engine" / "project-linked-pages.txt"
    manifest.write_text("\n".join(changed) + ("\n" if changed else ""), encoding="utf-8")
    print(f"Linked real projects from {len(changed)} city-service pages")


if __name__ == "__main__":
    main()
