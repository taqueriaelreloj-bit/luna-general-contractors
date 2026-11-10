import {readFile, writeFile, readdir} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const stylesheet = '<link rel="stylesheet" href="nextdoor-award.css?v=20261109-1">';
const profile = 'https://nextdoor.com/page/luna-general-contractors-grand-prairie-tx/';

function award(spanish) {
  const title = spanish ? 'Favorito del vecindario 2024' : '2024 Neighborhood Fave';
  const description = spanish ? 'Reconocimiento de nuestros vecinos' : 'Recognized by our neighbors';
  const action = spanish ? 'Ver en Nextdoor →' : 'View on Nextdoor →';
  return `<a class="nextdoor-fave-award" data-nextdoor-fave="2024" href="${profile}" target="_blank" rel="noopener noreferrer">
              <img src="assets/awards/nextdoor-neighborhood-faves-2024.jpg" width="1042" height="1042" alt="Nextdoor Neighborhood Faves 2024" loading="lazy" decoding="async">
              <span class="nextdoor-fave-award__copy"><strong>${title}</strong><span>${description}</span><span class="nextdoor-fave-award__link">${action}</span></span>
            </a>`;
}

let covered = 0;
let updated = 0;
for (const file of (await readdir(root)).filter(file => file.endsWith('.html')).sort()) {
  const path = resolve(root, file);
  const original = await readFile(path, 'utf8');
  let html = original;
  const spanish = /<html\b[^>]*lang=["']es(?:-[^"']*)?["']/i.test(html);
  if (!html.includes('data-nextdoor-fave="2024"')) {
    if (/<div class="reviews-header">/.test(html)) {
      html = html.replace(/<div class="reviews-header">([\s\S]*?)<\/div>/,
        (_, content) => `<div class="reviews-header reviews-header-with-award">
            <div class="reviews-heading">${content}</div>
            ${award(spanish)}
          </div>`);
    } else if (/<div class="rating-summary">/.test(html) && /class="review-hero"/.test(html)) {
      html = html.replace(/<div class="rating-summary">[\s\S]*?<\/div>/,
        rating => `<div class="review-award-summary">${rating}${award(spanish)}</div>`);
    }
  }
  if (!html.includes('data-nextdoor-fave="2024"')) continue;
  covered++;
  if (!html.includes('href="nextdoor-award.css')) html = html.replace('</head>', `${stylesheet}\n</head>`);
  if (html !== original) {
    await writeFile(path, html);
    updated++;
  }
}
console.log(`Nextdoor 2024 award: ${covered} review pages covered; ${updated} pages updated.`);
