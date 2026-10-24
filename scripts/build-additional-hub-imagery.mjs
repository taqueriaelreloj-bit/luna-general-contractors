#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { access, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import pages from '../content/additional-hub-imagery.mjs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const check = process.argv.includes('--check');
const escapeHtml = value => String(value).replace(/[&<>"']/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[character]));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function imageDimensions(bytes) {
  if(bytes.subarray(0,4).toString()==='RIFF'&&bytes.subarray(8,12).toString()==='WEBP'){
    const kind=bytes.subarray(12,16).toString();
    if(kind==='VP8 '&&bytes.subarray(23,26).toString('hex')==='9d012a')return {width:bytes.readUInt16LE(26)&16383,height:bytes.readUInt16LE(28)&16383};
    if(kind==='VP8X')return {width:1+bytes.readUIntLE(24,3),height:1+bytes.readUIntLE(27,3)};
    if(kind==='VP8L'&&bytes[20]===47){const n=bytes.readUInt32LE(21);return {width:(n&16383)+1,height:((n>>>14)&16383)+1};}
    throw new Error('Unsupported WebP dimensions');
  }
  assert(bytes.subarray(0, 8).toString('hex') === '89504e470d0a1a0a', 'Expected a PNG signature.');
  assert(bytes.subarray(12, 16).toString('ascii') === 'IHDR', 'Expected a PNG IHDR chunk.');
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

function gitBlobSha(bytes) {
  return createHash('sha1')
    .update(Buffer.from(`blob ${bytes.length}\0`, 'utf8'))
    .update(bytes)
    .digest('hex');
}

async function validateImage(image, page) {
  assert(image.file.startsWith('assets/images/illustrations/') && !image.file.includes('..'), `Unsafe path: ${image.file}`);
  assert(image.alt.includes('Dallas-Fort Worth') && image.alt.toLowerCase().includes(page.serviceTerm), `Missing region/service alt context: ${image.file}`);
  assert(image.caption.includes('Dallas-Fort Worth') && image.caption.toLowerCase().includes(page.serviceTerm), `Missing region/service caption context: ${image.file}`);
  const bytes = await readFile(resolve(root, image.file));
  const dimensions = imageDimensions(bytes);
  assert(dimensions.width === image.width && dimensions.height === image.height, `Dimension mismatch: ${image.file}`);
  if (image.sha256) {
    assert(createHash('sha256').update(bytes).digest('hex') === image.sha256, `SHA-256 mismatch: ${image.file}`);
  } else {
    assert(gitBlobSha(bytes) === image.gitBlobSha, `Git blob SHA mismatch: ${image.file}`);
  }
}

function section(page) {
  const start = `<!-- ${page.id}:start -->`;
  const end = `<!-- ${page.id}:end -->`;
  const cards = page.images.map(image => `<figure class="generated-image-card" data-representative-generated-illustration="true"><img src="${escapeHtml(image.file)}" alt="${escapeHtml(image.alt)}" width="${image.width}" height="${image.height}" loading="lazy" decoding="async"><figcaption><h3>${escapeHtml(image.title)}</h3><p>${escapeHtml(page.visibleCaption)}</p></figcaption></figure>`).join('\n');
  return `${start}\n<section class="section generated-image-section" id="${escapeHtml(page.id)}" aria-labelledby="${escapeHtml(page.id)}-title"><div class="container"><header class="generated-image-heading"><div><p class="eyebrow gold">Generated planning illustrations</p><h2 id="${escapeHtml(page.id)}-title">${escapeHtml(page.title)}</h2></div><p>${escapeHtml(page.intro)}</p></header><div class="generated-image-grid">${cards}</div></div></section>\n${end}`;
}

function replaceSection(html, page, markup) {
  const start = `<!-- ${page.id}:start -->`;
  const end = `<!-- ${page.id}:end -->`;
  const hasStart = html.includes(start);
  const hasEnd = html.includes(end);
  assert(hasStart === hasEnd, `Unpaired markers in ${page.file}.`);
  if (hasStart) {
    const matcher = new RegExp(`${start.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[\\s\\S]*?${end.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`);
    return html.replace(matcher, markup);
  }
  const mainEnd = html.lastIndexOf('</main>');
  assert(mainEnd >= 0, `Missing </main> in ${page.file}.`);
  return `${html.slice(0, mainEnd)}\n${markup}\n${html.slice(mainEnd)}`;
}

const stale = [];
for (const page of pages.filter(page => page.file !== 'index.html')) {
  assert(page.intro.includes('Dallas-Fort Worth') && page.intro.toLowerCase().includes(page.serviceTerm), `Missing regional service context: ${page.file}`);
  assert(page.visibleCaption?.includes('Dallas–Fort Worth') && page.visibleCaption.toLowerCase().includes(page.serviceTerm), `Missing concise regional service caption: ${page.file}`);
  assert(page.images.length > 0, `No images configured: ${page.file}`);
  await Promise.all(page.images.map(image => validateImage(image, page)));
  const file = resolve(root, page.file);
  await access(file);
  const html = await readFile(file, 'utf8');
  const next = replaceSection(html, page, section(page));
  if (check) {
    if (next !== html) stale.push(page.file);
  } else {
    await writeFile(file, next);
  }
}

if (check && stale.length) throw new Error(`Additional imagery is stale: ${stale.join(', ')}`);
console.log(`${check ? 'Verified' : 'Built'} additional imagery for ${pages.length} hubs.`);
