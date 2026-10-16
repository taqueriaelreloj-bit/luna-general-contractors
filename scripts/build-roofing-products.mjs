import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import pages from '../content/roofing-product-pages.mjs';
import products from '../content/roofing-products.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const start = '<!-- roofing-products:start -->';
const end = '<!-- roofing-products:end -->';
const version = '20261016-products-1';
const external = (url, text) => `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(text)}</a>`;

function card(product, note, city) {
  return `<article class="rp-card" aria-labelledby="rp-${product.id}">
  <header class="rp-card-header"><p class="rp-brand">${escape(product.brand)}</p><h3 id="rp-${product.id}">${escape(product.model)}</h3></header>
  <figure class="rp-photo"><a class="rp-image-link" href="${escape(product.imageSource)}" target="_blank" rel="noopener noreferrer" aria-label="View ${escape(product.brand)} package source at Lowe’s"><img src="${escape(product.image)}" alt="${escape(product.alt)}" width="400" height="240" loading="lazy" decoding="async"></a><figcaption>${external(product.imageSource, product.caption)}</figcaption></figure>
  <div class="rp-body">
    <p class="rp-feature">${escape(product.feature)}</p>
    <p class="rp-project-note"><strong>For your ${escape(city)} project</strong>${escape(note)}</p>
    <dl class="rp-warranty"><dt>Manufacturer shingle warranty*</dt><dd>Limited lifetime</dd><dt>${escape(product.period)} period*</dt><dd>${escape(product.years)}</dd></dl>
    <details><summary>${escape(product.brand)} coverage details</summary><p>${escape(product.warranty)}</p></details>
    <div class="rp-links">${external(product.productUrl, 'Official product details')}${external(product.warrantyUrl, 'Manufacturer warranty')}</div>
  </div>
</article>`;
}

function showroom(page, cta = '#estimate-form') {
  return `${start}
<section class="roof-products roof-products--${escape(page.layout)}" id="roof-products" aria-labelledby="rp-heading">
  <header class="rp-header"><p class="rp-eyebrow">Material selection / ${escape(page.city)}, Texas</p><h2 id="rp-heading">${escape(page.title)}</h2><p>${escape(page.intro)}</p></header>
  <div class="rp-grid">${products.map((product, i) => card(product, page.notes[i], page.city)).join('\n')}</div>
  <aside class="rp-focus" aria-labelledby="rp-focus-heading"><h3 id="rp-focus-heading">${escape(page.focus)}</h3><p>${escape(page.detail)}</p></aside>
  <p class="rp-fine-print"><strong>*Manufacturer coverage:</strong> Lifetime is a defined limited-warranty term for eligible owners and properties, not the expected service life of the roof. Standard manufacturer coverage for product defects is separate from installer workmanship. Enhanced programs have additional component, installation, registration and sometimes contractor requirements; availability must be confirmed in writing. The applicable manufacturer document controls.</p>
  <p class="rp-fine-print"><strong>About the photos:</strong> Retailer package examples with source links. Packaging and colors may vary; supplier availability, the exact model and final color must be confirmed for your estimate. These images do not indicate inventory or manufacturer certification.</p>
  <div class="rp-next"><p><strong>Have a material in mind?</strong><br>Include the brand and model when requesting your estimate.</p><a class="btn btn-gold" href="${cta}">Discuss your roofing options →</a></div>
</section>
${end}`;
}

function replaceShowroom(html, section, marker) {
  const begin = html.indexOf(start);
  if (begin >= 0) {
    const finish = html.indexOf(end, begin);
    if (finish < 0) throw new Error('Incomplete product section marker');
    return html.slice(0, begin) + section + html.slice(finish + end.length);
  }
  if (!html.includes(marker)) throw new Error(`Missing insertion point: ${marker}`);
  return html.replace(marker, section + '\n' + marker);
}

function stylesheet(html) {
  // Avoid accumulating stylesheet links when this build is repeated.
  html = html.replace(/\s*<link rel="stylesheet" href="\/?roofing-products\.css(?:\?[^"<>]*)?">/g, '');
  return html.replace('</head>', `  <link rel="stylesheet" href="roofing-products.css?v=${version}">\n</head>`);
}

// Guard the editorial input before modifying any pages.
if (pages.length !== 36 || new Set(pages.map(page => page.slug)).size !== 36) throw new Error('Expected 36 distinct city entries');
for (const field of ['title', 'intro', 'detail']) {
  if (new Set(pages.map(page => page[field])).size !== pages.length) throw new Error(`Repeated ${field}`);
}
if (new Set(pages.flatMap(page => page.notes)).size !== 108) throw new Error('Expected 108 distinct product-selection notes');
const pending = [];
for (const page of pages) {
  if (page.notes.length !== products.length) throw new Error(`Missing notes: ${page.slug}`);
  const path = resolve(root, `${page.slug}-roofing.html`);
  let html = await readFile(path, 'utf8');
  html = replaceShowroom(html, showroom(page), '<section class="roofing-visit-guide"');
  html = stylesheet(html);
  html = html.replace(/src="script\.js(?:\?[^"<>]*)?"/g, `src="script.js?v=${version}"`);
  pending.push([path, html]);
}

const centralPath = resolve(root, 'roofing.html');
let central = await readFile(centralPath, 'utf8');
const centralPage = {
  city: 'DFW', layout: 'catalog', title: 'Three shingle products. A clearer material decision.',
  intro: 'See the package, identify the model and compare what belongs in the complete roof assembly. These architectural asphalt shingles are examples to discuss for a suitable sloped roof; metal, tile and low-slope systems need their own specifications.',
  notes: [
    'Compare the proposed HDZ shingle together with the starter, ridge caps, deck protection and flashing. Ask for every selected component to be named in the written estimate.',
    'Review the Designer color blend on a physical sample and confirm the exact product line. Compare the installed scope as well as the visible finish.',
    'Discuss Landmark as part of the whole roof assembly, including the deck, underlayment and ventilation. Keep the approved color and warranty document with the project record.'
  ],
  focus: 'Choose the roof system before the final color',
  detail: 'Roof slope, deck condition, drainage, ventilation and transition details guide the assembly. After those are established, compare samples and identify the manufacturer, model, accessories and applicable warranty in the estimate.'
};
const centralSection = showroom(centralPage, '#estimate-form');
if (central.includes(start)) central = replaceShowroom(central, centralSection, '');
else {
  const old = /<h3 class="roofing-warranty-heading">[\s\S]*?<p class="roofing-warranty-note">[\s\S]*?<\/p>/;
  if (!old.test(central)) throw new Error('Missing central warranty section');
  central = central.replace(old, centralSection);
}
central = central.replace(/src="script\.js(?:\?[^"<>]*)?"/g, `src="script.js?v=${version}"`);
pending.push([centralPath, stylesheet(central)]);
for (const [path, html] of pending) await writeFile(path, html, 'utf8');
console.log(`Built product showrooms for ${pages.length} city pages and roofing.html.`);
