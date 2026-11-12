#!/usr/bin/env python3
"""图手术合并：旧图谱 − (changed∪deleted 文件的节点/边) + 新批产物 → 新 assembled graph
用法: python3 surgery_merge.py [--dry]
守恒公式: nodes_after = nodes_before - removed + added_new; 悬空边必须有去向报告
"""
import json, os, sys, glob, collections

REPO = '/usr-data/data2/repos/pytorch-landscape/repos/vllm'
W = '~/ai/work4ai/讲透vLLM/_update-20261028'
DRY = '--dry' in sys.argv

delta = json.load(open(f'{W}/delta.json'))
remove_files = set(delta['changed']) | set(delta['deleted'])
print(f'[输入] changed={len(delta["changed"])} deleted={len(delta["deleted"])} → 手术移除文件集={len(remove_files)}')

g = json.load(open(f'{REPO}/.understand-anything/knowledge-graph.json'))
nodes, edges = g['nodes'], g['edges']
n0, e0 = len(nodes), len(edges)

# --- 1. 移除 ---
removed_nodes = [n for n in nodes if n.get('filePath') in remove_files]
kept_nodes = [n for n in nodes if n.get('filePath') not in remove_files]
removed_ids = {n['id'] for n in removed_nodes}
# 无 filePath 节点不应存在（前面验证全有）；按 id 前缀二次兜底
def id_file(nid):
    if nid.startswith('file:'): return nid[5:]
    if ':' in nid: return nid.split(':', 1)[1].rsplit('.py', 1)[0] + '.py' if False else None
    return None
kept_edges = []
dropped_touch = 0
for e in edges:
    if e['source'] in removed_ids or e['target'] in removed_ids:
        dropped_touch += 1
    else:
        kept_edges.append(e)
print(f'[移除] 节点 -{len(removed_nodes)} (剩余 {len(kept_nodes)}), 触及边 -{dropped_touch} (剩余 {len(kept_edges)})')

# --- 2. 并入新产物 ---
products = sorted(glob.glob(f'{W}/products/batch-*.json'))
new_nodes, new_edges_raw = [], []
for p in products:
    b = json.load(open(p))
    new_nodes += b.get('nodes', [])
    new_edges_raw += b.get('edges', [])
print(f'[并入] 产物 {len(products)} 批: 新节点 {len(new_nodes)}, 新边 {len(new_edges_raw)}')

# 归一化：func:→function:；类型/前缀校验
# 2026-10-31 扩：batch-104 实证 step/pipeline/service/schema 为 file-analyzer.md L127/L160-177 规范合法类型（CI step/Dockerfile/CI yaml/proto）；
# validator fileTypes 与 phase4_prep FILE_LEVEL_TYPES 同源；step 为子节点类型（同 class/function，不入 layers）
VALID = {'file', 'class', 'function', 'module', 'concept', 'config', 'document',
         'service', 'pipeline', 'schema', 'table', 'resource', 'endpoint', 'step'}
def norm_node(n):
    t = n.get('type')
    if t == 'func': n['type'] = 'function'
    i = n.get('id', '')
    if i.startswith('func:'): i = 'function:' + i[5:]
    n['id'] = i
    for k in ('summary', 'tags', 'complexity'):
        n.setdefault(k, [] if k == 'tags' else ('' if k != 'complexity' else 'simple'))
    return n
new_nodes = [norm_node(n) for n in new_nodes if n.get('id') and n.get('type') in VALID]

kept_ids = {n['id'] for n in kept_nodes}
seen = set(); add_nodes = []
dup_new = 0
for n in new_nodes:
    if n['id'] in seen: dup_new += 1; continue
    seen.add(n['id'])
    if n['id'] in kept_ids: dup_new += 1; continue  # 与未变文件撞 id（异常，跳过并计）
    add_nodes.append(n)
final_nodes = kept_nodes + add_nodes
final_ids = {n['id'] for n in final_nodes}

# 边：源目标都须在终集；去重（同 source/target/type）
# 2026-10-31 兜底：file: 端点悬空但磁盘存在（基线洞二环，如 rust lib.rs barrel）→ 补最小节点救边；
# 不造假摘要（诚实标注未深析）。符号级悬空仍诚实丢弃（重构阵亡）。
edge_seen = set(); add_edges = []; dangling = 0; dup_edge = 0; rescued_files = set()
def ensure_file_node(sid):
    p = sid[5:]
    if not os.path.exists(os.path.join(REPO, p)): return False
    rescued_files.add(p)
    final_nodes.append({'id': sid, 'type': 'file', 'name': os.path.basename(p), 'filePath': p,
        'summary': '基线洞补录节点（旧轮未收录，本轮为保活引用边自动补建，未做深度分析）',
        'tags': ['baseline-hole', 'auto-rescued'], 'complexity': 'simple'})
    final_ids.add(sid)
    return True
for e in new_edges_raw:
    s, t, ty = e.get('source'), e.get('target'), e.get('type')
    if not s or not t or not ty: dangling += 1; continue
    if s.startswith('func:'): s = 'function:' + s[5:]
    if t.startswith('func:'): t = 'function:' + t[5:]
    if s.startswith('file:') and s not in final_ids: ensure_file_node(s)
    if t.startswith('file:') and t not in final_ids: ensure_file_node(t)
    if s not in final_ids or t not in final_ids: dangling += 1; continue
    k = (s, t, ty)
    if k in edge_seen: dup_edge += 1; continue
    edge_seen.add(k)
    e['source'], e['target'] = s, t
    add_edges.append(e)
final_edges = kept_edges + add_edges
print(f'[兜底救边] 磁盘存在的悬空 file: 端点补录 {len(rescued_files)} 个最小节点')

# --- 3. 空 __init__.py 补平凡节点（changed 集内被剔的 0 字节包标记）---
empty_inits = [p for p in delta['changed'] if p.endswith('__init__.py')
               and os.path.getsize(os.path.join(REPO, p)) == 0]
for p in empty_inits:
    nid = f'file:{p}'
    if nid not in {n['id'] for n in final_nodes}:
        final_nodes.append({'id': nid, 'type': 'file', 'name': os.path.basename(p),
            'filePath': p, 'summary': '空包标记文件（__init__.py，无实现内容）',
            'tags': ['package-marker'], 'complexity': 'simple'})
print(f'[兜底] 空 __init__ 补节点 {len(empty_inits)} 个')

# --- 4. 汇总 ---
print(f'[守恒] 节点 {n0} -{len(removed_nodes)} +{len(add_nodes)} = {len(final_nodes)}')
print(f'[守恒] 边   {e0} -{dropped_touch} +{len(add_edges)} = {len(final_edges)}')
print(f'[质量] 新节点重复丢弃 {dup_new}, 新边悬空 {dangling}, 新边重复 {dup_edge}')
# 悬空终检
fids = {n['id'] for n in final_nodes}
bad = sum(1 for e in final_edges if e['source'] not in fids or e['target'] not in fids)
print(f'[终检] 悬空边残留 {bad} (必须 0)')

if not DRY and bad == 0:
    out = {'nodes': final_nodes, 'edges': final_edges,
           'layers': g.get('layers', []), 'tour': g.get('tour', []),
           'meta': g.get('meta', {})}
    json.dump(out, open(f'{REPO}/.understand-anything/intermediate/assembled-graph.json', 'w'),
              ensure_ascii=False)
    print('[落盘] intermediate/assembled-graph.json 已更新（layers/tour 待重算，勿直接 finalize）')
    # 统计快照
    tc = collections.Counter(n['type'] for n in final_nodes)
    json.dump({'nodes': len(final_nodes), 'edges': len(final_edges),
               'types': dict(tc), 'removed_nodes': len(removed_nodes),
               'dropped_touch': dropped_touch, 'add_nodes': len(add_nodes),
               'add_edges': len(add_edges), 'dangling': dangling},
              open(f'{W}/surgery-report.json', 'w'), ensure_ascii=False, indent=1)
else:
    print('[DRY/失败] 未落盘')
