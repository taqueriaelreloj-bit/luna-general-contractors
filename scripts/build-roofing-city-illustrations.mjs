import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import pages from '../content/roofing-city-illustrations.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const start = '<!-- roofing-city-illustrations:start -->';
const end = '<!-- roofing-city-illustrations:end -->';
const escapeHtml = value => String(value).replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[character]));

function section(page) {
  const heading = escapeHtml(page.heading || 'Metal and TPO roofing options');
  const disclosure = escapeHtml(page.disclosure || `These representative illustrations show two roofing system types that may be considered for properties in ${page.city}. They are not photographs of completed Luna projects in this city.`);
  const cards = page.images.map(image => `<figure class="rcy-card"><img src="${escapeHtml(image.file)}" alt="${escapeHtml(image.alt)}" width="1536" height="1024" loading="lazy" decoding="async"><figcaption><strong>${escapeHtml(image.title)}</strong><span>${escapeHtml(image.caption)}</span></figcaption></figure>`).join('\n');
  return `${start}
<section class="roofing-city-illustrations" id="roofing-city-illustrations" aria-labelledby="rcy-title-${page.slug}"><header class="rcy-header"><p class="rcy-eyebrow">Roofing system examples</p><h2 id="rcy-title-${page.slug}">${heading}</h2><p>${disclosure}</p></header><div class="rcy-grid">
${cards}
</div></section>
${end}`;
}

for (const page of pages) {
  const path = resolve(root, page.file || `${page.slug}-roofing.html`);
  let html = await readFile(path, 'utf8');
  const block = section(page);
  const startIndex = html.indexOf(start);
  const endIndex = html.indexOf(end);
  if (startIndex >= 0 && endIndex >= startIndex) {
    html = html.slice(0, startIndex) + block + html.slice(endIndex + end.length);
  } else {
    const anchor = '<!-- commercial-roofing:end -->';
    const anchorIndex = html.indexOf(anchor);
    if (anchorIndex < 0) throw new Error(`Missing commercial roofing marker: ${page.slug}`);
    html = html.slice(0, anchorIndex + anchor.length) + '\n' + block + html.slice(anchorIndex + anchor.length);
  }
  if (!html.includes('roofing-city-illustrations.css')) {
    if (!html.includes('</head>')) throw new Error(`Missing head close: ${page.slug}`);
    html = html.replace('</head>', '  <link rel="stylesheet" href="roofing-city-illustrations.css?v=20261022-city-1">\n</head>');
  }
  await writeFile(path, html, 'utf8');
}
console.log(`Built representative roof system sections for ${pages.length} city pages.`);
