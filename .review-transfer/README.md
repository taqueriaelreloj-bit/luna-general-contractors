# Gallery image integration review transfer

This branch transports public website derivatives and a code patch. Do NOT merge this transfer branch into main or deploy its ZIP files. Apply the payload to a separate worktree based on 905764191a5b6d1d609627f96c6f8a82904882c8 (tree 4d5229830841b934efb716ff527e3b6abbb7c620), validate, then commit only resulting website source/assets on a separate integration branch.

Payload: manifest.json lists 143 image ZIPs, 4747 new derivative paths, and one site-code.zip. The existing pilot ZIP is obsolete and is NOT part of this manifest. All ZIP and member SHA256 hashes, byte counts and exact paths are listed. There are 1009 target pages and 5045 unique assigned images; 298 already-existing assigned files remain in the base repository. Original work-photo files are preserved.

Safe application:
1. Fetch this review branch through the authorized repository connection. Record its exact commit. Keep transfer files separate from the clean application worktree.
2. Verify manifest.json SHA256 against the separately supplied receipt. Verify EVERY archive SHA256 and size before reading members.
3. Reject any extra/missing ZIP members, duplicate member paths, absolute paths, drive paths, backslashes, '..', symlink entries, or resolved destinations outside the application worktree. Image members must start assets/images/illustrations/page-owned/ and match manifest paths exactly. Verify every member byte count and SHA256 before writing. Do not overwrite existing files unless exact verified identical bytes.
4. Extract the 4747 image members. For site-code.zip, inspect site-changes.patch and all new-files before applying. Write the six declared new files only to their target_path, requiring them to be absent. Run git apply --check on site-changes.patch, then git apply. Do not execute unreviewed transfer content automatically.
5. Inspect newly authored scripts/apply-page-owned-imagery.py, scripts/validate-page-owned-imagery.py and content/page-owned-imagery.mjs, plus modified generators, script.js, caption validator and sitemap validator. The Python postprocessor writes only scoped page/CSS changes; reversible removals default to Git's private path, not public site files.

Static checks (Python 3 and Node required):
  node --check script.js
  python scripts/validate-page-owned-imagery.py
  node scripts/validate-generated-image-captions.mjs
  python scripts/validate-image-sitemap.py
  python scripts/apply-page-owned-imagery.py --check
  python scripts/validate_seo.py
  python scripts/validate_sitemap_exclusions.py
  python -m unittest discover -s tests -v

In another disposable worktree, test node scripts/build-service-site.mjs and rerun the validators. The final common postprocessor prevents future generators from restoring historical photo placements. Historical photo records and original files remain archived in source, not displayed.

Browser QA remains required; cloud static checks are NOT visual approval. Serve locally. Automate navigation to all 1009 manifest pages, load/decode images (including lazy images), validate each page's five assigned paths, no withheld work-photo DOM/CSS/network placements, no broken images, no page JavaScript errors, and responsive overflow. Review actual screenshots at desktop/mobile sizes across all service families, homepage, Spanish, cases, reviews, privacy and preview pages. Explicitly inspect all eight real-project case pages: generated scenes must be separated as planning/design concepts, never under before/after or completed-job evidence headings. Preserve supported case text without implying the images document that job. Test menu open/close, repeated navigation, Back/Forward, gallery interactions and estimate form rendering without submitting customer data. Report exact rendered coverage and remaining limitations; do not label unrendered pages visually approved.

Three technical component illustrations are intentionally preserved pending a separate replacement batch. Privacy policy body is unchanged; its separate neutral gallery makes no policy/security claim. Captions are short subject/service plus city/DFW. Generated concepts must not be represented as completed customer projects or before/after evidence.

Only after browser QA, inspect git diff/status for scope and preserved originals, commit actual site files (not .review-transfer), and use the authorized publishing workflow. Main must remain unchanged until validation is accepted. Verify exact production commit, deployment result and live pages before reporting publication complete.
