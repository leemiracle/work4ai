#!/usr/bin/env python3
"""矩阵总分析：3模型 × 3变体 × 102case
- 分模型×变体×类别 通过率/score/token/延迟
- McNemar exact（slim vs orig，配对 by case）
- 中文语言保留率（lang=zh case 的输出含 CJK 比例）
- arch 案例调整视图（V1 设计边界公平性）
- 输出 markdown 表格到 results/matrix_v2.md
"""
import json, re, math
from collections import defaultdict

ART = "~/ai/work4ai/工程化手册库/prompt工程手册/prompts/eval_artifacts"
RUNS = {"glm-4-flash": f"{ART}/results/v2_flash.json",
        "glm-4.7": f"{ART}/results/v2_47.json",
        "glm-5.3": f"{ART}/results/v2_53.json"}
SHORT = {"additive_orig.json": "orig", "additive_slim.json": "slim", "fact_v1.json": "V1"}
def variant_of(pid):
    for k, v in SHORT.items():
        if pid.endswith(k): return v
    return pid

data = {}  # model -> {(desc): {variant: result}}
meta = {}
for model, path in RUNS.items():
    R = json.load(open(path))["results"]
    idx2v = {}
    for i, p in enumerate(R["prompts"]):
        lab = p.get("label") or p.get("id") or ""
        idx2v[i] = "orig" if "orig" in lab else ("slim" if "slim" in lab else "V1")
    d = defaultdict(dict)
    for r in R["results"]:
        v = variant_of(r["promptId"]) if not isinstance(r.get("promptIdx"), int) else idx2v[r["promptIdx"]]
        desc = r["testCase"]["description"]
        d[desc][v] = r
    data[model] = d

def cat(desc): return desc.split("]")[0][1:]

# ---------- 总矩阵 ----------
lines = []
A = lines.append
A("# mem0 黄金集 v2 矩阵（3 模型 × 3 变体 × 102 case，2026-08-17）\n")
A("| 模型 | 变体 | normal | edge | adv | 总通过 | score | tok/case in | 延迟ms |")
A("|---|---|---|---|---|---|---|---|---|")
for model in RUNS:
    for v in ["V1", "orig", "slim"]:
        st = defaultdict(lambda: [0, 0, 0.0, 0, 0.0])  # cat -> [pass, n, score, tok_in, lat]
        tot = [0, 0, 0.0, 0, 0.0]
        for desc, vs in data[model].items():
            r = vs.get(v)
            if not r: continue
            c = cat(desc)
            ok = 1 if r["success"] else 0
            for bucket in ([st[c], tot] if c != "all" else [tot]):
                bucket[0] += ok; bucket[1] += 1; bucket[2] += r.get("score") or 0
                bucket[3] += (r.get("tokenUsage") or {}).get("prompt", 0); bucket[4] += r.get("latencyMs") or 0
        cells = []
        for c in ["normal", "edge", "adv"]:
            p, n = st[c][0], st[c][1]
            cells.append(f"{p}/{n}" + (f" ({p/n:.2f})" if n else ""))
        A(f"| {model} | {v} | {cells[0]} | {cells[1]} | {cells[2]} | **{tot[0]}/{tot[1]} ({tot[0]/tot[1]:.1%})** | {tot[2]/tot[1]:.3f} | {tot[3]//tot[1]} | {int(tot[4]/tot[1])} |")
    A("| | | | | | | | | |")

# ---------- McNemar exact ----------
def mcnemar(b, c):
    n = b + c
    if n == 0: return 1.0
    p = sum(math.comb(n, k) for k in range(0, min(b, c) + 1)) / 2 ** n * 2
    return min(p, 1.0)

A("\n## McNemar（配对 by case，slim vs orig vs V1）\n")
A("| 模型 | 对比 | b (A过B败) | c (A败B过) | exact p | 结论 |")
A("|---|---|---|---|---|---|")
for model in RUNS:
    for a, b_ in [("slim", "orig"), ("slim", "V1"), ("orig", "V1")]:
        bb = cc = 0
        for desc, vs in data[model].items():
            ra, rb = vs.get(a), vs.get(b_)
            if not ra or not rb: continue
            if ra["success"] and not rb["success"]: bb += 1
            if not ra["success"] and rb["success"]: cc += 1
        p = mcnemar(bb, cc)
        concl = "显著" if p < 0.05 else ("趋势" if p < 0.15 else "不显著")
        A(f"| {model} | {a} vs {b_} | {bb} | {cc} | {p:.4f} | {concl} |")

# ---------- 中文语言保留 ----------
A("\n## 中文语言保留（lang=zh，7 case：normal 6 + edge 1）\n")
A("| 模型 | 变体 | 输出含 CJK 的 zh case 数 |")
A("|---|---|---|")
cjk = re.compile(r"[\u4e00-\u9fff]")
for model in RUNS:
    for v in ["V1", "orig", "slim"]:
        n = hit = 0
        for desc, vs in data[model].items():
            r = vs.get(v)
            if not r or r["vars"].get("lang") != "zh": continue
            n += 1
            if cjk.search(str((r.get("response") or {}).get("output", ""))): hit += 1
        A(f"| {model} | {v} | {hit}/{n} |")

# ---------- arch 调整视图 ----------
A("\n## arch 调整（assistant 侧 6 case：V1 设计上只提 user）\n")
A("| 模型 | V1(arch6) | orig(arch6) | slim(arch6) | V1(其余96) | orig(其余96) | slim(其余96) |")
A("|---|---|---|---|---|---|---|")
for model in RUNS:
    row = [model]
    for scope in ["arch", "rest"]:
        for v in ["V1", "orig", "slim"]:
            p = n = 0
            for desc, vs in data[model].items():
                r = vs.get(v)
                if not r: continue
                is_arch = r["vars"].get("arch") == "1"
                if (scope == "arch") != is_arch: continue
                n += 1; p += 1 if r["success"] else 0
            row.append(f"{p}/{n}")
    A("| " + " | ".join(row) + " |")

# ---------- 失败模式横切（每模型×变体 top 失败 case） ----------
A("\n## 各模型失败集中点（slim 变体，失败 case 描述）\n")
for model in RUNS:
    fails = [desc for desc, vs in data[model].items() if vs.get("slim") and not vs["slim"]["success"]]
    A(f"- **{model}** slim 失败 {len(fails)}: " + "; ".join(d.split('] ')[1][:40] for d in fails[:12]))

out = "\n".join(lines)
open(f"{ART}/results/matrix_v2.md", "w").write(out)
print(out)
