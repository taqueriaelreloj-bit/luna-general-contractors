import {execFileSync} from 'node:child_process';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
// Keep city imagery last: upstream generators may replace guide/photo markup, while
// this scoped pass owns the final 828 city-service gallery blocks.
for(const script of ['build-service-art.mjs','build-page-endings.mjs','build-service-guides.mjs','build-service-hub-illustrations.mjs','repair-project-photo-references.mjs','build-roofing-material-guides.mjs','build-mitigation-projects.mjs','build-mitigation-illustrations.mjs','build-page-endings.mjs','build-customer-reviews.mjs','build-service-city-imagery.mjs']){
 execFileSync(process.execPath,[resolve(root,'scripts',script)],{cwd:root,stdio:'inherit'});
}
