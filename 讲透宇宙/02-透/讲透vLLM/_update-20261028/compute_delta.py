#!/usr/bin/env python3
"""vLLM understand 图谱增量对账：旧图谱节点覆盖 × git 基线→HEAD 变更 × 新扫描全集 → delta.json"""
import json, subprocess, os, sys, collections

REPO = '/usr-data/data2/repos/pytorch-landscape/repos/vllm'
UA = os.path.join(REPO, '.understand-anything')
OUT = '~/ai/work4ai/讲透vLLM/_update-20261028'
BASELINE = '7894394b0759ba0f2d9c9cca249a6e49ecdd814f'

# 1. 旧图谱节点归因（所有带 filePath 的节点）
g = json.load(open(os.path.join(UA, 'knowledge-graph.json')))
covered_by_file = collections.defaultdict(list)
for n in g['nodes']:
    fp = n.get('filePath')
    if fp:
        covered_by_file[fp].append(n['id'])
covered = set(covered_by_file)
print(f'[1] 旧图谱: {len(g["nodes"])} 节点, 有 filePath 的文件 {len(covered)} 个')

# 2. git 变更（无 rename 检测，M/A/D 干净分类）
r = subprocess.run(['git', '-C', REPO, 'diff', '--no-renames', '--name-status',
                    f'{BASELINE}..HEAD'], capture_output=True, text=True)
git_status = {}  # path -> status
for line in r.stdout.splitlines():
    st, path = line.split('\t', 1)
    git_status[path.strip('"')] = st
print(f'[2] git 变更路径: {len(git_status)} (M={sum(1 for v in git_status.values() if v=="M")}, A={sum(1 for v in git_status.values() if v=="A")}, D={sum(1 for v in git_status.values() if v=="D")})')

# 3. 当前扫描全集
scan = json.load(open(os.path.join(UA, 'intermediate/scan-result.json')))
current = {f['path'] for f in scan['files']}
print(f'[3] 当前扫描: {len(current)} 文件')

# 旧扫描全集（fingerprints 基线）
fp = json.load(open(os.path.join(UA, 'fingerprints.json')))
old_scanned = set(fp['files'].keys())
print(f'[3b] 旧扫描基线: {len(old_scanned)} 文件')

# 4. 三清单
deleted = sorted(p for p in covered if p not in current)                 # 有节点但已消失
changed = sorted(p for p in covered if git_status.get(p) in ('M', 'A') and p in current)  # 有节点且变了
added_all = sorted(p for p in current if p not in old_scanned and p not in covered)      # 真新增（旧扫描没有）
print(f'[4] 裸数字: deleted={len(deleted)} changed={len(changed)} added_all={len(added_all)}')

# 5. added 过滤（沿用原覆盖策略：主干优先，数据文件裁剪）
DATA_PAT = ('.json', '.png', '.jpg', '.svg', '.bin', '.lock', '.csv')
DATA_DIRS = ('tests/', 'docs/', 'examples/', 'benchmarks/', '.github/', 'csrc/',
             'tools/', 'scripts/')  # csrc C++ 原图未覆盖；tests 等原裁剪
def keep(p):
    if p.startswith(DATA_DIRS): return False
    if p.endswith(DATA_PAT): return False
    # .agents/.claude 等 dot 技能目录：原图基本无节点，跳过
    if p.startswith(('.agents/', '.claude/', '.opencode/', '.devcontainer/')): return False
    return True
added = [p for p in added_all if keep(p)]
# changed 里也过滤掉已不该覆盖的（如 .agents md）
changed_f = [p for p in changed if keep(p)]
dropped_from_changed = len(changed) - len(changed_f)
print(f'[5] added 过滤后: {len(added)} (裁 {len(added_all)-len(added)}); changed 过滤后: {len(changed_f)} (裁 {dropped_from_changed})')

# added 分布
c = collections.Counter('/'.join(p.split('/')[:2]) for p in added)
print('    added top 前缀:', c.most_common(12))
cc = collections.Counter('/'.join(p.split('/')[:2]) for p in changed_f)
print('    changed top 前缀:', cc.most_common(12))

# 6. 落盘
delta = {
    'baseline': BASELINE, 'head': subprocess.run(['git','-C',REPO,'rev-parse','HEAD'],
        capture_output=True,text=True).stdout.strip(),
    'deleted': deleted, 'changed': changed_f, 'added': added,
    'added_dropped': [p for p in added_all if not keep(p)],
    'covered_count': len(covered), 'old_scanned_count': len(old_scanned),
    'current_scan_count': len(current),
}
json.dump(delta, open(os.path.join(OUT, 'delta.json'), 'w'), ensure_ascii=False, indent=1)
reanalyze = sorted(set(changed_f) | set(added))
json.dump({'files': reanalyze}, open(os.path.join(OUT, 'reanalyze-set.json'), 'w'), ensure_ascii=False, indent=1)
print(f'[6] 重分析全集: {len(reanalyze)} 文件 (changed {len(changed_f)} + added {len(added)})')
