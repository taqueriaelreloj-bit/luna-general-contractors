import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import hubs from '../content/service-hub-illustrations.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const start='<!-- service-hub-illustrations:start -->';
const end='<!-- service-hub-illustrations:end -->';
const esc=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const section=hub=>{
 const heading=hub.service+' service illustrations';
 const disclosure=hub.key==='insurance-claims'
  ? 'These are representative planning illustrations, not photos of completed Luna projects. They do not depict a specific insurance claim, carrier decision, coverage approval, or claim result.'
  : 'These representative service illustrations show materials, preparation, work details, and design concepts. They are not photographs of completed Luna client projects.';
 return `${start}\n<section class="service-hub-illustrations" id="service-illustrations" aria-labelledby="shi-title">
 <div class="shi-container"><header class="shi-heading"><p class="shi-eyebrow">Representative service imagery</p><h2 id="shi-title">${esc(heading)}</h2><p>${esc(disclosure)}</p></header>
 <div class="shi-grid">${hub.images.map(image=>`<figure class="shi-card"><img src="${esc(image.file)}" alt="${esc(image.alt)}" width="1536" height="1024" loading="lazy" decoding="async"><figcaption>${esc(image.caption)}</figcaption></figure>`).join('')}
 </div></div></section>\n${end}`;
};
for(const hub of hubs){
 const path=resolve(root,hub.hub);
 let html=await readFile(path,'utf8');
 const block=section(hub);
 if(html.includes(start)&&html.includes(end)){
   html=html.replace(new RegExp(start+'[\\s\\S]*?'+end),block);
 }else{
   const anchor='<!-- service-guide:end -->';
   if(!html.includes(anchor))throw new Error(`Missing service-guide marker in ${hub.hub}`);
   html=html.replace(anchor,anchor+'\n'+block);
 }
 const cssLink='<link rel="stylesheet" href="service-hub-illustrations.css?v=20261022-hubs-1">';
 if(!html.includes('service-hub-illustrations.css')){
   if(!html.includes('</head>'))throw new Error(`Missing head close in ${hub.hub}`);
   html=html.replace('</head>',cssLink+'\n</head>');
 }
 await writeFile(path,html);
 console.log(`Updated ${hub.hub} with ${hub.images.length} representative illustrations`);
}
