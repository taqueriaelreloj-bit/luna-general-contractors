import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import notes from '../content/mitigation-location-notes.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const catalog=JSON.parse(await readFile(resolve(root,'content/mitigation-project-photos.json'),'utf8'));
const guideManifest=JSON.parse(await readFile(resolve(root,'content/service-guide-manifest.json'),'utf8'));
const assignments=guideManifest.filter(a=>a.key==='water-damage-restoration').map(a=>({...a}));
assignments.push({file:'water-damage-insurance-claims-arlington.html',city:'Arlington',index:40,article:true});
const e=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const photoById=new Map(catalog.photos.map(p=>[p.id,p]));
const groups=[
 {id:'site',label:'Site conditions and drying setup',description:'Room views, exposed flooring, perimeter details and drying equipment photographed at the property.'},
 {id:'equipment',label:'Drying equipment identification',description:'Air mover and dehumidifier labels recorded for this project.'},
 {id:'initial',label:'Initial inspection photographs',description:'The initial inspection record is dated October 1, 2026. These images document the instrument displays and inspected material.'},
 {id:'followup',label:'Follow-up moisture checks',description:'The follow-up inspection record is dated October 15, 2026. Meter displays are individual observations; their interpretation depends on the measurement mode, material and project record.'}
];
const card=id=>{const p=photoById.get(id);return `<figure class="mp-card"><a class="mp-image" href="${e(p.src)}" target="_blank" rel="noopener" aria-label="View larger photograph: ${e(p.title)}"><img src="${e(p.src)}" alt="${e(p.alt)}" width="${p.width}" height="${p.height}" loading="lazy" decoding="async"><span aria-hidden="true">View photo ↗</span></a><figcaption><h3>${e(p.title)}</h3><p>${e(p.description)}</p></figcaption></figure>`;};
const selections=a=>{
 if(a.hub)return catalog.photos.map(p=>p.id);
 const n=a.index;
 const selected=[...new Set([[41,43,44,45,46,47][n%6],33+n%10,22+n%11,2+n%16,18+n%4,33+(n+5)%15])];
 if(a.slug==='hurst') selected.push(46); // Add a distinct authentic Arlington room photo to meet the substantive-scene minimum.
 return selected;
};
const start='<!-- mitigation-projects:start -->',end='<!-- mitigation-projects:end -->';
function gallery(a,ids){
 const local=Boolean(a.slug),arlington=a.slug==='arlington';
 const title=arlington?'An Arlington dry-out project, documented in photos':a.hub?'Inside a Luna dry-out project':`Mitigation project photos for ${a.city} property owners`;
 const intro=local?`Luna General Contractors provides water extraction, structural drying and reconstruction in ${a.city}. This photo selection highlights the field documentation behind a mitigation project.`:'Explore the inspection photographs, equipment and exposed conditions recorded during a Luna General Contractors dry-out project.';
 const context=local&&notes[a.slug]?`<p class="mp-context"><strong>For your ${e(a.city)} estimate:</strong> ${e(notes[a.slug].check)}</p>`:'';
 const credit=`<div class="mp-project-credit"><strong>${e(catalog.project.credit)}</strong><p>The documented work covers four bedrooms, the living room and the laundry room. Photos show inspection readings, drying equipment and exposed materials during the project.</p></div>`;
 const body=a.hub?groups.map(g=>{const photos=catalog.photos.filter(p=>p.group===g.id);return `<details class="mp-collection"${g.id==='site'?' open':''}><summary>${g.label} · ${photos.length} photos</summary><p>${g.description}</p><div class="mp-grid">${photos.map(p=>card(p.id)).join('\n')}</div></details>`;}).join('\n'):`<div class="mp-grid ${['','mp-grid--feature','mp-grid--wide'][a.index%3]}">${ids.map(card).join('\n')}</div>`;
 return `${start}\n<section class="mp-gallery" id="mitigation-projects" data-mitigation-projects aria-labelledby="mp-title"><div class="container"><header class="mp-heading"><div><p class="mp-eyebrow">${local?`Luna General Contractors · Mitigation in ${e(a.city)}`:'Luna General Contractors · Project photography'}</p><h2 id="mp-title">${e(title)}</h2></div><p class="mp-intro">${e(intro)}</p></header>${credit}${body}${context}<div class="mp-bottom"><p>${a.hub?'Select a photo to view it at full size.':'Selected photos from the documented Arlington project. Explore all 46 project photos in the complete gallery.'}</p><a href="${a.hub?'arlington-water-damage-restoration.html#estimate-form':'mitigation.html#mitigation-projects'}">${a.hub?'Discuss a mitigation project →':'View all project photos →'}</a></div></div></section>\n${end}`;
}
const output=[];
for(const a of assignments){
 let html=await readFile(resolve(root,a.file),'utf8');
 const ids=selections(a),section=gallery(a,ids);
 // The dedicated, documented gallery supersedes this generic portfolio placeholder.
 html=html.replace(/<figure class="sg-photo shared-project-gallery">[\s\S]*?<\/figure>/,'');
 if(html.includes(start)){const from=html.indexOf(start),to=html.indexOf(end,from);if(to<0)throw new Error(`Unclosed project section: ${a.file}`);html=html.slice(0,from)+section+html.slice(to+end.length);}
 else if(html.includes('<!-- service-guide:end -->'))html=html.replace('<!-- service-guide:end -->','<!-- service-guide:end -->\n'+section);
 else if(html.includes('<section class="local-form'))html=html.replace('<section class="local-form',section+'\n<section class="local-form');
 else html=html.replace('</main>',section+'\n</main>');
 if(!html.includes('mitigation-projects.css'))html=html.replace('</head>','<link rel="stylesheet" href="mitigation-projects.css?v=20261017-photos-1">\n</head>');
 const socialPhoto=photoById.get(a.hub?41:ids[0]);
 html=html.replace(/(<meta property="og:image" content=")[^"]+("\s*\/?\s*>)/,`$1https://lunageneralcontractors.com/${socialPhoto.src}$2`);
 html=html.replace(/(<meta name="twitter:image" content=")[^"]+("\s*\/?\s*>)/,`$1https://lunageneralcontractors.com/${socialPhoto.src}$2`);
 html=html.replace(/(<meta property="og:image:alt" content=")[^"]+("\s*\/?\s*>)/,`$1${e(socialPhoto.alt)}$2`);
 // A project gallery is present, so the generic portfolio script should not insert another one.
 html=html.replace(/script\.js\?v=[^"']+/g,'script.js?v=20261017-mitigation-photos-1');
 await writeFile(resolve(root,a.file),html);
 output.push({file:a.file,city:a.city,projectCity:catalog.project.city,photos:ids});
}
await writeFile(resolve(root,'content/mitigation-photo-pages.json'),JSON.stringify(output,null,2)+'\n');
console.log(`Added documented project photographs to ${output.length} mitigation-related pages.`);
