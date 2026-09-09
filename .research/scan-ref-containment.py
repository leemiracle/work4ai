#!/usr/bin/env python3
"""违规blob的分支包含分析：哪些 ref 够得着 ≥10MB blob 或 pdf blob。
体积红线审计配套工具（2026-09-10 起红线：仓库无 PDF、无 ≥10MB 文件）。
用法: python .research/scan-ref-containment.py"""
import subprocess


def run(args, inp=None):
    r = subprocess.run(args, capture_output=True, input=inp)
    if r.returncode != 0:
        raise RuntimeError(f"{args}: {r.stderr.decode('utf-8','replace')}")
    return r.stdout.decode("utf-8", "replace")


ids = [l.strip() for l in run(["git", "rev-list", "--objects", "--all", "--no-object-names"]).splitlines() if l.strip()]
batch = run(["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
            inp=("\n".join(ids) + "\n").encode())
sizes = {}
for line in batch.splitlines():
    p = line.split()
    if len(p) == 3 and p[1] == "blob":
        sizes[p[0]] = int(p[2])

path_out = run(["git", "rev-list", "--objects", "--all"])
paths = {}
for line in path_out.splitlines():
    if " " in line:
        h, p = line.split(" ", 1)
        if h in sizes:
            paths.setdefault(h, set()).add(p)

bad = {h for h, s in sizes.items() if s >= 10 * 1024 * 1024} | \
      {h for h, ps in paths.items() if any(x.lower().endswith(".pdf") for x in ps)}
print(f"违规 blob 总数: {len(bad)} (≥10MB {sum(1 for h in bad if sizes[h]>=10*1024*1024)} + pdf {sum(1 for h in bad if sizes[h]<10*1024*1024)})")

refs = [l for l in run(["git", "for-each-ref", "--format=%(refname)"]).splitlines() if l.strip()]
for ref in refs:
    reach = run(["git", "rev-list", "--objects", ref, "--no-object-names"]).splitlines()
    hit = bad & set(reach)
    if hit:
        tot = sum(sizes[h] for h in hit) / 1024 / 1024
        print(f"  {ref}: 命中 {len(hit)} 个违规blob, 合计 {tot:.0f}MB")
    else:
        print(f"  {ref}: 干净")
