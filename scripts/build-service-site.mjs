import {execFileSync} from 'node:child_process';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
for(const script of ['build-service-art.mjs','build-page-endings.mjs','build-service-guides.mjs','repair-project-photo-references.mjs','build-roofing-material-guides.mjs','build-mitigation-projects.mjs','build-page-endings.mjs','build-customer-reviews.mjs']){
 execFileSync(process.execPath,[resolve(root,'scripts',script)],{cwd:root,stdio:'inherit'});
}
