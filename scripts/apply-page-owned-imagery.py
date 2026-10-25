#!/usr/bin/env python3
"""Deterministic final imagery pass. No network, Git, publishing or image generation.

Manifest: {"page.html": {category,label,city,images:[{slot,src,width,height}],placement_hold}}.
Default is dry-run. --apply writes only after all eligible pages validate; --check
fails if output is stale. This pass belongs last in build-service-site.mjs.
"""
import argparse,html,json,re,sys
from pathlib import Path

START='<!-- page-owned-imagery:start -->';END='<!-- page-owned-imagery:end -->'
STYLE='<link rel="stylesheet" href="page-owned-imagery.css?v=20261025-full-image-1">'
CSS='''.page-owned-gallery{margin:32px auto;padding:clamp(16px,2.5vw,28px);background:#f4f4f1;color:#17191c;border-top:4px solid #e5a000}.page-owned-gallery__heading{margin:0 0 14px;font-size:clamp(1.3rem,2vw,1.8rem)}.page-owned-gallery__track{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}.page-owned-gallery__item{min-width:0;margin:0;background:#fff;border:1px solid #deded8;border-radius:5px;overflow:hidden}.page-owned-gallery__thumbnail{display:block;width:100%;aspect-ratio:4/3;overflow:hidden;padding:0;border:3px solid transparent;background:#fff;color:inherit;cursor:pointer;text-align:inherit;transition:border-color .16s ease,box-shadow .16s ease}.page-owned-gallery__thumbnail[aria-current="true"]{border-color:#b87b00;box-shadow:0 0 0 2px rgba(184,123,0,.22)}.page-owned-gallery__thumbnail:focus-visible,.page-owned-gallery__control:focus-visible{outline:3px solid #005fcc;outline-offset:3px}.page-owned-gallery__thumbnail img{display:block;width:100%;height:100%;aspect-ratio:auto;object-fit:cover}.page-owned-gallery__item figcaption{min-height:3.1em;padding:9px 10px;color:#17191c;font-size:.88rem;font-weight:700;line-height:1.35}.page-owned-gallery__controls{display:flex;align-items:center;justify-content:flex-end;gap:10px;margin-top:14px}.page-owned-gallery__control{min-width:44px;min-height:44px;padding:8px 14px;border:1px solid #24282c;border-radius:4px;background:#17191c;color:#fff;font:inherit;font-weight:700;cursor:pointer}.page-owned-gallery__control:disabled{opacity:.48;cursor:not-allowed}.page-owned-gallery__status{min-width:6.5em;margin-right:auto;color:#50545a;font-size:.9rem}.poi-notice{color:#50545a;line-height:1.5}.poi-roofing-page .mr-story,.poi-roofing-page .mr-detail-row,.poi-roofing-page .cr-assembly{display:block}
.poi-hero{position:relative;isolation:isolate;overflow:hidden;background:#05080a}.poi-hero-image{position:absolute;inset:0;z-index:0;display:block;width:100%;height:100%;object-fit:cover}.poi-hero::after{content:"";position:absolute;inset:0;z-index:1;pointer-events:none;background:linear-gradient(90deg,rgba(2,4,6,.94),rgba(2,4,6,.65) 55%,rgba(2,4,6,.25))}.poi-hero>.trade-hero-copy{position:relative;z-index:2}.poi-gallery-anchor{display:block;scroll-margin-top:1rem}
@media(max-width:900px){.page-owned-gallery__track{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:620px){.page-owned-gallery{padding:16px}.page-owned-gallery__track{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(150px,72vw);grid-template-columns:none;overflow-x:auto;padding-bottom:4px;scroll-snap-type:x mandatory;scrollbar-width:thin}.page-owned-gallery__item{scroll-snap-align:start}.page-owned-gallery__item figcaption{font-size:.84rem}.page-owned-gallery__controls{justify-content:space-between}.page-owned-gallery__status{margin-right:0}.poi-hero-image{object-position:center}}
.page-owned-gallery__all-link{display:inline-flex;align-items:center;min-height:44px;padding:8px 12px;color:#17252b;font-weight:800;text-decoration:underline;text-underline-offset:3px}.page-owned-gallery__all-link:hover{color:#8a5a00}.page-owned-gallery__all-link:focus-visible{outline:3px solid #005fcc;outline-offset:3px}
@media(max-width:620px){.page-owned-gallery__controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));justify-content:stretch}.page-owned-gallery__status,.page-owned-gallery__all-link{grid-column:1/-1}.page-owned-gallery__all-link{width:max-content;padding-left:0}.page-owned-gallery__control{width:100%}}
.page-owned-gallery__thumbnail{aspect-ratio:16/10;background:#111820}.page-owned-gallery__thumbnail img{object-fit:contain;background:#111820}
'''
FIGURE=re.compile(r'<figure\b[^>]*>.*?</figure>',re.S|re.I)
SRC=re.compile(r'<img\b[^>]*\bsrc="([^"]+)"',re.I)
SENSITIVE=set()

def bounded(pattern,replacement,text,allowed):
 result,n=re.subn(pattern,replacement,text,flags=re.S)
 if n not in allowed:raise ValueError(f'Unexpected structure: {pattern}: {n}')
 return result

def block(text,start,end):
 if text.count(start)!=text.count(end) or text.count(start)>1:raise ValueError(f'Unpaired/duplicate {start}')
 return re.search(re.escape(start)+r'.*?'+re.escape(end),text,re.S)

def remove_previous(text):
 for start,end in [(START,END),('<!-- page-owned-concepts:start -->','<!-- page-owned-concepts:end -->')]:
  m=block(text,start,end)
  if m:text=text[:m.start()]+text[m.end():]
 # Initial migration may have the earlier pilot's explicit section rather than markers.
 text=bounded(r'<section class="page-owned-roof-gallery"[^>]*>.*?</section>','',text,{0,1})
 # Remove only this pass's stylesheet; it is reinstated deterministically.
 # Input pages may retain CRLF line endings on Windows.
 return re.sub(r'<link rel="stylesheet" href="page-owned-imagery\.css(?:\?v=[^"]+)?">(?:\r?\n)?','',text)

def remove_obsolete_home_project_cards(text):
 # The former homepage project grid mixed incomplete, misleading comparisons with
 # a verified-case-study claim. Preserve source files, but do not present those
 # cards until truthful page-specific replacements exist.
 text=bounded(r'<section class="section projects-section" id="projects">.*?</section>','',text,{0,1})
 return text.replace('href="#projects"','href="projects.html"')

def remove_home_legacy_gallery_blocks(text):
 # Homepage slots 02--03 used to live near the footer while slots 04--05
 # used the shared marker. The reusable component owns all five slots beside
 # reviews, so remove only those deterministic legacy containers.
 m=block(text,'<!-- additional-services-imagery:start -->','<!-- additional-services-imagery:end -->')
 if m:text=text[:m.start()]+text[m.end():]
 return text

def replace_preview_advantage(text,entry):
 # The preview formerly paired this block with a removed portfolio photo and a
 # "Real Luna project" label. Keep the layout useful with its own page-owned
 # design scene instead of implying that the visual documents completed work.
 image=entry['images'][0]
 caption='Design concepts · Dallas–Fort Worth'
 figure=(f'<figure class="v2-advantage-image" data-page-owned-inline="true" '
         f'data-page-owned-slot="{int(image["slot"]):02}">'
         f'<img data-page-owned-inline="true" src="{html.escape(image["src"],quote=True)}" '
         f'alt="Material selections and design concepts · Dallas–Fort Worth" '
         f'width="{int(image["width"])}" height="{int(image["height"])}" '
         f'loading="lazy" decoding="async"><figcaption>{caption}</figcaption></figure>')
 return bounded(r'<(div|figure)\b[^>]*\bclass="v2-advantage-image"[^>]*>.*?</\1>',figure,text,{1})

def hero_image(entry):
 slot=entry.get('hero_slot')
 if slot is None:return None
 image=next((item for item in entry['images'] if item['slot']==slot),None)
 if image is None:raise ValueError('Missing declared hero slot')
 return image

def insert_owned_hero(text,entry,page):
 image=hero_image(entry)
 if image is None:return text,None
 # Rebuild from the exact page-owned source on every pass so a repeated final
 # generation never accumulates hero markup.
 text=re.sub(r'\s*<img\b[^>]*\bdata-page-owned-hero="true"[^>]*>','',text,flags=re.I)
 match=re.search(r'<section\b(?=[^>]*\bclass="[^"]*\btrade-hero\b[^"]*")[^>]*>',text,re.I)
 if not match:raise ValueError('Missing trade hero '+page)
 opening=match.group()
 def add_class(class_match):
  classes=class_match[1].split()
  if 'poi-hero' not in classes:classes.append('poi-hero')
  return 'class="'+' '.join(classes)+'"'
 opening=re.sub(r'class="([^"]*)"',add_class,opening,count=1,flags=re.I)
 city=entry.get('city') or 'Dallas-Fort Worth';subject=image.get('caption_subject',entry['label'])
 alt=html.escape(f'{subject} - {city}',quote=True)
 markup=(f'<img class="poi-hero-image" data-page-owned-hero="true" src="{html.escape(image["src"],quote=True)}" '
         f'alt="{alt}" width="{int(image["width"])}" height="{int(image["height"])}" decoding="async" fetchpriority="high">')
 return text[:match.start()]+opening+markup+text[match.end():],image

def ensure_gallery_anchor(text,entry):
 if hero_image(entry) is None or 'id="gallery"' in text:return text
 # Some hubs keep their four non-hero scenes in an existing additional-images
 # section rather than the common hub marker. Give the existing section's
 # location a stable target instead of duplicating those owned scenes.
 marker=re.search(r'<!-- additional-[a-z0-9-]+-imagery:start -->',text,re.I)
 if not marker:raise ValueError('Missing gallery target for root hero')
 anchor='<span id="gallery" class="poi-gallery-anchor" aria-hidden="true"></span>'
 return text[:marker.start()]+anchor+text[marker.start():]

def render_gallery(entry,images,genuine=()):
 label=entry['label'];city=entry.get('city') or 'Dallas–Fort Worth'
 gallery_id=' id="gallery"' if hero_image(entry) else ''
 heading=entry.get('gallery_title') or ('Planning & design ideas' if entry['category']=='project-case-studies' else f'{label} · {city}')
 cards=[]
 for i in sorted(images,key=lambda x:x['slot']):
  esc=lambda v:html.escape(str(v),quote=True)
  subject=i.get('caption_subject',label)
  caption=f'{subject} · {city}'
  alt=f'{subject if "concept" in subject.lower() else subject+" design concept"} · {city}'
  slot=f'{int(i["slot"]):02}'
  # The button's aria-label already names the action. Avoid an additional
  # absolutely positioned screen-reader span: five such spans in the mobile
  # horizontal track can enlarge the document's scroll width in Chromium.
  cards.append(f'<figure class="page-owned-gallery__item" data-representative-generated-illustration="true" data-page-owned-slot="{slot}"><button class="page-owned-gallery__thumbnail" type="button" data-page-owned-gallery-thumbnail="true" aria-current="{str(i["slot"]==1).lower()}" aria-label="View {esc(caption)}"><img data-page-owned-gallery-image="true" src="{esc(i["src"])}" alt="{esc(alt)}" width="{int(i["width"])}" height="{int(i["height"])}" loading="lazy" decoding="async"></button><figcaption>{esc(caption)}</figcaption></figure>')
 controls='<div class="page-owned-gallery__controls" data-page-owned-gallery-controls hidden><span class="page-owned-gallery__status" data-page-owned-gallery-status aria-live="polite">Image 1 of 5</span><a class="page-owned-gallery__all-link" href="gallery.html" data-page-owned-gallery-all>View Full Gallery</a><button class="page-owned-gallery__control" type="button" data-page-owned-gallery-previous aria-label="Show previous image" disabled>Previous</button><button class="page-owned-gallery__control" type="button" data-page-owned-gallery-next aria-label="Show next image">Next</button></div>'
 return START+'<section class="page-owned-gallery container"'+gallery_id+' data-page-owned-gallery="true" data-page-owned-imagery="true" aria-labelledby="page-owned-gallery-title"><h2 class="page-owned-gallery__heading" id="page-owned-gallery-title">'+html.escape(heading)+'</h2><div class="page-owned-gallery__track" data-page-owned-gallery-track>'+''.join(cards+list(genuine))+'</div>'+controls+'</section>'+END

def insert_homepage_gallery(text,entry):
 gallery=render_gallery(entry,entry['images'])
 pattern=r'(<div\b[^>]*\bdata-homepage-reviews\b[^>]*>)(.*?)(</div>)'
 return bounded(pattern,lambda m:m[1]+gallery+m[3],text,{1})

def keep_genuine(markup):
 genuine=[]
 for f in FIGURE.findall(markup):
  if any(x in f for x in ['data-media-kind="genuine-portfolio-photo"','data-media-kind="portfolio-photo"','data-substantive-scene="portfolio-photo"']):raise ValueError('Unremoved work-photo figure: confirm asset inventory before proceeding')
  elif 'representative-illustration' not in f and 'data-representative-generated-illustration="true"' not in f:raise ValueError('Unclassified figure in replaceable gallery')
 return genuine

def clean_basic_service_art(text):
 # Component illustrations remain until the separate three-card replacement batch.
 return text

def transform_roof(text,entry,hub=False):
 for name in ['roofing-products','metal-roofing','commercial-roofing']:
  if not block(text,f'<!-- {name}:start -->',f'<!-- {name}:end -->'):raise ValueError('Missing roof guide '+name)
 # Retain brand text/links; never put generated generic scenes inside brand cards.
 text=bounded(r'<figure class="rp-photo">.*?</figure>','',text,{0,3})
 text=bounded(r'<p class="rp-fine-print"><strong>(?:About the photos|Material selection):</strong>.*?</p>','<p class="rp-fine-print"><strong>Material selection:</strong> Confirm supplier availability, the exact model and final color for your estimate.</p>',text,{0,1})
 text=text.replace('before comparing the packages below.','before comparing the product references below.')
 for role in ['primary','detail']:
  text=bounded(r'<figure class="mr-photo mr-photo--(?:panorama|landscape|portrait) mr-photo--'+role+r'">.*?</figure>','',text,{0,1})
 text=bounded(r'<p class="mr-photo-note">.*?</p>','',text,{0,1})
 text=bounded(r'<div class="cr-reference-photos">.*?</div>','',text,{0,1})
 if hub:
  if re.search(r'<img[^>]*src="(?:https?://|assets/metal-roofing/|assets/commercial-roofing/(?:membrane-work.jpg|epdm-roof.jpg))',text):raise ValueError('Unclassified remaining roofing hub reference')
  return text
 old=block(text,'<!-- roofing-city-illustrations:start -->','<!-- roofing-city-illustrations:end -->')
 gallery=render_gallery(entry,entry['images'])
 if old:text=text[:old.start()]+text[old.end():]
 anchor='<!-- commercial-roofing:end -->';text=text.replace(anchor,anchor+gallery,1)
 if not re.search(r'<body\b[^>]*\bclass=',text):text=text.replace('<body','<body class="poi-roofing-page"',1)
 else:text=re.sub(r'(<body\b[^>]*\bclass=")([^"]*)',lambda m:m[1]+m[2] if 'poi-roofing-page' in m[2].split() else m[1]+m[2]+' poi-roofing-page',text,count=1)
 if re.search(r'<img[^>]*src="(?:https?://|assets/metal-roofing/|assets/commercial-roofing/(?:membrane-work.jpg|epdm-roof.jpg))',text):raise ValueError('Unclassified remaining roof reference image')
 return text

def replace_root_hub_gallery(text,entry,page,images):
 markers={
  'roofing.html':('<!-- roofing-hub-illustrations:start -->','<!-- roofing-hub-illustrations:end -->'),
  'mitigation.html':('<!-- mitigation-illustrations:start -->','<!-- mitigation-illustrations:end -->'),
 }
 marker=markers.get(page)
 if not marker:return text,False
 old=block(text,*marker)
 if not old:raise ValueError('Missing root hub illustration marker '+page)
 gallery=render_gallery(entry,images)
 return text[:old.start()]+marker[0]+gallery+marker[1]+text[old.end():],True

def dedupe_assigned_figures(text,entry):
 # The gallery intentionally repeats every owned scene as a compact thumbnail.
 # Protect that deterministic marker block while removing legacy duplicate
 # figures elsewhere on the same page.
 gallery=block(text,START,END)
 protected='__PAGE_OWNED_GALLERY__'
 gallery_markup=''
 if gallery:
  gallery_markup=gallery.group()
  text=text[:gallery.start()]+protected+text[gallery.end():]
 assigned={item['src'] for item in entry['images']}
 # A hero is intentionally outside a figure. Treat it as already owned before
 # walking figures so its old gallery card is removed rather than duplicated.
 seen={m[1] for tag in re.findall(r'<img\b[^>]*>',text,re.I) if 'data-page-owned-hero="true"' in tag for m in [SRC.search(tag)] if m};removals=[]
 for match in FIGURE.finditer(text):
  sources=SRC.findall(match[0])
  matched=[source for source in sources if source in assigned]
  if len(matched)==1:
   source=matched[0]
   if source in seen:removals.append((match.start(),match.end()))
   else:seen.add(source)
 for start,end in reversed(removals):text=text[:start]+text[end:]
 # Upstream builders may introduce spacer-only or repeated blank lines around
 # regenerated blocks. Normalize them once at the final ownership boundary so
 # repeated aggregate builds are byte-stable without changing semantics.
 text=re.sub(r'[ \t]+(?=\n)','',text)
 text=re.sub(r'\n{3,}','\n\n',text)
 return text.replace(protected,gallery_markup)

def transform(original,entry,page):
 # Recover genuine gallery figures before clearing previous owned markup.
 prior=block(original,START,END);prior_genuine=keep_genuine(prior.group()) if prior else []
 text=remove_previous(original)
 if page=='index.html':
  text=remove_obsolete_home_project_cards(text)
  text=remove_home_legacy_gallery_blocks(text)
 if page=='home-v2-preview.html':text=replace_preview_advantage(text,entry)
 if page=='roofing.html':text=transform_roof(text,entry,hub=True)
 text,hero=insert_owned_hero(text,entry,page)
 hero_src=hero['src'] if hero else None
 city=block(text,'<!-- service-city-imagery:start -->','<!-- service-city-imagery:end -->')
 roofing=entry['category']=='roofing' and page.endswith('-roofing.html')
 if page=='index.html':
  # Slot 01 remains the accessible homepage hero. The same page-owned scene
  # is also a compact thumbnail so visitors can inspect all five scenes below
  # the moved reviews without borrowing media from another URL.
  text=insert_homepage_gallery(text,entry)
 elif roofing:text=transform_roof(text,entry)
 elif city:
  genuine=keep_genuine(city.group())+prior_genuine
  genuine=list(dict.fromkeys(genuine))
  text=text[:city.start()]+'<!-- service-city-imagery:start -->'+render_gallery(entry,entry['images'],genuine)+'<!-- service-city-imagery:end -->'+text[city.end():]
  text=clean_basic_service_art(text)
 else:
  text,replaced_root_gallery=replace_root_hub_gallery(text,entry,page,entry['images'])
  if not replaced_root_gallery:
   hub=block(text,'<!-- service-hub-illustrations:start -->','<!-- service-hub-illustrations:end -->')
   if hub:
    if not all(s.startswith('assets/images/illustrations/') for s in SRC.findall(hub.group())):raise ValueError('Unclassified hub image')
    gallery=render_gallery(entry,entry['images'],prior_genuine)
    text=text[:hub.start()]+'<!-- service-hub-illustrations:start -->'+gallery+'<!-- service-hub-illustrations:end -->'+text[hub.end():]
   else:
    gallery=render_gallery(entry,entry['images'],prior_genuine)
    anchor='<!-- shared-customer-reviews:start -->' if '<!-- shared-customer-reviews:start -->' in text else '</main>'
    if anchor in text:offset=text.index(anchor)
    else:
     m=re.search(r'<footer\b',text,re.I)
     if not m:raise ValueError('No safe gallery insertion anchor')
     offset=m.start()
    text=text[:offset]+gallery+text[offset:]
 text=ensure_gallery_anchor(text,entry)
 text=dedupe_assigned_figures(text,entry)
 # Every manifest page can render page-owned content in a legacy service block,
 # even when it has no generic gallery marker. Reinstall this stylesheet on all
 # transformed pages so the output never depends on a marker shape.
 if '</head>' not in text:raise ValueError('Missing head close')
 text=text.replace('</head>',STYLE+'\n</head>',1)
 # Genuine non-illustrative/non-reference image elements remain intact.
 removed_prefixes=('assets/images/illustrations/','assets/service-guides/')
 if roofing or page=='roofing.html':removed_prefixes+=('assets/metal-roofing/','assets/commercial-roofing/','https://mobileimages.lowes.com/')
 for image in re.findall(r'<img\b[^>]*>',original):
  src=SRC.search(image)
  if src and not src[1].startswith(removed_prefixes) and image not in text:raise ValueError('Genuine or unclassified image changed: '+src[1])
 for i in entry['images']:
  if i['src'] not in SRC.findall(text):raise ValueError('Assigned image absent: '+i['src'])
 if hero:
  if text.count('data-page-owned-hero="true"')!=1:raise ValueError('Expected one page-owned hero '+page)
  if SRC.findall(text).count(hero_src)!=2:raise ValueError('Expected hero and gallery thumbnail '+page)
 if text.count(START)>1:raise ValueError('Duplicate owned gallery')
 return text

# Confirmed work-photo placements are removed; source assets are never modified.
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import posixpath,hashlib

def photo_key(value,file='index.html'):
 value=html.unescape(value).strip()
 if value.startswith('data:'):return None
 u=urlsplit(value)
 if u.netloc and u.netloc not in {'lunageneralcontractors.com','www.lunageneralcontractors.com'}:return None
 path=unquote(u.path)
 if not path:return None
 if path.startswith('/'):return posixpath.normpath(path.lstrip('/'))
 return posixpath.normpath(posixpath.join(posixpath.dirname(file),path))

class PhotoNodes(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=False);self.text=text;self.lines=[0];self.nodes=[];self.stack=[]
  self.lines += [m.end() for m in re.finditer('\n',text)];self.feed(text);self.close()
 def pos(self):
  line,col=self.getpos();return self.lines[line-1]+col
 def handle_starttag(self,tag,attrs):
  start=self.pos();raw=self.get_starttag_text();node={'tag':tag,'attrs':dict(attrs),'start':start,'open_end':start+len(raw),'end':None,'parent':self.stack[-1] if self.stack else None}
  self.nodes.append(node)
  if tag in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:node['end']=node['open_end']
  else:self.stack.append(node)
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  if self.stack and self.stack[-1] is self.nodes[-1]:self.stack.pop()['end']=self.nodes[-1]['open_end']
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i]['tag']==tag:
    end=self.text.find('>',self.pos())+1
    for n in self.stack[i:]:n['end']=end
    del self.stack[i:];break

def strip_real_photos(text,assets,file):
 edits=[]
 def known(value):return photo_key(value or '',file) in assets
 if file.endswith('.css'):
  for m in re.finditer(r'url\(\s*(["\']?)(.*?)\1\s*\)',text,re.I):
   if known(m[2]):edits.append((m.start(),m.end(),'none','confirmed-photo-css-url',photo_key(m[2],file)))
 else:
  tree=PhotoNodes(text)
  for n in tree.nodes:
   a=n['attrs'];tag=n['tag'];matched=[(k,v) for k,v in a.items() if v and k in {'src','href','xlink:href','poster','data-src','data-image','data-full','data-before','data-after','data-background','content'} and known(v)]
   if a.get('srcset'):
    matched += [('srcset',x.strip().split()[0]) for x in a['srcset'].split(',') if x.strip() and known(x.strip().split()[0])]
   if matched:
    target=n
    if tag in {'img','source','image','video'}:
     chain=[];parent=n['parent']
     while parent:
      chain.append(parent);parent=parent['parent']
     comparisons=[p for p in chain if re.search(r'(?:before[-_]?after|comparison-slider|ba-slider)',p['attrs'].get('class','')+' '+p['attrs'].get('id',''),re.I)]
     gallery_classes={'city-gallery','portfolio-proof','gallery-section','mp-gallery','project-gallery'}
     galleries=[p for p in chain if gallery_classes.intersection(p['attrs'].get('class','').split()) and p['end'] is not None and all(known(src) for src in SRC.findall(text[p['start']:p['end']]))]
     figures=[p for p in chain if p['tag']=='figure'];pictures=[p for p in chain if p['tag']=='picture']
     if galleries:target=galleries[-1]
     elif comparisons:target=comparisons[0]
     elif figures:target=figures[0]
     elif pictures:target=pictures[0]
    elif tag not in {'a','meta'}:
     # Remove exact data/reference attributes rather than an unrelated container.
     raw=text[n['start']:n['open_end']];new=raw
     for k,v in matched:new=re.sub(r'\s+'+re.escape(k)+r'\s*=\s*(["\']).*?\1',lambda m:'' if known(re.search(r'=\s*(["\'])(.*?)\1',m[0],re.S)[2]) else m[0],new,flags=re.S)
     if new!=raw:edits.append((n['start'],n['open_end'],new,'confirmed-photo-attribute',','.join(photo_key(v,file) or '' for k,v in matched)))
     continue
    if target['end'] is None:raise ValueError('Unclosed photo wrapper in '+file)
    edits.append((target['start'],target['end'],'','confirmed-photo-placement',','.join(photo_key(v,file) or '' for k,v in matched)))
  # CSS references inside style attributes and style blocks are handled without deleting layout.
  for m in re.finditer(r'url\(\s*(["\']?)(.*?)\1\s*\)',text,re.I):
   if known(m[2]):edits.append((m.start(),m.end(),'none','confirmed-photo-css-url',photo_key(m[2],file)))
  # Structured social/project metadata must not continue advertising removed photo evidence.
  OMIT=object()
  def clean(value):
   if isinstance(value,str):return OMIT if known(value) else value
   if isinstance(value,list):return [c for v in value if (c:=clean(v)) is not OMIT]
   if isinstance(value,dict):return {k:c for k,v in value.items() if (c:=clean(v)) is not OMIT}
   return value
  for m in re.finditer(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',text,re.S|re.I):
   try:old=json.loads(m[1]);new=clean(old)
   except json.JSONDecodeError:continue
   if old!=new:edits.append((m.start(1),m.end(1),json.dumps(new,separators=(',',':')),'confirmed-photo-structured-metadata',''))
 # Remove stale gallery presentation claims only when this document lost photo placements.
 if edits and not file.endswith('.css'):
  replacements={
   'Open a case study to see the documented challenge, completed scope, materials, date and project photographs.':'Open a case study to see the documented challenge, completed scope, materials and date.',
   'Completed work is supported with project photos, locations and individual case-study pages.':'Explore project locations and individual case-study summaries.',
   'Representative portfolio images are labeled clearly when the original project photographs are not published.':'Project photography is not displayed on this page.',
   'Existing Luna portfolio photographs are identified as Dallas-Fort Worth references, not work in this page’s city.':'',
  }
  for before,after in replacements.items():
   for match in re.finditer(re.escape(before),text):edits.append((match.start(),match.end(),after,'removed-photo-evidence-label',''))
  for match in re.finditer(r'<h[1-6]\b[^>]*>\s*(?:Project Gallery|Project Photos|Before\s*(?:&amp;|and|/|&amp;amp;)\s*After|Galería del proyecto|Antes y después)\s*</h[1-6]>',text,re.I):
   edits.append((match.start(),match.end(),'','empty-photo-gallery-heading',''))
 # Prefer containing removals; reject unrelated overlapping replacements.
 chosen=[]
 for edit in sorted(edits,key=lambda e:(e[0],-(e[1]-e[0]))):
  if chosen and edit[0]<chosen[-1][1]:
   if edit[1]<=chosen[-1][1] and chosen[-1][2]=='':continue
   if edit[:3]==chosen[-1][:3]:continue
   raise ValueError('Overlapping photo-removal edits in '+file)
  chosen.append(edit)
 result=text
 for start,end,new,reason,src in reversed(chosen):result=result[:start]+new+result[end:]
 log=[{'file':file,'start':a,'end':b,'before':text[a:b],'after':new,'reason':why,'asset':src} for a,b,new,why,src in chosen]
 return result,log


def concise_image_text(text,entry,page):
 text=re.sub(r'(src=["\']script\.js)(?:\?[^"\']*)?(["\'])',r'\1?v=20261025-page-owned-gallery\2',text)
 # The aggregate service builders still emit this old preface on six hub
 # sections. The final ownership pass keeps the concise useful heading but
 # removes the redundant concept label so aggregate regeneration is stable.
 text=text.replace('<p class="eyebrow gold">Design concepts</p>','')
 if page=='index.html':
  text=re.sub(r'(href=["\']styles\.css)(?:\?[^"\']*)?(["\'])',r'\1?v=20261024-home-trust-icons-1\2',text)
 city=entry.get('city') or 'Dallas–Fort Worth';label=entry['label']
 def short_figure(match):
  figure=match.group();sources=SRC.findall(figure)
  if len(sources)!=1:return figure
  src=sources[0]
  technical=src.startswith('assets/service-guides/') or (src.startswith('assets/commercial-roofing/') and src.endswith('.svg'))
  concept=src.startswith('assets/images/illustrations/')
  if not (technical or concept):return figure
  subject=next((i.get('caption_subject',label) for i in entry.get('images',[]) if i['src']==src),label)
  if technical:
   subject=Path(src).stem.replace('-reference','').replace('-',' ').capitalize()
   subject={'Tpo':'TPO','Pvc':'PVC','Epdm':'EPDM','Gypsum':'Drywall'}.get(subject,subject)
  caption=html.escape(subject+' · '+city)
  figure=re.sub(r'<figcaption\b[^>]*>.*?</figcaption>',lambda m:'<figcaption>'+caption+'</figcaption>',figure,flags=re.S)
  alt=html.escape(subject+(' illustration' if technical else ' concept')+' · '+city,quote=True)
  figure=re.sub(r'(<img\b[^>]*\balt=")[^"]*',lambda m:m[1]+alt,figure,count=1)
  return figure
 text=FIGURE.sub(short_figure,text)
 text=re.sub(r'<p class="sg-note sg-note--generated-media">.*?</p>','',text,flags=re.S)
 text=re.sub(r'<p\b[^>]*>\s*Generated planning illustrations\s*</p>','',text,flags=re.S)
 text=re.sub(r'<p>Generated illustrations support[^<]+</p>','',text)
 # Remove old boilerplate only inside image-caption context, never educational body.
 for match in re.finditer(r'<figcaption\b[^>]*>(.*?)</figcaption>',text,re.S):
  visible=html.unescape(re.sub('<[^>]+>',' ',match[1]));visible=' '.join(visible.split())
  if re.search(r'Original category illustration|Model appearance varies|not a (?:Luna |completed )?project|Generated planning illustrations',visible,re.I):
   raise ValueError('Retired image-caption boilerplate in '+page)
 # A removed work photo must not leave its social-image dimensions or actual-job alt.
 text=re.sub(r'<meta\b(?=[^>]*(?:property|name)=["\'](?:og:image(?::[^"\']*)?|twitter:image(?::[^"\']*)?|twitter:card)["\'])[^>]*>','',text,flags=re.I)
 if not entry.get('placement_hold') and entry.get('images'):
  image=entry['images'][0];url='https://lunageneralcontractors.com/'+image['src']
  alt=html.escape((label if 'concept' in label.lower() else label+' design concept')+' · '+city,quote=True)
  card='<meta name="twitter:card" content="summary_large_image">'
  meta='<meta property="og:image" content="'+html.escape(url,quote=True)+'"><meta property="og:image:width" content="'+str(image['width'])+'"><meta property="og:image:height" content="'+str(image['height'])+'"><meta property="og:image:alt" content="'+alt+'"><meta name="twitter:image" content="'+html.escape(url,quote=True)+'"><meta name="twitter:image:alt" content="'+alt+'">'+card
  text=text.replace('</head>',meta+'</head>',1)
 if page=='projects.html':
  text=text.replace('See real Luna roofing, bathroom and kitchen work plus detailed construction case studies across Dallas–Fort Worth.','Explore design concepts and construction case summaries across Dallas–Fort Worth.')
  text=text.replace('See real Luna roofing, bathroom and kitchen work plus detailed local project case studies.','Explore design concepts and construction case summaries across Dallas-Fort Worth.')
  text=text.replace('Real project case studies organized by city and service.','Project case studies organized by city and service.')
  text=text.replace('Every image below shows actual completed work','The gallery shows design concepts')
  def normalize_projects_schema(match):
   try: schema=json.loads(match[1])
   except json.JSONDecodeError: return match[0]
   if isinstance(schema,dict) and schema.get('@type')=='ImageGallery':
    return ''
   if isinstance(schema,dict) and schema.get('@type')=='CollectionPage':
    schema=dict(schema)
    schema['description']='Explore design concepts and construction case summaries across Dallas–Fort Worth.'
    schema.pop('primaryImageOfPage',None)
    return match[0][:match[0].index(match[1])]+json.dumps(schema,separators=(',',':'))+match[0][match[0].index(match[1])+len(match[1]):]
   return match[0]
  text=re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',normalize_projects_schema,text,flags=re.S|re.I)
  # Repairs a pre-existing interrupted migration safely; normal output never has this form.
  text=re.sub(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>.*?Real Luna General Contractors Project Photos.*?(?=<link rel="stylesheet" href="page-owned-imagery\.css">)','',text,flags=re.S|re.I)
  if not re.search(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>\s*\{[^<]*"@type":"ImageGallery"',text,re.S|re.I):
   gallery={
    '@context':'https://schema.org',
    '@type':'ImageGallery',
    'name':'Design concepts — Dallas–Fort Worth',
    'url':'https://lunageneralcontractors.com/projects.html#page-owned-imagery',
    'associatedMedia':[
     {'@type':'ImageObject','contentUrl':'https://lunageneralcontractors.com/'+image['src'],'caption':'Design concepts · Dallas–Fort Worth','width':image['width'],'height':image['height']}
     for image in entry['images']
    ],
   }
   text=text.replace('</head>','<script type="application/ld+json">'+json.dumps(gallery,separators=(',',':'))+'</script></head>',1)
 # Upstream builders may introduce spacer-only or repeated blank lines around
 # regenerated blocks. Normalize them once at the final ownership boundary so
 # repeated aggregate builds are byte-stable without changing semantics.
 text=re.sub(r'[ \t]+(?=\n)','',text)
 return re.sub(r'\n{3,}','\n\n',text)


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--manifest',type=Path);ap.add_argument('--photo-manifest',type=Path);ap.add_argument('--removal-log',type=Path);ap.add_argument('--page-offset',type=int,default=0);ap.add_argument('--page-limit',type=int);g=ap.add_mutually_exclusive_group();g.add_argument('--apply',action='store_true');g.add_argument('--check',action='store_true');args=ap.parse_args()
 root=args.root.resolve();manifest=args.manifest or root/'content/page-owned-imagery.json';data=json.loads(manifest.read_text(encoding='utf-8'));prepared=[];held=[];removals=[]
 photo_manifest=args.photo_manifest or root/'content/real-job-photo-placements.json'
 photo_data=json.loads(photo_manifest.read_text(encoding='utf-8'));assets=set(photo_data if isinstance(photo_data,list) else photo_data['assets'])
 reasons={} if isinstance(photo_data,list) else photo_data.get('reasons',{})
 if not assets or any(not isinstance(x,str) or '..' in Path(x).parts or x.startswith(('http:','https:','data:','/')) for x in assets):raise ValueError('Photo manifest needs confirmed public relative paths')
 if args.page_offset<0 or args.page_limit is not None and args.page_limit<1:raise ValueError('Invalid page batch')
 entries=sorted(data.items())[args.page_offset:args.page_offset+args.page_limit if args.page_limit is not None else None]
 for page,entry in entries:
  if not re.fullmatch(r'[a-zA-Z0-9_.-]+\.html',page):raise ValueError('Unsafe page path')
  path=root/page;before=path.read_text(encoding='utf-8');stripped,logs=strip_real_photos(before,assets,page)
  for log in logs:
   if any(reasons.get(a)=='withheld-conflicting-provenance' for a in log['asset'].split(',')):log['reason']='withheld-conflicting-provenance-placement'
  removals.extend(logs)
  if entry.get('placement_hold') or entry['category'] in SENSITIVE:
   held.append(page);after=stripped
  else:
   imgs=entry['images']
   if len(imgs)!=5 or {i['slot'] for i in imgs}!={1,2,3,4,5} or len({i['src'] for i in imgs})!=5:raise ValueError('Invalid five-slot assignment '+page)
   for i in imgs:
    if not i['src'].startswith('assets/images/illustrations/') or '..' in Path(i['src']).parts or not (root/i['src']).is_file():raise ValueError('Unsafe/missing asset '+i['src'])
    if not isinstance(i['width'],int) or not isinstance(i['height'],int) or min(i['width'],i['height'])<1:raise ValueError('Invalid dimensions')
   after=transform(stripped,entry,page)
   if transform(after,entry,page)!=after:raise ValueError('Non-idempotent output '+page)
  after=concise_image_text(after,entry,page)
  repeated,_=strip_real_photos(after,assets,page)
  if not entry.get('placement_hold') and entry['category'] not in SENSITIVE:repeated=transform(repeated,entry,page)
  repeated=concise_image_text(repeated,entry,page)
  if repeated!=after:raise ValueError('Final caption/metadata pass is not idempotent: '+page)
  again,remaining=strip_real_photos(after,assets,page)
  if remaining or again!=after:raise ValueError('Work-photo placement survived removal: '+page)
  if before!=after:prepared.append((path,after))
 # Stylesheets can retain actual photo backgrounds independently of HTML markup.
 if args.page_offset==0 and args.page_limit is None:
  for path in sorted(root.rglob('*.css')):
   if any(x.startswith('.') for x in path.relative_to(root).parts):continue
   file=path.relative_to(root).as_posix();before=path.read_text(encoding='utf-8');after,logs=strip_real_photos(before,assets,file);removals.extend(logs)
   if after!=before:prepared.append((path,after))
 css=root/'page-owned-imagery.css';css_stale=not css.exists() or css.read_text(encoding='utf-8')!=CSS
 if args.apply:
  if removals:
   if args.removal_log:logpath=args.removal_log
   else:
    import subprocess
    raw=subprocess.check_output(['git','rev-parse','--git-path','page-owned-photo-removals.json'],cwd=root,text=True).strip()
    logpath=Path(raw) if Path(raw).is_absolute() else root/raw
   previous=json.loads(logpath.read_text(encoding='utf-8')) if logpath.exists() else []
   logpath.parent.mkdir(parents=True,exist_ok=True)
   previous.append({'assets':sorted(assets),'edits':removals,'files':[{'file':str(p.relative_to(root)),'before_document':p.read_text(encoding='utf-8'),'before_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(s.encode()).hexdigest()} for p,s in prepared]})
   logpath.write_text(json.dumps(previous,indent=2),encoding='utf-8')
  for p,s in prepared:p.write_text(s,encoding='utf-8')
  if css_stale:css.write_text(CSS,encoding='utf-8')
 print(json.dumps({'mode':'apply' if args.apply else 'check' if args.check else 'dry-run','page_batch':{'offset':args.page_offset,'count':len(entries)},'changed_files':len(prepared),'concept_placement_held_pages':held,'photo_placements_removed':len(removals),'stylesheet_stale':css_stale}))
 if args.check and (prepared or css_stale):sys.exit(1)

if __name__=='__main__':main()
