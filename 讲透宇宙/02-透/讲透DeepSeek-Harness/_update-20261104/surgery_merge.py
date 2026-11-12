#!/usr/bin/env python3
"""图手术合并（deepseek-harness 0.1.2→0.2.2 刷新轮）：旧图谱 − (changed∪deleted 文件的节点/边) + 新批产物 → assembled graph
改造自 vLLM 轮 2026-10-28 surgery_merge.py（钉版条款：悬空边三分类，严禁一律静默 drop）
用法: python3 surgery_merge.py [--dry]
守恒公式: nodes_after = nodes_before - removed + added_new; 悬空边必须有去向报告
"""
import json, os, sys, glob, collections

REPO = '/usr-data/data2/repos/deepseek-ai/deepseek-harness'
W = '/data/usershare/ai/work4ai/讲透DeepSeek-Harness/_update-20261104'
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
# VALID = file-analyzer 规范合法类型（vLLM 轮 2026-10-31 扩版：step/pipeline/service/schema 合法）
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
# 兜底：file: 端点悬空但磁盘存在（基线洞/barrel）→ 补最小节点救边，不造假摘要；
# 符号级悬空（changed 文件重构后消失的符号）诚实丢弃，报告计数。
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
symbol_dangling = []
for e in new_edges_raw:
    s, t, ty = e.get('source'), e.get('target'), e.get('type')
    if not s or not t or not ty: dangling += 1; continue
    if s.startswith('func:'): s = 'function:' + s[5:]
    if t.startswith('func:'): t = 'function:' + t[5:]
    if s.startswith('file:') and s not in final_ids: ensure_file_node(s)
    if t.startswith('file:') and t not in final_ids: ensure_file_node(t)
    if s not in final_ids or t not in final_ids:
        dangling += 1
        symbol_dangling.append((s, t, ty))
        continue
    k = (s, t, ty)
    if k in edge_seen: dup_edge += 1; continue
    edge_seen.add(k)
    e['source'], e['target'] = s, t
    add_edges.append(e)
final_edges = kept_edges + add_edges
print(f'[兜底救边] 磁盘存在的悬空 file: 端点补录 {len(rescued_files)} 个最小节点')
if rescued_files:
    sf = sorted(rescued_files)
    print('  基线洞文件样本:', sf[:10])

# --- 3. 汇总 ---
print(f'[守恒] 节点 {n0} -{len(removed_nodes)} +{len(add_nodes)} (+{len(rescued_files)}兜底) = {len(final_nodes)}')
print(f'[守恒] 边   {e0} -{dropped_touch} +{len(add_edges)} = {len(final_edges)}')
print(f'[质量] 新节点重复丢弃 {dup_new}, 新边悬空 {dangling} (符号级,诚实丢弃), 新边重复 {dup_edge}')
# 悬空终检
fids = {n['id'] for n in final_nodes}
bad = sum(1 for e in final_edges if e['source'] not in fids or e['target'] not in fids)
print(f'[终检] 悬空边残留 {bad} (必须 0)')
# 符号级悬空归因（前缀分布，供人工复核）
pref = collections.Counter(s.split(':')[0] for s,t,ty in symbol_dangling)
print(f'[归因] 符号级悬空端点类型分布: {dict(pref)}')

if not DRY and bad == 0:
    out = {'nodes': final_nodes, 'edges': final_edges,
           'layers': g.get('layers', []), 'tour': g.get('tour', []),
           'meta': g.get('meta', {})}
    json.dump(out, open(f'{REPO}/.understand-anything/intermediate/assembled-graph.json', 'w'),
              ensure_ascii=False)
    print('[落盘] intermediate/assembled-graph.json 已更新（layers/tour 待重算，勿直接 finalize）')
    tc = collections.Counter(n['type'] for n in final_nodes)
    json.dump({'nodes': len(final_nodes), 'edges': len(final_edges),
               'types': dict(tc), 'removed_nodes': len(removed_nodes),
               'dropped_touch': dropped_touch, 'add_nodes': len(add_nodes),
               'add_edges': len(add_edges), 'dangling': dangling,
               'rescued_files': sorted(rescued_files),
               'symbol_dangling_sample': symbol_dangling[:200]},
              open(f'{W}/surgery-report.json', 'w'), ensure_ascii=False, indent=1)
else:
    print('[DRY/失败] 未落盘')
