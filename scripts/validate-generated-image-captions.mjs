#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const pages = [
  ['index.html', 'General contracting services — Dallas–Fort Worth', 2],
  ['kitchens.html', 'Kitchen remodeling services — Dallas–Fort Worth', 4],
  ['bathrooms.html', 'Bathroom remodeling services — Dallas–Fort Worth', 1],
  ['carpentry.html', 'Carpentry services — Dallas–Fort Worth', 3],
  ['painting.html', 'Interior painting services — Dallas–Fort Worth', 1],
  ['siding.html', 'Siding services — Dallas–Fort Worth', 1],
  ['fencing.html', 'Fencing services — Dallas–Fort Worth', 1],
  ['roofing.html', 'Roofing services — Dallas–Fort Worth', 10],
  ['mitigation.html', 'Water damage mitigation — Dallas–Fort Worth', 20]
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function generatedCardCaptions(html) {
  return [...html.matchAll(/<figure\b[^>]*\bdata-representative-generated-illustration="true"[^>]*>[\s\S]*?<figcaption><h3>[^<]+<\/h3><p>([^<]+)<\/p><\/figcaption><\/figure>/g)].map(match => match[1]);
}

let totalCards = 0;
for (const [file, caption, expectedCount] of pages) {
  const html = await readFile(resolve(root, file), 'utf8');
  const captions = generatedCardCaptions(html);
  assert(captions.length === expectedCount, `${file}: expected ${expectedCount} generated card captions, got ${captions.length}.`);
  assert(captions.every(value => value === caption), `${file}: generated card caption does not match the concise service-and-region label.`);
  assert(!captions.some(value => /representative|not a Luna|product photograph|evidence of work/i.test(value)), `${file}: an old disclaimer remains in a generated card caption.`);
  assert(html.includes('Generated planning illustrations'), `${file}: missing section-level generated-image notice.`);
  totalCards += captions.length;
}

const home = await readFile(resolve(root, 'index.html'), 'utf8');
assert(home.includes('<p class="hero-image-disclosure">General contractor services — Dallas–Fort Worth</p>'), 'index.html: hero caption is not concise service-and-region copy.');
assert(home.includes('alt="Generated illustration of a broad residential property for Dallas-Fort Worth general contractor services."'), 'index.html: hero alt is missing generated-image provenance.');

const kitchens = await readFile(resolve(root, 'kitchens.html'), 'utf8');
const kitchenSceneCaptions = [...kitchens.matchAll(/<article class="sg-card[^>]*\bsg-card--scene-[^"]*"[^>]*>[\s\S]*?<figcaption>([^<]+)<\/figcaption>/g)].map(match => match[1]);
assert(kitchenSceneCaptions.length === 3, `kitchens.html: expected three generated service-guide cards, got ${kitchenSceneCaptions.length}.`);
assert(kitchenSceneCaptions.every(value => value === 'Kitchen remodeling services — Dallas–Fort Worth'), 'kitchens.html: service-guide card captions are not concise kitchen-and-region copy.');
assert(kitchens.includes('Generated planning illustrations shown above are not product photographs or completed-project evidence.'), 'kitchens.html: missing the one-time kitchen generated-image disclosure.');
assert(kitchens.includes('<figure class="sg-photo shared-project-gallery"><img src="dfw-kitchen-remodel-quartz-island-2018.jpg"') && kitchens.includes('<p class="sg-eyebrow">Luna project reference</p>'), 'kitchens.html: genuine portfolio-photo provenance was removed.');

assert(totalCards === 43, `Expected 43 generated card captions across the nine release pages, got ${totalCards}.`);
console.log(`Validated ${totalCards + kitchenSceneCaptions.length + 1} concise generated-image captions across nine release pages.`);
