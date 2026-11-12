#!/usr/bin/env python3
"""锚终验：解析 md 中全路径 行号锚，逐条到仓内核实行号存在性（先 basename 消歧再判界）。用法：python3 verify_anchors.py <md> <repo_root>"""
import re, sys, os, collections

md, root = sys.argv[1], sys.argv[2]
text = open(md, encoding="utf-8").read()
raw = re.findall(r"`([a-zA-Z0-9_./-]+\.(?:md|mjs|json|yml|ts)):([0-9]+)(?:-([0-9]+))?`", text)
# 展开区间锚
anchors = []
for path, s, e in raw:
    if e:
        anchors.extend([(path, i) for i in range(int(s), int(e) + 1)])
    else:
        anchors.append((path, int(s)))

# basename 唯一性消歧表
bybase = collections.defaultdict(set)
for dp, dn, fns in os.walk(root):
    if ".git" in dp or ".understand-anything" in dp:
        continue
    for fn in fns:
        bybase[fn].add(os.path.relpath(os.path.join(dp, fn), root))

bad = 0
seen = set()
for path, ln in anchors:
    key = (path, ln)
    if key in seen:
        continue
    seen.add(key)
    full = path if os.path.exists(os.path.join(root, path)) else None
    if not full:
        base = os.path.basename(path)
        cands = [c for c in bybase.get(base, set()) if c.endswith(path) or path.endswith(c)]
        if len(cands) == 1:
            full = cands[0]
        elif os.path.exists(os.path.join(root, "plugins/codex", path)):
            full = os.path.join("plugins/codex", path)  # 插件内短路径约定
    if not full:
        print(f"UNRESOLVED {path}:{ln}")
        bad += 1
        continue
    lines = open(os.path.join(root, full), encoding="utf-8").readlines()
    if ln < 1 or ln > len(lines):
        print(f"OUT-OF-RANGE {full}:{ln} (file {len(lines)}L)")
        bad += 1
print(f"[{os.path.basename(md)}] unique anchors {len(seen)}, bad {bad}")
sys.exit(1 if bad else 0)
