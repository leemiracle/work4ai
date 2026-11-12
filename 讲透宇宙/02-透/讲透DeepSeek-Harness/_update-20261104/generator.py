#!/usr/bin/env python3
"""Assemble products/batch-NNN.json from semantic data + extracted.json.
Usage: python3 generator.py <batchIndex>
Semantic data lives in data_<NNN>.py (per-file nodes, member nodes, manual edges)."""
import json, os, re, sys
from collections import Counter
from importlib import import_module

BASE = '/data/usershare/ai/work4ai/讲透DeepSeek-Harness/_update-20261104'
ROOT = '/usr-data/data2/repos/deepseek-ai/deepseek-harness'
EXT = json.load(open(os.path.join(BASE, 'extracted.json')))
MANUAL_RESOLVE = {
    # spec -> project path (verified against package.json exports / tsdown entries)
    '@deepseek-ai/dsh-subprocess-local/runner': 'packages/subprocess/subprocess-local/src/bin.ts',
}

def build(batch_index: int):
    b = getattr(import_module(f'data_{batch_index}'), 'BATCH')
    files = json.load(open(os.path.join(BASE, f'batches/batch-{batch_index:03d}.json')))['files']
    nodes, edges = [], []
    node_ids = set()

    def add_node(n):
        if n['id'] in node_ids: raise SystemExit(f"dup node id {n['id']}")
        node_ids.add(n['id']); nodes.append(n)

    for rel in files:
        meta = b['files'].get(rel)
        if meta is None:
            raise SystemExit(f"missing semantic entry for {rel}")
        ntype, summary, tags, cplx = meta['type'], meta['summary'], meta['tags'], meta['complexity']
        prefix = {'file': 'file', 'config': 'config', 'document': 'document'}[ntype]
        add_node({'id': f'{prefix}:{rel}', 'type': ntype, 'name': os.path.basename(rel),
                  'filePath': rel, 'summary': summary, 'tags': tags, 'complexity': cplx})
        r = EXT.get(rel, {})
        for imp in r.get('imports', []):
            tgt = imp['resolved']
            if tgt is None: continue
            if isinstance(tgt, str) and tgt.startswith('UNRESOLVED:'):
                tgt = MANUAL_RESOLVE.get(imp['spec'])
                if tgt is None:
                    raise SystemExit(f"unresolved import {rel}: {imp['spec']}")
            src_id, tgt_id = f'file:{rel}', f'file:{tgt}'
            if src_id == tgt_id: continue
            edges.append({'source': src_id, 'target': tgt_id, 'type': 'imports', 'direction': 'forward', 'weight': 0.7})
        for m in meta.get('members', []):
            mid = f"{m['kind']}:{rel}:{m['name']}"
            add_node({'id': mid, 'type': m['kind'], 'name': m['name'], 'filePath': rel,
                      'lineRange': [m['start'], m['end']], 'summary': m['summary'],
                      'tags': m['tags'], 'complexity': m['complexity']})
            edges.append({'source': f'file:{rel}', 'target': mid, 'type': 'contains', 'direction': 'forward', 'weight': 1.0})
            if m.get('exported'):
                edges.append({'source': f'file:{rel}', 'target': mid, 'type': 'exports', 'direction': 'forward', 'weight': 0.8})
    for e in b.get('extra_edges', []):
        edges.append(e)
    for e in edges:
        if e['source'] == e['target']: raise SystemExit(f"self edge {e}")
        for side in ('source', 'target'):
            sid = e[side]
            if sid in node_ids: continue
            if sid.startswith('file:') and os.path.exists(os.path.join(ROOT, sid[5:])): continue
            m = re.match(r'^(?:class|function):([^:]+):.+$', sid)
            if m and os.path.exists(os.path.join(ROOT, m.group(1))): continue
            raise SystemExit(f"edge endpoint not found: {sid} (type {e['type']})")
    expected = 0
    for rel in files:
        for imp in EXT.get(rel, {}).get('imports', []):
            if imp['resolved'] is not None: expected += 1
    actual = sum(1 for e in edges if e['type'] == 'imports')
    if expected != actual: raise SystemExit(f"imports mismatch: expected {expected}, got {actual}")
    out = {'nodes': nodes, 'edges': edges}
    os.makedirs(os.path.join(BASE, 'products'), exist_ok=True)
    path = os.path.join(BASE, f'products/batch-{batch_index:03d}.json')
    json.dump(out, open(path, 'w'), indent=1, ensure_ascii=False)
    nc = Counter(n['type'] for n in nodes)
    ec = Counter(e['type'] for e in edges)
    print(f"batch-{batch_index:03d}: nodes={len(nodes)} ({dict(nc)}) edges={len(edges)} ({dict(ec)}) imports={ec['imports']}/{expected} -> {path}")

if __name__ == '__main__':
    build(int(sys.argv[1]))
