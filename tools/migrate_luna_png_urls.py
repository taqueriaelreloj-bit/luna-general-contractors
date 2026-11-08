"""Replace verified Luna image references with their published PNG equivalents.

Keeps original asset files, captions, alt attributes, destination links, and
unmapped references intact. Run only after the complete image host is live.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

PUBLIC_ORIGIN = 'https://luna-public-png-images.taqueriaelreloj.chatgpt.site'
REFERENCE = re.compile(
    r'(?:https?://(?:www\.)?lunageneralcontractors\.com/'
    r'|(?<![A-Za-z0-9_:/.-])(?:\./|/)?)'
    r'(?P<path>assets/images/[A-Za-z0-9_./%+\-]+\.(?:webp|png))'
    r'(?![A-Za-z0-9_.-])'
)

def migrate(root, manifest_path):
    rows = json.loads(manifest_path.read_text())
    assert len(rows) == 7657
    replacements = {}
    for r in rows:
        assert r['source_path'].startswith('assets/images/')
        assert r['path'].startswith('images/assets/images/') and r['path'].endswith('.png')
        assert '..' not in Path(r['path']).parts
        assert r['source_path'] not in replacements
        replacements[r['source_path']] = PUBLIC_ORIGIN + '/' + r['path']
    files = [p for p in root.iterdir() if p.is_file() and p.suffix in {'.html', '.css', '.js', '.xml'}]
    files += [root / p for p in ['content/general-gallery-data.json', 'content/component-card-gallery-data.json', 'content/page-owned-gallery-data.json']]
    changed = []
    used = set()
    untouched = set()
    total = 0
    for p in sorted(files):
        original = p.read_text()
        count = 0
        def replace(m):
            nonlocal count
            source = m.group('path')
            if source not in replacements:
                untouched.add(source)
                return m.group(0)
            count += 1
            used.add(source)
            return replacements[source]
        updated = REFERENCE.sub(replace, original)
        if updated != original:
            assert count > 0
            if p.suffix == '.json':
                json.loads(updated)
            # No eligible reference may remain, and a second pass must be inert.
            assert not any(m.group('path') in replacements for m in REFERENCE.finditer(updated))
            assert REFERENCE.sub(lambda m: replacements.get(m.group('path'), m.group(0)), updated) == updated
            p.write_text(updated)
            total += count
            changed.append({'path': str(p.relative_to(root)), 'replacements': count,
                            'before_sha256': hashlib.sha256(original.encode()).hexdigest(),
                            'after_sha256': hashlib.sha256(updated.encode()).hexdigest()})
    assert used == set(replacements), f'{len(set(replacements)-used)} prepared images are absent from website references'
    return {'origin': PUBLIC_ORIGIN, 'prepared_images': len(rows), 'unique_images_referenced': len(used),
            'changed_files': changed, 'total_references_replaced': total,
            'unmapped_image_references_preserved': sorted(untouched),
            'original_assets_deleted': False, 'alt_text_or_page_copy_changed': False}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--report', type=Path, required=True)
    args = ap.parse_args()
    report = migrate(args.root, args.manifest)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k not in {'changed_files', 'unmapped_image_references_preserved'}} | {'changed_file_count': len(report['changed_files'])}))
