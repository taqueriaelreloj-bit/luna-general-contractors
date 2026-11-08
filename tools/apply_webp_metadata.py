"""Install the previously verified WebP files without re-encoding WebP pixels."""
from pathlib import Path
import base64, gzip, hashlib, io, json, re, struct, subprocess, sys
from PIL import Image, features, __version__
ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def chunks(data):
    assert data[:4]==b'RIFF' and data[8:12]==b'WEBP'
    assert int.from_bytes(data[4:8],'little')+8==len(data)
    result=[];offset=12
    while offset<len(data):
        size=int.from_bytes(data[offset+4:offset+8],'little');end=offset+8+size+(size&1)
        assert end<=len(data);result.append(data[offset:end]);offset=end
    return result
def lossless(data):
    before=Image.open(io.BytesIO(data));before.load()
    image=before if before.mode in ('RGB','RGBA') else before.convert('RGBA')
    out=io.BytesIO();image.save(out,format='WEBP',lossless=True,quality=75,method=1,exact=True,
        xmp=before.info.get('xmp',b''),exif=before.info.get('exif',b''),icc_profile=before.info.get('icc_profile',b''))
    result=out.getvalue();after=Image.open(io.BytesIO(result));after.load()
    assert before.size==after.size and before.convert('RGBA').tobytes()==after.convert('RGBA').tobytes()
    for key in ('xmp','exif','icc_profile'):
        assert before.info.get(key,b'')==after.info.get(key,b'')
    return result
def apply():
    patch=Path(sys.argv[1]);out_report=Path(sys.argv[2])
    payload=b''.join(p.read_bytes() for p in sorted(patch.glob('*.part')))
    manifest=json.loads(gzip.decompress(payload));assert manifest['count']==7657
    assert __version__==manifest['pillow_version'] and features.version('webp')==manifest['webp_version']
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0');tracked=[p for p in tracked if p]
    png_paths=[p for p in tracked if p.lower().endswith('.png')]
    assert len(png_paths)==67, f'PNG inventory changed: {len(png_paths)}'
    png_map={p:str(Path(p).with_suffix('.webp')) for p in png_paths}
    assert all(not (ROOT/p).exists() for p in png_map.values())
    installed=[];old_bytes=new_bytes=0
    for r in manifest['records']:
        src=ROOT/r['source'];dest=ROOT/r['target'];old=src.read_bytes()
        assert sha(old)==r['source_sha256'],f'Changed source: {r["source"]}'
        if src.suffix=='.png':
            before=Image.open(io.BytesIO(old));before.load();im=before if before.mode in ('RGB','RGBA') else before.convert('RGBA')
            out=io.BytesIO();im.save(out,format='WEBP',lossless=True,quality=75,method=1,exact=True);basis=out.getvalue()
        else: basis=old
        original=chunks(basis);parts=[]
        for c in r['chunks']:
            if isinstance(c,int):parts.append(original[c])
            elif isinstance(c,dict):
                data=c['xmp'].encode();parts.append(b'XMP '+struct.pack('<I',len(data))+data+(b'\0' if len(data)&1 else b''))
            else:parts.append(base64.b64decode(c))
        body=b'WEBP'+b''.join(parts);new=b'RIFF'+struct.pack('<I',len(body))+body
        assert sha(new)==r['target_sha256'],f'Prepared file differs: {r["target"]}'
        image=Image.open(io.BytesIO(new));image.load();xmp=image.info.get('xmp',b'')
        assert b'AltTextAccessibility' in xmp and b'PinterestDescription' in xmp and b'dc:subject' in xmp
        if src.suffix=='.png': assert before.convert('RGBA').tobytes()==image.convert('RGBA').tobytes()
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(new)
        installed.append(r['target']);old_bytes+=len(old);new_bytes+=len(new)
    other=[]
    for srcname,destname in png_map.items():
        src=ROOT/srcname;dest=ROOT/destname
        if destname not in installed:
            old=src.read_bytes();new=lossless(old);dest.write_bytes(new)
            old_bytes+=len(old);new_bytes+=len(new);other.append(destname)
        assert dest.exists() and Image.open(dest).format=='WEBP'
    # Replace full paths and basenames in source manifests and their generators.
    # Basenames are globally unique for these PNG assets; fail closed otherwise.
    names={Path(k).name:Path(v).name for k,v in png_map.items()}
    assert len(names)==len(png_map)
    pattern=re.compile('|'.join(re.escape(x) for x in sorted(names,key=len,reverse=True)))
    edited=[]
    for rel in tracked:
        path=ROOT/rel
        if rel.startswith('.git/') or path.suffix.lower() in {'.png','.webp','.jpg','.jpeg','.gif','.ico','.pdf','.zip','.gz'}:continue
        try:text=path.read_text(encoding='utf-8')
        except (UnicodeDecodeError,IsADirectoryError):continue
        changed=pattern.sub(lambda m:names[m.group()],text)
        if changed!=text:path.write_text(changed,encoding='utf-8');edited.append(rel)
    # Refresh integrity fields in active JSON manifests after metadata changes.
    metadata={name:{'sha256':sha((ROOT/name).read_bytes()),'bytes':(ROOT/name).stat().st_size} for name in installed+other}
    def refresh(node):
        changed=False
        if isinstance(node,dict):
            path=next((node.get(k) for k in ('path','src','image') if isinstance(node.get(k),str) and node.get(k) in metadata),None)
            if path:
                for key,value in metadata[path].items():
                    if key in node and node[key]!=value:node[key]=value;changed=True
            for value in node.values():changed=refresh(value) or changed
        elif isinstance(node,list):
            for value in node:changed=refresh(value) or changed
        return changed
    for rel in tracked:
        if rel.startswith('content/') and rel.endswith('.json'):
            path=ROOT/rel;data=json.loads(path.read_text())
            if refresh(data):
                path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
                if rel not in edited:edited.append(rel)
    for srcname in png_map:(ROOT/srcname).unlink()
    # No active source reference may retain any deleted image filename.
    for rel in tracked:
        path=ROOT/rel
        if not path.exists() or path.suffix.lower() in {'.webp','.jpg','.jpeg','.gif','.ico','.pdf','.zip','.gz'}:continue
        try:text=path.read_text(encoding='utf-8')
        except UnicodeDecodeError:continue
        assert not pattern.search(text),f'Stale PNG reference: {rel}'
    assert not list((ROOT/'assets').rglob('*.png'))
    report={'prepared_webp_installed':len(installed),'exact_sha256_verified':len(installed),
        'additional_png_converted_losslessly':len(other),'png_files_removed':len(png_map),
        'source_text_files_updated':len(edited),'text_files':edited,'png_to_webp':png_map,
        'old_image_bytes':old_bytes,'new_image_bytes':new_bytes,'bytes_saved':old_bytes-new_bytes}
    out_report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('text_files','png_to_webp')}),flush=True)
if __name__=='__main__':apply()
