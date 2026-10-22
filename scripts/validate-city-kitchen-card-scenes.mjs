import {readFile,readdir,stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {cityKitchenCardSceneAssets,cityKitchenCardSceneSources} from '../content/city-kitchen-card-scenes.mjs';
import {cityGuideCaption} from '../content/service-guide-media.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
if(process.argv.length!==2)throw new Error('This validator does not accept arguments.');

const cities=await Promise.all(
 (await readdir(resolve(root,'luna_engine/content/cities')))
  .filter(name=>name.endsWith('.json'))
  .sort()
  .map(async name=>JSON.parse(await readFile(resolve(root,'luna_engine/content/cities',name),'utf8')))
);
if(cities.length!==36)throw new Error(`Expected 36 city records, found ${cities.length}.`);

const start='<!-- service-guide:start -->';
const end='<!-- service-guide:end -->';
const noticeStart='<!-- city-kitchen-generated-media:start -->';
const noticeEnd='<!-- city-kitchen-generated-media:end -->';
const sceneIds=['cabinet','quartz','porcelain'];
const allowedByScene={
 cabinet:new Set(cityKitchenCardSceneSources.cabinet),
 quartz:new Set(cityKitchenCardSceneSources.quartz),
 porcelain:new Set(cityKitchenCardSceneSources.tile)
};
const errors=[];
const fail=message=>errors.push(message);
const count=(text,needle)=>text.split(needle).length-1;
const sectionOf=(html,file)=>{
 const from=html.indexOf(start),to=html.indexOf(end,from);
 if(from<0||to<0||to<from){fail(`${file}: missing paired service-guide markers`);return '';}
 return html.slice(from,to+end.length);
};
const attr=(tag,name)=>tag.match(new RegExp(`(?:^|\\s)${name.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\$&')}="([^"]*)"`,'i'))?.[1]||'';
const imageTag=markup=>markup.match(/<img\b[^>]*>/i)?.[0]||'';
const gitBlobSha=data=>createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${data.length}\0`),data])).digest('hex');
const pngDimensions=data=>{
 if(data.length<24||!data.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))||data.toString('ascii',12,16)!=='IHDR')throw new Error('expected a PNG with an IHDR chunk');
 return {width:data.readUInt32BE(16),height:data.readUInt32BE(20)};
};

const expectedAssets=new Map(cityKitchenCardSceneAssets.map(asset=>[asset.src,asset]));
if(expectedAssets.size!==Object.values(cityKitchenCardSceneSources).flat().length)throw new Error('Duplicate approved city-kitchen scene sources.');
for(const [source,asset] of expectedAssets){
 try{
  const info=await stat(resolve(root,source));
  if(!info.isFile())fail(`${source}: approved scene source is not a file`);
  else{
   const data=await readFile(resolve(root,source));
   if(!/^[a-f0-9]{40}$/i.test(asset.sha)||gitBlobSha(data)!==asset.sha)fail(`${source}: approved scene blob SHA does not match the manifest`);
   const dimensions=pngDimensions(data);
   if(dimensions.width!==asset.width||dimensions.height!==asset.height)fail(`${source}: approved scene dimensions are ${dimensions.width}x${dimensions.height}, expected ${asset.width}x${asset.height}`);
  }
 }catch(error){
  fail(`${source}: approved scene verification failed (${error.code||error.message})`);
 }
}

for(const city of cities){
 const file=`${city.slug}-kitchen-remodeling.html`;
 const section=sectionOf(await readFile(resolve(root,file),'utf8'),file);
 if(!section)continue;
 if(/assets\/service-guides\/(?:cabinet|countertop|tile)\.svg/i.test(section))fail(`${file}: legacy flat material SVG remains in the kitchen guide`);
 if(count(section,noticeStart)!==1||count(section,noticeEnd)!==1)fail(`${file}: expected one generated-media notice`);
 if(!section.includes('Generated planning illustrations shown above are not product photographs or completed-project evidence.'))fail(`${file}: missing concise generated-media provenance notice`);
 if(section.includes('not a Luna project or product photograph'))fail(`${file}: legacy per-card disclaimer remains`);
 const expectedCaption=cityGuideCaption('Kitchen remodeling',city.name);
 for(const sceneId of sceneIds){
  const cardMatch=section.match(new RegExp(`<article\\b[^>]*\\bclass="[^"]*\\bsg-card--scene-${sceneId}\\b[^"]*"[^>]*>[\\s\\S]*?<\\/article>`, 'i'));
  if(!cardMatch){fail(`${file}: missing ${sceneId} generated scene card`);continue;}
  const card=cardMatch[0],tag=imageTag(card),source=attr(tag,'src');
  if(!tag){fail(`${file}: ${sceneId} scene card has no image`);continue;}
  if(!allowedByScene[sceneId].has(source))fail(`${file}: ${sceneId} scene uses an unapproved source (${source||'missing'})`);
  if(!attr(tag,'alt').trim())fail(`${file}: ${sceneId} scene has no alt text`);
  if(!card.includes(`<figcaption>${expectedCaption}</figcaption>`))fail(`${file}: ${sceneId} scene lacks the concise service-and-city caption`);
 }
}

if(errors.length)throw new Error(`City kitchen scene validation failed (${errors.length} issue${errors.length===1?'':'s'}):\n- ${errors.join('\n- ')}`);
console.log(`Validated concise generated material scenes across ${cities.length} city kitchen pages.`);
