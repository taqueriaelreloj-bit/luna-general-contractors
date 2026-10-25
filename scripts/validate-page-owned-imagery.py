"""Validate generated-only page placements without changing any source file."""
import json,re,struct,hashlib,sys
from pathlib import Path
from collections import defaultdict
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
ROOT_HERO_PAGES={
 'roofing.html','mitigation.html','insurance-claims.html','kitchens.html',
 'bathrooms.html','flooring.html','painting.html','drywall.html','siding.html',
 'carpentry.html','fencing.html','commercial.html',
}
GALLERY=re.compile(r'<section\b(?=[^>]*\bdata-page-owned-gallery="true")[^>]*>.*?</section>',re.I|re.S)
GALLERY_FIGURE=re.compile(r'<figure\b[^>]*\bdata-page-owned-slot="(\d{2})"[^>]*>(.*?)</figure>',re.I|re.S)
class Images(HTMLParser):
 def __init__(self):super().__init__();self.items=[]
 def handle_starttag(self,t,a):
  if t=='img':self.items.append(dict(a))
def dimensions(path):
 b=path.read_bytes()
 if b.startswith(b'\x89PNG\r\n\x1a\n'):return struct.unpack('>II',b[16:24])
 if b[:4]==b'RIFF' and b[8:12]==b'WEBP':
  if b[12:16]==b'VP8 ':return (int.from_bytes(b[26:28],'little')&16383,int.from_bytes(b[28:30],'little')&16383)
  if b[12:16]==b'VP8X':return (1+int.from_bytes(b[24:27],'little'),1+int.from_bytes(b[27:30],'little'))
  if b[12:16]==b'VP8L':
   n=int.from_bytes(b[21:25],'little');return ((n&16383)+1,((n>>14)&16383)+1)
 raise ValueError('Unsupported/malformed assigned image: '+str(path))
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def srcset_sources(value):
 return [entry.strip().split()[0] for entry in value.split(',') if entry.strip()]
def local_image_path(page,src):
 if not src or src.startswith(('data:','http://','https://','/')):return None
 path=(ROOT/Path(page).parent/src.split('?',1)[0].split('#',1)[0]).resolve()
 try:path.relative_to(ROOT.resolve())
 except ValueError:return None
 return path if path.is_file() else None
def gallery_errors(page,entry,body):
 errors=[];galleries=GALLERY.findall(body)
 if len(galleries)!=1:return [page+': expected exactly one reusable page-owned gallery']
 gallery=galleries[0];figures=GALLERY_FIGURE.findall(gallery)
 expected=sorted(entry['images'],key=lambda item:item['slot'])
 if len(figures)!=5:errors.append(page+': gallery needs five static figures')
 if [slot for slot,_ in figures]!=[f'{item["slot"]:02}' for item in expected]:errors.append(page+': gallery slots must be 01 through 05 in manifest order')
 for item,(slot,figure) in zip(expected,figures):
  if f'src="{item["src"]}"' not in figure:errors.append(page+': gallery source mismatch for slot '+slot)
  if 'data-page-owned-gallery-thumbnail="true"' not in figure:errors.append(page+': gallery thumbnail missing for slot '+slot)
  if 'data-page-owned-gallery-image="true"' not in figure:errors.append(page+': gallery image marker missing for slot '+slot)
  if re.search(r'<figure\b[^>]*(?:\bhidden\b|\baria-hidden="true")',figure,re.I):errors.append(page+': gallery fallback figure is hidden for slot '+slot)
  alt=re.search(r'<img\b[^>]*\balt="([^"]*)"',figure,re.I)
  caption=re.search(r'<figcaption\b[^>]*>(.*?)</figcaption>',figure,re.I|re.S)
  if not alt or not alt[1].strip():errors.append(page+': gallery alt is empty for slot '+slot)
  if not caption or not re.sub(r'<[^>]+>','',caption[1]).strip():errors.append(page+': gallery caption is empty for slot '+slot)
 for control in ('previous','next'):
  if not re.search(r'<button\b(?=[^>]*\btype="button")(?=[^>]*\bdata-page-owned-gallery-'+control+r'\b)(?=[^>]*\baria-label="[^"]+")[^>]*>',gallery,re.I):errors.append(page+': accessible '+control+' gallery control is missing')
 if not re.search(r'data-page-owned-gallery-status\b[^>]*\baria-live="polite"',gallery,re.I):errors.append(page+': live gallery status is missing')
 if 'data-page-owned-gallery-controls' not in gallery:errors.append(page+': gallery controls wrapper is missing')
 return errors
def main():
 data=json.loads((ROOT/'content/page-owned-imagery.json').read_text(encoding='utf-8'));photo_data=json.loads((ROOT/'content/real-job-photo-placements.json').read_text(encoding='utf-8'));photos=photo_data if isinstance(photo_data,list) else photo_data['assets'];owners=defaultdict(set);assigned={};content_owners=defaultdict(set);errors=[]
 for page,e in data.items():
  h=(ROOT/page).read_text(encoding='utf-8');parser=Images();parser.feed(h);srcs={i.get('src') for i in parser.items}
  if h.count('<link rel="stylesheet" href="page-owned-imagery.css">')!=1:
   errors.append(page+': page-owned stylesheet link is missing or duplicated')
  errors.extend(gallery_errors(page,e,h))
  if len(e['images'])!=5 or len({i['src'] for i in e['images']})!=5:errors.append(page+': five unique assignments required')
  for src in srcs:owners[src].add(page)
  for item in parser.items:
   for src in srcset_sources(item.get('srcset','')):owners[src].add(page)
  for i in e['images']:
   if i['src'] not in srcs:errors.append(page+': missing '+i['src'])
   if i['src'] in assigned:errors.append('Repeated assignment: '+i['src'])
   assigned[i['src']]=page
   p=ROOT/i['src']
   if not p.is_file():errors.append('Missing image file: '+i['src']);continue
   if dimensions(p)!=(i['width'],i['height']):errors.append('Dimension mismatch: '+i['src'])
   content_owners[digest(p)].add((page,i['src']))
  if page in ROOT_HERO_PAGES:
   hero=[item for item in parser.items if item.get('data-page-owned-hero')=='true']
   expected=next((item for item in e['images'] if item['slot']==e.get('hero_slot')),None)
   if expected is None:errors.append(page+': missing declared hero slot')
   elif len(hero)!=1 or hero[0].get('src')!=expected['src']:
    errors.append(page+': owned hero does not match its declared page-owned source')
   elif srcs and sum(1 for item in parser.items if item.get('src')==expected['src'])!=2:
    errors.append(page+': hero must render once as hero and once as its gallery thumbnail')
   if '--trade-image:url(' in h.replace(' ','').lower():errors.append(page+': archived photo hero reference remains')
   if 'id="gallery"' not in h:errors.append(page+': hero gallery anchor is missing')
  if page=='home-v2-preview.html':
   inline=[item for item in parser.items if item.get('data-page-owned-inline')=='true']
   expected=e['images'][0]
   if len(inline)!=1 or inline[0].get('src')!=expected['src']:
    errors.append(page+': preview advantage scene does not match its page-owned source')
   if 'Completed Luna General Contractors bathroom project' in h:
    errors.append(page+': stale completed-project aria label remains')
  if page=='index.html':
   home_hero=e['images'][0]['src']
   if sum(1 for item in parser.items if item.get('src')==home_hero)!=2:
    errors.append(page+': homepage hero must also be its gallery thumbnail')
   if '<!-- additional-services-imagery:start -->' in h:
    errors.append(page+': legacy homepage imagery block remains')
   if h.find('data-homepage-reviews')>h.find('data-page-owned-gallery'):
    errors.append(page+': homepage gallery must be inside the reviews mount')
  for src in photos:
   if src in h:errors.append(page+': removed work-photo reference remains: '+src)
  for i in parser.items:
   if not (i.get('alt') or '').strip():errors.append(page+': empty image alt')
   if (i.get('src') or '').startswith(('http://','https://')):errors.append(page+': external image remains')
 # Public runtime code and CSS must not reinsert archived photos after page load.
 for pattern in ('*.css','*.js'):
  for path in ROOT.rglob(pattern):
   if any(part in ('.git','node_modules') for part in path.relative_to(ROOT).parts):continue
   body=path.read_text(encoding='utf-8',errors='replace')
   for src in photos:
    if src in body:errors.append(str(path.relative_to(ROOT))+': runtime photo reference remains: '+src)
 runtime=(ROOT/'script.js').read_text(encoding='utf-8')
 if 'const pageWorkSlides =' in runtime or 'pageMainForWork.append(workGallery)' in runtime:errors.append('Legacy runtime work-photo injector remains')
 rendered_digest_pages=defaultdict(set)
 for page in data:
  h=(ROOT/page).read_text(encoding='utf-8');parser=Images();parser.feed(h)
  rendered_sources={item.get('src') for item in parser.items if item.get('src')}
  rendered_sources.update(source for item in parser.items for source in srcset_sources(item.get('srcset','')))
  for src in rendered_sources:
   path=local_image_path(page,src)
   if path:
    value=digest(path)
    if value in content_owners:rendered_digest_pages[value].add(page)
 for src,page in assigned.items():
  if owners[src]!={page}:errors.append('Image appears on another canonical page: '+src)
 for value,uses in content_owners.items():
  if len(uses)!=1:errors.append('Same generated bytes are assigned to multiple pages: '+value)
  owner_page=next(iter(uses))[0]
  if rendered_digest_pages[value]!={owner_page}:errors.append('Page-owned generated bytes render outside their owner page: '+value)
 for pattern in ('*.css','*.js'):
  for path in ROOT.rglob(pattern):
   if any(part in ('.git','node_modules') for part in path.relative_to(ROOT).parts):continue
   body=path.read_text(encoding='utf-8',errors='replace')
   for src in assigned:
    if src in body:errors.append(str(path.relative_to(ROOT))+': page-owned image is reused at runtime: '+src)
 for src in photos:
  if not (ROOT/src).is_file():errors.append('Original photo was not preserved: '+src)
 gallery_css=(ROOT/'page-owned-imagery.css').read_text(encoding='utf-8')
 for token in ('.page-owned-gallery__track','grid-template-columns:repeat(5','scroll-snap-type:x mandatory','.page-owned-gallery__control'):
  if token not in gallery_css:errors.append('Reusable gallery stylesheet is missing: '+token)
 preview_css=(ROOT/'home-v2-preview.css').read_text(encoding='utf-8')
 if 'Real Luna project' in preview_css:errors.append('Preview CSS still claims a real Luna project')
 home=(ROOT/'index.html').read_text(encoding='utf-8')
 for retired in ('projects-section','Recent Projects','View verified case study','bath-pair','roof-pair','floor-pair','kitchen-pair'):
  if retired in home:errors.append('Homepage obsolete project-card content remains: '+retired)
 if len(data)!=1009 or len(assigned)!=5045:errors.append('Expected 1009 pages and 5045 assigned images')
 if errors:
  print(json.dumps({'errors':errors},indent=2));raise SystemExit(1)
 print(json.dumps({'pages':len(data),'exclusive_assigned_paths':len(assigned),'original_photo_assets_preserved':len(photos),'missing_or_external_images':0,'dimension_checks':'passed'}))
if __name__=='__main__':main()
