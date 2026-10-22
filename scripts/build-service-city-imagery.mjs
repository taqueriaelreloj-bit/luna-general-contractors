import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import profiles from '../content/service-guide-profiles.mjs';
import serviceMedia,{targetServiceKeys} from '../content/service-guide-media.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const check=process.argv.includes('--check');
const start='<!-- service-city-imagery:start -->';
const end='<!-- service-city-imagery:end -->';
const guideEnd='<!-- service-guide:end -->';
const cssLink='<link rel="stylesheet" href="service-city-imagery.css?v=20261022-city-imagery-1">';
const esc=value=>String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const escapeRegExp=value=>String(value).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');

const generated=JSON.parse(await readFile(resolve(root,'content/service-guide-manifest.json'),'utf8'));
const assignments=generated.filter(item=>item.slug&&!item.hub&&!item.article&&item.key!=='water-damage-restoration');
const assignmentKeys=[...new Set(assignments.map(item=>item.key))].sort();
const expectedKeys=[...targetServiceKeys].sort();
if(assignments.length!==828)throw new Error(`Expected 828 city-service assignments, found ${assignments.length}`);
if(JSON.stringify(assignmentKeys)!==JSON.stringify(expectedKeys))throw new Error('City-service assignments and service-media manifest do not cover the same keys');
if(new Set(assignments.map(item=>item.file)).size!==assignments.length)throw new Error('Duplicate city-service assignment file');

const validateMedia=(key,entry)=>{
 if(!profiles[key])throw new Error(`Missing service profile for media: ${key}`);
 if(!entry||!Array.isArray(entry.items)||entry.items.length<5)throw new Error(`Need five substantive media items for ${key}`);
 const ids=new Set,srcs=new Set;
 for(const item of entry.items){
  if(!item.substantive)throw new Error(`Non-substantive item in ${key}: ${item.id}`);
  if(!['representative-illustration','genuine-portfolio-photo'].includes(item.kind))throw new Error(`Invalid media kind for ${item.id}`);
  if(!item.id||ids.has(item.id))throw new Error(`Duplicate media id for ${key}: ${item.id}`);
  if(!item.src||srcs.has(item.src))throw new Error(`Duplicate or missing media source for ${key}: ${item.src}`);
  if(item.src.startsWith('/')||item.src.includes('..')||!/^([\w-]+\/)*[\w.-]+\.(?:webp|jpe?g|png)$/i.test(item.src))throw new Error(`Unsafe or unsupported media path for ${item.id}: ${item.src}`);
  if(!item.serviceKeys?.includes(key))throw new Error(`Media service allowlist does not include ${key}: ${item.id}`);
  if(!item.alt||!item.caption||!item.attribution||!item.width||!item.height||!Array.isArray(item.sceneTags)||!item.sceneTags.length)throw new Error(`Incomplete media metadata: ${item.id}`);
  if(item.kind==='representative-illustration'&&!/^[a-f0-9]{40}$/i.test(item.sha||''))throw new Error(`Representative illustration needs a Git blob SHA: ${item.id}`);
  if(item.src.endsWith('.svg')||item.src.includes('assets/service-guides/'))throw new Error(`Non-scene asset cannot be substantive: ${item.id}`);
  if(key==='backsplash-installation'&&item.sceneTags.includes('flooring'))throw new Error(`Flooring scene cannot be used for backsplash installation: ${item.id}`);
  ids.add(item.id);srcs.add(item.src);
 }
};
for(const key of expectedKeys)validateMedia(key,serviceMedia[key]);

const card=(item,city)=>{
 const illustration=item.kind==='representative-illustration';
 const kind=illustration?'Representative illustration':'Existing Luna portfolio photograph';
 const scene=illustration?'representative-illustration':'portfolio-photo';
 const disclosure=illustration
  ? `This representative illustration is not a photograph of a Luna job or work completed in ${city}.`
  : `${item.attribution} It is not represented as work completed in ${city}.`;
 return `<figure class="sci-card" data-media-id="${esc(item.id)}" data-media-kind="${esc(item.kind)}"><img src="${esc(item.src)}" alt="${esc(item.alt)}" width="${esc(item.width)}" height="${esc(item.height)}" loading="lazy" decoding="async" data-substantive-scene="${scene}"><figcaption><p class="sci-kind">${kind}</p><p>${esc(item.caption)}</p><p class="sci-disclosure">${esc(disclosure)}</p></figcaption></figure>`;
};
const section=assignment=>{
 const entry=serviceMedia[assignment.key],profile=profiles[assignment.key];
 const insurance=assignment.key==='insurance-claims'
  ? '<p class="sci-claim-note">These visuals do not depict a specific claim, carrier decision, coverage determination, adjustment, or result.</p>'
  : '';
 return `${start}\n<section class="service-city-imagery" data-service-guide-media data-service-key="${esc(assignment.key)}" data-media-count="${entry.items.length}" aria-labelledby="sci-title"><header class="sci-heading"><p class="sci-eyebrow">Service planning imagery</p><h3 id="sci-title">${esc(profile.name)} imagery for ${esc(assignment.city)}</h3><p>These service-appropriate scenes support planning conversations. Representative illustrations are labeled, and genuine portfolio photographs are identified as Dallas-Fort Worth references rather than work in this page's city.</p>${insurance}</header><div class="sci-grid">${entry.items.map(item=>card(item,assignment.city)).join('')}</div></section>\n${end}`;
};
const prepareLegacyPhoto=(html,assignment)=>{
 const entry=serviceMedia[assignment.key],profile=profiles[assignment.key];
 const matcher=new RegExp(`(<figure class="sg-photo shared-project-gallery")(\\s*[^>]*>\\s*<img src="${escapeRegExp(profile.photo)}"[^>]*>[\\s\\S]*?<\\/figure>\\s*)`);
 const found=html.match(matcher);
 const remove=entry.suppressLegacyPhoto||entry.items.some(item=>item.src===profile.photo);
 if(!found){
  if(remove)return html;
  throw new Error(`Missing legacy portfolio photo in ${assignment.file}`);
 }
 if(remove)return html.replace(matcher,'');
 if(found[0].includes('data-substantive-scene="portfolio-photo"'))return html;
 const attributes=` data-service-guide-portfolio="${esc(profile.photo)}" data-substantive-scene="portfolio-photo"`;
 return html.replace(matcher,`${found[1]}${attributes}${found[2]}`);
};
const replaceSection=(html,markup,file)=>{
 const hasStart=html.includes(start),hasEnd=html.includes(end);
 if(hasStart!==hasEnd)throw new Error(`Unpaired city-imagery markers in ${file}`);
 if(hasStart)return html.replace(new RegExp(`${escapeRegExp(start)}[\\s\\S]*?${escapeRegExp(end)}`),markup);
 if(!html.includes(guideEnd))throw new Error(`Missing service-guide marker in ${file}`);
 return html.replace(guideEnd,`${guideEnd}\n${markup}`);
};

const stale=[];
for(const assignment of assignments){
 const path=resolve(root,assignment.file);
 let html=await readFile(path,'utf8');
 html=prepareLegacyPhoto(html,assignment);
 html=replaceSection(html,section(assignment),assignment.file);
 if(!html.includes('service-city-imagery.css')){
  if(!html.includes('</head>'))throw new Error(`Missing head close in ${assignment.file}`);
  html=html.replace('</head>',`${cssLink}\n</head>`);
 }
 if(check){
  const existing=await readFile(path,'utf8');
  if(existing!==html)stale.push(assignment.file);
 }else await writeFile(path,html);
}
if(check&&stale.length)throw new Error(`City-service imagery is stale (${stale.length} files): ${stale.slice(0,8).join(', ')}`);
console.log(`${check?'Verified':'Built'} city-service imagery for ${assignments.length} pages across ${expectedKeys.length} service families`);
