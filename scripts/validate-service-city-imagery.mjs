import {readFile,readdir,stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import profiles from '../content/service-guide-profiles.mjs';
import serviceMedia,{cityGuideCaption,targetServiceKeys} from '../content/service-guide-media.mjs';
import pageOwnedCityMedia from '../content/page-owned-city-media.mjs';

// This validator owns the city-service imagery block.  It intentionally does
// not invoke the broader guide generator, which has unrelated generated-page
// responsibilities.  New binary illustration blobs may be validated before
// materialization with --allow-remote-blobs, but only when their immutable
// Git blob SHA is declared in the media manifest.
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const allowRemoteBlobs=process.argv.includes('--allow-remote-blobs');
const requireCityContext=process.argv.includes('--require-city-context');
const onlyServiceArg=process.argv.find(arg=>arg.startsWith('--only-service='));
const onlyService=onlyServiceArg?.slice('--only-service='.length);
const onlyPageArg=process.argv.find(arg=>arg.startsWith('--only='));
const onlyPage=onlyPageArg?.slice('--only='.length);
const unexpectedArgs=process.argv.slice(2).filter(arg=>arg!=='--allow-remote-blobs'&&arg!=='--require-city-context'&&arg!==onlyServiceArg&&arg!==onlyPageArg);
if(unexpectedArgs.length)throw new Error(`Unknown argument(s): ${unexpectedArgs.join(', ')}`);
if(onlyServiceArg&&!onlyService)throw new Error('The --only-service option needs a service key.');
if(onlyPageArg&&!onlyPage)throw new Error('The --only option needs one city-service filename.');
if(onlyPage&&onlyService)throw new Error('Use either --only or --only-service, not both.');
if(requireCityContext&&!onlyService&&!onlyPage)throw new Error('The --require-city-context option requires --only-service or --only to prevent a broad validation claim.');

const start='<!-- service-city-imagery:start -->';
const end='<!-- service-city-imagery:end -->';
const cssHref='service-city-imagery.css';
const errors=[];
const fail=message=>errors.push(message);
const count=(text,needle)=>text.split(needle).length-1;
const attr=(tag,name)=>{
 const match=tag.match(new RegExp(`(?:^|\\s)${name.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\$&')}="([^"]*)"`,'i'));
 return match?.[1];
};
const decode=value=>String(value)
 .replace(/&#39;/g,"'").replace(/&quot;/g,'"').replace(/&gt;/g,'>').replace(/&lt;/g,'<').replace(/&amp;/g,'&');
const normalize=value=>decode(String(value).replace(/<[^>]*>/g,' ').replace(/\s+/g,' ')).trim();
const isInsideRoot=path=>!relative(root,path).startsWith('..');
const gitBlobSha=data=>createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${data.length}\0`),data])).digest('hex');
const imageDimensions=data=>{
 if(data.length>=24&&data.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))&&data.toString('ascii',12,16)==='IHDR'){
  return {width:data.readUInt32BE(16),height:data.readUInt32BE(20)};
 }
 if(data.length>=12&&data.toString('ascii',0,4)==='RIFF'&&data.toString('ascii',8,12)==='WEBP'){
  for(let offset=12;offset+8<=data.length;){
   const chunk=data.toString('ascii',offset,offset+4),size=data.readUInt32LE(offset+4),start=offset+8;
   if(start+size>data.length)throw new Error('truncated WebP chunk');
   if(chunk==='VP8X'&&size>=10)return {width:data.readUIntLE(start+4,3)+1,height:data.readUIntLE(start+7,3)+1};
   if(chunk==='VP8 '&&size>=10&&data[start+3]===0x9d&&data[start+4]===0x01&&data[start+5]===0x2a)return {width:data.readUInt16LE(start+6)&0x3fff,height:data.readUInt16LE(start+8)&0x3fff};
   if(chunk==='VP8L'&&size>=5&&data[start]===0x2f)return {width:(data[start+1]|((data[start+2]&0x3f)<<8))+1,height:(((data[start+2]&0xc0)>>6)|(data[start+3]<<2)|((data[start+4]&0x0f)<<10))+1};
   offset=start+size+(size%2);
  }
  throw new Error('unsupported WebP bitstream');
 }
 if(data.length>=4&&data[0]===0xff&&data[1]===0xd8){
  const sof=new Set([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf]);
  for(let offset=2;offset<data.length;){
   if(data[offset]!==0xff){offset++;continue;}
   while(offset<data.length&&data[offset]===0xff)offset++;
   const marker=data[offset++];
   if(marker===0xd8||marker===0x01||(marker>=0xd0&&marker<=0xd7))continue;
   if(marker===0xd9||marker===0xda)break;
   if(offset+2>data.length)break;
   const size=data.readUInt16BE(offset);
   if(size<2||offset+size>data.length)throw new Error('truncated JPEG segment');
   if(sof.has(marker)){
    if(size<7)throw new Error('invalid JPEG frame segment');
    return {width:data.readUInt16BE(offset+5),height:data.readUInt16BE(offset+3)};
   }
   offset+=size;
  }
  throw new Error('JPEG frame dimensions not found');
 }
 throw new Error('unsupported image format');
};

const generated=JSON.parse(await readFile(resolve(root,'content/service-guide-manifest.json'),'utf8'));
// The final page-owned imagery pass deliberately replaces the legacy
// service-city card markup. Keep this validator useful after that final pass
// by validating the equivalent page-owned contract rather than requiring
// retired `.service-city-imagery` cards to reappear.
const finalPageOwned=JSON.parse(await readFile(resolve(root,'content/page-owned-imagery.json'),'utf8'));
const assignments=generated.filter(item=>item.slug&&!item.hub&&!item.article&&item.key!=='water-damage-restoration');
const expectedKeys=[...targetServiceKeys].sort();
const assignmentKeys=[...new Set(assignments.map(item=>item.key))].sort();
if(assignments.length!==828)fail(`Expected 828 city-service pages, found ${assignments.length}`);
if(JSON.stringify(assignmentKeys)!==JSON.stringify(expectedKeys))fail('City-service assignments and service-media keys differ');
if(new Set(assignments.map(item=>item.file)).size!==assignments.length)fail('Duplicate city-service assignment file');
if(JSON.stringify(Object.keys(serviceMedia).sort())!==JSON.stringify(expectedKeys))fail('Service-media manifest has unexpected or missing service keys');
if(onlyService&&!expectedKeys.includes(onlyService))fail(`Unknown service key for --only-service: ${onlyService}`);
if(onlyPage&&!pageOwnedCityMedia[onlyPage]&&!finalPageOwned[onlyPage])fail(`The --only page has no declared page-owned media override: ${onlyPage}`);
const selectedAssignments=onlyPage
 ? assignments.filter(assignment=>assignment.file===onlyPage)
 : onlyService?assignments.filter(assignment=>assignment.key===onlyService):assignments;
if(!selectedAssignments.length)fail(`No city-service assignments for ${onlyPage||onlyService||'the requested selection'}`);
const selectedServiceKeys=[...new Set(selectedAssignments.map(assignment=>assignment.key))];
const entryFor=assignment=>pageOwnedCityMedia[assignment.file]||serviceMedia[assignment.key];
const pageOwnedGeneratedSources=new Map;
// Source paths alone do not prove uniqueness: a byte-identical generated
// scene can be copied under a new filename. Require every page-owned
// illustration blob SHA to have exactly one page owner as well.
const pageOwnedGeneratedBlobShas=new Map;
for(const [file,entry] of Object.entries(pageOwnedCityMedia)){
 for(const item of entry?.items||[]){
  if(item.kind!=='representative-illustration')continue;
  const owner=pageOwnedGeneratedSources.get(item.src);
  if(owner&&owner!==file)fail(`Page-owned generated scene is assigned to more than one page: ${item.src}`);
  pageOwnedGeneratedSources.set(item.src,file);
  const shaOwner=pageOwnedGeneratedBlobShas.get(item.sha);
  if(shaOwner)fail(`Page-owned generated scene Git blob SHA is assigned more than once: ${item.sha} (${shaOwner} and ${file})`);
  pageOwnedGeneratedBlobShas.set(item.sha,file);
 }
}

const mediaByFile=new Map;
const deferredRemoteBlobSources=new Set;
for(const assignment of selectedAssignments){
 const {key,file}=assignment,entry=entryFor(assignment),override=pageOwnedCityMedia[file];
 if(!profiles[key]){fail(`Missing service profile for ${key}`);continue;}
 if(override&&(!override.pageOwned||override.serviceKey!==key))fail(`Invalid page-owned media override for ${file}`);
 if(!entry||!Array.isArray(entry.items)||entry.items.length<5){fail(`Need at least five media items for ${key}`);continue;}
 const byId=new Map,srcs=new Set;
 for(const item of entry.items){
  if(!item?.substantive)fail(`Non-substantive media in ${key}: ${item?.id||'(missing id)'}`);
  if(!['representative-illustration','genuine-portfolio-photo'].includes(item?.kind))fail(`Invalid media kind in ${key}: ${item?.id||'(missing id)'}`);
  if(!item?.id||byId.has(item.id))fail(`Duplicate/missing media id in ${key}: ${item?.id||'(missing id)'}`);
  if(!item?.src||srcs.has(item.src))fail(`Duplicate/missing media source in ${key}: ${item?.src||'(missing src)'}`);
  if(!item?.serviceKeys?.includes(key))fail(`Media allowlist does not include ${key}: ${item?.id||'(missing id)'}`);
  if(!item?.alt||!item?.caption||!item?.attribution||!Number.isSafeInteger(item?.width)||!Number.isSafeInteger(item?.height)||item.width<1||item.height<1)fail(`Incomplete metadata for ${key}: ${item?.id||'(missing id)'}`);
  if(/\.svg(?:$|[?#])/i.test(item?.src||'')||String(item?.src||'').includes('assets/service-guides/'))fail(`Non-scene asset declared substantive: ${key}/${item?.id||'(missing id)'}`);
  if(item?.sha&&!/^[a-f0-9]{40}$/.test(item.sha))fail(`Invalid Git blob SHA for ${key}/${item.id}`);
  if(item?.id)byId.set(item.id,item);
  if(item?.src)srcs.add(item.src);
 }
 mediaByFile.set(file,byId);
}

const checkSource=async(item,context)=>{
 const {src,sha,width,height}=item,absolute=resolve(root,src);
 if(!isInsideRoot(absolute)){fail(`Image source escapes repository root: ${context}: ${src}`);return;}
 let info;
 try{
  info=await stat(absolute);
 }catch(error){
  if((error.code==='ENOENT'||error.code==='ENOTDIR')&&allowRemoteBlobs&&sha&&/^[a-f0-9]{40}$/.test(sha)){
   deferredRemoteBlobSources.add(src);
  }else if(error.code==='ENOENT'||error.code==='ENOTDIR'){
   fail(`Missing image source: ${context}: ${src}`);
  }else{
   fail(`Could not stat image source: ${context}: ${src} (${error.message})`);
  }
  return;
 }
 if(!info.isFile()){fail(`Image source is not a file: ${context}: ${src}`);return;}
 let data;
 try{
  data=await readFile(absolute);
 }catch(error){
  fail(`Could not read image source: ${context}: ${src} (${error.message})`);
  return;
 }
 if(sha&&gitBlobSha(data)!==sha)fail(`Git blob SHA mismatch: ${context}: ${src}`);
 try{
  const actual=imageDimensions(data);
  if(actual.width!==width||actual.height!==height)fail(`Image dimensions differ from manifest: ${context}: ${src} is ${actual.width}x${actual.height}, expected ${width}x${height}`);
 }catch(error){
  fail(`Could not read local image dimensions: ${context}: ${src} (${error.message})`);
 }
};
const checkedSources=new Set;
for(const assignment of selectedAssignments){
 for(const item of entryFor(assignment)?.items||[]){
  const sourceKey=`${item.src}|${item.sha||''}`;
  if(checkedSources.has(sourceKey))continue;
  checkedSources.add(sourceKey);
  await checkSource(item,`${assignment.file}/${item.id}`);
 }
}

const extractCards=section=>section.match(/<figure\b[^>]*\bclass="[^"]*\bsci-card\b[^"]*"[^>]*>[\s\S]*?<\/figure>/gi)||[];
const escapeRegex=value=>String(value).replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
const finalImageTag=(html,src)=>html.match(new RegExp(`<img\\b[^>]*\\bsrc="${escapeRegex(src)}"[^>]*>`, 'i'))?.[0]||'';
const validateFinalPageOwned=(assignment,html,entry)=>{
 const prefix=`${assignment.file}:`;
 if(!Array.isArray(entry?.images)||entry.images.length!==5||new Set(entry.images.map(item=>item.src)).size!==5){
  fail(`${prefix} final page-owned manifest needs five unique images`);
  return;
 }
 if(entry.city!==assignment.city)fail(`${prefix} final page-owned city differs from assignment`);
 if(count(html,start)!==1||count(html,end)!==1)fail(`${prefix} expected exactly one paired imagery marker`);
 if((html.match(/<link\b[^>]*\bhref="page-owned-imagery\.css(?:\?[^\"]*)?"[^>]*>/gi)||[]).length!==1)fail(`${prefix} expected exactly one page-owned imagery stylesheet link`);
 if(!html.includes('data-page-owned-imagery="true"'))fail(`${prefix} missing final page-owned gallery marker`);
 if(/Representative illustration|not a photograph of a Luna job|not project photographs or product photographs/i.test(html))fail(`${prefix} retired generated-media boilerplate remains`);
 for(const image of entry.images){
  const tag=finalImageTag(html,image.src);
  if(!tag){fail(`${prefix} missing final page-owned source ${image.src}`);continue;}
  const alt=decode(attr(tag,'alt')||'');
  if(!alt.trim()||!alt.includes(entry.city))fail(`${prefix} missing concise city-aware alt text for ${image.src}`);
  if(Number(attr(tag,'width'))!==image.width||Number(attr(tag,'height'))!==image.height)fail(`${prefix} intrinsic dimensions differ for ${image.src}`);
  if(/\bdata-page-owned-hero="true"/i.test(tag)){
   if(attr(tag,'fetchpriority')!=='high'||attr(tag,'decoding')!=='async'||attr(tag,'loading')==='lazy')fail(`${prefix} final hero needs high-priority async markup for ${image.src}`);
  }else if(attr(tag,'loading')!=='lazy'||attr(tag,'decoding')!=='async')fail(`${prefix} final page-owned image needs lazy/async markup for ${image.src}`);
 }
 if(assignment.key==='insurance-claims'){
  // Final page-owned galleries use short service-and-city captions. The
  // durable insurance guardrail belongs in the canonical FAQ, rather than in
  // a repeated visual-media disclaimer whose retired wording users removed.
  if(!html.includes('Do you act as a public adjuster?'))fail(`${prefix} canonical public-adjuster FAQ was not preserved`);
  if(!html.includes('coverage decisions and policy interpretation remain with the insurer and policyholder'))fail(`${prefix} pre-existing insurance disclaimer was not preserved`);
 }
};
const validatePage=(assignment,html)=>{
 const prefix=`${assignment.file}:`;
 const finalEntry=finalPageOwned[assignment.file];
 if(finalEntry){validateFinalPageOwned(assignment,html,finalEntry);return;}
 const override=pageOwnedCityMedia[assignment.file];
 const pageOwned=override?.pageOwned===true;
 if(count(html,start)!==1||count(html,end)!==1)fail(`${prefix} expected exactly one paired imagery marker`);
 const blocks=html.match(new RegExp(`${start.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\$&')}[\\s\\S]*?${end.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\$&')}`,'g'))||[];
 if(blocks.length!==1)return;
 const section=blocks[0];
 const hasCaptionContext=section.includes('data-caption-context="service-city"');
 const hasGeneratedSectionNotice=section.includes('data-generated-section-notice="true"');
 const usesCityContext=pageOwned||requireCityContext||hasCaptionContext||hasGeneratedSectionNotice;
 const cssMatches=html.match(/<link\b[^>]*\bhref="service-city-imagery\.css(?:\?[^\"]*)?"[^>]*>/gi)||[];
 if(cssMatches.length!==1)fail(`${prefix} expected exactly one city-imagery stylesheet link`);
 const sectionTag=section.match(/<section\b[^>]*\bclass="[^"]*\bservice-city-imagery\b[^"]*"[^>]*>/i)?.[0];
 if(!sectionTag){fail(`${prefix} missing city-imagery section`);return;}
 if(!/\bdata-service-guide-media(?:\s|>)/i.test(sectionTag))fail(`${prefix} missing data-service-guide-media`);
 if(decode(attr(sectionTag,'data-service-key')||'')!==assignment.key)fail(`${prefix} wrong data-service-key`);
 if(pageOwned&&attr(sectionTag,'data-page-owned-city-media')!=='true')fail(`${prefix} missing page-owned city-media marker`);
 const expected=mediaByFile.get(assignment.file);
 if(!expected){fail(`${prefix} no media manifest resolved for this page`);return;}
 if(Number(attr(sectionTag,'data-media-count'))!==expected.size)fail(`${prefix} data-media-count does not match manifest`);
 if(count(section,'id="sci-title"')!==1||!section.includes('aria-labelledby="sci-title"'))fail(`${prefix} missing unique gallery heading relationship`);
 if(!normalize(section).includes(`imagery for ${assignment.city}`))fail(`${prefix} gallery heading does not identify ${assignment.city}`);
 if(usesCityContext){
  if(!hasCaptionContext)fail(`${prefix} missing city-context caption marker`);
  if(pageOwned){
   if(hasGeneratedSectionNotice||section.includes('data-generated-section-notice="true"'))fail(`${prefix} legacy generated-media notice remains on page-owned gallery`);
   if(section.includes('Representative illustration'))fail(`${prefix} legacy representative label remains on page-owned gallery`);
   if(section.includes(`not a photograph of a Luna job or work completed in ${assignment.city}.`))fail(`${prefix} legacy city/job disclaimer remains on page-owned gallery`);
  }else{
   if(!hasGeneratedSectionNotice)fail(`${prefix} missing city-context generated-media notice`);
   if(!section.includes('data-generated-section-notice="true"'))fail(`${prefix} missing city-context generated-media notice`);
   if(!section.includes('not project photographs or product photographs'))fail(`${prefix} missing concise generated-media provenance notice`);
   if(!/Dallas-Fort Worth references, not work in this page(?:'|')s city\./.test(section))fail(`${prefix} missing city-safe portfolio context`);
  }
 }else if(!section.includes('Dallas-Fort Worth references rather than work in this page\'s city'))fail(`${prefix} missing city-safe gallery disclosure`);
 if((section.match(/<div\b[^>]*\bclass="[^"]*\bsci-grid\b[^"]*"[^>]*>/gi)||[]).length!==1)fail(`${prefix} expected one gallery grid`);
 const cards=extractCards(section);
 if(cards.length!==expected.size)fail(`${prefix} expected ${expected.size} media cards, found ${cards.length}`);
 const seenIds=new Set,seenSources=new Set;
 for(const figure of cards){
  const figureTag=figure.match(/^<figure\b[^>]*>/i)?.[0]||'';
  const id=decode(attr(figureTag,'data-media-id')||'');
  const kind=decode(attr(figureTag,'data-media-kind')||'');
  const item=expected.get(id);
  if(!item){fail(`${prefix} unexpected media id ${id||'(missing)'}`);continue;}
  if(seenIds.has(id))fail(`${prefix} duplicate media id ${id}`);
  seenIds.add(id);
  if(kind!==item.kind)fail(`${prefix} wrong kind for ${id}`);
  const imageTag=figure.match(/<img\b[^>]*>/i)?.[0];
  if(!imageTag){fail(`${prefix} missing image for ${id}`);continue;}
  const src=decode(attr(imageTag,'src')||'');
  if(src!==item.src)fail(`${prefix} wrong source for ${id}`);
  if(seenSources.has(src))fail(`${prefix} duplicate gallery source ${src}`);
  seenSources.add(src);
  if(!decode(attr(imageTag,'alt')||'').trim())fail(`${prefix} missing alt text for ${id}`);
  if(decode(attr(imageTag,'alt')||'')!==item.alt)fail(`${prefix} alt text differs from manifest for ${id}`);
  if(Number(attr(imageTag,'width'))!==item.width||Number(attr(imageTag,'height'))!==item.height)fail(`${prefix} intrinsic dimensions differ for ${id}`);
  if(attr(imageTag,'loading')!=='lazy'||attr(imageTag,'decoding')!=='async')fail(`${prefix} missing lazy/async loading attributes for ${id}`);
  const substantive=attr(imageTag,'data-substantive-scene');
  const expectedScene=item.kind==='representative-illustration'?'representative-illustration':'portfolio-photo';
  if(substantive!==expectedScene)fail(`${prefix} wrong substantive-scene type for ${id}`);
  if(/\.svg(?:$|[?#])/i.test(src)||src.includes('assets/service-guides/'))fail(`${prefix} non-substantive image emitted for ${id}`);
  const text=normalize(figure);
  if(usesCityContext){
   const expectedCaption=item.displayCaption||cityGuideCaption(profiles[assignment.key].name,assignment.city);
   if(!text.includes(expectedCaption))fail(`${prefix} concise service-and-city caption missing for ${id}`);
   if(!figure.includes('class="sci-caption" data-caption-context="service-city"'))fail(`${prefix} caption context marker missing for ${id}`);
   if(item.kind==='representative-illustration'){
    if(text.includes('Representative illustration'))fail(`${prefix} legacy representative caption remains for ${id}`);
    if(text.includes(`not a photograph of a Luna job or work completed in ${assignment.city}.`))fail(`${prefix} legacy city/job disclaimer remains for ${id}`);
   }else if(!text.includes(item.attribution)){
    fail(`${prefix} portfolio attribution missing for ${id}`);
   }
  }else{
   if(!text.includes(item.caption))fail(`${prefix} caption differs from manifest for ${id}`);
   if(item.kind==='representative-illustration'){
    if(!text.includes('Representative illustration'))fail(`${prefix} missing representative label for ${id}`);
    if(!text.includes(`not a photograph of a Luna job or work completed in ${assignment.city}.`))fail(`${prefix} missing city/job disclaimer for ${id}`);
   }else{
    if(!text.includes('Existing Luna portfolio photograph'))fail(`${prefix} missing portfolio label for ${id}`);
    if(!text.includes('Dallas-Fort Worth')||!text.includes(`not represented as work completed in ${assignment.city}.`))fail(`${prefix} missing portfolio attribution/city disclaimer for ${id}`);
   }
  }
 }
 if(seenIds.size!==expected.size)fail(`${prefix} media IDs do not cover manifest`);
 if(assignment.key==='insurance-claims'){
  for(const phrase of ['specific claim','carrier decision','coverage determination','adjustment','result']){
   if(!section.includes(phrase))fail(`${prefix} insurance imagery disclaimer missing “${phrase}”`);
  }
  if(!html.includes('coverage decisions and policy interpretation remain with the insurer and policyholder'))fail(`${prefix} pre-existing insurance disclaimer was not preserved`);
 }
};

for(const assignment of selectedAssignments){
 try{validatePage(assignment,await readFile(resolve(root,assignment.file),'utf8'));}
 catch(error){fail(`${assignment.file}: ${error.message}`);}
}

// No other page family—including completed mitigation and roofing pages—may
// receive this city-service gallery or its stylesheet by accident.
const targetFiles=new Set(assignments.map(item=>item.file));
for(const file of (await readdir(root)).filter(name=>name.endsWith('.html'))){
 const html=await readFile(resolve(root,file),'utf8');
 for(const [source,owner] of pageOwnedGeneratedSources){
  if(file!==owner&&html.includes(source))fail(`${file}: page-owned generated scene is reused from ${owner}: ${source}`);
 }
 if(targetFiles.has(file))continue;
 if(html.includes(start)||html.includes(end)||html.includes(cssHref))fail(`${file}: city-service imagery leaked outside the 828-page scope`);
}

const stripComments=css=>css.replace(/\/\*[\s\S]*?\*\//g,'');
const findClosingBrace=(css,opening)=>{
 let depth=0;
 for(let index=opening;index<css.length;index++){
  if(css[index]==='{')depth++;
  else if(css[index]==='}'&&!--depth)return index;
 }
 return -1;
};
const parseCssRules=(css,context='root')=>{
 const rules=[];
 let cursor=0;
 while(cursor<css.length){
  const opening=css.indexOf('{',cursor);
  if(opening<0)break;
  const header=css.slice(cursor,opening).trim();
  const closing=findClosingBrace(css,opening);
  if(closing<0){fail('Unbalanced brace in service-city-imagery.css');break;}
  const body=css.slice(opening+1,closing);
  if(header.startsWith('@')){
   if(/^@media/i.test(header))rules.push(...parseCssRules(body,`${context}/${header.replace(/\s+/g,'')}`));
  }else if(header){
   for(const selector of header.split(',').map(value=>value.trim()).filter(Boolean))rules.push({context,selector,body});
  }
  cursor=closing+1;
 }
 return rules;
};
const css=stripComments(await readFile(resolve(root,cssHref),'utf8'));
const rules=parseCssRules(css);
const selectorKeys=new Set;
for(const rule of rules){
 const key=`${rule.context}|${rule.selector}`;
 if(selectorKeys.has(key))fail(`Duplicate CSS selector in one context: ${key}`);
 selectorKeys.add(key);
 if(!/^\.(?:service-city-imagery|sci-)/.test(rule.selector))fail(`Unscoped CSS selector: ${rule.selector}`);
}
const ruleBody=(context,selector)=>rules.find(rule=>rule.context===context&&rule.selector===selector)?.body||'';
if(!/grid-template-columns\s*:\s*repeat\(3,/i.test(ruleBody('root','.sci-grid')))fail('Missing three-column desktop gallery rule');
if(!/grid-template-columns\s*:\s*repeat\(2,/i.test(ruleBody('root/@media(max-width:900px)','.sci-grid')))fail('Missing two-column tablet gallery rule');
if(!/grid-template-columns\s*:\s*1fr/i.test(ruleBody('root/@media(max-width:640px)','.sci-grid')))fail('Missing one-column mobile gallery rule');
if(!/width\s*:\s*100%/i.test(ruleBody('root','.sci-card img')))fail('Gallery images are not responsive');

if(errors.length){
 throw new Error(`Service-city imagery validation failed (${errors.length} issue${errors.length===1?'':'s'}):\n- ${errors.slice(0,40).join('\n- ')}${errors.length>40?`\n- … ${errors.length-40} more`:''}`);
}
console.log(`Validated ${selectedAssignments.length} city-service page${selectedAssignments.length===1?'':'s'} and ${selectedServiceKeys.length} service ${selectedServiceKeys.length===1?'family':'families'}${requireCityContext?' with concise service-and-city captions':''}${allowRemoteBlobs?`; ${deferredRemoteBlobSources.size} remote illustration blobs are deferred to publish verification`:''}.`);
