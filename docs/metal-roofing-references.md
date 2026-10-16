# Metal roofing references

Published scope: 36 city roofing pages plus `roofing.html`.

## Editing and rebuilding

- `content/metal-roofing-pages.mjs`: 36 individually written headings, introductions, project discussions and sets of three comparison points. Each city has its own project question, rather than substituted place names.
- `content/metal-roofing-systems.mjs`: shared factual descriptions and official manufacturer links.
- `assets/metal-roofing/sources.json`: downloaded image provenance, author metadata, licenses, dimensions and review date.
- `scripts/build-metal-roofing.mjs`: creates static sections, material navigation and the scoped stylesheet link. It prepares all output before writing and replaces only its own markers on later runs.
- `metal-roofing.css`: responsive layouts; images retain their original proportions.

After any regeneration of the root roofing pages, run the shingle generator followed by the metal generator:

```sh
node scripts/build-roofing-products.mjs
node scripts/build-metal-roofing.mjs
```

The new section uses `#metal-roofing`. It sits outside the existing shingle block. The estimate form, bottom contact bar and footer are retained. Content and references are present in HTML without requiring JavaScript. No forms were submitted.

## Official product references

Research reviewed October 16, 2026. Facts about the exact reference profiles are not universal specifications for all metal roofs. Roof slope, fastening, support, finish, accessories and eligibility must be confirmed for the proposed assembly.

- Englert A1000: https://www.englertinc.com/metal-roofing/metal-roof-panel-a1000 — architectural snap-lock system with concealed clips and fasteners, without mechanical seaming for this model.
- Englert warranties: https://www.englertinc.com/warranties
- MBCI PBR: https://shop.mbci.com/store/mbci/en/Products/Panels/Exposed-Fastener-Panels/PBR/p/PBR — exposed-fastener ribbed roof/wall panel.
- MBCI warranties: https://www.mbci.com/resource-center/resources/warranties/
- DECRA Shingle XD: https://www.decra.com/metal-shingle-roofing — stone-coated steel with a dimensional shingle appearance.
- DECRA warranty resources: https://www.decra.com/register-warranty

Links are references, not assertions of manufacturer authorization, certification, stock or warranty eligibility. Manufacturer coverage is separated from contractor workmanship. No blanket lifespan, insurance discount, energy savings or weather rating is promised.

## Freely licensed photographs

Five photos are distributed as two complementary references on each page. These are material examples, not documented Luna projects or identified examples of the named manufacturers' products. Every display includes the author, original source link and license link. No editorial image edits were made; downloaded Wikimedia thumbnails are used where available. Images are proportionally scaled, not cropped.

| Asset | Author | License | Original source |
| --- | --- | --- | --- |
| `standing-seam-house.jpg` | Doug Oliver Development | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Standing_seam_metal_roof.jpg |
| `exposed-fasteners.jpg` | ralmonline alm | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Corrugated_metal_roof.jpg |
| `standing-seam-profile.jpg` | Wikideas1 | CC0 | https://commons.wikimedia.org/wiki/File:Standing_seam_metal_roof_2.jpg |
| `green-ribbed-roof.jpg` | Wikideas1 | CC0 | https://commons.wikimedia.org/wiki/File:Corrugated_metal_roof_green.jpg |
| `standing-seam-closeup.webp` | Wikideas1 | CC0 | https://commons.wikimedia.org/wiki/File:Standing_seam_metal_roof_up_close.webp |

Licenses: https://creativecommons.org/licenses/by/2.0/ and https://creativecommons.org/publicdomain/zero/1.0/.

Local copies keep the published photos independent of third-party image delivery. The total downloaded image payload is approximately 587 kB; each page lazy-loads only its two selected photographs.
