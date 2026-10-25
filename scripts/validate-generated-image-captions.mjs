#!/usr/bin/env node
import {readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const manifest=JSON.parse(await readFile(resolve(root,'content/page-owned-imagery.json'),'utf8'));
const plain=text=>text.replace(/<[^>]+>/g,' ').replace(/&amp;/g,'&').replace(/&#39;/g,"'").replace(/&quot;/g,'"').replace(/\s+/g,' ').trim();
const hasShortServiceCityCaption=(value,city)=>{
  const normalizedValue=value.replace(/[\u2010-\u2015]/g,'-');
  const normalizedCity=city.replace(/[\u2010-\u2015]/g,'-');
  const prefix=normalizedValue.slice(0,Math.max(0,normalizedValue.length-normalizedCity.length)).trimEnd();
  return normalizedValue.endsWith(normalizedCity)&&/[-\u00b7]$/.test(prefix);
};

let captions=0,slots=0;
for(const [file,entry] of Object.entries(manifest)){
  const html=await readFile(resolve(root,file),'utf8');
  if(entry.images.length!==5||new Set(entry.images.map(i=>i.src)).size!==5)throw new Error(`Five distinct scenes required: ${file}`);
  const gallery=html.match(/<section\b(?=[^>]*\bdata-page-owned-gallery="true")[^>]*>[\s\S]*?<\/section>/i)?.[0];
  if(!gallery)throw new Error(`Missing reusable page-owned gallery: ${file}`);
  const galleryFigures=[...gallery.matchAll(/<figure\b[^>]*\bdata-page-owned-slot="(\d{2})"[^>]*>[\s\S]*?<\/figure>/gi)];
  if(galleryFigures.length!==5)throw new Error(`Gallery needs five static thumbnails: ${file}`);
  const expected=[...entry.images].sort((a,b)=>a.slot-b.slot);
  for(const [index,match] of galleryFigures.entries()){
    const slot=match[1],figure=match[0],expectedImage=expected[index];
    if(slot!==String(expectedImage.slot).padStart(2,'0')||!figure.includes(`src="${expectedImage.src}"`))throw new Error(`Gallery slot/source mismatch: ${file}: ${slot}`);
    if(!figure.includes('data-page-owned-gallery-thumbnail="true"')||!figure.includes('data-page-owned-gallery-image="true"'))throw new Error(`Gallery thumbnail semantics missing: ${file}: ${slot}`);
    if(/<figure\b[^>]*(?:\bhidden\b|\baria-hidden="true")/i.test(figure))throw new Error(`Gallery fallback is hidden: ${file}: ${slot}`);
    const caption=figure.match(/<figcaption\b[^>]*>([\s\S]*?)<\/figcaption>/i)?.[1];
    const value=plain(caption||''),city=entry.city||'Dallas-Fort Worth';
    if(value.length>100||!hasShortServiceCityCaption(value,city))throw new Error(`Gallery caption must be short subject + city: ${file}: ${value}`);
    if(/generated planning|original category|model appearance|not a|completed.project evidence/i.test(value))throw new Error(`Retired gallery caption boilerplate: ${file}`);
    if(!figure.match(/<img\b[^>]*\balt="[^"]+"/i))throw new Error(`Gallery needs factual alt text: ${file}: ${slot}`);
  }
  if(!/<button\b(?=[^>]*\btype="button")(?=[^>]*\bdata-page-owned-gallery-previous\b)[^>]*>/i.test(gallery)||!/<button\b(?=[^>]*\btype="button")(?=[^>]*\bdata-page-owned-gallery-next\b)[^>]*>/i.test(gallery)||!/<[^>]*data-page-owned-gallery-status[^>]*\baria-live="polite"/i.test(gallery))throw new Error(`Accessible gallery controls missing: ${file}`);
  for(const image of entry.images){
    if(!html.includes(`src="${image.src}"`))throw new Error(`Missing assigned scene ${file}: ${image.src}`);
    slots++;
  }
  for(const match of html.matchAll(/<figure\b[^>]*>[\s\S]*?<\/figure>/g)){
    const source=match[0].match(/<img\b[^>]*\bsrc="([^"]+)"/)?.[1];
    if(!source||!/^assets\/(?:images\/illustrations\/|service-guides\/|commercial-roofing\/.*\.svg$)/.test(source))continue;
    const caption=match[0].match(/<figcaption\b[^>]*>([\s\S]*?)<\/figcaption>/)?.[1];
    if(caption===undefined)continue;
    const value=plain(caption),city=entry.city||'Dallas-Fort Worth';
    if(value.length>100||!hasShortServiceCityCaption(value,city))throw new Error(`Caption must be short subject + city: ${file}: ${value}`);
    if(/generated planning|original category|model appearance|not a|completed.project evidence/i.test(value))throw new Error(`Retired caption boilerplate: ${file}`);
    const alt=match[0].match(/<img\b[^>]*\balt="([^"]+)"/)?.[1];
    if(!alt?.trim())throw new Error(`Missing accessible image text: ${file}`);
    captions++;
  }
}
if(slots!==5045)throw new Error(`Expected 5045 assigned images, got ${slots}`);
console.log(`Validated ${slots} assigned image slots and ${captions} concise image captions across ${Object.keys(manifest).length} pages.`);
