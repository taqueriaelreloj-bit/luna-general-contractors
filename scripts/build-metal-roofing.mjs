import { readFile, writeFile, access } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import pages from '../content/metal-roofing-pages.mjs';
import cityPages from '../content/roofing-product-pages.mjs';
import systems from '../content/metal-roofing-systems.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sources = JSON.parse(await readFile(resolve(root, 'assets/metal-roofing/sources.json'), 'utf8'));
const start = '<!-- metal-roofing:start -->';
const end = '<!-- metal-roofing:end -->';
const version = '20261016-metal-1';
const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const external = (url, text) => `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(text)}</a>`;
const imageText = {
  'standing-seam-profile': ['Wikideas1', 'Standing-seam roof profile', 'Dark standing-seam roof on a low-rise building, showing long panel runs'],
  'green-ribbed-roof': ['Wikideas1', 'Ribbed panels in a colored finish', 'Green ribbed metal roofing on connected gabled roof sections'],
  'standing-seam-closeup': ['Wikideas1', 'A closer look at the roof edge', 'Burgundy standing-seam metal panels at an eave above a gutter'],
  'standing-seam-house': ['Doug Oliver Development', 'Metal across gables and porches', 'Light-colored house with silver standing-seam metal roofing over gables and porches'],
  'exposed-fasteners': ['ralmonline alm', 'Visible fasteners on a ribbed roof', 'Installation reference showing silver ribbed metal panels with visible screw heads']
};

function photo(id, role) {
  const source = sources.find(item => item.id === id);
  const [author, title, alt] = imageText[id];
  const shape = source.width / source.height > 3 ? 'panorama' : source.height > source.width ? 'portrait' : 'landscape';
  return `<figure class="mr-photo mr-photo--${shape} mr-photo--${role}">
  <div class="mr-image"><img src="${escape(source.file)}" alt="${escape(alt)}" width="${source.width}" height="${source.height}" loading="lazy" decoding="async"></div>
  <figcaption><strong>${escape(title)}</strong><span>Reference photo · ${escape(author)} · ${external(source.source, 'Source')} · ${external(source.licenseUrl, source.license)}</span></figcaption>
</figure>`;
}

function systemCard(system, i) {
  return `<article class="mr-system" aria-labelledby="mr-system-${system.id}">
  <div class="mr-system-top"><span class="mr-number">0${i + 1}</span><p class="mr-label">${escape(system.label)}</p></div>
  <h4 id="mr-system-${system.id}">${escape(system.name)}</h4>
  <p class="mr-model">Product reference: <strong>${escape(system.model)}</strong></p>
  <p>${escape(system.description)}</p>
  <p class="mr-consideration">${escape(system.consideration)}</p>
  <div class="mr-links">${external(system.productUrl, 'Official product details ↗')}${external(system.warrantyUrl, 'Manufacturer warranty ↗')}</div>
</article>`;
}

function section(page) {
  const primary = sources.find(item => item.id === page.photo);
  const panoramic = primary.width / primary.height > 3;
  const cta = page.slug === 'roofing' ? 'index.html#estimate-form' : '#estimate-form';
  return `${start}
<section class="metal-roofing metal-roofing--${escape(page.layout)}" id="metal-roofing" aria-labelledby="mr-heading">
  <header class="mr-header"><p class="mr-eyebrow">Metal roofing / ${escape(page.city)}, Texas</p><h2 id="mr-heading">${escape(page.title)}</h2><p class="mr-intro">${escape(page.intro)}</p></header>
  <div class="mr-story${panoramic ? ' mr-story--panorama' : ''}">
    ${photo(page.photo, 'primary')}
    <div class="mr-focus"><p class="mr-label">Your project, in focus</p><h3>${escape(page.focus)}</h3><p>${escape(page.detail)}</p><ol>${page.points.map(point => `<li>${escape(point)}</li>`).join('')}</ol></div>
  </div>
  <div class="mr-catalog-heading"><div><p class="mr-eyebrow">Compare the construction</p><h3>Three metal-roof directions</h3></div><p>Use these manufacturer references to identify the profile and assembly you want to discuss.</p></div>
  <div class="mr-systems">${systems.map(systemCard).join('\n')}</div>
  <div class="mr-detail-row">${photo(page.secondary, 'detail')}<aside class="mr-warranty"><h3>Get the metal warranty in writing</h3><p>Coating, base-metal and weathertightness coverage can have different terms. Ask for the current manufacturer document for the exact product, plus any component, installation, registration or installer requirements.</p><p>Keep manufacturer coverage separate from the contractor’s workmanship terms. Asphalt-shingle warranty terms do not describe a metal system.</p></aside></div>
  <p class="mr-photo-note">Photos illustrate metal-roof appearances and details; they are not identified as Luna projects or as the named manufacturers’ products. Images are displayed proportionally from the credited originals or Wikimedia thumbnails.</p>
  <div class="mr-next"><div><strong>Bring your metal-roof idea to the estimate.</strong><p>Share the roof area, preferred profile and any photos of the existing condition.</p></div><a class="btn btn-gold" href="${cta}">Discuss metal roofing →</a></div>
</section>
${end}`;
}

function integrate(html, content) {
  const navigation = '<!-- roofing-material-nav:start --><nav class="roofing-material-nav" aria-label="Roof material guides"><strong>Explore roofing materials</strong><a href="#roof-products">Asphalt shingles</a><a href="#metal-roofing">Metal roofing ↓</a></nav><!-- roofing-material-nav:end -->';
  const oldNavigation = /<!-- roofing-material-nav:start -->[\s\S]*?<!-- roofing-material-nav:end -->/;
  if (oldNavigation.test(html)) html = html.replace(oldNavigation, navigation);
  else html = html.replace('<!-- roofing-products:start -->', navigation + '\n<!-- roofing-products:start -->');
  const begin = html.indexOf(start);
  if (begin >= 0) {
    const finish = html.indexOf(end, begin);
    if (finish < 0) throw new Error('Incomplete metal-roofing section marker');
    html = html.slice(0, begin) + content + html.slice(finish + end.length);
  } else {
    const anchor = '<!-- roofing-products:end -->';
    if (!html.includes(anchor)) throw new Error('Build the shingle product section first');
    html = html.replace(anchor, anchor + '\n' + content);
  }
  html = html.replace(/\s*<link rel="stylesheet" href="\/?metal-roofing\.css(?:\?[^"<>]*)?">/g, '');
  return html.replace('</head>', `  <link rel="stylesheet" href="metal-roofing.css?v=${version}">\n</head>`);
}

// Validate editorial inputs and prepare every page before writing any output.
if (pages.length !== 36 || new Set(pages.map(page => page.slug)).size !== 36) throw new Error('Expected 36 distinct cities');
for (const key of ['title', 'intro', 'focus', 'detail']) {
  if (new Set(pages.map(page => page[key])).size !== pages.length) throw new Error(`Repeated city ${key}`);
}
if (new Set(pages.flatMap(page => page.points)).size !== 108) throw new Error('Expected 108 distinct city comparison points');
for (const source of sources) {
  if (!['CC0', 'CC BY 2.0'].includes(source.license)) throw new Error(`Unreviewed license: ${source.id}`);
  await access(resolve(root, source.file));
}
const prepared = [];
for (const page of pages) {
  const city = cityPages.find(item => item.slug === page.slug);
  if (!city || page.points.length !== 3 || !imageText[page.photo] || !imageText[page.secondary]) throw new Error(`Incomplete input: ${page.slug}`);
  const path = resolve(root, `${page.slug}-roofing.html`);
  prepared.push([path, integrate(await readFile(path, 'utf8'), section({...page, city: city.city, layout: city.layout}))]);
}
const mainPage = {
  slug: 'roofing', city: 'DFW', layout: 'catalog',
  title: 'Metal roofing: see the profile, understand the system',
  intro: 'Standing seams, exposed-fastener panels and stone-coated steel offer different appearances and construction details. Start with the roof slope, support and transitions; then compare the exact manufacturer, model and finish for your Dallas–Fort Worth property.',
  focus: 'Build the comparison around the whole roof',
  detail: 'A metal-roof estimate should describe what supports the panels, how they attach and how water is handled at edges and penetrations. Review the covering alongside deck preparation, underlayment, flashing and accessories so the finished price corresponds to a defined assembly.',
  points: ['Name the panel profile, metal substrate, gauge and finish.', 'Match slope and attachment requirements to the selected product.', 'Review manufacturer coverage and workmanship terms separately.'],
  photo: 'standing-seam-house', secondary: 'standing-seam-closeup'
};
const main = resolve(root, 'roofing.html');
prepared.push([main, integrate(await readFile(main, 'utf8'), section(mainPage))]);
for (const [path, html] of prepared) await writeFile(path, html, 'utf8');
console.log(`Added metal-roofing references to ${prepared.length} pages.`);
