// Page-scoped generated imagery. The manifest contains no Library/private IDs.
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {dirname,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export const pageImagery=JSON.parse(readFileSync(resolve(root,'content/page-owned-imagery.json'),'utf8'));
export const gitBlobSha=bytes=>createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
export function resolveOwnedScenes(manifest,file,readAsset){
 const page=manifest[file];
 if(!page||page.images?.length!==5)throw new Error(`Missing five page-owned scenes: ${file}`);
 const context=page.city||'Dallas-Fort Worth';
 const label=page.label||page.category;
 return page.images.map(image=>{
  if(!/^assets\/images\/[\w./-]+\.(?:png|webp|jpe?g)$/.test(image.src)||image.src.includes('..'))throw new Error(`Unsafe scene: ${image.src}`);
  const bytes=readAsset(image.src);
  let width=image.width,height=image.height;
  if(bytes.subarray(0,8).toString('hex')==='89504e470d0a1a0a'){width=bytes.readUInt32BE(16);height=bytes.readUInt32BE(20);}
  if(!(width>0&&height>0))throw new Error(`Missing dimensions: ${image.src}`);
  return {src:image.src,file:image.src,sha:gitBlobSha(bytes),gitBlobSha:gitBlobSha(bytes),width,height,
   title:label,alt:`${label} design concept · ${context}`,
   caption:`${label} · ${context}`,slot:image.slot,ownerPage:file};
 });
}
export const ownedScenes=file=>resolveOwnedScenes(pageImagery,file,src=>{
 const path=resolve(root,src);if(relative(root,path).startsWith('..'))throw new Error(`Unsafe source ${src}`);
 return readFileSync(path);
});
export const ownedMedia=(file,serviceKey)=>({serviceKey,pageOwned:true,suppressLegacyPhoto:true,items:ownedScenes(file).map(image=>({
 ...image,id:`${file.replace(/\.html$/,'')}-scene-${image.slot}`,kind:'representative-illustration',substantive:true,
 serviceKeys:[serviceKey],sceneTags:[serviceKey,'service-planning'],attribution:'AI-created illustrative concept; not actual project evidence.',displayCaption:image.caption
}))});
