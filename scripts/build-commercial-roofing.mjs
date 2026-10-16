import { readFile, writeFile, access } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import pages from '../content/commercial-roofing-pages.mjs';
import cities from '../content/roofing-product-pages.mjs';
import { membranes, otherSystems } from '../content/commercial-roofing-systems.mjs';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const start = '<!-- commercial-roofing:start -->';
const end = '<!-- commercial-roofing:end -->';
const version = '20261016-commercial-1';
const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const external = (url, label) => `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(label)}</a>`;

function membraneCard(product, note, city) {
  return `<article class="cr-membrane" aria-labelledby="cr-${product.id}">
  <div class="cr-material-art"><img src="${product.image}" alt="${escape(product.alt)}" width="600" height="260" loading="lazy" decoding="async"><span>Illustration · generic material</span></div>
  <div class="cr-card-body"><header><p class="cr-label">${escape(product.fullName)}</p><h4 id="cr-${product.id}">${escape(product.name)}</h4><p class="cr-brand">Reference: ${escape(product.brand)}</p></header>
  <p>${escape(product.description)}</p><p class="cr-selection">${escape(product.detail)}</p>
  <p class="cr-city-note"><strong>For your ${escape(city)} property</strong>${escape(note)}</p>
  <details class="cr-warranty-detail"><summary><span>Manufacturer warranty reference</span><strong>${escape(product.warrantyLabel)}</strong></summary><p>${escape(product.warranty)}</p><p>${external(product.warrantyUrl, 'Read the manufacturer terms ↗')}</p></details>
  <div class="cr-card-links">${external(product.source, 'Official system reference ↗')}</div></div>
</article>`;
}

function familyCard(system, i) {
  return `<details class="cr-family" id="cr-family-${system.id}"><summary><span class="cr-family-number">${String(i + 4).padStart(2, '0')}</span><span><strong>${escape(system.name)}</strong><small>${escape(system.family)}</small></span><span class="cr-expand" aria-hidden="true">+</span></summary><div class="cr-family-body"><p>${escape(system.description)}</p><p><strong>Compare in the estimate:</strong> ${escape(system.ask)}</p>${external(system.source, system.sourceName + ' ↗')}${system.id === 'metal' ? '<a class="cr-inline-link" href="#metal-roofing">See metal profiles on this page →</a>' : ''}${system.id === 'steep' ? '<a class="cr-inline-link" href="#roof-products">See shingle product examples →</a>' : ''}</div></details>`;
}

function section(page) {
  const cta = page.slug === 'roofing' ? 'index.html#estimate-form' : '#estimate-form';
  return `${start}
<section class="commercial-roofing commercial-roofing--${escape(page.layout)}" id="commercial-roofing" aria-labelledby="cr-heading">
  <header class="cr-hero"><div><p class="cr-eyebrow">Commercial roofing / ${escape(page.city)}, Texas</p><h2 id="cr-heading">${escape(page.title)}</h2><p class="cr-intro">${escape(page.intro)}</p></div><aside class="cr-project-brief"><p class="cr-label">Project planning</p><h3>${escape(page.briefTitle)}</h3><p>${escape(page.brief)}</p></aside></header>
  <nav class="cr-jump" aria-label="Commercial roofing guide"><a href="#cr-single-ply">TPO, PVC &amp; EPDM</a><a href="#cr-more-systems">More roof systems</a><a href="#cr-assembly">Assembly &amp; details</a><a href="#cr-coverage">Warranty questions</a></nav>
  <div class="cr-content"><div class="cr-section-heading" id="cr-single-ply"><p class="cr-eyebrow">01 / Single-ply membranes</p><h3>Start with TPO. Compare the alternatives.</h3><p>These membrane families can look similar from the ground. Their chemistry, seams, accessories and approved assemblies differ.</p></div>
  <div class="cr-membranes">${membranes.map((product, i) => membraneCard(product, page.notes[i], page.city)).join('\n')}</div>
  <div class="cr-section-heading" id="cr-more-systems"><p class="cr-eyebrow">02 / The wider material guide</p><h3>Other commercial roof systems</h3><p>Open a system to see how it is built and what to compare. Selection depends on the building, its existing condition and the proposed work.</p></div>
  <div class="cr-families">${otherSystems.map(familyCard).join('\n')}</div>
  <div class="cr-section-heading" id="cr-assembly"><p class="cr-eyebrow">03 / Beyond the membrane</p><h3>The roof includes everything beneath and around it.</h3></div>
  <div class="cr-assembly"><figure><img src="assets/commercial-roofing/roof-assembly.svg" alt="Concept diagram of a commercial roof: membrane, optional cover board, insulation and structural deck; actual assemblies vary" width="850" height="440" loading="lazy" decoding="async"><figcaption>Original illustration. The specified system determines the layers, attachment and any air or vapor controls.</figcaption></figure><div class="cr-assembly-notes"><h4>Four items to keep in the proposal</h4><ol><li><strong>Existing condition</strong>Deck, roof layers, moisture findings and the basis for repair, removal or recover.</li><li><strong>Drainage</strong>Roof slope, tapered insulation where specified, drains, scuppers and overflow paths.</li><li><strong>Details &amp; access</strong>Curbs, penetrations, edges, walls and protected routes to equipment.</li><li><strong>Installation &amp; closeout</strong>Approved assembly, work sequence, product records and manufacturer requirements.</li></ol></div></div>
  <div class="cr-reference-photos"><figure><img src="assets/commercial-roofing/membrane-work.jpg" alt="Reference photograph of membrane-sealing equipment on a light-colored flat roof" width="1018" height="797" loading="lazy" decoding="async"><figcaption><strong>Membrane seam equipment</strong>Radomil · ${external('https://commons.wikimedia.org/wiki/File:Roof_working1_RB.JPG','Original photo')} · ${external('https://creativecommons.org/licenses/by-sa/3.0/','CC BY-SA 3.0')}</figcaption></figure><figure><img src="assets/commercial-roofing/epdm-roof.jpg" alt="EPDM membrane reference on a low-slope roof with a perimeter wall" width="1280" height="1065" loading="lazy" decoding="async"><figcaption><strong>EPDM roof surface</strong>KVDP · ${external('https://commons.wikimedia.org/wiki/File:FinishedEPDMcoveredRoof.jpg','Original photo / public-domain dedication')}</figcaption></figure><p>Reference photographs, not Luna project photos or evidence of a specific product currently offered. Images are proportionally resized without cropping or editorial changes; the seam-equipment photo remains available under CC BY-SA 3.0.</p></div>
  <aside class="cr-coverage" id="cr-coverage"><div><p class="cr-eyebrow">04 / Manufacturer coverage</p><h3>Ask what the years actually cover.</h3></div><div><p>The GAF periods above refer to limited material coverage for leaks caused by manufacturing defects, subject to exclusions and a prorated remedy. Carlisle’s referenced periods are system-program options. These are different scopes of coverage, not equivalent offers or predictions of roof life.</p><p>Request the exact warranty or guarantee form, covered components, required inspections, registration and installer qualifications. Manufacturer coverage and contractor workmanship should be documented separately. References here do not establish Luna’s authorization for a manufacturer program.</p></div></aside>
  <div class="cr-next"><div><strong>Tell us about the building and the roof concern.</strong><p>Include the property address, building use, existing material if known, and any inspection photos.</p></div><a class="btn btn-gold" href="${cta}">Request a commercial roof estimate →</a></div>
  </div>
</section>
${end}`;
}

function integrate(html, content) {
  const begin = html.indexOf(start);
  if (begin >= 0) {
    const finish = html.indexOf(end, begin);
    if (finish < 0) throw new Error('Incomplete commercial section marker');
    html = html.slice(0, begin) + content + html.slice(finish + end.length);
  } else {
    const anchor = '<!-- metal-roofing:end -->';
    if (!html.includes(anchor)) throw new Error('Build the metal roofing guide first');
    html = html.replace(anchor, anchor + '\n' + content);
  }
  const nav = '<!-- roofing-material-nav:start --><nav class="roofing-material-nav" aria-label="Roof material guides"><strong>Explore roofing materials</strong><a href="#roof-products">Asphalt shingles</a><a href="#metal-roofing">Metal roofing</a><a href="#commercial-roofing">Commercial / TPO ↓</a></nav><!-- roofing-material-nav:end -->';
  const navMarker = /<!-- roofing-material-nav:start -->[\s\S]*?<!-- roofing-material-nav:end -->/;
  if (!navMarker.test(html)) throw new Error('Missing material navigation');
  html = html.replace(navMarker, nav);
  html = html.replace(/\s*<link rel="stylesheet" href="\/?commercial-roofing\.css(?:\?[^"<>]*)?">/g, '');
  return html.replace('</head>', `  <link rel="stylesheet" href="commercial-roofing.css?v=${version}">\n</head>`);
}

if (pages.length !== 36 || new Set(pages.map(page => page.slug)).size !== 36) throw new Error('Expected 36 unique city entries');
for (const key of ['title', 'intro', 'briefTitle', 'brief']) {
  if (new Set(pages.map(page => page[key])).size !== pages.length) throw new Error(`Repeated city ${key}`);
}
if (new Set(pages.flatMap(page => page.notes)).size !== 108) throw new Error('Expected 108 original membrane-selection notes');
for (const file of [...membranes.map(product => product.image), 'assets/commercial-roofing/roof-assembly.svg', 'assets/commercial-roofing/membrane-work.jpg', 'assets/commercial-roofing/epdm-roof.jpg']) await access(resolve(root, file));
const pending = [];
for (const page of pages) {
  const city = cities.find(item => item.slug === page.slug);
  if (!city || page.notes.length !== 3) throw new Error(`Incomplete input for ${page.slug}`);
  const path = resolve(root, `${page.slug}-roofing.html`);
  pending.push([path, integrate(await readFile(path, 'utf8'), section({...page, city:city.city, layout:city.layout}))]);
}
const central = {
  slug:'roofing', city:'DFW', layout:'catalog', title:'Commercial roofing, from TPO to complete roof assemblies.',
  intro:'Compare the main roofing families for Dallas–Fort Worth businesses: TPO, PVC, EPDM, modified bitumen, built-up roofing, metal, foam and liquid systems. Start with the building’s roof condition, drainage and use, then identify the product and assembly that belong in the estimate.',
  briefTitle:'A clear scope comes before the product order',
  brief:'Share the building use, existing roof records, interior concerns and any equipment changes. Ask for a roof-area plan that connects those conditions to the proposed repair, restoration or replacement.',
  notes:[
    'For a TPO estimate, identify the membrane line and thickness alongside insulation, cover board and attachment.',
    'For PVC or PVC KEE, document the exact formulation and discuss any exposure from the building’s operation.',
    'For EPDM, compare attachment, seam accessories, access protection and the requested manufacturer program.'
  ]
};
const centralPath = resolve(root, 'roofing.html');
pending.push([centralPath, integrate(await readFile(centralPath,'utf8'), section(central))]);
// The general commercial page links visitors to the complete roofing guide.
const commercialPath = resolve(root, 'commercial.html');
let commercial = await readFile(commercialPath, 'utf8');
const teaser = '<!-- commercial-roofing-link:start --><section class="section"><div class="container"><p class="eyebrow gold">Commercial roof materials</p><h2>TPO, PVC, EPDM &amp; Other Commercial Roof Systems</h2><p>Explore membrane options, asphalt-based systems, metal, coatings and specialty assemblies, with manufacturer references and warranty questions for your property.</p><a class="btn btn-gold" href="roofing.html#commercial-roofing">Explore Commercial Roofing →</a></div></section><!-- commercial-roofing-link:end -->';
const oldTeaser = /<!-- commercial-roofing-link:start -->[\s\S]*?<!-- commercial-roofing-link:end -->/;
if (oldTeaser.test(commercial)) commercial = commercial.replace(oldTeaser, teaser);
else {
  const anchor = '<section class="section trade-overview">';
  if (!commercial.includes(anchor)) throw new Error('Missing commercial overview');
  commercial = commercial.replace(anchor, teaser + '\n' + anchor);
}
pending.push([commercialPath, commercial]);
for (const [path, html] of pending) await writeFile(path, html, 'utf8');
console.log('Built 37 commercial roofing guides and the commercial-page link.');
