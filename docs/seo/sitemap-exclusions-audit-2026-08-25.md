# Sitemap exclusion audit — 2026-08-25

## Scope

This audit classifies every root-level HTML page omitted from `sitemap.xml` on commit `06705071ce78`.

- Root-level HTML files: 1006
- Sitemap URLs: 540
- Root-level HTML files outside the sitemap at audit time: 466
- Generated copies under `luna_engine/dist/`: excluded from this count because they are build artifacts, not independent public-page decisions

## Classification

| Classification | Count | Recommendation |
|---|---:|---|
| Ready for sitemap | 1 | Added in the follow-up Weatherford sitemap update |
| Enrich, then index | 17 | Complete social metadata/local proof, validate, then add in small batches |
| Hold: low content | 15 | Expand substantially before considering indexing |
| Hold: template family | 432 | Improve and validate by service family; do not add all 432 at once |
| Exclude preview | 1 | Keep outside sitemap and retain `noindex` |

## Findings

### Ready now

- `weatherford.html` was the strongest omitted city hub and is now staged for sitemap inclusion: one H1, self-canonical, indexable robots directive, four JSON-LD blocks, Open Graph image, Twitter card, and approximately 780 visible words.

### Improve before indexing

- Six city hubs (`addison.html`, `aledo.html`, `benbrook.html`, `denton.html`, `flower-mound.html`, and `highland-village.html`) have valid headings, canonicals, and structured data, but need fuller social metadata and stronger local proof.
- `reviews.html` is useful and substantial, but lacks complete Open Graph/Twitter metadata.
- Ten longer local guides are viable candidates after completing social image coverage and re-running SEO validation.

### Keep out for now

- Fifteen short local articles contain only about 165–187 visible words and incomplete social metadata.
- 432 pages form 12 repeated service-city families across 36 cities. They have solid technical foundations, but indexing them all together would create a large templated expansion. Enrich and validate one family at a time.
- `home-v2-preview.html` is intentionally excluded: it canonicalizes to the homepage and already declares `noindex, nofollow`.

## Safe rollout

1. Add `weatherford.html` in its own small sitemap change. Completed in the follow-up PR.
2. Complete metadata and local-proof improvements for the seven hub/trust pages.
3. Improve and release the ten stronger local guides in a measured batch.
4. Expand the fifteen thin articles.
5. Review the 12 service-city families independently, starting with the families supported by real project evidence and internal links.

The complete page-by-page decision is stored in `seo/sitemap-exclusions.csv`.
