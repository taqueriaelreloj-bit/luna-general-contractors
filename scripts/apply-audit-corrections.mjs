import {readFile, writeFile, readdir} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

export const auditAssetVersion = '20261110-page-corrections-1';
export const fenceConcreteSelection = 'Fence-post footings need a project-specific mix, size, placement and curing plan based on the post system, soil and expected loads. Confirm the selected system instructions and site requirements before installation.';
export const fenceConcreteCoverage = 'Confirm the selected mix and post-system documentation. Material strength values do not establish the capacity or service life of an unspecified fence footing.';
export const paintingSelection = 'This reference is for interior surfaces only. Exterior work requires a coating approved for the exposure and substrate. Select sheen, preparation, primer and repair boundaries for the actual surface before ordering.';

// Apply only known audit corrections, preserving authored markup and all imagery.
// This pass is also run after the full site build so legacy templates cannot undo it.
export function correctPage(source, file) {
  let html = source;
  const spanish = /<html\b[^>]*lang=["']es(?:-[^"']*)?["']/i.test(html);
  // Legacy articles repeat their hero summary immediately above the first section.
  html = html.replace(/<p class="seo-article-lead">([^<]+)<\/p>/g, (paragraph, text) =>
    html.includes(`<p>${text}</p>`) ? '' : paragraph);
  html = html.replace(/(<p class="sg-eyebrow">)([^<]+) \/ ([^<]+), Texas(<\/p><h2 id="sg-title">)([^<]+)(<\/h2>)/g,
    (all, open, service, city, middle, title, close) => city === 'Dallas–Fort Worth' ? all : `${open}${service} / ${city}, Texas${middle}${service} in ${city}: planning the work${close}`);
  html = html.replace(/(<p>)For ([^<]+), this guide focuses on ([^<]+)\. Use it to discuss the conditions at your property and compare the proposed work\.<\/p>/g,
    (_, open, context, topic) => `${open}Planning ${context}? ${topic.charAt(0).toUpperCase()+topic.slice(1)}. Use the guidance below to review the proposed work and the conditions at your property.</p>`);

  const guide = html.match(/<div class="sg-brief">([\s\S]*?)<\/div>/)?.[1] || '';
  const guideParagraphs = new Set([...guide.matchAll(/<p>([\s\S]*?)<\/p>/g)].map(m => m[1]));
  html = html.replace(/(<h2>Local [^<]+ Services<\/h2>)((?:\s*<p>[^<]+<\/p>){1,2})/g, (_, heading, paragraphs) =>
    heading + paragraphs.replace(/\s*<p>([^<]+)<\/p>/g, (paragraph, text) => guideParagraphs.has(text) ? '' : paragraph));

  html = html.replace(/<form\b[^>]*>[\s\S]*?<\/form>/g, form => {
    if (!/(?:class="[^"]*\bestimate-form\b|id="estimate-form"|action="https:\/\/formspree\.io\/)/.test(form)) return form;
    form = form.replace(/<input\b[^>]*\bname="phone"[^>]*>/g, input =>
      /\btype=/.test(input) ? input.replace(/\btype="(?:text|tel)"/, 'type="tel"') : input.replace('<input', '<input type="tel"'));
    form = form.replace(/<input\b[^>]*\bname="address"[^>]*>/g, input => input.replace(/\srequired(?:=(?:"[^"]*"|'[^']*'|[^\s>]+))?/g, '').replace('placeholder="Project Address*"', 'placeholder="Project Address (Optional)"'));
    form = form.replace(/(<label(?:\s[^>]*)?>)(Project [Aa]ddress|Dirección del proyecto)(\s*<input)/g,
      (_, open, label, input) => `${open}${label} ${spanish ? '(Opcional)' : '(Optional)'}${input}`);
    if (!/href="privacy\.html(?:#[^"]*)?"/.test(form)) {
      const notice = spanish ? 'Cómo usamos su información y sus fotos: <a href="privacy.html">Aviso de privacidad</a>.' : 'How we use your contact information and photos: <a href="privacy.html">Privacy notice</a>.';
      form = form.replace('</form>', `<small class="form-privacy">${notice}</small></form>`);
    }
    return form;
  });
  // Include the heading when a legacy estimate card is the anchor destination.
  html = html.replace(/<aside\b([^>]*)>([\s\S]*?)<\/aside>/g, (aside, attributes, contents) => {
    if (/\bid=/.test(attributes) || !/<form\b[^>]*\bid="estimate-form"/.test(contents)) return aside;
    const body = contents.replace(/(<form\b[^>]*?)\s+id="estimate-form"/, '$1');
    return `<aside${attributes} id="estimate-form">${body}</aside>`;
  });

  html = html.replaceAll('Water extraction, drying, mold remediation, fire and smoke damage.', 'Water extraction, structural drying and reconstruction of water-damaged areas.')
    .replaceAll('Extracción de agua, secado, reparación por moho y restauración por fuego o humo.', 'Extracción de agua, secado estructural y reconstrucción de áreas dañadas por agua.')
    .replaceAll('coordinated framing, waterproofing and inward drainage', 'coordinated framing, waterproofing and drainage details consistent with the selected waterproofing system')
    .replaceAll('https://www.lpcorp.com/pbs', 'https://www.lpcorp.com/products/siding-trim/product-specifications');
  if (file === 'fencing.html' || file.endsWith('-fencing.html')) {
    html = html.replaceAll('A driveway often uses a specified ready-mix order. Thickness, base, reinforcement, joints, curing and access must be designed for the project; a bag example is not a driveway design.', fenceConcreteSelection)
      .replaceAll('The selected supplier’s material terms apply. Published strength values do not guarantee that an installed slab will never crack.', fenceConcreteCoverage);
  }
  if (file === 'painting.html' || file.endsWith('-painting.html')) {
    html = html.replaceAll('Select sheen, primer where required, color samples and repair boundaries. A paint-and-primer label does not eliminate every separate primer step.', paintingSelection);
  }
  if (file === 'insurance-claims.html') {
    html = html.replaceAll('href="#damage-documentation">View Damage Documentation', 'href="#service-materials">Review Documentation Guidance');
  }
  // Google Maps profile verified on November 10, 2026: 5.0 from 39 reviews.
  html = html.replaceAll('Based on 38 reviews', 'Based on 39 reviews · Checked Nov. 10, 2026')
    .replaceAll('Based on 38 Google reviews', 'Based on 39 Google reviews · Checked Nov. 10, 2026')
    .replaceAll('Basado en 38 reseñas', 'Basado en 39 reseñas · Verificado el 10 de noviembre de 2026')
    .replace(/("reviewCount"\s*:\s*)"38"/g, '$1"39"');
  if (file === 'reviews.html') {
    html = html.replaceAll('Source: Google →', 'Open Google profile →')
      .replaceAll('Source: Yelp →', 'Find Luna on Yelp →')
      .replaceAll('View 5 Yelp reviews →', 'Find Luna reviews on Yelp →')
      .replaceAll('View all Google reviews →', 'Open Google profile and reviews →')
      .replaceAll('Google shows 38 reviews for Luna General Contractors.', 'Google showed 39 reviews for Luna General Contractors when checked on November 10, 2026.')
      .replaceAll('The source button on each card opens the original platform so visitors can verify the current rating and available review text.', 'Google buttons open the business profile; Yelp buttons open a business search. These are platform links, not direct links to individual reviews. Check the platform for the current rating and available review text.');
  }
  html = html.replaceAll('Roof Replacement Cost in Dallas', 'Roof Replacement Cost Factors in Dallas');
  if (file === 'roof-replacement-cost-dallas.html') {
    html = html.replaceAll('Roof Replacement Cost Dallas', 'Roof Replacement in Dallas');
  }
  html = html.replace(/(href="(?:\.\/|\/)?styles\.css)(?:\?[^"<>]*)?"/g, `$1?v=${auditAssetVersion}"`)
    .replace(/(src="(?:\.\/|\/)?script\.js)(?:\?[^"<>]*)?"/g, `$1?v=${auditAssetVersion}"`);
  return html;
}

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const check = process.argv.includes('--check');
  const changed = [];
  for (const file of (await readdir(root)).filter(name => name.endsWith('.html')).sort()) {
    const path = resolve(root, file), before = await readFile(path, 'utf8'), after = correctPage(before, file);
    if (before !== after) {
      changed.push(file);
      if (!check) await writeFile(path, after);
    }
  }
  console.log(JSON.stringify({mode: check ? 'check' : 'apply', changed: changed.length, files: changed}));
  if (check && changed.length) process.exitCode = 1;
}
