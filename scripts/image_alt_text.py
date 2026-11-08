#!/usr/bin/env python3
"""Publish embedded image descriptions and authored service introductions.

Image bytes and XMP are read-only. JSON source manifests and HTML get the same
per-image alternative text, so regenerated galleries keep the descriptions.
"""
from __future__ import annotations
import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ALT_TAG = '{http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/}AltTextAccessibility'
RDF_LI = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li'
DOMAIN = 'lunageneralcontractors.com'
HUBS = {'roofing.html':'roofing','bathrooms.html':'bathroom-remodeling',
        'kitchens.html':'kitchen-remodeling','painting.html':'painting',
        'flooring.html':'flooring','drywall.html':'drywall',
        'mitigation.html':'water-damage-restoration','siding.html':'siding',
        'carpentry.html':'carpentry','fencing.html':'fencing',
        'commercial.html':'commercial-construction','insurance-claims.html':'insurance-claims'}

def embedded_alt(path: Path) -> str | None:
    data = path.read_bytes()
    if data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        return None
    pos = 12
    while pos + 8 <= len(data):
        kind = data[pos:pos+4]
        size = struct.unpack_from('<I', data, pos+4)[0]
        if pos + 8 + size > len(data):
            raise ValueError(f'Truncated WebP: {path}')
        if kind == b'XMP ':
            root = ET.fromstring(data[pos+8:pos+8+size])
            field = root.find('.//' + ALT_TAG)
            if field is not None:
                values = [''.join(e.itertext()).strip() for e in field.iter(RDF_LI)]
                if values and values[0]:
                    return values[0]
        pos += 8 + size + size % 2
    return None

def source_path(value: str) -> str:
    url = urlsplit(html.unescape(value))
    if url.netloc and url.hostname not in (DOMAIN, 'www.' + DOMAIN):
        return ''
    return unquote(url.path).removeprefix('./').lstrip('/')

class StartTags(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.offsets = [0]
        for match in re.finditer('\n', text):
            self.offsets.append(match.end())
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        line, column = self.getpos()
        raw = self.get_starttag_text()
        self.tags.append((self.offsets[line-1]+column, raw, tag, dict(attrs)))
    handle_startendtag = handle_starttag

def set_attribute(raw: str, name: str, value: str) -> str:
    pattern = re.compile(r'(\s' + re.escape(name) + r'\s*=\s*)(?:"[^"]*"|\x27[^\x27]*\x27|[^\s>]+)', re.I)
    escaped = html.escape(value, quote=True)
    if pattern.search(raw):
        return pattern.sub(lambda m: m[1] + '"' + escaped + '"', raw, count=1)
    end = len(raw) - (2 if raw.endswith('/>') else 1)
    return raw[:end] + ' ' + name + '="' + escaped + '"' + raw[end:]

def rewrite_html(text: str, alts: dict[str, str]) -> tuple[str, int]:
    tags = StartTags(text).tags
    social = {}
    for _, _, tag, attrs in tags:
        if tag == 'meta':
            key = attrs.get('property') or attrs.get('name')
            if key in ('og:image', 'twitter:image'):
                social[key + ':alt'] = alts.get(source_path(attrs.get('content') or ''))
    edits = []
    placements = 0
    for start, raw, tag, attrs in tags:
        after = raw
        if tag == 'img':
            alt = alts.get(source_path(attrs.get('src') or ''))
            if alt:
                placements += 1
                if attrs.get('alt') != alt:
                    after = set_attribute(raw, 'alt', alt)
        elif tag == 'meta':
            alt = social.get(attrs.get('property') or attrs.get('name'))
            if alt and attrs.get('content') != alt:
                after = set_attribute(raw, 'content', alt)
        if after != raw:
            edits.append((start, start+len(raw), after))
    for start, end, after in reversed(edits):
        text = text[:start] + after + text[end:]
    return text, placements

def service_copy(text, page, entry, profiles):
    key = HUBS.get(page)
    if not key:
        category = entry.get('category')
        if category in profiles and page.endswith('-' + category + '.html'):
            key = category
    if not key:
        return text, False
    location = 'Dallas–Fort Worth' if page in HUBS else entry.get('city')
    if not location:
        raise ValueError('Missing location for ' + page)
    profile = profiles[key]
    intro = html.escape(profile['hero'].format(location=location), quote=False)
    pattern = re.compile(r'(<h1\b[^>]*>.*?</h1>\s*<p\b[^>]*>).*?(</p>)', re.S | re.I)
    text, count = pattern.subn(lambda m: m[1] + intro + m[2], text, count=1)
    if count != 1:
        raise ValueError('No unique hero introduction for ' + page)
    description = profile['description'].format(location=location)
    edits = []
    for start, raw, tag, attrs in StartTags(text).tags:
        if tag == 'meta' and (attrs.get('name') == 'description' or
              (attrs.get('property') or attrs.get('name')) in ('og:description','twitter:description')):
            edits.append((start, start+len(raw), set_attribute(raw, 'content', description)))
    if not edits:
        raise ValueError('No description metadata for ' + page)
    for start, end, after in reversed(edits):
        text = text[:start] + after + text[end:]
    return text, True

def sync(root: Path, check: bool = False) -> dict:
    alts = {}
    for path in sorted((root/'assets/images').rglob('*.webp')):
        alt = embedded_alt(path)
        if alt:
            alts[path.relative_to(root).as_posix()] = alt
    if len(alts) != 7657:
        raise ValueError(f'Expected 7657 prepared image descriptions, found {len(alts)}')
    profiles = json.loads((root/'content/service-search-copy.json').read_text())
    owned_path = root/'content/page-owned-imagery.json'
    owned = json.loads(owned_path.read_text())
    changed = []
    def save(path, value):
        if value != path.read_text(encoding='utf-8'):
            changed.append(path.relative_to(root).as_posix())
            if not check:
                path.write_text(value, encoding='utf-8')
    for name in ('page-owned-imagery.json','component-card-imagery.json'):
        path = root/'content'/name
        data = json.loads(path.read_text())
        touched = False
        def visit(item):
            nonlocal touched
            if isinstance(item, dict):
                path = item.get('src') or item.get('path')
                alt = alts.get(path) if isinstance(path, str) else None
                if alt and item.get('alt') != alt:
                    item['alt'] = alt
                    touched = True
                for value in item.values(): visit(value)
            elif isinstance(item, list):
                for value in item: visit(value)
        visit(data)
        if touched:
            save(path, json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    placements = 0
    copy_pages = []
    for path in sorted(root.glob('*.html')):
        text = path.read_text(encoding='utf-8')
        after, count = rewrite_html(text, alts)
        placements += count
        after, has_copy = service_copy(after, path.name, owned.get(path.name, {}), profiles)
        if has_copy: copy_pages.append(path.name)
        save(path, after)
    result = {'prepared_images':len(alts),'html_image_placements':placements,
              'service_copy_pages':len(copy_pages),'service_copy_page_names':copy_pages,
              'changed_files':changed,'mode':'check' if check else 'apply'}
    print(json.dumps({k:v for k,v in result.items() if k not in ('changed_files','service_copy_page_names')}))
    if check and changed:
        raise ValueError(f'{len(changed)} files need image descriptions or service copy: {changed[:5]}')
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = sync(args.root, args.check)
    if args.report:
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
