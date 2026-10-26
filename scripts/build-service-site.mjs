import {execFileSync} from 'node:child_process';
import {existsSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
// Keep city imagery last: upstream generators may replace guide/photo markup, while
// this scoped pass owns the final 828 city-service gallery blocks.
for(const script of ['build-service-art.mjs','build-page-endings.mjs','build-service-guides.mjs','build-service-hub-illustrations.mjs','repair-project-photo-references.mjs','build-roofing-material-guides.mjs','build-mitigation-projects.mjs','build-mitigation-illustrations.mjs','build-page-endings.mjs','build-customer-reviews.mjs','build-service-city-imagery.mjs']){
 execFileSync(process.execPath,[resolve(root,'scripts',script)],{cwd:root,stdio:'inherit'});
}

// The former additional-hub planning-scene blocks duplicated the reusable
// five-scene gallery, so they stay retired. The final imagery pass below also
// strips any marker-bounded legacy copy from older generated source.

// Final pass restores page-owned concepts and removes real-work photo placements.
// Keep its recoverable audit log in the worktree, rather than in Git's metadata:
// linked worktrees may expose that metadata read-only during validation.
execFileSync(process.env.PYTHON || 'python',[
  resolve(root,'scripts/apply-page-owned-imagery.py'),
  '--apply',
  '--removal-log',resolve(root,'tmp','page-owned-photo-removals.json'),
],{cwd:root,stdio:'inherit'});

// The final imagery pass also reparents the existing form, factual reviews, and
// five owned thumbnails into the post-hero lead layout. Validate that contract
// before a general-gallery build can consume the same page inventory.
execFileSync(process.env.PYTHON || 'python',[
  resolve(root,'scripts/validate-page-lead-layout.py'),
],{cwd:root,stdio:'inherit'});

// Component cards are separate from each page's five-gallery contract. Validate
// them after the final imagery pass so aggregate rebuilds cannot restore an
// old SVG or photo into a mapped card slot.
if(existsSync(resolve(root,'content','component-card-imagery.json'))){
 execFileSync(process.env.PYTHON || 'python',[
  resolve(root,'scripts/validate-component-card-imagery.py'),
 ],{cwd:root,stdio:'inherit'});
}

// Build the separate browse UI after the final page-owned pass. It deliberately
// consumes the immutable ownership manifest without becoming a sixth placement
// or an image-sitemap owner for any scene.
execFileSync(process.env.PYTHON || 'python',[
  resolve(root,'scripts/build-page-owned-general-gallery.py'),
  '--apply',
],{cwd:root,stdio:'inherit'});
