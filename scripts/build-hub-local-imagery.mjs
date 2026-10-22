import { createHash } from 'node:crypto';
import { access, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import hubs from '../content/hub-local-imagery.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const check = process.argv.includes('--check');
const onlyArg = process.argv.find(arg => arg.startsWith('--only='));
const only = onlyArg?.slice('--only='.length);
const escapeHtml = value => String(value).replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));

if (onlyArg && !only) throw new Error('The --only option needs a hub key.');
const selected = only ? hubs.filter(hub => hub.key === only) : hubs;
if (!selected.length) throw new Error(`Unknown hub key: ${only}`);

function pngDimensions(bytes) {
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (bytes.length < 24 || !bytes.subarray(0, 8).equals(signature) || bytes.readUInt32BE(8) !== 13 || bytes.subarray(12, 16).toString('ascii') !== 'IHDR') throw new Error('Expected a valid PNG header.');
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

function gitBlobSha(bytes) {
  return createHash('sha1')
    .update(Buffer.from(`blob ${bytes.length}\0`, 'utf8'))
    .update(bytes)
    .digest('hex');
}

async function validateImage(image, hub) {
  if (!hub.context || !hub.serviceTerm || !hub.intro.includes(hub.context) || !hub.intro.includes(hub.serviceTerm)) throw new Error(`Missing regional service context for ${hub.key}.`);
  if (!image.alt.includes(hub.context) || !image.alt.includes(hub.serviceTerm) || !image.caption.includes(hub.context) || !image.caption.includes(hub.serviceTerm)) throw new Error(`Image descriptions need the regional service context for ${image.file}.`);
  if (!image.file.startsWith('assets/images/illustrations/') || image.file.includes('..')) throw new Error(`Unsafe image path for ${hub.key}.`);
  const path = resolve(root, image.file);
  await access(path);
  const bytes = await readFile(path);
  const dimensions = pngDimensions(bytes);
  if (dimensions.width !== image.width || dimensions.height !== image.height) throw new Error(`Dimension mismatch for ${image.file}: expected ${image.width}x${image.height}, got ${dimensions.width}x${dimensions.height}.`);
  if (image.sha256) {
    const hash = createHash('sha256').update(bytes).digest('hex');
    if (hash !== image.sha256) throw new Error(`SHA-256 mismatch for ${image.file}.`);
  } else if (image.gitBlobSha) {
    if (gitBlobSha(bytes) !== image.gitBlobSha) throw new Error(`Git blob SHA mismatch for ${image.file}.`);
  } else {
    throw new Error(`Missing image integrity hash for ${image.file}.`);
  }
}

function section(hub) {
  const cards = hub.images.map(image => `<figure class="mi-card${image.className ? ` ${image.className}` : ''}" data-representative-generated-illustration="true"><img src="${escapeHtml(image.file)}" alt="${escapeHtml(image.alt)}" width="${image.width}" height="${image.height}" loading="lazy" decoding="async"><figcaption><h3>${escapeHtml(image.title)}</h3><p>${escapeHtml(image.caption)}</p></figcaption></figure>`).join('\n');
  return `${hub.start}\n<section class="mi-section" id="${escapeHtml(hub.sectionId)}" aria-labelledby="${escapeHtml(hub.key)}-imagery-title"><div class="container">\n  <header class="mi-heading"><div><p class="mi-eyebrow">${escapeHtml(hub.eyebrow)}</p><h2 id="${escapeHtml(hub.key)}-imagery-title">${escapeHtml(hub.title)}</h2></div>\n  <p class="mi-intro">${escapeHtml(hub.intro)}</p></header>\n  <div class="mi-grid">${cards}</div>\n</div></section>\n${hub.end}`;
}

function replaceSection(html, hub, markup) {
  const hasStart = html.includes(hub.start);
  const hasEnd = html.includes(hub.end);
  if (hasStart !== hasEnd) throw new Error(`Unpaired markers in ${hub.file}.`);
  if (hasStart) return html.replace(new RegExp(`${hub.start.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\s\\S]*?${hub.end.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`), markup);
  const legacyStart = html.indexOf(`<section class="mi-section" id="${hub.sectionId}"`);
  if (legacyStart < 0) throw new Error(`Missing ${hub.sectionId} section in ${hub.file}.`);
  const legacyEnd = html.indexOf('</section>', legacyStart);
  if (legacyEnd < 0) throw new Error(`Unclosed ${hub.sectionId} section in ${hub.file}.`);
  return html.slice(0, legacyStart) + markup + html.slice(legacyEnd + '</section>'.length);
}

const stale = [];
for (const hub of selected) {
  if (!Array.isArray(hub.images) || hub.images.length < 5) throw new Error(`${hub.key} needs at least five images.`);
  await Promise.all(hub.images.map(image => validateImage(image, hub)));
  const pagePath = resolve(root, hub.file);
  let html = await readFile(pagePath, 'utf8');
  if (!html.includes('mitigation-illustrations.css')) throw new Error(`Missing responsive imagery stylesheet in ${hub.file}.`);
  const next = replaceSection(html, hub, section(hub));
  if (check) {
    if (next !== html) stale.push(hub.file);
  } else {
    await writeFile(pagePath, next);
  }
}
if (check && stale.length) throw new Error(`Hub imagery is stale: ${stale.join(', ')}`);
console.log(`${check ? 'Verified' : 'Built'} local imagery for ${selected.map(hub => hub.key).join(', ')}.`);
