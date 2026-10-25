#!/usr/bin/env python3
"""Verify the post-hero form/reviews/gallery contract without changing pages."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGERY_START = '<!-- page-owned-imagery:start -->'
IMAGERY_END = '<!-- page-owned-imagery:end -->'
REVIEWS_START = '<!-- shared-customer-reviews:start -->'
REVIEWS_END = '<!-- shared-customer-reviews:end -->'
LEAD_START = '<!-- page-lead-layout:start -->'
LEAD_END = '<!-- page-lead-layout:end -->'


def exactly_one(text, token, page, errors):
    if text.count(token) != 1:
        errors.append(f'{page}: expected one {token!r}, found {text.count(token)}')


def main():
    manifest = json.loads((ROOT / 'content' / 'page-owned-imagery.json').read_text(encoding='utf-8'))
    errors = []
    covered = 0
    exceptions = []
    for page in sorted(manifest):
        text = (ROOT / page).read_text(encoding='utf-8')
        exactly_one(text, IMAGERY_START, page, errors)
        exactly_one(text, IMAGERY_END, page, errors)
        if page == 'index.html':
            if not re.search(r'<section\b[^>]*class="[^"]*estimate-reviews-section', text, re.I):
                errors.append('index.html: homepage estimate/reviews section missing')
            if 'data-homepage-reviews' not in text:
                errors.append('index.html: homepage review mount missing')
            if text.count('id="estimate-form"') != 1:
                errors.append('index.html: expected one estimate form')
            covered += 1
            continue
        if page == 'privacy.html':
            if 'id="estimate-form"' in text:
                errors.append('privacy.html: intentionally form-free page gained an estimate form')
            exceptions.append(page)
            continue
        if page == 'reviews.html':
            if 'class="review-list"' not in text:
                errors.append('reviews.html: dedicated review content missing')
            if text.count('id="estimate-form"') != 1:
                errors.append('reviews.html: expected one estimate form')
            exceptions.append(page)
            continue

        exactly_one(text, LEAD_START, page, errors)
        exactly_one(text, LEAD_END, page, errors)
        exactly_one(text, REVIEWS_START, page, errors)
        exactly_one(text, REVIEWS_END, page, errors)
        if text.count('id="estimate-form"') != 1:
            errors.append(f'{page}: expected one estimate form')
            continue
        start, end = text.find(LEAD_START), text.find(LEAD_END)
        if start < 0 or end < start:
            continue
        lead = text[start:end]
        form_at = lead.find('id="estimate-form"')
        reviews_at = lead.find(REVIEWS_START)
        gallery_at = lead.find(IMAGERY_START)
        if min(form_at, reviews_at, gallery_at) < 0 or not (form_at < reviews_at < gallery_at):
            errors.append(f'{page}: lead order is not form -> reviews -> gallery')
        main_at = text.find('<main')
        if main_at < 0 or start < main_at:
            errors.append(f'{page}: lead wrapper is not inside main')
        covered += 1

    gallery = (ROOT / 'gallery.html').read_text(encoding='utf-8')
    if LEAD_START in gallery or 'data-estimate-reviews-layout' in gallery:
        errors.append('gallery.html: general gallery was changed by lead layout')
    if 'data-general-gallery-source' not in gallery:
        errors.append('gallery.html: general-gallery data source missing')

    script = (ROOT / 'script.js').read_text(encoding='utf-8')
    if 'hasLeadEstimateReviewsLayout' not in script:
        errors.append('script.js: lead-layout guard missing')
    if 'form.closest("[data-estimate-reviews-layout=\'true\']")' not in script:
        errors.append('script.js: duplicate compact-review guard missing')

    result = {
        'pages_in_manifest': len(manifest),
        'lead_layout_pages': covered - 1,
        'homepage': 'validated',
        'exceptions': exceptions,
        'general_gallery_unchanged': not any('gallery.html:' in error for error in errors),
        'errors': errors,
    }
    print(json.dumps(result, indent=2))
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
