import {readFile,writeFile,access} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const kitchenArticle=resolve(root,'kitchen-remodeling-ideas-texas.html');
const kitchenHtml=await readFile(kitchenArticle,'utf8');
await writeFile(kitchenArticle,kitchenHtml.replaceAll('assets/flooring/floor-concept-11.jpg','dfw-kitchen-remodel-quartz-island-2018.jpg'));
const repairs={
 'bathroom-vanity-lighting-upgrade-duncanville.html':['dfw-bathroom-remodel-vanity-2020.jpg','bathroom-double-vanity-finished.webp'],
 'custom-tile-tub-shower-cedar-hill.html':['bathroom-subway-tile-tub.webp','bathroom-marble-project-progress.webp','bathroom-marble-shower-tub.webp'],
 'luxury-master-bathroom-remodel-midlothian.html':['bathroom-original-tub-before.jpg','bathroom-waterproofing-progress.jpg','bathroom-marble-project-progress.webp','bathroom-marble-shower-tub.webp','bathroom-double-vanity-finished.webp','dfw-bathroom-remodel-glass-shower-2020.jpg','dfw-bathroom-remodel-finished-2020.jpg','dfw-bathroom-remodel-vanity-2020.jpg','bathroom-luxury-tub-original.webp']
};
for(const [file,replacements] of Object.entries(repairs)){
 let html=await readFile(resolve(root,file),'utf8'),index=0;const mapping=new Map();
 const figures=[...html.matchAll(/<figure>\s*<img src="([^"<>]+)"[\s\S]*?<\/figure>/g)];
 for(const [figure,src] of figures){
  try{await access(resolve(root,src));continue;}catch{}
  const replacement=replacements[index++];if(!replacement)throw new Error(`No replacement ${file} ${src}`);
  await access(resolve(root,replacement));mapping.set(src,replacement);
  html=html.replace(figure,`<figure><img src="${replacement}" alt="Related bathroom work from Luna's DFW portfolio, not attributed to this specific project" width="1188" height="891" loading="lazy" decoding="async"><figcaption>Related DFW portfolio reference. This photograph is not attributed to the project described above.</figcaption></figure>`);
 }
 if(mapping.size){
  html=html.replace('<h2>Project Gallery</h2>','<h2>Related DFW Bathroom Portfolio</h2><p>The original image references for this case study are unavailable. The following existing Luna portfolio photographs illustrate related bathroom work and are not presented as photographs of this specific project.</p>');
  html=html.replace(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g,(block,json)=>{
   let data;try{data=JSON.parse(json);}catch{return block;}
   const walk=v=>{if(typeof v==='string'){for(const [from,to]of mapping)v=v.replace(from,to);return v;}if(Array.isArray(v))return v.map(walk);if(v&&typeof v==='object'){for(const key of Object.keys(v))v[key]=walk(v[key]);if(v['@type']==='ImageObject')v.caption='Related bathroom work from the DFW portfolio; not attributed to this specific project.';}return v;};
   return `<script type="application/ld+json">${JSON.stringify(walk(data))}</script>`;
  });
  await writeFile(resolve(root,file),html);
 }
 console.log(`${file}: repaired ${mapping.size} unavailable photo references`);
}
