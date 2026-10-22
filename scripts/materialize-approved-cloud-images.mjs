#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, '..');
const manifestPath = path.join(root, 'content', 'cloud-approved-images.json');
const materialize = process.argv.includes('--materialize');
const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
const outputDir = path.join(root, manifest.destination);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function blobSha(buffer) {
  return createHash('sha1')
    .update(Buffer.from(`blob ${buffer.length}\0`, 'utf8'))
    .update(buffer)
    .digest('hex');
}

function pngSize(buffer) {
  const signature = '89504e470d0a1a0a';
  assert(buffer.subarray(0, 8).toString('hex') === signature, 'Expected a PNG signature.');
  assert(buffer.subarray(12, 16).toString('ascii') === 'IHDR', 'Expected a PNG IHDR chunk.');
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

function validate(buffer, item, label) {
  assert(buffer.length === item.bytes, `${label}: expected ${item.bytes} bytes, received ${buffer.length}.`);
  assert(blobSha(buffer) === item.blobSha, `${label}: Git blob SHA mismatch.`);
  const size = pngSize(buffer);
  assert(size.width === item.width && size.height === item.height,
    `${label}: expected ${item.width}x${item.height}, received ${size.width}x${size.height}.`);
}

async function download(item) {
  const api = `https://api.github.com/repos/taqueriaelreloj-bit/luna-general-contractors/git/blobs/${item.blobSha}`;
  const response = await fetch(api, {
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'luna-image-materializer'
    }
  });
  assert(response.ok, `${item.filename}: GitHub Git Blob API returned HTTP ${response.status}.`);
  const payload = await response.json();
  assert(payload.sha === item.blobSha, `${item.filename}: API SHA does not match the manifest.`);
  assert(payload.encoding === 'base64', `${item.filename}: expected base64 Git Blob payload.`);
  return Buffer.from(payload.content.replace(/\s/g, ''), 'base64');
}

await fs.mkdir(outputDir, { recursive: true });
let created = 0;
let verified = 0;
for (const item of manifest.images) {
  assert(path.basename(item.filename) === item.filename, `Unsafe filename: ${item.filename}`);
  const destination = path.join(outputDir, item.filename);
  try {
    const existing = await fs.readFile(destination);
    validate(existing, item, item.filename);
    verified += 1;
    continue;
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }

  assert(materialize, `${item.filename}: missing; rerun with --materialize to use the Git Blob API.`);
  const bytes = await download(item);
  validate(bytes, item, item.filename);
  try {
    const handle = await fs.open(destination, 'wx');
    try {
      await handle.writeFile(bytes);
    } finally {
      await handle.close();
    }
    created += 1;
  } catch (error) {
    if (error?.code !== 'EEXIST') throw error;
    const existing = await fs.readFile(destination);
    validate(existing, item, item.filename);
  }
  verified += 1;
}

console.log(`Verified ${verified}/${manifest.images.length} approved cloud PNGs; materialized ${created}.`);
