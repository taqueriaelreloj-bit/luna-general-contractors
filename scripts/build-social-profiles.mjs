import {readFile,writeFile,readdir} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export const profiles=[
 ['facebook','Facebook','Latest updates','Novedades','https://www.facebook.com/profile.php?id=61593674657367','f'],
 ['tiktok','TikTok','On-site videos','Videos de obra','https://www.tiktok.com/@luna.general.cont','♪'],
 ['youtube','YouTube','Project videos','Videos de proyectos','https://www.youtube.com/@lunageneralcontractors','▶'],
 ['instagram','Instagram','Project photos','Fotos de proyectos','https://www.instagram.com/lunageneralcontractors/','◎'],
 ['yelp','Yelp','Customer reviews','Reseñas de clientes','https://www.yelp.com/biz/luna-general-contractors-grand-prairie','✳'],
 ['google','Google Business Profile','Reviews & information','Reseñas e información','https://www.google.com/maps/place/Luna+general+Contractors/@32.6546538,-97.0347791,17z/data=!3m1!4b1!4m6!3m5!1s0x864e89ec7a7b50e7:0xcc66b3bf2bc95eca!8m2!3d32.6546538!4d-97.0347791!16s%2Fg%2F11j65h1_vv','G'],
 ['pinterest','Pinterest','Ideas & project photos','Ideas y fotos','https://www.pinterest.com/lunabestcontractors/','P'],
 ['x','X','News & updates','Noticias y novedades','https://x.com/lunabestgc','𝕏'],
 ['yellowpages','Yellow Pages','Business information','Información del negocio',null,'YP'],
 ['mapquest','MapQuest','Find our business','Encuentra nuestro negocio','https://www.mapquest.com/us/texas/luna-general-contractors-516521428','⌖']
];
const esc=s=>s.replaceAll('&','&amp;').replaceAll('"','&quot;');
function panel(es){return '<aside class="luna-social-panel" data-luna-social aria-label="'+(es?'Redes y perfiles de Luna':'Luna social and business profiles')+'"><p class="luna-social-eyebrow">'+(es?'SIGUE NUESTRO TRABAJO':'FOLLOW OUR WORK')+'</p><h2>'+(es?'Mira a Luna en acción.':'See Luna in action.')+'</h2><p class="luna-social-intro">'+(es?'Explora fotos, videos y novedades de Luna General Contractors.':'Explore project photos, videos and updates from Luna General Contractors.')+'</p><div class="luna-social-grid">'+profiles.map(([id,name,en,sp,url,icon],i)=>'<'+(url?'a':'div')+' class="luna-social-card luna-social-'+id+(i<2?' luna-social-featured':'')+'"'+(url?' href="'+esc(url)+'" target="_blank" rel="noopener noreferrer"':' aria-disabled="true" data-profile-pending="true"')+'><span class="luna-social-icon" aria-hidden="true">'+icon+'</span><strong>'+name+'</strong><span>'+ (url?(es?sp:en):(es?'Enlace pendiente':'Link pending'))+'</span></'+(url?'a':'div')+'>').join('')+'</div></aside>';}
function endTag(h,start,tag){const re=new RegExp('<\\/?'+tag+'\\b[^>]*>','gi');re.lastIndex=start;let depth=0,m;while((m=re.exec(h))){depth+=m[0].startsWith('</')?-1:1;if(!depth)return re.lastIndex;}throw Error('Unbalanced '+tag);}
let count=0,schemas=0;
for(const f of (await readdir(root)).filter(f=>f.endsWith('.html'))){
 const path=resolve(root,f);let h=await readFile(path,'utf8'); if(!/<main[\s>]/i.test(h))continue;
 const es=/<html[^>]*lang=["']es/i.test(h);
 h=h.replace(/<aside class="luna-social-panel"[\s\S]*?<\/aside>/g,()=>panel(es));
 if(!h.includes('data-luna-social')){
  let m=/<div class="reviews-shell">/.exec(h);
  if(m){let end=endTag(h,m.index,'div'),innerStart=m.index+m[0].length;h=h.slice(0,m.index)+'<div class="reviews-shell luna-reviews-social"><div class="luna-reviews-main">'+h.slice(innerStart,end-6)+'</div>'+panel(es)+'</div>'+h.slice(end);}
  else if(f==='reviews.html'){m=/<div class="review-list">/.exec(h);if(!m)throw Error('Missing review list');let end=endTag(h,m.index,'div');h=h.slice(0,m.index)+'<div class="luna-review-directory">'+h.slice(m.index,end)+panel(es)+'</div>'+h.slice(end);}
  else {let end=h.lastIndexOf('</main>');h=h.slice(0,end)+'<section class="container luna-social-standalone"><div><h2>Real Customer Reviews</h2><p><a href="reviews.html">Read customer reviews and their original sources →</a></p></div>'+panel(es)+'</section>'+h.slice(end);}
 }
 if(!h.includes('luna-social.css'))h=h.replace('</head>','<link rel="stylesheet" href="luna-social.css?v=20261117-1">\n</head>');
 h=h.replace(/(<script\b[^>]*type=["']application\/ld\+json["'][^>]*>)([\s\S]*?)(<\/script>)/gi,(all,open,json,close)=>{
   let data;try{data=JSON.parse(json)}catch{return all}let changed=false;
   function visit(n){if(!n||typeof n!=='object')return;
    const types=[n['@type']].flat();if(types.some(t=>['LocalBusiness','GeneralContractor','HomeAndConstructionBusiness','Organization'].includes(t))&&(/Luna/i.test(n.name||'')||String(n['@id']||'').startsWith('https://lunageneralcontractors.com/'))){
     const previous=[n.sameAs||[]].flat();const old=previous.filter(url=>url!=="https://www.google.com/maps/search/?api=1&query=Luna%20General%20Contractors%2C%204906%20Red%20River%20Trail%2C%20Grand%20Prairie%2C%20TX%2075052"&&!/^https:\/\/(?:www\.)?yellowpages\.com\//.test(url));const next=[...new Set([...old,...profiles.map(p=>p[4]).filter(Boolean)])];if(JSON.stringify(previous)!==JSON.stringify(next)){n.sameAs=next;changed=true;schemas++;}
    }for(const v of Object.values(n))if(typeof v==='object')if(Array.isArray(v))v.forEach(visit);else visit(v);
   }visit(data);return changed?open+'\n'+JSON.stringify(data,null,2)+'\n'+close:all;
 });
 await writeFile(path,h);count++;
}
console.log('Social profiles: '+count+' HTML pages covered; '+schemas+' existing entities updated.');
