# Approved generated image batch

These PNGs are user-approved, AI-generated representative illustrations. They are not evidence of Luna jobs, locations, inspections, insurance claims, completed work, or product endorsements.

`content/cloud-approved-images.json` records every filename, Git blob SHA, byte count, pixel dimensions, Library identifier, caption, and provenance note. The files are materialized only through GitHub's Git Blob API by `scripts/materialize-approved-cloud-images.mjs`, which verifies the Git blob SHA, PNG signature, byte count, and dimensions before creating an absent destination file.
