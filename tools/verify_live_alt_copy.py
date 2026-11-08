from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from urllib.request import Request, urlopen
sys.path.insert(0, str(Path.cwd()/'scripts'))
from image_alt_text import embedded_alt, source_path, StartTags, HUBS

ROOT = Path.cwd()
BASE = 'https://lunageneralcontractors.com/'
ALTS = {p.relative_to(ROOT).as_posix():alt for p in (ROOT/'assets/images').rglob('*.webp') if (alt:=embedded_alt(p))}
OWNED = json.loads((ROOT/'content/page-owned-imagery.json').read_text())
PROFILES = json.loads((ROOT/'content/service-search-copy.json').read_text())

def fetch(path):
    last = None
    for attempt in range(3):
        try:
            req = Request(BASE+path, headers={'User-Agent':'Luna-Published-Alt-Verification/1.0','Cache-Control':'no-cache'})
            with urlopen(req, timeout=30) as response:
                return response.status, response.read()
        except Exception as exc:
            last = str(exc)
            time.sleep(attempt+1)
    raise RuntimeError(last)

def values(text):
    return [(source_path(a.get('src') or ''), a.get('alt')) for _,_,t,a in StartTags(text).tags
            if t=='img' and source_path(a.get('src') or '') in ALTS]

def intro(text):
    match = re.search(r'<h1\b[^>]*>.*?</h1>\s*<p\b[^>]*>(.*?)</p>',text,re.S|re.I)
    return match[1] if match else None

def page_check(name):
    row={'page':name,'url':BASE+name}
    try:
        expected=(ROOT/name).read_text()
        status,data=fetch(name)
        actual=data.decode('utf-8')
        observed=values(actual)
        assert observed==values(expected),'Published image sources/alt differ from expected source'
        assert all(alt==ALTS[path] for path,alt in observed),'Published alt differs from embedded image metadata'
        key=HUBS.get(name) or OWNED.get(name,{}).get('category')
        copy_target=name in HUBS or key in PROFILES and name.endswith('-'+key+'.html')
        if copy_target:
            assert intro(actual)==intro(expected),'Published service introduction is stale'
            metas=lambda t:{a.get('property') or a.get('name'):a.get('content') for _,_,tag,a in StartTags(t).tags if tag=='meta' and (a.get('property') or a.get('name')) in ('description','og:description','twitter:description')}
            assert metas(actual)==metas(expected),'Published service description is stale'
        row.update(ok=True,http_status=status,placements=len(observed),images=[x[0] for x in observed],service_copy_checked=bool(copy_target))
    except Exception as exc:
        row.update(ok=False,error=str(exc))
    return row

pages=[]
names=sorted(set(OWNED)|{'gallery.html'})
with ThreadPoolExecutor(max_workers=8) as pool:
    for f in as_completed([pool.submit(page_check,name) for name in names]):
        pages.append(f.result())
        if len(pages)%250==0:print(json.dumps({'pages_checked':len(pages),'errors':sum(not p['ok'] for p in pages)}),flush=True)
gallery=[]
for name in ('page-owned-gallery-data.json','component-card-gallery-data.json','general-gallery-data.json'):
    row={'file':'content/'+name}
    try:
        status,data=fetch(row['file']);records=json.loads(data)
        tracked=[r for r in records if r.get('src') in ALTS]
        assert all(r.get('alt')==ALTS[r['src']] for r in tracked),'Gallery JSON has stale alt text'
        row.update(ok=True,http_status=status,matched_records=len(tracked))
    except Exception as exc:row.update(ok=False,error=str(exc))
    gallery.append(row)
summary={'checked_at_utc':datetime.now(timezone.utc).isoformat(),
         'verification_source':'Public HTTP URLs after deployment',
         'pages_checked':len(pages),'pages_passed':sum(p['ok'] for p in pages),
         'pages_failed':sum(not p['ok'] for p in pages),
         'unique_prepared_images_verified':len({s for p in pages if p['ok'] for s in p['images']}),
         'html_image_placements_verified':sum(p.get('placements',0) for p in pages),
         'service_copy_pages_verified':sum(p.get('service_copy_checked',False) for p in pages),
         'gallery_data_checks':gallery}
report={'summary':summary,'pages':sorted(pages,key=lambda p:p['page'])}
Path('/tmp/Luna_Alt_Text_SEO_Verificado_2026-11-08.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('FINAL_ALT_COPY_VERIFICATION '+json.dumps(summary),flush=True)
assert summary['pages_failed']==0 and summary['unique_prepared_images_verified']==7657
assert all(r['ok'] for r in gallery)
