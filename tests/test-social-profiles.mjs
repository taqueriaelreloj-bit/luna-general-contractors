import {readFileSync,readdirSync,writeFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const files=readdirSync(root).filter(f=>f.endsWith('.html'));
const originals=execFileSync('git',['cat-file','--batch'],{cwd:root,input:files.map(f=>'HEAD:'+f+'\n').join(''),maxBuffer:120*1024*1024});
let at=0,fail=[],covered=0;
function assert(ok,msg){if(!ok)fail.push(msg);}
function sections(h){const result=[];const re=/<(article|div)\b[^>]*class="[^"]*\b(?:review-card|full-review)\b[^"]*"[^>]*>/g;let m;while((m=re.exec(h))){const tags=new RegExp('<\\/?'+m[1]+'\\b[^>]*>','g');tags.lastIndex=m.index;let depth=0,t;while((t=tags.exec(h))){depth+=t[0].startsWith('</')?-1:1;if(!depth){result.push(h.slice(m.index,tags.lastIndex));break;}}}return result;}
const schema=h=>[...h.matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)].map(m=>JSON.parse(m[1]));
function stripSame(n){if(Array.isArray(n))return n.map(stripSame);if(n&&typeof n==='object'){let x={};for(const[k,v]of Object.entries(n))if(k!=='sameAs')x[k]=stripSame(v);return x;}return n;}
for(const f of files){
 let nl=originals.indexOf(10,at),len=Number(originals.subarray(at,nl).toString().split(' ').at(-1));let old=originals.subarray(nl+1,nl+1+len).toString();at=nl+1+len+1;
 const h=readFileSync(resolve(root,f),'utf8');
 assert((h.match(/data-luna-social\b/g)||[]).length===1,f+': panel duplicate/missing');
 const block=h.match(/<aside class="luna-social-panel"[\s\S]*?<\/aside>/)?.[0]||'';
 assert((block.match(/<a /g)||[]).length===9,f+': platform count');
 assert(block.includes(/<html[^>]*lang=["']es/i.test(h)?'SIGUE NUESTRO TRABAJO':'FOLLOW OUR WORK'),f+': language');
 assert(block.includes('data-profile-pending="true"')&&block.includes('Yellow Pages')&&!block.includes('yellowpages.com'),f+': Yellow Pages disabled');
 assert(sections(old).length===sections(h).length,f+': review count');
 assert(block.indexOf('luna-social-facebook')<block.indexOf('luna-social-tiktok')&&block.indexOf('luna-social-tiktok')<block.indexOf('luna-social-youtube'),f+': order');
 assert(block.indexOf('luna-social-pinterest')>block.indexOf('luna-social-google'),f+': pinterest order');
 assert(JSON.stringify(sections(old.replaceAll("\r\n","\n")))===JSON.stringify(sections(h.replaceAll("\r\n","\n"))),f+': changed review');
 for(const re of [/<title>[\s\S]*?<\/title>/g,/<link[^>]*rel="canonical"[^>]*>/g,/<meta[^>]*name="robots"[^>]*>/g,/<h1\b[^>]*>[\s\S]*?<\/h1>/g])assert(JSON.stringify(old.match(re))===JSON.stringify(h.match(re)),f+': metadata');
 const a=schema(old),b=schema(h);assert(!JSON.stringify(b).includes('yellowpages.com'),f+': Yellow Pages schema');assert(JSON.stringify(stripSame(a))===JSON.stringify(stripSame(b)),f+': schema changed beyond sameAs');
 assert(block.includes('0xcc66b3bf2bc95eca')&&!block.includes('maps/search'),f+': direct Google profile');
 assert(!JSON.stringify(b).includes('maps/search'),f+': Google schema must be direct');
 assert(block.includes('https://www.tiktok.com/@lunageneralcontractors')&&!h.includes('https://www.tiktok.com/@luna.general.cont'),f+': current TikTok handle');
 assert(!h.includes('Jeff Weizen'),f+': AI text');
 covered++;
}
const hashes=files.map(f=>createHash('sha256').update(readFileSync(resolve(root,f))).digest('hex'));
execFileSync(process.execPath,[resolve(root,'scripts/build-social-profiles.mjs')],{cwd:root});
files.forEach((f,i)=>assert(hashes[i]===createHash('sha256').update(readFileSync(resolve(root,f))).digest('hex'),f+': not idempotent'));
const report={covered,failures:fail.length,fail};
writeFileSync(resolve(root,'social-qa.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));if(fail.length)process.exitCode=1;
