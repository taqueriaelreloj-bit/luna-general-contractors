#!/usr/bin/env node
import {readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const manifest=JSON.parse(await readFile(resolve(root,'content/page-owned-imagery.json'),'utf8'));
let captions=0,slots=0;
const plain=text=>text.replace(/<[^>]+>/g,' ').replace(/&amp;/g,'&').replace(/&#39;/g,"'").replace(/&quot;/g,'"').replace(/\s+/g,' ').trim();
for(const [file,entry] of Object.entries(manifest)){
 const html=await readFile(resolve(root,file),'utf8');
 if(entry.images.length!==5||new Set(entry.images.map(i=>i.src)).size!==5)throw new Error(`Five distinct scenes required: ${file}`);
 for(const i of entry.images){if(!html.includes(`src="${i.src}"`))throw new Error(`Missing assigned scene ${file}: ${i.src}`);slots++;}
 for(const match of html.matchAll(/<figure\b[^>]*>[\s\S]*?<\/figure>/g)){
  const source=match[0].match(/<img\b[^>]*\bsrc="([^"]+)"/)?.[1];
  if(!source||!/^assets\/(?:images\/illustrations\/|service-guides\/|commercial-roofing\/.*\.svg$)/.test(source))continue;
  const caption=match[0].match(/<figcaption\b[^>]*>([\s\S]*?)<\/figcaption>/)?.[1];
  if(caption===undefined)continue;
  const value=plain(caption),city=entry.city||'Dallas–Fort Worth';
  if(value.length>100||!value.endsWith(` · ${city}`))throw new Error(`Caption must be short subject + city: ${file}: ${value}`);
  if(/generated planning|original category|model appearance|not a|completed.project evidence/i.test(value))throw new Error(`Retired caption boilerplate: ${file}`);
  const alt=match[0].match(/<img\b[^>]*\balt="([^"]+)"/)?.[1];
  if(!alt?.trim())throw new Error(`Missing accessible image text: ${file}`);
  captions++;
 }
}
if(slots!==5045)throw new Error(`Expected 5045 assigned images, got ${slots}`);
console.log(`Validated ${slots} assigned image slots and ${captions} concise image captions across ${Object.keys(manifest).length} pages.`);
