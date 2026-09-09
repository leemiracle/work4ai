#!/usr/bin/env python3
# 用法: python .research/scan-large-files.py [SIZE_MB,默认10] —— 定期审计体积红线(2026-09-10起policy: 无PDF无≥10MB文件)
"""全历史大文件/PDF 扫描：git rev-list --objects --all + cat-file batch-check。
输出: ①历史中 >SIZE_MB 的 blob 及其出现路径与引用它的提交数 ②历史中 .pdf/.PDF 后缀 blob ③当前树违规清单
用法: python .scan-large.py [SIZE_MB，默认10]
"""
import subprocess
import sys
from collections import defaultdict

SIZE_LIMIT = int(sys.argv[1]) * 1024 * 1024 if len(sys.argv) > 1 else 10 * 1024 * 1024


def run(args, inp=None):
    r = subprocess.run(args, capture_output=True, input=inp)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace"))
    return r.stdout.decode("utf-8", "replace")


# 1. 收集所有 blob 与路径
out = run(["git", "rev-list", "--objects", "--all", "--no-object-names"])
ids = [l.strip() for l in out.splitlines() if l.strip()]
batch = run(["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)",
             ], inp=("\n".join(ids) + "\n").encode())
sizes = {}  # hash -> size
for line in batch.splitlines():
    parts = line.split()
    if len(parts) == 3 and parts[1] == "blob":
        sizes[parts[0]] = int(parts[2])

# 路径映射（rev-list --objects 输出 hash + path）
path_out = run(["git", "rev-list", "--objects", "--all"])
paths = defaultdict(set)  # hash -> {path}
for line in path_out.splitlines():
    if " " in line:
        h, p = line.split(" ", 1)
        if h in sizes:
            paths[h].add(p)

big = {h: s for h, s in sizes.items() if s >= SIZE_LIMIT}
pdfs = {h for h, ps in paths.items() if any(p.lower().endswith(".pdf") for p in ps)}

print(f"== 历史中 ≥{SIZE_LIMIT//1024//1024}MB 的 blob: {len(big)} 个 ==")
for h, s in sorted(big.items(), key=lambda x: -x[1])[:40]:
    print(f"  {s/1024/1024:8.1f}MB {h[:12]} {'; '.join(sorted(paths.get(h, ['?']))[:2])}")

print(f"\n== 历史中 .pdf 路径的 blob: {len(pdfs)} 个 ==")
shown = 0
for h in sorted(pdfs, key=lambda h: -sizes[h]):
    if shown >= 40:
        print(f"  ...（其余 {len(pdfs)-40} 个略）")
        break
    print(f"  {sizes[h]/1024/1024:8.2f}MB {h[:12]} {'; '.join(sorted(paths[h])[:2])}")
    shown += 1

# 3. 当前树
cur_out = run(["git", "ls-files", "-z", "--", "*.pdf", "*.PDF"])
cur_pdfs = [p for p in cur_out.split("\0") if p]
ls_out = run(["git", "ls-files", "-s"])
cur_all = [l.split("\t")[1] for l in ls_out.splitlines() if "\t" in l]
print(f"\n== 当前树 .pdf 文件: {len(cur_pdfs)} 个 ==")
for p in cur_pdfs[:40]:
    print("  ", p)
cur_big = []
tree_out = run(["git", "ls-tree", "-r", "-l", "HEAD"])
for line in tree_out.splitlines():
    # 格式: "<mode> <type> <hash> <size>\t<path>"（size在首段尾部,空格分隔）
    if "\t" not in line:
        continue
    meta, path = line.split("\t", 1)
    fields = meta.rsplit(" ", 1)
    if len(fields) != 2 or not fields[1].strip().isdigit():
        continue
    sz = int(fields[1])
    if sz >= SIZE_LIMIT:
        cur_big.append((sz, path))
print(f"\n== 当前树 ≥{SIZE_LIMIT//1024//1024}MB 文件: {len(cur_big)} 个 ==")
for s, p in sorted(cur_big, reverse=True)[:40]:
    print(f"  {s/1024/1024:8.1f}MB {p}")
