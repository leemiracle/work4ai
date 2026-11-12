#!/usr/bin/env python3
"""把 reanalyze-set 分批 v2：tier 排序流式切块（同 tier 目录亲和），纯文档批 45 / 代码批 25
v1 教训：按包分组导致 615 组/645 批（均值 6 文件）——dsh 是 379 微包仓，必须跨包合并"""
import json, os, collections

W = '/data/usershare/ai/work4ai/讲透DeepSeek-Harness/_update-20261104'
files = json.load(open(f'{W}/reanalyze-set.json'))['files']

PRIORITY = [
    'packages/core', 'packages/api', 'packages/session', 'packages/agent',
    'packages/context', 'packages/compaction', 'packages/llm', 'packages/shell',
    'packages/subprocess', 'packages/terminal', 'packages/ssh', 'packages/sandbox',
    'packages/fs', 'packages/skill', 'packages/mcp', 'packages/web',
    'packages/subagent', 'packages/team', 'packages/jobs', 'packages/workflow',
    'packages/todo', 'packages/plan', 'packages/goal', 'packages/guard',
    'packages/deliverables', 'packages/attachment', 'packages/spill',
    'packages/typert', 'packages/sdk', 'packages/host', 'packages/client',
    'packages/boot', 'packages/bundle', 'packages/preset', 'packages/extensions',
    'packages/session-query', 'packages/storage', 'packages/workspace',
    'packages/interaction', 'packages/acp', 'packages/feedback',
    'packages/identity', 'packages/settings', 'packages/credentials',
    'packages/computer-use', 'packages/browser-use', 'packages/ptc-runtime',
    'packages/util', 'packages/test-support', 'packages/experimental',
    'docs', '.agents', 'apps', 'scripts', 'native', 'python',
]
def tier(p):
    for i, pre in enumerate(PRIORITY):
        if p.startswith(pre + '/') or p == pre:
            return i
    return len(PRIORITY)

def group_key(p):
    parts = p.split('/')
    if parts[0] == 'packages' and len(parts) >= 3:
        return '/'.join(parts[:3])
    if len(parts) >= 2:
        return '/'.join(parts[:2])
    return parts[0]

DOC_EXT = {'.md', '.json', '.yaml', '.yml', '.txt', '.example'}
stream = sorted(files, key=lambda p: (tier(p), group_key(p), p))

batches, cur, cur_doc = [], [], True
def flush():
    global cur, cur_doc
    if cur:
        batches.append({'batchIndex': len(batches) + 1, 'files': cur})
    cur, cur_doc = [], True

for p in stream:
    is_doc = os.path.splitext(p)[1] in DOC_EXT
    limit = 45 if cur_doc and is_doc else 25
    if len(cur) >= limit or (cur and tier(p) != tier(cur[0])):
        flush()
        limit = 45 if is_doc else 25
    cur.append(p)
    cur_doc = cur_doc and is_doc
flush()

os.makedirs(f'{W}/batches', exist_ok=True)
for f in os.listdir(f'{W}/batches'):
    os.remove(os.path.join(f'{W}/batches', f))
for b in batches:
    json.dump(b, open(f"{W}/batches/batch-{b['batchIndex']:03d}.json", 'w'),
              ensure_ascii=False, indent=1)
json.dump({'count': len(batches), 'totalFiles': sum(len(b['files']) for b in batches)},
          open(f'{W}/batches/_meta.json', 'w'), ensure_ascii=False, indent=1)

sizes = [len(b['files']) for b in batches]
tiers = collections.Counter(tier(b['files'][0]) for b in batches)
print(f'批数 {len(batches)} / 文件 {sum(sizes)} / 批容量 min={min(sizes)} max={max(sizes)} 均值={sum(sizes)/len(sizes):.1f}')
print('tier 分布:', sorted(tiers.items()))
assert sorted(p for b in batches for p in b['files']) == sorted(files), '覆盖缺口!'
print('覆盖断言 PASS')
