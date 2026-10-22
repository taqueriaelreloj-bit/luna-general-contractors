import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const pages=JSON.parse(await readFile(resolve(root,'content/mitigation-illustrations.json'),'utf8'));
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const start='<!-- mi-city-illustrations:start -->';
const end='<!-- mi-city-illustrations:end -->';
const style='<link rel="stylesheet" href="mitigation-illustrations.css?v=20261022-city-1">';

for(const page of pages){
  if(!page.file||!Array.isArray(page.images)||page.images.length===0) throw new Error('Invalid mitigation illustration manifest entry');
  const path=resolve(root,page.file);
  let html=await readFile(path,'utf8');
  const cards=page.images.map(image=>{
    if(!image.path||!image.alt||!image.title||!image.caption) throw new Error('Illustration entry is missing path or accessible copy');
    return `<figure class="mi-card"><img src="${escape(image.path)}" alt="${escape(image.alt)}" width="1536" height="1024" loading="lazy" decoding="async"><figcaption><h3>${escape(image.title)}</h3><p>${escape(image.caption)}</p></figcaption></figure>`;
  }).join('\n');
  const section=`${start}
<section class="mi-section" id="mitigation-illustrations" aria-labelledby="mi-title"><div class="container">
  <header class="mi-heading"><div><p class="mi-eyebrow">Representative service imagery</p><h2 id="mi-title">${escape(page.title)}</h2></div>
  <p class="mi-intro">${escape(page.intro)} These representative scenes illustrate service steps; they are not photos of completed Luna client projects.</p></header>
  <div class="mi-grid">${cards}</div>
</div></section>
${end}`;
  if(html.includes(start)){
    const from=html.indexOf(start),to=html.indexOf(end,from);
    if(to<0) throw new Error(`Unclosed illustration block in ${page.file}`);
    html=html.slice(0,from)+section+html.slice(to+end.length);
  } else {
    const marker='<!-- mitigation-projects:start -->';
    if(!html.includes(marker)) throw new Error(`Missing authentic project gallery marker in ${page.file}`);
    html=html.replace(marker,`${section}\n${marker}`);
  }
  if(!html.includes('mitigation-illustrations.css')) html=html.replace('</head>',`${style}\n</head>`);
  await writeFile(path,html);
}
console.log(`Applied representative mitigation imagery to ${pages.length} pages.`);
