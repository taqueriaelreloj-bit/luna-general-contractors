import {readFile,readdir,stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import profiles from '../content/service-guide-profiles.mjs';
import serviceMedia,{targetServiceKeys} from '../content/service-guide-media.mjs';

// This validator owns the city-service imagery block.  It intentionally does
// not invoke the broader guide generator, which has unrelated generated-page
// responsibilities.  New binary illustration blobs may be validated before
// materialization with --allow-remote-blobs, but only when their immutable
// Git blob SHA is declared in the media manifest.
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const allowRemoteBlobs=process.argv.includes('--allow-remote-blobs');
const unexpectedArgs=process.argv.slice(2).filter(arg=>arg!=='--allow-remote-blobs');
if(unexpectedArgs.length)throw new Error(`Unknown argument(s): ${unexpectedArgs.join(', ')}`);

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

const generated=JSON.parse(await readFile(resolve(root,'content/service-guide-manifest.json'),'utf8'));
const assignments=generated.filter(item=>item.slug&&!item.hub&&!item.article&&item.key!=='water-damage-restoration');
const expectedKeys=[...targetServiceKeys].sort();
const assignmentKeys=[...new Set(assignments.map(item=>item.key))].sort();
if(assignments.length!==828)fail(`Expected 828 city-service pages, found ${assignments.length}`);
if(JSON.stringify(assignmentKeys)!==JSON.stringify(expectedKeys))fail('City-service assignments and service-media keys differ');
if(new Set(assignments.map(item=>item.file)).size!==assignments.length)fail('Duplicate city-service assignment file');
if(JSON.stringify(Object.keys(serviceMedia).sort())!==JSON.stringify(expectedKeys))fail('Service-media manifest has unexpected or missing service keys');

const mediaByKey=new Map;
const remoteBlobSources=new Map;
const deferredRemoteBlobSources=new Set;
for(const key of expectedKeys){
 const entry=serviceMedia[key];
 if(!profiles[key]){fail(`Missing service profile for ${key}`);continue;}
 if(!entry||!Array.isArray(entry.items)||entry.items.length<5){fail(`Need at least five media items for ${key}`);continue;}
 const byId=new Map,srcs=new Set;
 for(const item of entry.items){
  if(!item?.substantive)fail(`Non-substantive media in ${key}: ${item?.id||'(missing id)'}`);
  if(!['representative-illustration','genuine-portfolio-photo'].includes(item?.kind))fail(`Invalid media kind in ${key}: ${item?.id||'(missing id)'}`);
  if(!item?.id||byId.has(item.id))fail(`Duplicate/missing media id in ${key}: ${item?.id||'(missing id)'}`);
  if(!item?.src||srcs.has(item.src))fail(`Duplicate/missing media source in ${key}: ${item?.src||'(missing src)'}`);
  if(!item?.serviceKeys?.includes(key))fail(`Media allowlist does not include ${key}: ${item?.id||'(missing id)'}`);
  if(!item?.alt||!item?.caption||!item?.attribution||!Number.isFinite(item?.width)||!Number.isFinite(item?.height)||item.width<1||item.height<1)fail(`Incomplete metadata for ${key}: ${item?.id||'(missing id)'}`);
  if(/\.svg(?:$|[?#])/i.test(item?.src||'')||String(item?.src||'').includes('assets/service-guides/'))fail(`Non-scene asset declared substantive: ${key}/${item?.id||'(missing id)'}`);
  if(item?.sha&&!/^[a-f0-9]{40}$/.test(item.sha))fail(`Invalid Git blob SHA for ${key}/${item.id}`);
  if(item?.sha)remoteBlobSources.set(item.src,item.sha);
  if(item?.id)byId.set(item.id,item);
  if(item?.src)srcs.add(item.src);
 }
 mediaByKey.set(key,byId);
}

const checkSource=async(src,sha,context)=>{
 const absolute=resolve(root,src);
 if(!isInsideRoot(absolute)){fail(`Image source escapes repository root: ${context}: ${src}`);return;}
 try{
  const info=await stat(absolute);
  if(!info.isFile()){fail(`Image source is not a file: ${context}: ${src}`);return;}
  if(sha){
   const actual=gitBlobSha(await readFile(absolute));
   if(actual!==sha)fail(`Git blob SHA mismatch: ${context}: ${src}`);
  }
 }catch{
  if(!(allowRemoteBlobs&&sha&&/^[a-f0-9]{40}$/.test(sha))){
   fail(`Missing image source: ${context}: ${src}`);
  }else{
   deferredRemoteBlobSources.add(src);
  }
 }
};
for(const key of expectedKeys){
 for(const item of serviceMedia[key]?.items||[])await checkSource(item.src,item.sha,`${key}/${item.id}`);
}

const extractCards=section=>section.match(/<figure\b[^>]*\bclass="[^"]*\bsci-card\b[^"]*"[^>]*>[\s\S]*?<\/figure>/gi)||[];
const validatePage=(assignment,html)=>{
 const prefix=`${assignment.file}:`;
 if(count(html,start)!==1||count(html,end)!==1)fail(`${prefix} expected exactly one paired imagery marker`);
 const blocks=html.match(new RegExp(`${start.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\$&')}[\\s\\S]*?${end.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\$&')}`,'g'))||[];
 if(blocks.length!==1)return;
 const section=blocks[0];
 const cssMatches=html.match(/<link\b[^>]*\bhref="service-city-imagery\.css(?:\?[^\"]*)?"[^>]*>/gi)||[];
 if(cssMatches.length!==1)fail(`${prefix} expected exactly one city-imagery stylesheet link`);
 const sectionTag=section.match(/<section\b[^>]*\bclass="[^"]*\bservice-city-imagery\b[^"]*"[^>]*>/i)?.[0];
 if(!sectionTag){fail(`${prefix} missing city-imagery section`);return;}
 if(!/\bdata-service-guide-media(?:\s|>)/i.test(sectionTag))fail(`${prefix} missing data-service-guide-media`);
 if(decode(attr(sectionTag,'data-service-key')||'')!==assignment.key)fail(`${prefix} wrong data-service-key`);
 const expected=mediaByKey.get(assignment.key);
 if(Number(attr(sectionTag,'data-media-count'))!==expected.size)fail(`${prefix} data-media-count does not match manifest`);
 if(count(section,'id="sci-title"')!==1||!section.includes('aria-labelledby="sci-title"'))fail(`${prefix} missing unique gallery heading relationship`);
 if(!normalize(section).includes(`imagery for ${assignment.city}`))fail(`${prefix} gallery heading does not identify ${assignment.city}`);
 if(!section.includes('Dallas-Fort Worth references rather than work in this page\'s city'))fail(`${prefix} missing city-safe gallery disclosure`);
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
  if(!text.includes(item.caption))fail(`${prefix} caption differs from manifest for ${id}`);
  if(item.kind==='representative-illustration'){
   if(!text.includes('Representative illustration'))fail(`${prefix} missing representative label for ${id}`);
   if(!text.includes(`not a photograph of a Luna job or work completed in ${assignment.city}.`))fail(`${prefix} missing city/job disclaimer for ${id}`);
  }else{
   if(!text.includes('Existing Luna portfolio photograph'))fail(`${prefix} missing portfolio label for ${id}`);
   if(!text.includes('Dallas-Fort Worth')||!text.includes(`not represented as work completed in ${assignment.city}.`))fail(`${prefix} missing portfolio attribution/city disclaimer for ${id}`);
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

for(const assignment of assignments){
 try{validatePage(assignment,await readFile(resolve(root,assignment.file),'utf8'));}
 catch(error){fail(`${assignment.file}: ${error.message}`);}
}

// No other page family—including completed mitigation and roofing pages—may
// receive this city-service gallery or its stylesheet by accident.
const targetFiles=new Set(assignments.map(item=>item.file));
for(const file of (await readdir(root)).filter(name=>name.endsWith('.html'))){
 if(targetFiles.has(file))continue;
 const html=await readFile(resolve(root,file),'utf8');
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
console.log(`Validated ${assignments.length} city-service pages and ${expectedKeys.length} service families${allowRemoteBlobs?`; ${deferredRemoteBlobSources.size} remote illustration blobs are deferred to publish verification`:''}.`);
