import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import profiles from '../content/service-guide-profiles.mjs';
import serviceMedia,{cityGuideCaption,targetServiceKeys} from '../content/service-guide-media.mjs';
import pageOwnedCityMedia from '../content/page-owned-city-media.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const check=process.argv.includes('--check');
const cityContext=process.argv.includes('--city-context');
const onlyServiceArg=process.argv.find(arg=>arg.startsWith('--only-service='));
const onlyService=onlyServiceArg?.slice('--only-service='.length);
const onlyPageArg=process.argv.find(arg=>arg.startsWith('--only='));
const onlyPage=onlyPageArg?.slice('--only='.length);
const unknownArgs=process.argv.slice(2).filter(arg=>arg!=='--check'&&arg!=='--city-context'&&arg!==onlyServiceArg&&arg!==onlyPageArg);
if(unknownArgs.length)throw new Error(`Unknown argument(s): ${unknownArgs.join(', ')}`);
if(onlyServiceArg&&!onlyService)throw new Error('The --only-service option needs a service key.');
if(onlyPageArg&&!onlyPage)throw new Error('The --only option needs one city-service filename.');
if(onlyPage&&onlyService)throw new Error('Use either --only or --only-service, not both.');
if(cityContext&&!onlyService&&!onlyPage)throw new Error('The --city-context option requires --only-service or --only to prevent a broad city-page rewrite.');
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
if(onlyService&&!expectedKeys.includes(onlyService))throw new Error(`Unknown service key for --only-service: ${onlyService}`);
if(onlyPage&&!pageOwnedCityMedia[onlyPage])throw new Error(`The --only page has no declared page-owned media override: ${onlyPage}`);
const selectedAssignments=onlyPage
 ? assignments.filter(assignment=>assignment.file===onlyPage)
 : onlyService?assignments.filter(assignment=>assignment.key===onlyService):assignments;
if(!selectedAssignments.length)throw new Error(`No city-service assignments for ${onlyPage||onlyService||'the requested selection'}`);
const normalizeEol=value=>value.replace(/\r\n/g,'\n');
const preserveEol=(existing,content)=>{
 const normalized=normalizeEol(content);
 return existing.includes('\r\n')?normalized.replace(/\n/g,'\r\n'):normalized;
};

const validateMedia=(key,entry,context=key)=>{
 if(!profiles[key])throw new Error(`Missing service profile for media: ${key}`);
 if(!entry||!Array.isArray(entry.items)||entry.items.length<5)throw new Error(`Need five substantive media items for ${context}`);
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
const pageOwnedGeneratedSources=new Map;
for(const [file,entry] of Object.entries(pageOwnedCityMedia)){
 const assignment=assignments.find(item=>item.file===file);
 if(!assignment)throw new Error(`Page-owned media override is not a city-service page: ${file}`);
 if(entry?.serviceKey&&entry.serviceKey!==assignment.key)throw new Error(`Page-owned media service mismatch for ${file}`);
 if(entry?.pageOwned!==true)throw new Error(`Page-owned media override must declare pageOwned: true for ${file}`);
 validateMedia(assignment.key,entry,file);
 for(const item of entry.items){
  if(item.kind!=='representative-illustration')continue;
  const owner=pageOwnedGeneratedSources.get(item.src);
  if(owner&&owner!==file)throw new Error(`Page-owned generated scene is assigned to more than one page: ${item.src}`);
  pageOwnedGeneratedSources.set(item.src,file);
 }
}
const mediaFor=assignment=>pageOwnedCityMedia[assignment.file]||serviceMedia[assignment.key];

const card=(item,serviceName,city,useCityContext)=>{
 const illustration=item.kind==='representative-illustration';
 const kind=illustration?'Representative illustration':'Existing Luna portfolio photograph';
 const scene=illustration?'representative-illustration':'portfolio-photo';
 if(useCityContext){
  const credit=illustration?'':`<p class="sci-credit">${esc(item.attribution)}</p>`;
  return `<figure class="sci-card" data-media-id="${esc(item.id)}" data-media-kind="${esc(item.kind)}"><img src="${esc(item.src)}" alt="${esc(item.alt)}" width="${esc(item.width)}" height="${esc(item.height)}" loading="lazy" decoding="async" data-substantive-scene="${scene}"><figcaption><p class="sci-caption" data-caption-context="service-city">${esc(item.displayCaption||cityGuideCaption(serviceName,city))}</p>${credit}</figcaption></figure>`;
 }
 const disclosure=illustration
  ? `This representative illustration is not a photograph of a Luna job or work completed in ${city}.`
  : `${item.attribution} It is not represented as work completed in ${city}.`;
 return `<figure class="sci-card" data-media-id="${esc(item.id)}" data-media-kind="${esc(item.kind)}"><img src="${esc(item.src)}" alt="${esc(item.alt)}" width="${esc(item.width)}" height="${esc(item.height)}" loading="lazy" decoding="async" data-substantive-scene="${scene}"><figcaption><p class="sci-kind">${kind}</p><p>${esc(item.caption)}</p><p class="sci-disclosure">${esc(disclosure)}</p></figcaption></figure>`;
};
const section=(assignment,entry,useCityContext)=>{
 const profile=profiles[assignment.key],pageOwned=entry.pageOwned===true;
 const insurance=assignment.key==='insurance-claims'
  ? '<p class="sci-claim-note">These visuals do not depict a specific claim, carrier decision, coverage determination, adjustment, or result.</p>'
  : '';
 const notice=useCityContext&&pageOwned&&entry.suppressVisibleGeneratedNotice
  ? ''
  : useCityContext
  ? '<p class="sci-disclosure" data-generated-section-notice="true">Generated planning illustrations in this section are not project photographs or product photographs. Existing Luna portfolio photographs are identified as Dallas-Fort Worth references, not work in this page’s city.</p>'
  : '<p>These service-appropriate scenes support planning conversations. Representative illustrations are labeled, and genuine portfolio photographs are identified as Dallas-Fort Worth references rather than work in this page\'s city.</p>';
 const pageOwnedAttr=pageOwned?' data-page-owned-city-media="true"':'';
 return `${start}\n<section class="service-city-imagery" data-service-guide-media data-service-key="${esc(assignment.key)}" data-media-count="${entry.items.length}"${pageOwnedAttr} aria-labelledby="sci-title"><header class="sci-heading"><p class="sci-eyebrow">Service planning imagery</p><h3 id="sci-title">${esc(profile.name)} imagery for ${esc(assignment.city)}</h3>${notice}${insurance}</header><div class="sci-grid">${entry.items.map(item=>card(item,profile.name,assignment.city,useCityContext)).join('')}</div></section>\n${end}`;
};
const prepareLegacyPhoto=(html,assignment,entry)=>{
 const profile=profiles[assignment.key];
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
for(const assignment of selectedAssignments){
 const path=resolve(root,assignment.file);
 let html=await readFile(path,'utf8');
  const entry=mediaFor(assignment);
 const preserveCityContext=html.includes('data-caption-context="service-city"')||html.includes('data-generated-section-notice="true"');
  const useCityContext=cityContext||entry.pageOwned===true||preserveCityContext;
  html=prepareLegacyPhoto(html,assignment,entry);
  html=replaceSection(html,section(assignment,entry,useCityContext),assignment.file);
 if(!html.includes('service-city-imagery.css')){
  if(!html.includes('</head>'))throw new Error(`Missing head close in ${assignment.file}`);
  html=html.replace('</head>',`${cssLink}\n</head>`);
 }
 const existing=await readFile(path,'utf8');
 if(check){
  if(normalizeEol(existing)!==normalizeEol(html))stale.push(assignment.file);
 }else{
  const next=preserveEol(existing,html);
  if(existing!==next)await writeFile(path,next);
 }
}
if(check&&stale.length)throw new Error(`City-service imagery is stale (${stale.length} files): ${stale.slice(0,8).join(', ')}`);
const selection=onlyPage?onlyPage:onlyService?onlyService:'all services';
console.log(`${check?'Verified':'Built'} city-service imagery for ${selectedAssignments.length} page${selectedAssignments.length===1?'':'s'} (${selection})`);
