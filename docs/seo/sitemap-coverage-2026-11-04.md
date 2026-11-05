# Published sitemap coverage

The page sitemap now includes 1,009 of the 1,010 root HTML files. The only
exception is `home-v2-preview.html`, an unpublished homepage preview whose
canonical points to `/` and whose `noindex, nofollow` remains unchanged.

The 463 newly included pages comprise 461 service/template pages, `privacy.html`,
and `gallery.html`. Their robots metadata now allows indexing. This deliberately
replaces the previous family-level holding policy. It does not establish that
the repeated content has been improved or that Google will index or rank it.

Existing sitemap lastmod dates are preserved. Newly added entries omit lastmod
rather than imply an editorial update. Page bodies, project images, image
ownership manifests, and the separate image sitemap are unchanged. The gallery
is indexable as a browsing page without claiming ownership of its images.

## Scoped maintenance

- `python scripts/reconcile_sitemap.py --check` verifies complete root-page
  coverage, unique canonical URLs, robots controls, and explicit exclusions.
- `python scripts/reconcile_sitemap.py --apply` restores coverage and approved
  indexing controls without rebuilding page content or altering image ownership.
- `python -m unittest -v tests.test_sitemap_coverage tests.test_generate_seo_pages`
  covers regeneration, preview exclusion, idempotence, dates, and failure cases.
- `python scripts/validate_sitemap_exclusions.py` and
  `python scripts/validate_seo.py` retain the existing SEO checks.

The primary SEO generator preserves existing root pages; the exclusion pass
reconciles coverage, and the gallery builder preserves its indexable status.
Broad content generators are not required to make or test this change.
