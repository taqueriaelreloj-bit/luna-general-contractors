import {readFile, writeFile, readdir, mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {dirname, resolve} from 'node:path';
const root=resolve(dirname(fileURLToPath(import.meta.url)), '..');
const home=await readFile(resolve(root,'index.html'),'utf8');
const footerMatch=home.match(/<footer class="site-footer"[\s\S]*?<\/footer>/);
if(!footerMatch) throw new Error('Home footer missing');
const footer=footerMatch[0].replace('<footer class="site-footer"','<footer class="site-footer" data-complete-footer="true"')
 .replace('href="#home"','href="index.html"').replace('href="#about"','href="index.html#about"').replace('href="#projects"','href="projects.html"').replace('href="#contact"','href="#site-contact"')
 .replace(/<svg[^>]*>[\s\S]*?<\/svg>/g,'').replace('<span id="year"></span>','<span data-footer-year>2026</span>');
const ending=`<!-- page-ending:start -->
<section class="contact-section complete-contact" id="site-contact" aria-labelledby="site-contact-heading"><div class="container contact-grid"><div><p class="eyebrow">Start Your Project</p><h2 id="site-contact-heading">Request Your Free Estimate</h2><p>Tell us about your property and the work you have in mind. We can discuss the scope, access, material selections and next steps.</p></div><div class="contact-actions"><a class="btn btn-gold" href="tel:+18177845998">Call (817) 784-5998</a><a class="btn btn-outline" href="mailto:lunabestcontractors@gmail.com">Email lunabestcontractors@gmail.com</a></div></div></section>
<!-- page-ending:end -->`;
const form=`<section class="local-form complete-estimate" id="estimate-form"><div class="container"><p class="eyebrow gold">Let's discuss your project</p><h2>Request a Free Estimate</h2><form action="https://formspree.io/f/maqrzbol" method="POST" class="estimate-form"><label>Full name<input name="name" autocomplete="name" required></label><label>Phone number<input type="tel" name="phone" autocomplete="tel" required></label><label>Email<input type="email" name="email" autocomplete="email" required></label><label>Project address<input name="address" autocomplete="street-address"></label><label>Project details<textarea name="message" rows="4" required></textarea></label><button class="btn btn-gold" type="submit">Request Your Estimate</button><small>We respect your privacy. <a href="privacy.html">Privacy notice</a>.</small><p class="form-message" role="status" aria-live="polite"></p></form></div></section>`;
const inventory=[];
for(const name of (await readdir(root)).filter(n=>n.endsWith('.html')).sort()){
 let html=await readFile(resolve(root,name),'utf8');
 if(!/<body[\s>]/i.test(html) || !/<main[\s>]/i.test(html)) {inventory.push({file:name,skipped:'No normal page body/main'});continue;}
 const isHome=['index.html','es.html'].includes(name);
 if(!/\bcomplete-page\b/.test(html)) html=html.replace(/<body([^>]*)>/,(_,attrs)=> /class=/.test(attrs)?`<body${attrs.replace(/class="([^"]*)"/,'class="$1 complete-page"')}>`:`<body${attrs} class="complete-page">`);
 html=html.replace(/\s*<link[^>]*href="\/?(?:\.\.\/)*styles\.css(?:\?[^"<>]*)?"[^>]*>/g,'');
 html=html.replace('</head>','<link rel="stylesheet" href="styles.css?v=20261016-services-1">\n<link rel="stylesheet" href="service-guides.css?v=20261016-services-1">\n</head>');
 html=html.replace(/\s*<link[^>]*href="service-guides\.css(?:\?[^"<>]*)?"[^>]*>(?=[\s\S]*<link[^>]*href="service-guides\.css)/g,'');
 html=html.replace(/\s*<script[^>]*src="(?:\.\.\/)*script\.js(?:\?[^"<>]*)?"[^>]*>\s*<\/script>/g,'');
 html=html.replace('</body>','<script src="script.js?v=20261016-services-1" defer></script>\n</body>');
 if(!isHome){
  html=html.replace(/<section class="roofing-end-bar"[^>]*>[\s\S]*?<\/section>/g,'');
  html=html.replace(/<section class="trade-cta"[^>]*>[\s\S]*?<\/section>/g,section=>section.includes('Tell us what you need. Our team will contact you')?'':section);
  html=html.replace(/<section class="local-form"[^>]*>[\s\S]*?<\/section>/g,section=>/<form\b/.test(section)?section:'');
  if(!/id="contact"/.test(html))html=html.replaceAll('href="#contact"','href="#site-contact"');
  html=html.replace(/<!-- page-ending:start -->[\s\S]*?<!-- page-ending:end -->\s*/g,'');
  html=html.replace(/<footer\b[\s\S]*?<\/footer>/g,'');
  if(!/id="estimate-form"/.test(html) && name!=='privacy.html') html=html.replace('</main>',`${form}\n</main>`);
  const contact=name==='privacy.html'?ending.replace('',''):ending;
  html=html.replace('</main>',`${contact}\n</main>`).replace('</main>',`</main>\n${footer}`);
  let hasFloatingCall=false;
  html=html.replace(/<a\b[^>]*class="[^"]*\bfloating-call\b[^"]*"[^>]*>[\s\S]*?<\/a>/g,anchor=>{if(hasFloatingCall)return '';hasFloatingCall=true;return anchor;});
  if(!hasFloatingCall) html=html.replace('</body>','<a class="floating-call" href="tel:+18177845998" aria-label="Call Luna General Contractors" data-label="Call now">☎</a>\n</body>');
 }
 if(name==='es.html')html=html.replaceAll('href="#inicio"','href="#page-top"');
 const eol=html.includes('\r\n')?'\r\n':'\n';
 html=html.replace(/[\t ]+(?=\r?$)/gm,'').replace(/\r?\n(?:[\t ]*\r?\n){2,}/g,eol+eol).trimEnd()+eol;
 await writeFile(resolve(root,name),html);
 inventory.push({file:name,home:isHome,footer:true,estimate:/id="estimate-form"/.test(html)});
}
await mkdir(resolve(root,'content'),{recursive:true});
await writeFile(resolve(root,'content/page-inventory.json'),JSON.stringify(inventory,null,2)+'\n');
console.log(`Complete static page endings: ${inventory.filter(p=>p.footer).length}; skipped: ${inventory.filter(p=>p.skipped).length}`);
