#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, '..');
const materialize = process.argv.includes('--materialize');
const manifestArg = process.argv.find(arg => arg.startsWith('--manifest='));
const manifestRelative = manifestArg ? manifestArg.slice('--manifest='.length) : 'content/cloud-approved-images.json';
const unknownArgs = process.argv.slice(2).filter(arg => arg !== '--materialize' && arg !== manifestArg);
if (unknownArgs.length) throw new Error('Unknown argument(s): ' + unknownArgs.join(', '));
if (!manifestRelative || path.isAbsolute(manifestRelative) || manifestRelative.split(/[\\/]/).includes('..')) {
  throw new Error('Manifest must be a repository-relative path.');
}
const manifestPath = path.resolve(root, manifestRelative);
if (!manifestPath.startsWith(root + path.sep)) throw new Error('Manifest escapes repository root.');
const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
const outputDir = path.resolve(root, manifest.destination || '');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function gitBlobSha(buffer) {
  return createHash('sha1')
    .update(Buffer.from('blob ' + buffer.length + '\0', 'utf8'))
    .update(buffer)
    .digest('hex');
}

function sha256(buffer) {
  return createHash('sha256').update(buffer).digest('hex');
}

function pngSize(buffer) {
  const signature = '89504e470d0a1a0a';
  assert(buffer.subarray(0, 8).toString('hex') === signature, 'Expected a PNG signature.');
  assert(buffer.subarray(12, 16).toString('ascii') === 'IHDR', 'Expected a PNG IHDR chunk.');
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

function validateManifest() {
  assert(manifest && manifest.version === 1, 'Manifest must declare version 1.');
  assert(manifest.source === 'GitHub Git Blob API', 'Manifest source must be GitHub Git Blob API.');
  assert(typeof manifest.destination === 'string' && manifest.destination.length > 0, 'Manifest needs a destination.');
  assert(outputDir.startsWith(root + path.sep), 'Manifest destination escapes repository root.');
  assert(Array.isArray(manifest.images) && manifest.images.length > 0, 'Manifest needs at least one image.');
  const names = new Set();
  for (const item of manifest.images) {
    assert(path.basename(item.filename) === item.filename && /^[\w.-]+\.png$/i.test(item.filename), 'Unsafe filename: ' + item.filename);
    assert(!names.has(item.filename), 'Duplicate filename: ' + item.filename);
    names.add(item.filename);
    assert(Number.isSafeInteger(item.bytes) && item.bytes > 0, item.filename + ': invalid byte count.');
    assert(Number.isSafeInteger(item.width) && item.width > 0 && Number.isSafeInteger(item.height) && item.height > 0, item.filename + ': invalid dimensions.');
    assert(/^[a-f0-9]{40}$/i.test(item.blobSha || ''), item.filename + ': invalid Git blob SHA.');
    assert(/^[a-f0-9]{64}$/i.test(item.sha256 || ''), item.filename + ': invalid SHA-256.');
    assert(typeof item.libraryFileId === 'string' && item.libraryFileId.length > 0, item.filename + ': missing Library identity.');
  }
}

function validate(buffer, item, label) {
  assert(buffer.length === item.bytes, label + ': expected ' + item.bytes + ' bytes, received ' + buffer.length + '.');
  assert(gitBlobSha(buffer) === item.blobSha, label + ': Git blob SHA mismatch.');
  assert(sha256(buffer) === item.sha256, label + ': SHA-256 mismatch.');
  const size = pngSize(buffer);
  assert(size.width === item.width && size.height === item.height,
    label + ': expected ' + item.width + 'x' + item.height + ', received ' + size.width + 'x' + size.height + '.');
}

async function download(item) {
  const api = 'https://api.github.com/repos/taqueriaelreloj-bit/luna-general-contractors/git/blobs/' + item.blobSha;
  const response = await fetch(api, {
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'User-Agent': 'luna-approved-image-materializer'
    }
  });
  assert(response.ok, item.filename + ': GitHub Git Blob API returned HTTP ' + response.status + '.');
  const payload = await response.json();
  assert(payload.sha === item.blobSha, item.filename + ': API SHA does not match the manifest.');
  assert(payload.encoding === 'base64', item.filename + ': expected base64 Git Blob payload.');
  return Buffer.from(String(payload.content).replace(/\s/g, ''), 'base64');
}

validateManifest();
await fs.mkdir(outputDir, { recursive: true });
let created = 0;
let verified = 0;
for (const item of manifest.images) {
  const destination = path.join(outputDir, item.filename);
  try {
    validate(await fs.readFile(destination), item, item.filename);
    verified += 1;
    continue;
  } catch (error) {
    if (error?.code !== 'ENOENT') throw error;
  }

  assert(materialize, item.filename + ': missing; rerun with --materialize to use the Git Blob API.');
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
    validate(await fs.readFile(destination), item, item.filename);
  }
  verified += 1;
}

console.log('Verified ' + verified + '/' + manifest.images.length + ' approved cloud PNGs; materialized ' + created + '.');
