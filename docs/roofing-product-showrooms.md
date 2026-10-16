# Roofing product showrooms

Editorial/product sources reviewed October 16, 2026. The 36 root city roofing pages and `roofing.html` contain static product sections, so the package photographs, descriptions and source links do not depend on JavaScript.

## Editing

- `content/roofing-product-pages.mjs`: 36 individual introductions, selection notes and project considerations. Geography is context, not evidence of material performance.
- `content/roofing-products.mjs`: exact product names, primary manufacturer links, shared standard warranty facts, and attributed retailer package examples.
- `roofing-products.css`: four responsive presentations: catalog, rows, contrast and spotlight. Layout does not imply a product ranking.
- `scripts/build-roofing-products.mjs`: run with Node from any working directory after editing the source data. It replaces marked blocks in root HTML and stops if expected content or unique editorial entries are missing. Run this after any external process that regenerates the root city pages. The Luna Engine preview files are not the deployed files edited by this script.

The same three factual product specifications appear across pages intentionally. Warranty facts must not be altered to create textual variety. City introductions, all 108 selection notes, and closing project guidance are individually written. Product cards contain no price, stock, review, certification or performance-rating claims.

## Primary sources

- GAF Timberline HDZ product: https://www.gaf.com/en-us/roofing-materials/residential-roofing-materials/shingles/timberline-hdz
- GAF warranty comparison: https://www.gaf.com/en-us/resources/warranties/residential
- Owens Corning Duration Designer: https://www.owenscorning.com/en-us/roofing/shingles/trudefinition-duration-designer
- Owens Corning SureNail: https://www.owenscorning.com/en-us/roofing/surenail
- Owens Corning warranties: https://www.owenscorning.com/en-us/roofing/warranty
- CertainTeed Landmark product and warranty summary: https://www.certainteed.com/products/residential-roofing-products/landmark

Standard limited lifetime eligibility and 10-year initial protection periods are qualified on every section. These initial periods are not statements that the entire warranty ends after 10 years. Enhanced system warranties are not offered automatically, and no contractor qualification is asserted.

## Photographs

The user requested package photos and approved example images with linked sources. These are existing retailer-hosted images; their origin is linked immediately under each image and in the data file. No branded packaging was generated or altered. The GAF photograph is labeled as a Timberline package example from the HDZ listing rather than asserting that an older wrapper depicts a current production label. Packaging, color and availability are explicitly subject to confirmation. External image availability remains a dependency.

## Estimate section

`script.js` leaves the existing form in `.local-form` on `roofing-location-page` pages. Other pages keep the existing relocation behavior. The city contact bar and footer remain in the static HTML; the products stylesheet also gives the lower form a readable panel and space above the floating call control. No forms are submitted as part of this change.

The shared gallery previously called `scrollIntoView` on every 6.5-second autoplay tick, pulling readers back to the gallery. It now scrolls only after a visitor's gallery action. The initial-load handler also respects existing section anchors on internal pages, including `#roof-products` and `#estimate-form`.
