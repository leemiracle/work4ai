#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E 案例仿真执行器：DEC T1-T5 的参数化仿真（ThinkBase 企业知识库 RAG）
====================================================================
定位（诚实声明）：这是**参数化仿真**，不是真实系统——机制参数从 87 条投诉的
客服分布（34/31/19/12/4）与领域常识校准，seed 固定可复现。作用：把 e2e 演练
从"纸面契约"推进到"可运行的 Evidence"，走完三段式回流。

执行 DEC 的任务映射：
  T1 复现 87 条投诉的可观测预言（H1/H2/H3 各自检验）
  T2 200 条分层错误集（3行业×3查询类型×5维度 = 45 格配额）
  T4 管线基线冻结（事件级错误率）
  T5 归因判决：三个竞争假设定量裁决 + 干预实验（span对齐/版本重排/结构chunking）
运行：python3 e2e_kb_sim.py
"""
import random
from collections import Counter

random.seed(20260904)  # 冻结基线的一部分

# ---------------- 语料结构参数（T1 审计的静态事实） ----------------
CORPUS = dict(
    industries=["finance", "tech", "hr"],
    query_types=["fact", "process", "data"],
    doc_struct_share=0.35,     # 语料中结构化文档（表格/多级列表）占比——HC 的对照基线
    topk_contains_correct=0.92 # 现状检索质量：正确文档在 top-k 的概率（HA 预言锚点）
)

# 管线现状缺陷机制（Domain L3 假设的参数化）：
#   H1 无 span 对齐 → attribution 错误 = "文档对了但 claim 不可定位"
#      且 factuality 投诉中一部分实为"答案对但无法核证"（感知幻觉）
#   H2 版本盲检索 → 旧版与新版词面平权，过期引用集中于版本迭代文档
#   H3 chunking 破坏 → 结构化文档的 completeness 错误率显著高于散文

# ---------------- T1：87 条投诉的预言检验 ----------------
def t1_reproduce(n=87):
    # 维度标签按客服分布生成（34/31/19/12/4）
    dims = (["attribution"]*30 + ["factuality"]*27 + ["freshness"]*16 +
            ["completeness"]*11 + ["business"]*3)  # 87 条按比例取整
    c = Counter(dims)
    ha = hb = hc = resid = 0
    for d in dims:
        if d == "attribution":
            # HA 预言：正确文档在 top-k 且内容一致（P=0.92）
            if random.random() < CORPUS["topk_contains_correct"]: ha += 1
            else: resid += 1
        elif d == "factuality":
            # 诊断：55% 实为对齐感知型（答案对但无法核证→被判不可信），45% 真编造
            if random.random() < 0.55: ha += 1
            else: resid += 1
        elif d == "freshness":
            # HB 预言：正确版本已在索引、被版本盲打分挤出（P=0.85）
            if random.random() < 0.85: hb += 1
            else: resid += 1
        elif d == "completeness":
            # HC 预言：错误富集于结构化文档（P=0.78 vs 语料占比 0.35）
            if random.random() < 0.78: hc += 1
            else: resid += 1
        else:
            resid += 1  # business 正确性：三假设射程外
    return c, ha, hb, hc, resid

# ---------------- T2：200 条分层错误集 ----------------
def t2_error_dataset(total=200):
    dims = ["attribution", "factuality", "freshness", "completeness", "business"]
    quota = Counter()
    cells = [(i, q, d) for i in CORPUS["industries"] for q in CORPUS["query_types"] for d in dims]
    for k in range(total):
        quota[cells[k % len(cells)]] += 1   # 45 格轮转配额（3x3x5=45，200/45≈4-5条/格）
    per_dim = Counter()
    for (i, q, d), n in quota.items(): per_dim[d] += n
    return quota, per_dim

# ---------------- T4：事件级基线（每 1000 次问答的错误率） ----------------
def t4_baseline(events=4000):
    base = dict(attribution=0.18, factuality=0.025, freshness=0.11,
                completeness=0.07, business=0.025)
    stats = Counter()
    for _ in range(events):
        r = random.random(); acc = 0
        for dim, p in base.items():
            acc += p
            if r < acc: stats[dim] += 1; break
    return {d: round(stats[d]/events, 4) for d in base}

# ---------------- T5：三干预实验 + 归因判决 ----------------
def t5_interventions(baseline):
    fix = dict(span_align=dict(attribution=0.90, factuality=0.55),  # 对齐修：attribution -90%，感知幻觉中55%为对齐型可修
               version_rerank=dict(freshness=0.88),                 # 版本重排：过期 -88%
               struct_chunk=dict(completeness=0.75))                # 结构感知：completeness -75%
    after = dict(baseline)
    for name, fixes in fix.items():
        for dim, red in fixes.items():
            # 感知幻觉的修复：55% 对齐型由 span_align 修（factuality 的 red 已折算）
            after[dim] = round(after[dim] * (1 - red), 4)
    metrics = dict(
        attribution_coverage = round(1 - after["attribution"], 4),
        perceived_hallucination = round(after["factuality"], 4),
        stale_citation_rate = round(after["freshness"], 4),
    )
    return after, metrics

def main():
    print("=" * 62)
    print("E2E 仿真：ThinkBase 可信度修复（DEC T1-T5，seed=20260904）")
    print("=" * 62)

    c, ha, hb, hc, resid = t1_reproduce()
    print(f"\n[T1 复现] 87 条投诉维度分布（对照客服标签 34/31/19/12/4）：")
    print("  " + "  ".join(f"{k}:{v}" for k, v in c.most_common()))
    print(f"  预言检验：HA命中={ha}（{ha/87:.0%}） HB命中={hb}（{hb/87:.0%}）"
          f" HC命中={hc}（{hc/87:.0%}） 射程外/残差={resid}（{resid/87:.0%}）")
    print(f"  HC 富集检验：投诉中结构化文档 {hc/(hc+max(1,(11-hc))) if hc else 0:.0%}"
          f" vs 语料结构化占比 {CORPUS['doc_struct_share']:.0%} → 富集倍数 "
          f"{(hc/max(1,11-hc))/(CORPUS['doc_struct_share']/(1-CORPUS['doc_struct_share'])):.1f}x")

    quota, per_dim = t2_error_dataset()
    print(f"\n[T2 错误集] 200 条 / 45 格（3行业×3查询×5维度），维度配额：")
    print("  " + "  ".join(f"{k}:{v}" for k, v in per_dim.most_common()))

    baseline = t4_baseline()
    print(f"\n[T4 基线冻结] 事件级错误率（4000 events）：")
    for k, v in baseline.items(): print(f"  {k:<14}{v:.2%}")

    after, metrics = t5_interventions(baseline)
    print(f"\n[T5 干预实验] 三干预全上后的残余错误率：")
    for k, v in after.items(): print(f"  {k:<14}{v:.2%}  (基线 {baseline[k]:.2%})")
    print(f"\n  → 三门槛预估（对 PRC.success_definition）：")
    checks = [("引用覆盖率>=95%", metrics["attribution_coverage"] >= 0.95, f"{metrics['attribution_coverage']:.1%}"),
              ("幻觉率<=2%",     metrics["perceived_hallucination"] <= 0.02, f"{metrics['perceived_hallucination']:.1%}"),
              ("过期引用<=3%",   metrics["stale_citation_rate"] <= 0.03,       f"{metrics['stale_citation_rate']:.1%}")]
    for name, ok, val in checks:
        print(f"    {'✅' if ok else '❌'} {name}: 实测 {val}")

    total_h = ha + hb + hc
    print(f"\n[判决] 归因权重：HA引用对齐 {ha/87:.0%} / HB版本盲检索 {hb/87:.0%} /"
          f" HC结构破坏 {hc/87:.0%} / 残差 {resid/87:.0%}")
    winner = max([("HA 引用对齐缺失", ha), ("HB 版本盲检索", hb), ("HC chunking 破坏", hc)], key=lambda x: x[1])
    print(f"  → 主根因：{winner[0]}（{winner[1]/87:.0%}）——T4 优先实施 span 对齐器")
    print("""\n[仿真边界声明]
1. 参数化仿真：机制参数校准自 87 条客服分布+管线现状审计假设，非真实系统数据；
2. 置信度：HA 的 factuality 重分类（55% 对齐感知型）是最大不确定源，T2 错误集
   人工标注（kappa>=0.8）后应重跑本仿真校准；
3. 三门槛实测值为机制推演，真实验收以 DEC.acceptance 的 pytest 命令为准。""")

if __name__ == "__main__":
    main()
