from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlsplit,urlunsplit
from urllib.error import HTTPError,URLError
from html.parser import HTMLParser
from datetime import datetime,timezone
import base64,gzip,hashlib,json,struct,time,xml.etree.ElementTree as ET

DOMAIN='https://lunageneralcontractors.com/'
NS={'dc':'http://purl.org/dc/elements/1.1/','iptc':'http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/','lgc':'https://lunageneralcontractors.com/ns/organizational-metadata/1.0/','rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#','exif':'http://ns.adobe.com/exif/1.0/'}
FIELDS={'title':('dc','title'),'visual_description':('dc','description'),'alt_text':('iptc','AltTextAccessibility'),'keywords':('dc','subject'),'pinterest_description':('lgc','PinterestDescription'),'destination_url':('lgc','DestinationURL')}
def field(root,ns,name):
    el=root.find('.//{'+NS[ns]+'}'+name)
    if el is None:return []
    vals=el.findall('.//{'+NS['rdf']+'}li')
    return [''.join(x.itertext()).strip() for x in vals] if vals else [''.join(el.itertext()).strip()]
def parse(packet):
    root=ET.fromstring(packet)
    data={k:field(root,*v) for k,v in FIELDS.items()}
    data['assigned_date']=field(root,'lgc','AssignedOrganizationDateTime')
    data['assigned_date_purpose']=field(root,'lgc','AssignedDatePurpose')
    data['service_area']=field(root,'lgc','ServiceArea')
    data['location_purpose']=field(root,'lgc','LocationPurpose')
    return data
def get_xmp(data):
    assert data[:4]==b'RIFF' and data[8:12]==b'WEBP','Invalid WebP header'
    assert int.from_bytes(data[4:8],'little')+8==len(data),'Invalid WebP size'
    p=12;packets=[]
    while p<len(data):
        assert p+8<=len(data),'Truncated chunk header'
        n=int.from_bytes(data[p+4:p+8],'little');end=p+8+n+(n&1);assert end<=len(data),'Truncated chunk'
        if data[p:p+4]==b'XMP ':packets.append(data[p+8:p+8+n])
        p=end
    assert len(packets)==1,'Missing or multiple XMP packets'
    return packets[0]
def fetch(url):
    for attempt in range(3):
        try:
            req=Request(url,headers={'User-Agent':'Luna-Website-Metadata-Audit/1.0','Cache-Control':'no-cache'})
            with urlopen(req,timeout=40) as response:return response.read(),response.status,response.headers.get('Content-Type',''),response.geturl()
        except HTTPError as error:
            if error.code not in (429,500,502,503,504) or attempt==2:raise
            wait=min(45,int(error.headers.get('Retry-After','5')) if error.headers.get('Retry-After','5').isdigit() else 5)
            time.sleep(max(wait,5*(attempt+1)))
        except (URLError,TimeoutError):
            if attempt==2:raise
            time.sleep(5*(attempt+1))

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--patch-dir',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
    inp=b''.join(p.read_bytes() for p in sorted(Path(args.patch_dir).glob('*.part')))
    manifest=json.loads(gzip.decompress(inp));records=manifest['records'];assert len(records)==7657
    expected={}
    for r in records:
        packet=next(c['xmp'] for c in r['chunks'] if isinstance(c,dict) and 'xmp' in c)
        expected[r['target']]=parse(packet)
    def check_image(r):
        url=urljoin(DOMAIN,r['target']);result={'path':r['target'],'url':url,'expected_sha256':r['target_sha256']}
        try:
            data,status,ctype,finalurl=fetch(url);actual=parse(get_xmp(data));digest=hashlib.sha256(data).hexdigest()
            missing=[k for k in FIELDS if not actual[k] or any(not x for x in actual[k])]
            differences=[k for k in FIELDS if actual[k]!=expected[r['target']][k]]
            result.update({'http_status':status,'content_type':ctype,'bytes':len(data),'sha256':digest,'sha256_matches_prepared':digest==r['target_sha256'],'missing_fields':missing,'different_fields':differences,'fields':actual})
            result['ok']=status==200 and 'image/webp' in ctype.lower() and digest==r['target_sha256'] and not missing and not differences
        except Exception as error:result.update({'ok':False,'error':str(error)})
        return result
    images=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(check_image,r) for r in records]
        for future in as_completed(futures):
            images.append(future.result())
            if len(images)%500==0:print(json.dumps({'images_checked':len(images),'image_errors':sum(not r['ok'] for r in images)}),flush=True)
    class Images(HTMLParser):
        def __init__(self):super().__init__();self.images=[];self.title=[];self.in_title=False
        def handle_starttag(self,tag,attrs):
            if tag=='img':self.images.append(dict(attrs))
            if tag=='title':self.in_title=True
        def handle_endtag(self,tag):
            if tag=='title':self.in_title=False
        def handle_data(self,data):
            if self.in_title:self.title.append(data)
    pages=sorted({values['destination_url'][0] for values in expected.values() if values['destination_url'] and values['destination_url'][0].startswith(DOMAIN)})
    def check_page(url):
        try:
            data,status,ctype,finalurl=fetch(url);p=Images();p.feed(data.decode('utf-8-sig'))
            items=[]
            for img in p.images:
                src=img.get('src','')
                if not src:continue
                absolute=urljoin(finalurl,src);parsed=urlsplit(absolute)
                if parsed.netloc!=urlsplit(DOMAIN).netloc:continue
                path=parsed.path.lstrip('/')
                if path not in expected:continue
                alt=img.get('alt');wanted=expected[path]['alt_text'][0]
                items.append({'path':path,'html_alt':alt,'html_alt_nonempty':bool(alt and alt.strip()),'html_alt_matches_embedded':alt==wanted})
            return {'url':url,'http_status':status,'title':''.join(p.title),'placements':items,'ok':status==200}
        except Exception as error:return {'url':url,'ok':False,'error':str(error),'placements':[]}
    page_results=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(check_page,u) for u in pages]
        for future in as_completed(futures):
            page_results.append(future.result())
            if len(page_results)%250==0:print(json.dumps({'pages_checked':len(page_results)}),flush=True)
    placements=[{'page_url':r['url'],**i} for r in page_results for i in r['placements']]
    unique_alt={r['path'] for r in placements if r['html_alt_nonempty']}
    exact_alt={r['path'] for r in placements if r['html_alt_matches_embedded']}
    summary={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'source':'public website HTTP responses; not source-repository-only checks','image_count':len(images),'images_passed':sum(r['ok'] for r in images),'images_failed':sum(not r['ok'] for r in images),'exact_file_matches':sum(r.get('sha256_matches_prepared',False) for r in images),'field_complete_counts':{k:sum(bool(r.get('fields',{}).get(k)) and all(r['fields'][k]) for r in images) for k in FIELDS},'pages_checked':len(page_results),'pages_failed':sum(not r['ok'] for r in page_results),'html_image_placements_checked':len(placements),'html_alt_missing_placements':sum(not r['html_alt_nonempty'] for r in placements),'unique_images_with_html_alt':len(unique_alt),'unique_images_with_html_alt_equal_to_embedded':len(exact_alt),'html_alt_different_placements':sum(r['html_alt_nonempty'] and not r['html_alt_matches_embedded'] for r in placements),'assigned_date_count':sum(bool(r.get('fields',{}).get('assigned_date')) for r in images),'service_area_count':sum(bool(r.get('fields',{}).get('service_area')) for r in images),'pinterest_native_fields_checked':False}
    report={'summary':summary,'images':sorted(images,key=lambda r:r['path']),'pages':sorted(page_results,key=lambda r:r['url'])}
    Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('FINAL_METADATA_AUDIT '+json.dumps(summary),flush=True)
if __name__=='__main__':main()
