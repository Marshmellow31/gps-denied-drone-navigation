#!/usr/bin/env python3
"""Copy inventoried native files to a new directory; preserve every source."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-parent', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    inventory = json.loads((Path(__file__).parent / 'EXTERNAL_DATA_INVENTORY.json').read_text())
    target = a.output.resolve()
    if target.exists():
        p.error('Output already exists; choose a new directory')
    source = a.source_parent.resolve()
    if source == target or source in target.parents:
        p.error('Output must be outside the source tree')
    required = sum(r['bytes'] for r in inventory['files'])
    ancestor = target.parent
    while not ancestor.exists():
        ancestor = ancestor.parent
    if shutil.disk_usage(ancestor).free < required + 1024**3:
        p.error(f'Need {required / 1024**3:.2f} GiB plus 1 GiB reserve on destination')
    for row in inventory['files']:
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe inventory path')
        src = source / relative
        if not src.is_file() or src.stat().st_size != row['bytes']:
            raise ValueError('Missing or size-changed source: ' + str(src))
    target.mkdir(parents=True, exist_ok=False)
    receipt = []
    for i, row in enumerate(inventory['files'], 1):
        src, dst = source / row['path'], target / row['path']
        before = digest(src)
        if row['sha256'] and before != row['sha256']:
            raise ValueError('Historical hash mismatch: ' + str(src))
        dst.parent.mkdir(parents=True, exist_ok=True)
        with src.open('rb') as inp, dst.open('xb') as out:
            shutil.copyfileobj(inp, out, 1024 * 1024)
        if digest(dst) != before:
            raise ValueError('Copied bytes differ: ' + str(dst))
        receipt.append({'path': row['path'], 'sha256': before, 'bytes': row['bytes']})
        if i % 100 == 0:
            print(f'Copied and verified {i}/{len(inventory["files"])} files', flush=True)
    (target / 'COPY_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'Copied and verified {len(receipt)} files; sources preserved')


if __name__ == '__main__':
    main()
