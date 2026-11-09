import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {removeRepeatedLocalIntro} from '../scripts/local-service-content.mjs';

const planning = 'Review the existing framing and the selected finish before construction.';
const guide = `<!-- service-guide:start --><section><p>${planning}</p></section><!-- service-guide:end -->`;
const local = paragraphs => `<h2>Local Carpentry Services</h2>${paragraphs}<div class="local-grid"><article>Service scope</article></div>`;

test('regenerated guide copy appears only once, while local evidence and FAQ remain', () => {
  const evidence = '<p>The owner has selected a painted finish.</p>';
  const faq = `<details><summary>Planning?</summary><p>${planning}</p></details>`;
  const result = removeRepeatedLocalIntro(guide + local(`<p>${planning}</p>${evidence}`) + faq);
  assert.equal(result, guide + local(evidence) + faq);
  assert.equal(removeRepeatedLocalIntro(result), result);
});

test('pages without an authored guide keep their original introduction', () => {
  const source = local(`<p>${planning}</p>`);
  assert.equal(removeRepeatedLocalIntro(source), source);
});

test('a formerly duplicated Grapevine introduction stays corrected after regeneration', () => {
  const page = readFileSync(new URL('../grapevine-carpentry.html', import.meta.url), 'utf8');
  const match = page.match(/<!-- service-guide:start -->([\s\S]*?)<!-- service-guide:end -->/);
  const paragraphs = [...match[1].matchAll(/<p\b[^>]*>([^<]{100,})<\/p>/g)].slice(0, 2).map(m => `<p>${m[1]}</p>`).join('');
  assert.ok(paragraphs);
  const regenerated = page.replace('<h2>Local Carpentry Services</h2>', '<h2>Local Carpentry Services</h2>' + paragraphs);
  assert.equal(removeRepeatedLocalIntro(regenerated), page);
});
