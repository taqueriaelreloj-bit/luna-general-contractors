import {readFile,writeFile,readdir} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import profiles from '../content/service-guide-profiles.mjs';
import products from '../content/service-products.mjs';
import conditions from '../content/service-project-conditions.mjs';
import mitigationNotes from '../content/mitigation-location-notes.mjs';
import equipmentPhotos from '../content/mitigation-equipment-photos.mjs';
import {replacements as mitigationReplacements, question as mitigationQuestion, answer as mitigationAnswer} from '../content/mitigation-scope.mjs';
import {cityKitchenCardScene,kitchenCardScene} from '../content/city-kitchen-card-scenes.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const check=process.argv.includes('--check');
const onlyArg=process.argv.find(arg=>arg.startsWith('--only='));
const onlyFile=onlyArg?.slice('--only='.length);
const onlyServiceArg=process.argv.find(arg=>arg.startsWith('--only-service='));
const onlyService=onlyServiceArg?.slice('--only-service='.length);
const cardsOnly=process.argv.includes('--cards-only');
const unknownArgs=process.argv.slice(2).filter(arg=>arg!=='--check'&&arg!=='--cards-only'&&arg!==onlyArg&&arg!==onlyServiceArg);
if(unknownArgs.length)throw new Error(`Unknown argument(s): ${unknownArgs.join(', ')}`);
const stale=[];
const normalizeEol=value=>value.replace(/\r\n/g,'\n');
const preserveEol=(existing,content)=>{
 const normalized=normalizeEol(content);
 return existing.includes('\r\n')?normalized.replace(/\n/g,'\r\n'):normalized;
};
const writeGenerated=async(path,content)=>{
 const existing=await readFile(path,'utf8');
 if(check){
  if(normalizeEol(existing)!==normalizeEol(content))stale.push(path);
  return;
 }
 const next=preserveEol(existing,content);
 if(existing!==next)await writeFile(path,next);
};
const e=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cities=await Promise.all((await readdir(resolve(root,'luna_engine/content/cities'))).filter(n=>n.endsWith('.json')).sort().map(async n=>JSON.parse(await readFile(resolve(root,'luna_engine/content/cities',n),'utf8'))));
const files=new Set((await readdir(root)).filter(n=>n.endsWith('.html')));
if(onlyArg&&!onlyFile)throw new Error('The --only option needs an HTML filename.');
if(onlyFile&&!files.has(onlyFile))throw new Error(`Missing selected guide ${onlyFile}`);
if(onlyServiceArg&&!onlyService)throw new Error('The --only-service option needs a service key.');
if(onlyService&&!profiles[onlyService])throw new Error(`Unknown service key for --only-service: ${onlyService}`);
if(cardsOnly&&(!onlyService||onlyFile))throw new Error('The --cards-only option requires exactly one --only-service selection.');
const external=(url,label)=>`<a href="${e(url)}" target="_blank" rel="noopener noreferrer">${e(label)}</a>`;
const start='<!-- service-guide:start -->',end='<!-- service-guide:end -->';
const assignments=[];
for(const [key,profile] of Object.entries(profiles)){
 for(const [index,city] of cities.entries()){
  const file=`${city.slug}-${key}.html`;
  if(!files.has(file))throw new Error(`Missing service page ${file}`);
  assignments.push({file,key,city:city.name,slug:city.slug,index});
 }
 if(profile.hub&&!assignments.some(p=>p.file===profile.hub)) assignments.push({file:profile.hub,key,city:'Dallas–Fort Worth',index:36,hub:true});
}
// Related mitigation articles retain their editorial body and receive the same practical references.
for(const file of ['water-damage-rebuild-process-dallas.html','drywall-repair-after-water-damage-grand-prairie.html','water-damage-cabinet-repair-lewisville.html']){
 if(files.has(file))assignments.push({file,key:'water-damage-restoration',city:'Dallas–Fort Worth',index:37+assignments.filter(x=>x.article).length,article:true});
}
function product(id,key){
 const p=products[id];if(!p)throw new Error(`Missing product ${id}`);
 return key==='water-damage-restoration'?{...p,...equipmentPhotos[id]}:p;
}
const kitchenHubScenes=Object.fromEntries(['cabinet','quartz','tile'].map(id=>{const scene=kitchenCardScene(id,'kitchens.html');return [id,{...scene,alt:'AI-created illustrative concept for Dallas-Fort Worth kitchen remodeling; not an actual project or product photograph.',caption:'Kitchen remodeling services — Dallas–Fort Worth'}];}));
function card(id,a){
 const p=product(id,a.key);
 const scene=(a.hub&&a.key==='kitchen-remodeling'?kitchenHubScenes[id]:null)
  ||(a.slug&&a.key==='kitchen-remodeling'?cityKitchenCardScene(id,a.city,a.index,p.brand):null);
 if(scene&&a.hub&&(!scene.alt.includes(scene.context)||!/Dallas(?:-|–)Fort Worth/.test(scene.caption)||!scene.caption.toLowerCase().includes('kitchen remodeling')))throw new Error(`Kitchen hub scene metadata needs its regional service context: ${id}`);
 if(scene&&a.slug&&(!scene.caption.includes(`${a.city}, Texas`)||!scene.caption.toLowerCase().includes('kitchen remodeling')))throw new Error(`Kitchen city scene metadata needs its service and city context: ${id}`);
 let visual=`<img src="assets/service-guides/${p.art}.svg" alt="Generic illustration of ${e(p.name.toLowerCase())}; not a photograph of the named brand" width="450" height="300" loading="lazy" decoding="async"><figcaption>Original category illustration · Model appearance varies</figcaption>`;
 if(scene)visual=`<img src="${e(scene.src)}" alt="${e(scene.alt)}" width="${scene.width}" height="${scene.height}" loading="lazy" decoding="async"><figcaption>${e(scene.caption)}</figcaption>`;
 if(p.crop){
  const c=p.crop,percent=v=>`${Number((v*100).toFixed(4))}%`;
  const cropStyle=`--photo-width:${percent(p.width/c.width)};--photo-height:${percent(p.height/c.height)};--photo-left:${percent(-c.x/c.width)};--photo-top:${percent(-c.y/c.height)}`;
  visual=`<a class="sg-equipment-window" href="${e(p.src)}" target="_blank" rel="noopener noreferrer" aria-label="View full project photo: ${e(p.name)}" style="${cropStyle}"><img src="${e(p.src)}" alt="${e(p.alt)}" width="${p.width}" height="${p.height}" loading="lazy" decoding="async"><span aria-hidden="true">View full photo ↗</span></a><figcaption>${e(p.caption)}</figcaption>`;
 }
 return `<article class="sg-card${scene?` ${scene.className}`:''}"><figure>${visual}</figure><div class="sg-card-body"><p class="sg-brand">${e(p.brand)}</p><h3>${e(p.name)}</h3><p>${e(p.description)}</p><p class="sg-spec"><strong>Selection check</strong><br>${e(p.selection)}</p><details><summary>Coverage and scope</summary><p>${e(p.coverage)}</p></details><p class="sg-source">${external(p.url,p.linkLabel||'Official reference →')}</p></div></article>`;
}
function guide(a){
 const p=profiles[a.key], ti=a.index%6, ci=Math.floor(a.index/6)%6;
 const topic=(a.key==='water-damage-restoration'&&a.slug?mitigationNotes[a.slug]:null)||p.topics[ti],condition=conditions[ci];
 const title=a.hub?`${p.name}: materials, methods and a clear scope.`:`${topic.title}. ${condition.title}.`;
 const photoIsSpecific=['door-installation','window-replacement','foundation-repair','insurance-claims'].includes(a.key);
 const photoLabel=photoIsSpecific?'Related work from the DFW portfolio':'Luna project reference';
 const photoNote=photoIsSpecific?'This portfolio image illustrates related construction or documentation work. It is not represented as a photograph of a named product, a foundation repair, or work in this page’s city.':'Existing Luna portfolio photograph from Dallas–Fort Worth. It is not a product photograph or a claim that the work was completed in this page’s city.';
 const substantivePhoto=a.slug&&a.key!=='water-damage-restoration'?' data-service-guide-portfolio="'+e(p.photo)+'" data-substantive-scene="portfolio-photo"':'';
 const intro=a.hub?p.intro:`For ${p.name.toLowerCase()} in ${a.city}, this guide focuses on ${topic.title.charAt(0).toLowerCase()+topic.title.slice(1)}. Use it to discuss the conditions at your property and compare the proposed work.`;
 const extra=a.key==='water-damage-restoration'?`<p class="sg-note"><strong>Water extraction, drying and reconstruction by Luna:</strong> Our team performs all three stages. We remove standing water, dry the affected areas with equipment selected for the conditions, and complete the agreed reconstruction after source correction and documented drying. Any required specialist assessment or remediation is identified separately in the scope. Equipment selection and drying duration depend on the property.</p>`:'';
 const process=a.key==='water-damage-restoration'?`<div class="sg-process"><article><span>01</span><h3>Extract the water</h3><p>Luna removes standing water from the affected areas. We review access, the reported source and site conditions to establish the extraction scope and any source-control or specialist work required.</p></article><article><span>02</span><h3>Dry and check moisture</h3><p>We perform structural drying with a plan for air movement, dehumidification and moisture checks suited to the materials and conditions. Readings guide the transition to reconstruction.</p></article><article><span>03</span><h3>Rebuild the affected areas</h3><p>After source correction and documented drying, Luna completes the agreed repairs to affected drywall, ceilings, trim, flooring, cabinets and other finishes. ${e(topic.check)}</p></article></div>`:`<div class="sg-process"><article><span>01</span><h3>Review the existing condition</h3><p>${e(topic.text.split('. ')[0]+'.')} Bring photographs, dimensions and any relevant previous repair records to the discussion.</p></article><article><span>02</span><h3>Define the complete selection</h3><p>Compare ${e(p.products.map(id=>products[id].name.toLowerCase()).join(', '))}. Specify the selected components and the preparation they require.</p></article><article><span>03</span><h3>Agree on the handoff</h3><p>${e(topic.check)} ${e(condition.text.split('. ').slice(-1)[0])}</p></article></div>`;
 const scopeFaq=a.key==='water-damage-restoration'&&!a.slug?`<details><summary>${e(mitigationQuestion)}</summary><p>${e(mitigationAnswer)}</p></details>`:'';
 const primary=a.key==='water-damage-restoration'?`${external('https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home','EPA: moisture and mold guidance')} · ${external('https://www.tdlr.texas.gov/mld/','Texas: mold assessment and remediation')}`:'';
 const mediaDisclosure=a.key==='kitchen-remodeling'?(a.slug?cityKitchenNotice():'<p class="sg-note sg-note--generated-media">Generated planning illustrations shown above are not product photographs or completed-project evidence. Brand names and official links are reference information.</p>'):'';
 const alt=`DFW portfolio reference for ${p.name.toLowerCase()} planning`;
 return `${start}
<section class="service-guide service-guide--${['catalog','editorial','technical','showcase'][a.index%4]}" id="service-materials" aria-labelledby="sg-title"><div class="container">
<header class="sg-heading"><p class="sg-eyebrow">${e(p.name)} / ${e(a.city)}, Texas</p><h2 id="sg-title">${e(title)}</h2><p>${e(intro)}</p></header>
<div class="sg-brief"><article><h3>${e(topic.title)}</h3><p>${e(topic.text)}</p></article><article><h3>${e(condition.title)}</h3><p>${e(condition.text)}</p></article></div>
<h3>${a.key==='water-damage-restoration'?'Equipment from a Luna mitigation project':'Compare the components behind the finished work'}</h3><div class="sg-cards">${p.products.map(id=>card(id,a)).join('\n')}</div>${mediaDisclosure}
${extra}
<figure class="sg-photo shared-project-gallery"${substantivePhoto}><img src="${e(p.photo)}" alt="${e(alt)}" width="1188" height="891" loading="lazy" decoding="async"><figcaption><p class="sg-eyebrow">${photoLabel}</p><h3>${e(topic.check)}</h3><p>${e(photoNote)}</p><a href="projects.html">Explore documented project work →</a></figcaption></figure>
${process}
<div class="sg-faq"><h3>Questions for this project</h3>${scopeFaq}<details><summary>${e(condition.question)}</summary><p>${e(condition.answer)}</p></details><details><summary>What needs to be confirmed before ${e(p.name.toLowerCase())} begins?</summary><p>${e(topic.check)} The written scope should also identify the selected products, work boundaries, required trade coordination and approval steps for changes.</p></details><details><summary>Are the listed manufacturers included in every estimate?</summary><p>No. These are references for comparing product categories. Availability, suitability, the exact model and the actual supplier must be confirmed for the property. A reference does not imply certification, stock or a brand affiliation.</p></details></div>
<p class="sg-note"><strong>Manufacturer coverage:</strong> Terms apply to the exact product and eligible application. Material coverage, complete-system programs and installation workmanship are different obligations. Request the current written warranty and care instructions; a warranty term is not a guaranteed service life.${a.key==='water-damage-restoration'?'':' Generic illustrations are original explanatory artwork, not branded packaging.'}</p>
<div class="sg-references"><strong>Reference library</strong><div class="sg-links">${p.products.map(id=>{const item=product(id,a.key);return external(item.url,item.referenceLabel||item.brand);}).join('')}</div>${primary}</div>
<div class="sg-next"><p><strong>Discuss the conditions at your property.</strong><br>Include the project address, relevant photos and your priorities.</p><a class="btn btn-gold" href="#estimate-form">Request your estimate →</a></div>
</div></section>
${end}`;
}

const matchingElementEnd=(html,startIndex,tag,file)=>{
 const token=new RegExp(`<\\/?${tag}\\b[^>]*>`,'gi');
 token.lastIndex=startIndex;
 let depth=0;
 for(let match=token.exec(html);match;match=token.exec(html)){
  if(match.index<startIndex)continue;
  if(match[0].startsWith('</')){
   if(--depth===0)return token.lastIndex;
  }else depth++;
 }
 throw new Error(`Unclosed ${tag} element in ${file}`);
};

const cityKitchenNoticeStart='<!-- city-kitchen-generated-media:start -->';
const cityKitchenNoticeEnd='<!-- city-kitchen-generated-media:end -->';
const cityKitchenNotice=()=>`${cityKitchenNoticeStart}<p class="sg-note sg-note--generated-media">Generated planning illustrations shown above are not product photographs or completed-project evidence. Brand names and official links are reference information.</p>${cityKitchenNoticeEnd}`;

const replaceCityKitchenCards=(html,a)=>{
 const guideStart=html.indexOf(start),guideEnd=html.indexOf(end,guideStart);
 if(guideStart<0||guideEnd<0)throw new Error(`Missing service-guide markers in ${a.file}`);
 const deckStart=html.indexOf('<div class="sg-cards">',guideStart);
 if(deckStart<0||deckStart>guideEnd)throw new Error(`Missing service-card deck in ${a.file}`);
 const deckEnd=matchingElementEnd(html,deckStart,'div',a.file);
 if(deckEnd>guideEnd)throw new Error(`Service-card deck escapes guide markers in ${a.file}`);
 const deck=`<div class="sg-cards">${profiles[a.key].products.map(id=>card(id,a)).join('\n')}</div>`;
 const noticeStart=html.indexOf(cityKitchenNoticeStart,deckEnd);
 const noticeEnd=noticeStart<0?-1:html.indexOf(cityKitchenNoticeEnd,noticeStart);
 if(noticeStart>=0&&(noticeEnd<0||noticeEnd>guideEnd))throw new Error(`Unclosed city kitchen media notice in ${a.file}`);
 const after=noticeStart>=0?noticeEnd+cityKitchenNoticeEnd.length:deckEnd;
 return html.slice(0,deckStart)+deck+cityKitchenNotice()+html.slice(after);
};

const manifest=[];
const selectedAssignments=onlyFile?assignments.filter(a=>a.file===onlyFile):onlyService?assignments.filter(a=>a.key===onlyService&&a.slug&&!a.article):assignments;
if(onlyFile&&!selectedAssignments.length)throw new Error(`No guide assignment for ${onlyFile}`);
if(onlyService&&!selectedAssignments.length)throw new Error(`No city-service guides for ${onlyService}`);
for(const a of selectedAssignments){
 let html=await readFile(resolve(root,a.file),'utf8');
 if(cardsOnly){
  if(a.key!=='kitchen-remodeling')throw new Error(`Cards-only replacement is limited to kitchen-remodeling: ${a.file}`);
  html=replaceCityKitchenCards(html,a);
 }else{
  const section=guide(a);
  if(html.includes(start)){const from=html.indexOf(start),to=html.indexOf(end,from);if(to<0)throw new Error(`Unclosed guide ${a.file}`);html=html.slice(0,from)+section+html.slice(to+end.length);}
  else if(a.article){html=html.replace(/<section class="local-form/,`${section}\n<section class="local-form`);if(!html.includes(start))html=html.replace('<!-- page-ending:start -->',`${section}\n<!-- page-ending:start -->`);}
  else {
   const main=html.indexOf('<main');const heroEnd=html.indexOf('</section>',main);
   if(main<0||heroEnd<0)throw new Error(`No hero insertion point ${a.file}`);
   html=html.slice(0,heroEnd+10)+'\n'+section+'\n'+html.slice(heroEnd+10);
  }
 }
 if(!cardsOnly){
 const p=profiles[a.key],t=(a.key==='water-damage-restoration'&&a.slug?mitigationNotes[a.slug]:null)||p.topics[a.index%6],c=conditions[Math.floor(a.index/6)%6];
 // Replace only the known old generic introduction; preserve curated case studies and city evidence.
 html=html.replace(/(<h2>Local [^<]+ Services<\/h2>)<p>[^<]+<\/p><p>We evaluate the property, discuss priorities, document the scope and coordinate the work so the project is based on actual site conditions rather than a generic online estimate\.<\/p>/,
 `$1<p>${e(t.text)}</p><p>${e(c.text)}</p>`);
 // Preserve the owner's confirmed service scope after every legacy generation pass.
 if(a.key==='water-damage-restoration'){
  if(!html.includes('mitigation-equipment.css'))html=html.replace('</head>','<link rel="stylesheet" href="mitigation-equipment.css?v=20261017-equipment-1">\n</head>');
  for(const [from,to] of mitigationReplacements) html=html.replaceAll(from,to).replaceAll(e(from),e(to));
  if(!html.includes('<li>Water extraction and removal</li>')) html=html.replace('<li>Water-damage reconstruction</li>','<li>Water extraction and removal</li><li>Structural drying and moisture checks</li><li>Water-damage reconstruction</li>');
 }
 if(a.file==='mitigation.html'){
  html=html.replace('<div><span>✓</span>Mitigation scope review</div>','<div><span>✓</span>Water extraction</div>').replace('<div><span>✓</span>Drying-documentation handoff</div>','<div><span>✓</span>Structural drying</div>').replace('<div><span>✓</span>Reconstruction planning</div>','<div><span>✓</span>Reconstruction and repairs</div>').replace('<div><span>✓</span>Mold remediation</div>','<div><span>✓</span>Specialist remediation requirements</div>');
 }
 if(a.hub&&a.key==='commercial-construction'){
  // Existing commercial-roofing teaser is retained.
 }
 }
 await writeGenerated(resolve(root,a.file),html);
 const p=profiles[a.key],t=(a.key==='water-damage-restoration'&&a.slug?mitigationNotes[a.slug]:null)||p.topics[a.index%6],c=conditions[Math.floor(a.index/6)%6];
 manifest.push({...a,name:p.name,topic:t.title,condition:c.title,layout:['catalog','editorial','technical','showcase'][a.index%4],products:p.products});
}
if(!onlyFile&&!onlyService)await writeGenerated(resolve(root,'content/service-guide-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
if(check&&stale.length)throw new Error(`Service guides are stale (${stale.length} files): ${stale.slice(0,8).join(', ')}`);
console.log(`${check?'Verified':'Built'} ${selectedAssignments.length}${onlyFile?` selected guide (${onlyFile})`:onlyService?` selected ${onlyService} guides`:` guides across ${Object.keys(profiles).length} service categories`}${cardsOnly?' (cards only)':''}`);
