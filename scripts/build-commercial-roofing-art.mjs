import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
const destination = resolve(dirname(fileURLToPath(import.meta.url)), '../assets/commercial-roofing');
await mkdir(destination, {recursive: true});

// Original editorial illustrations, not branded packages or installation details.
for (const [id, title, light, dark, seam] of [
  ['tpo', 'TPO membrane', '#ffffff', '#b9c9ce', 'HEAT-WELDED SEAMS'],
  ['pvc', 'PVC membrane', '#e8edf1', '#9faebb', 'HEAT-WELDED SEAMS'],
  ['epdm', 'EPDM membrane', '#53626b', '#25333d', 'SPECIFIED SEAM TAPE / ADHESIVE']
]) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="260" viewBox="0 0 600 260" role="img" aria-labelledby="title desc"><title id="title">${title} illustration</title><desc id="desc">A generic roofing membrane roll with sheet overlap. Conceptual illustration; not a product photograph or installation detail.</desc><defs><linearGradient id="roll" x2="0" y2="1"><stop stop-color="${light}"/><stop offset=".55" stop-color="${light}"/><stop offset="1" stop-color="${dark}"/></linearGradient><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#7c929c" stroke-opacity=".1"/></pattern></defs><rect width="600" height="260" fill="#eaf0f2"/><rect width="600" height="260" fill="url(#grid)"/><ellipse cx="318" cy="202" rx="209" ry="20" fill="#314b60" opacity=".13"/><path d="M110 190L368 221 506 156 248 126Z" fill="${dark}" stroke="#7d939e"/><path d="M115 182L369 211 496 150 241 121Z" fill="${light}" stroke="#8a9fa8"/><path d="M282 201L412 141" stroke="${id === 'epdm' ? '#151f27' : '#c1ccd0'}" stroke-width="12"/><path d="M282 201L412 141" stroke="#b98e26" stroke-width="2" stroke-dasharray="5 5"/><path d="M168 69L377 91C415 95 437 132 414 156L205 135Z" fill="url(#roll)" stroke="#7d939e"/><ellipse cx="180" cy="101" rx="35" ry="40" transform="rotate(-23 180 101)" fill="${light}" stroke="#7d939e" stroke-width="2"/><ellipse cx="180" cy="101" rx="18" ry="23" transform="rotate(-23 180 101)" fill="${dark}" stroke="#7d939e"/><ellipse cx="180" cy="101" rx="8" ry="11" transform="rotate(-23 180 101)" fill="#314b60"/><text x="26" y="29" font-family="Arial,sans-serif" font-size="12" letter-spacing="2" fill="#48616e">MATERIAL STUDY / ${id.toUpperCase()}</text><text x="26" y="240" font-family="Arial,sans-serif" font-size="11" letter-spacing="1" fill="#48616e">${seam}</text></svg>`;
  await writeFile(resolve(destination, `${id}-reference.svg`), svg, 'utf8');
}

const layers = [
  {y:230,color:'#657985',side:'#3c5361',name:'Structural deck'},
  {y:176,color:'#dcb65c',side:'#aa8234',name:'Insulation'},
  {y:126,color:'#b8bdb4',side:'#7d8b83',name:'Cover board, if specified'},
  {y:77,color:'#f5f7f5',side:'#c5d4d9',name:'Roof membrane'}
];
const artwork = layers.map((layer,i) => `<g><path d="M70 ${layer.y+60}L285 ${layer.y+120} 476 ${layer.y+48} 260 ${layer.y-12}Z" fill="${layer.color}" stroke="#ffffff" stroke-opacity=".45"/><path d="M70 ${layer.y+60}L285 ${layer.y+120} 476 ${layer.y+48}V${layer.y+65}L285 ${layer.y+137} 70 ${layer.y+77}Z" fill="${layer.side}"/><path d="M476 ${layer.y+48}H520" stroke="#d6e3e8" stroke-width="1.5"/><circle cx="536" cy="${layer.y+48}" r="12" fill="#f1bd39"/><text x="536" y="${layer.y+52}" text-anchor="middle" font-family="Arial" font-size="11" font-weight="bold" fill="#15232d">${4-i}</text><text x="558" y="${layer.y+53}" font-family="Arial,sans-serif" font-size="16" fill="#eef4f5">${layer.name}</text></g>`).join('');
await writeFile(resolve(destination, 'roof-assembly.svg'), `<svg xmlns="http://www.w3.org/2000/svg" width="850" height="440" viewBox="0 0 850 440" role="img" aria-labelledby="title desc"><title id="title">A low-slope roof is a layered assembly</title><desc id="desc">Concept diagram showing a membrane, an optional cover board, insulation and a structural deck. Actual assemblies, attachment and air or vapor control layers vary by project.</desc><rect width="850" height="440" rx="16" fill="#17313e"/><text x="38" y="37" fill="#eec24d" font-family="Arial,sans-serif" font-size="12" letter-spacing="2">UNDER THE SURFACE</text>${artwork}<text x="38" y="410" fill="#b9cbd3" font-family="Arial,sans-serif" font-size="13">Concept only · Layer order, attachment and additional components depend on the specified assembly.</text></svg>`, 'utf8');
console.log('Created four original commercial roofing illustrations.');
