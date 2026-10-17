import {readFile,writeFile,readdir} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const home=await readFile(resolve(root,'index.html'),'utf8');
const source=home.match(/<section\b[^>]*class="reviews-section"[^>]*>[\s\S]*?<\/section>/)?.[0];
if(!source)throw new Error('The home-page customer review section is missing.');
const start='<!-- shared-customer-reviews:start -->';
const end='<!-- shared-customer-reviews:end -->';
const css='<link rel="stylesheet" href="customer-reviews.css?v=20261017-reviews-1">';
const translations=[
 ['Real Customer Reviews','Reseñas de nuestros clientes'],
 ['5.0 Google Rating','Calificación de 5.0 en Google'],
 ['Based on 38 reviews','Basado en 38 reseñas'],
 ['View Our Google Profile →','Ver nuestro perfil de Google →'],
 ['Google review','Reseña en Google'],
 ['Professional, reliable and detail-oriented from planning through completion. The craftsmanship and finished work exceeded expectations.','Profesionales, confiables y atentos a los detalles desde la planificación hasta la entrega. La calidad y el resultado del trabajo superaron las expectativas.'],
 ['Top-notch communication, professionalism and attention to detail on a Jack-and-Jill bathroom renovation.','Excelente comunicación, profesionalismo y atención a los detalles en la renovación de un baño compartido entre dos habitaciones.'],
 ['Read review summary · Source: Google →','Leer resumen · Fuente: Google →'],
 ['Nextdoor Neighbor','Vecino de Nextdoor'],
 ['Fair price for great work. Definitely recommend them for general repairs and maintenance.','Un precio justo por un gran trabajo. Definitivamente los recomiendo para reparaciones generales y mantenimiento.'],
 ['View public recommendation →','Ver recomendación original →'],
 ['View All Customer Reviews →','Ver todas las reseñas →'],
 ['All Customer Reviews','Todas las reseñas de clientes'],
 ['Google, Nextdoor and public sources','Google, Nextdoor y fuentes públicas'],
 ['Read customer feedback with the original source identified for every review.','Lee los comentarios de clientes con la fuente original indicada en cada reseña.'],
 ['Free Estimates. No Obligation. Call Today!','Estimados gratis, sin compromiso. ¡Llama hoy!']
];

function section(language){
 let html=source
  .replace('class="reviews-section"','class="reviews-section shared-customer-reviews" data-shared-customer-reviews aria-labelledby="customer-reviews-title"')
  .replace('<h2>','<h2 id="customer-reviews-title">')
  // The home-page SVG symbols are not present on every service page.
  .replace(/<svg\b[^>]*>[\s\S]*?<\/svg>/g,'')
  .replace('Free Estimates.<br />No Obligation.<br />Call Today!','Free Estimates. No Obligation. Call Today!');
 if(language==='es')for(const [english,spanish]of translations)html=html.replaceAll(english,spanish);
 return `${start}\n${html.replace(/[\t ]+$/gm,'')}\n${end}`;
}

const pages=[];
for(const file of (await readdir(root)).filter(file=>file.endsWith('.html')).sort()){
 const path=resolve(root,file);
 let html=await readFile(path,'utf8');
 if(!/<body[\s>]/i.test(html)||!/<main[\s>]/i.test(html))continue;
 const language=/<html\b[^>]*lang=["']es(?:-[^"']*)?["']/i.test(html)?'es':'en';
 const block=section(language);
 if(html.includes(start)){
  const from=html.indexOf(start),to=html.indexOf(end,from);
  if(to<0)throw new Error(`Unclosed customer reviews section: ${file}`);
  html=html.slice(0,from)+block+html.slice(to+end.length);
 }else if(/class="[^"]*\b(?:reviews-section|review-list|full-review)\b/.test(html)||/id="reviews"/.test(html)){
  pages.push({file,language,reviews:'existing'});
  continue;
 }else{
  const estimate=/<section\b[^>]*id="estimate-form"[^>]*>/.exec(html);
  const position=estimate?.index??(html.includes('<!-- page-ending:start -->')?html.indexOf('<!-- page-ending:start -->'):html.lastIndexOf('</main>'));
  if(position<0)throw new Error(`No customer review insertion point: ${file}`);
  html=html.slice(0,position)+block+'\n'+html.slice(position);
 }
 if(!html.includes('customer-reviews.css'))html=html.replace('</head>',`${css}\n</head>`);
 await writeFile(path,html);
 pages.push({file,language,reviews:'shared-home-section'});
}
const inventory={source:'index.html#reviews',totalPages:pages.length,existingSections:pages.filter(p=>p.reviews==='existing').length,sharedSections:pages.filter(p=>p.reviews==='shared-home-section').length,pages};
await writeFile(resolve(root,'content/customer-review-pages.json'),JSON.stringify(inventory,null,2)+'\n');
console.log(`Customer reviews: ${inventory.totalPages} pages covered; ${inventory.existingSections} existing sections and ${inventory.sharedSections} shared sections.`);
