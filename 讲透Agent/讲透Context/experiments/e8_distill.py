#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E8 · 蒸馏率：sub-agent 回传多少才够——压缩比 × QA 保持曲线

讲透Context Ch08 的核心实验。对照 Anthropic 多 agent 系统的模式：
  "sub-agent 探索数万 token，只回传 1-2K 蒸馏摘要"——蒸馏率多少是安全线？

设计：
  - 源文档：~4500 字技术调研报告（脚本内置固定文本，含 12 个可测事实：
    版本号/日期/人名/公司/数字，关键词避开裸数字防误判）
  - 6 个条件 × 12 题（答题器固定 glm-4-flash temp=0）：
      full        原文直答（基线，~4.5K 字）
      summ_1_2    摘要到原文 1/2（目标 2250 字）
      summ_1_5    摘要到 1/5（900 字）——≈ Anthropic "数万→1-2K" 的典型比
      summ_1_10   摘要到 1/10（450 字）
      trunc_1_5   头部截断 1/5（对照：暴力截断 vs 理解压缩）
      trunc_tail  尾部截断 1/5（对照：位置效应——事实均匀分布时尾截应同样差）
  - 附带量化：LLM 压缩器守不守字数预算（E5 发现的复测）

用法：python3 e8_distill.py            # 全 glm，~3-4 min
      python3 e8_distill.py --plot
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import glm, save, RES_DIR

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK"]
plt.rcParams["axes.unicode_minus"] = False

DOC = """调研报告：实时协作白板项目技术选型（内部版）

一、背景与目标
本项目目标是在三个月内上线一款支持五十人同时编辑的实时协作白板。
调研组由陈默牵头，成员包括前端负责人林夏与后端负责人周砚。
调研窗口为 2026 年 5 月 11 日至 7 月 3 日，共评审六个候选方案。

二、候选方案与结论
1) CrdtBoard：基于 Yjs 的开源方案，Apache-2.0 许可。离线合并能力强，
   但大画布（万级图元）场景下内存占用偏高，实测峰值 2.4GB。
2) OtsLive：芬兰 Otu Oy 公司的商业方案，报价为首年 4.2 万欧元。
   性能最强（千人压测延迟 p99 为 180 毫秒），但闭源且数据必须托管在法兰克福。
3) WebSocket 自研：完全可控，但估算需要两人年，超出预算窗口。
4) WebRTC DataChannel：P2P 拓扑省服务器带宽，但企业防火墙穿透成功率仅七成。
5) Slabsync：加拿大 Brightleaf 公司的开源方案，MIT 许可，社区活跃度中等，
   最近一次发版是 2026 年 6 月 19 日，版本号 v0.9.2。
6) FlyBoard：国内厂商飞鹭科技的 SaaS，按席位收费每席每月 35 元，
   不支持私有化部署，被合规一票否决。

三、深入评估的两强
CrdtBoard 与 Slabsync 进入 PoC 阶段。PoC 于 6 月第二周完成：
- 五十人同编场景：CrdtBoard 同步延迟中位数 95 毫秒，Slabsync 为 210 毫秒；
- 断网恢复：CrdtBoard 全量恢复，Slabsync 丢失最近约 8 秒操作；
- 图形渲染：Slabsync 的 Canvas 分层渲染更省 CPU（低 22%）；
- 权限模型：CrdtBoard 只有三级角色，Slabsync 支持到画布区域级 ACL。

四、决策与代价
7 月 1 日评审会拍板：主体采用 CrdtBoard，渲染层借鉴 Slabsync 的分层方案。
主要风险登记为两项：大画布内存（缓解：视口裁剪+图元分页）与三级权限不够用
（缓解：在网关层自建区域级 ACL，预计增加三周工期）。
预算方面：方案本身零许可费，但自建 ACL 与渲染改造合计估算 28 人日。

五、遗留问题
国际化字体子集加载方案未定；审计日志是否入图数据库仍在争论，
支持方是周砚，反对方是陈默；下一次决策会定在 8 月 14 日。
"""

QUIZ = [  # (题, 答案关键词列表——命中任一即可，避开裸数字)
    ("牵头调研的人是谁？", ["陈默"]),
    ("调研窗口的开始日期？", ["5 月 11", "5月11"]),
    ("Otu Oy 方案的首年报价？", ["4.2 万", "4.2万"]),
    ("CrdtBoard 的实测内存峰值？", ["2.4"]),
    ("Slabsync 最近发版的版本号？", ["v0.9.2", "0.9.2"]),
    ("FlyBoard 每席每月多少钱？", ["35"]),
    ("评审会拍板日期？", ["7 月 1", "7月1"]),
    ("CrdtBoard 五十人同步延迟中位数？", ["95"]),
    ("Slabsync 断网会丢多久的操作？", ["8 秒", "8秒"]),
    ("渲染改造合计估算多少人日？", ["28"]),
    ("反对方把审计日志入图数据库的是谁？", ["陈默"]),
    ("WebRTC 方案的防火墙穿透成功率？", ["七成", "70%"]),
]

def compress(target_chars):
    """glm 压缩到目标字数。"""
    p = (f"把下面的调研报告压缩成摘要，字数必须在 {int(target_chars*0.9)} 到 {target_chars} 字之间"
         f"（这是硬性下限，短了就是失败），保留全部具体事实"
         f"（数字/日期/人名/公司/版本号/结论）。只输出摘要正文。\n\n{DOC}")
    r = glm("glm-4-flash", p, max_tokens=2000, temperature=0.1, retries=1)
    return r["content"]

def extractive(ratio_denom):
    """确定性抽取式压缩：按句切分，均匀保留，凑到目标字数。
    不依赖 LLM → 压缩比精确受控（干净的自变量）。"""
    import math
    sents = [s for s in re.split(r"(?<=[。；])", DOC) if s.strip()]
    target = len(DOC) / ratio_denom
    out, acc = [], 0
    step = max(1, math.ceil(sum(len(s) for s in sents) / max(target, 1) / 1))
    # 均匀采样句子直到达到 target
    idxs = list(range(0, len(sents), step))
    for i in idxs:
        if acc + len(sents[i]) > target * 1.15:
            break
        out.append(sents[i]); acc += len(sents[i])
    return "".join(out)

def ask(context, q):
    p = f"{context}\n\n---\n根据上文回答，只输出答案本身，不超过 15 字。\n问：{q}"
    r = glm("glm-4-flash", p, max_tokens=24, temperature=0.0, retries=1)
    return r["content"]

def run():
    n = len(QUZ) if False else len(QUIZ)
    conds = {}
    # 压缩（先做，量化预算纪律）
    targets = {"summ_1_2": 2250, "summ_1_5": 900, "summ_1_10": 450}
    summaries = {}
    budget = {}
    for name, tc in targets.items():
        s = compress(tc)
        summaries[name] = s
        budget[name] = {"target_chars": tc, "actual_chars": len(s),
                        "over_budget_pct": round((len(s) / tc - 1) * 100, 1)}
        print(f"{name}: 目标 {tc} 字 → 实际 {len(s)} 字（超 {budget[name]['over_budget_pct']}%）", flush=True)
    full_len = len(DOC)
    conds["full(4.5K字)"] = DOC
    for name, s in summaries.items():
        conds[name] = s
    # 受控压缩比轴：确定性抽取式（自变量干净）
    ext = {"ext_1_2": extractive(2), "ext_1_5": extractive(5), "ext_1_10": extractive(10)}
    for name, s in ext.items():
        conds[name] = s
        print(f"{name}: 抽取式 {len(s)} 字（目标 {full_len // int(name.split('_')[2])}）", flush=True)
    conds["trunc_1_5(头截)"] = DOC[: full_len // 5]
    conds["trunc_1_5(尾截)"] = DOC[-(full_len // 5):]

    results = {}
    for cname, ctx in conds.items():
        hits = 0
        detail = []
        for q, kws in QUIZ:
            a = ask(ctx, q)
            ok = any(k in a for k in kws)
            hits += ok
            detail.append({"q": q, "ans": a, "ok": ok})
        results[cname] = {"score": hits, "total": n, "detail": detail,
                          "ctx_chars": len(ctx),
                          "retention_vs_full": None}
        print(f"{cname:<16} {hits}/{n}", flush=True)

    base = results["full(4.5K字)"]["score"]
    for cname, r in results.items():
        r["retention_vs_full"] = round(r["score"] / base, 3) if base else None

    save("e8_distill", {
        "meta": {"date": "2026-08-26", "answerer/compressor": "glm-4-flash",
                 "doc_chars": full_len, "quiz": n,
                 "anthropic_ref": "sub-agent 数万 token 探索→回传 1-2K（≈1/5-1/10）"},
        "budget_discipline": budget,
        "results": {k: {kk: vv for kk, vv in v.items() if kk != "detail"}
                    for k, v in results.items()},
        "detail": {k: v["detail"] for k, v in results.items()},
    })
    print("落盘: results/e8_distill.json")

def plot():
    data = json.load(open(os.path.join(RES_DIR, "e8_distill.json"), encoding="utf-8"))
    res = data["results"]
    order = ["full(4.5K字)", "summ_1_2", "summ_1_5", "summ_1_10",
             "ext_1_2", "ext_1_5", "ext_1_10", "trunc_1_5(头截)", "trunc_1_5(尾截)"]
    names = ["原文\n4.5K字", "glm摘\n目标1/2", "glm摘\n目标1/5", "glm摘\n目标1/10",
             "抽取\n1/2", "抽取\n1/5", "抽取\n1/10", "头截\n1/5", "尾截\n1/5"]
    scores = [res[c]["score"] for c in order]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 4.6))
    colors = ["#264653"] + ["#e9c46a"] * 3 + ["#2a9d8f"] * 3 + ["#e76f51"] * 2
    ax1.bar(names, scores, color=colors)
    for i, s in enumerate(scores):
        ax1.text(i, s + 0.15, f"{s}/12", ha="center", fontsize=9)
    ax1.set_ylabel("QA 答对数")
    ax1.set_title("蒸馏率 × 事实保持（12 个具体事实）\n黄=LLM摘要(压缩比失控) 绿=抽取式(受控) 红=截断")
    ax1.set_ylim(0, 13.5)
    ax1.grid(axis="y", alpha=0.3)
    ax1.tick_params(axis="x", labelsize=7)

    # 受控蒸馏率曲线（抽取式）
    ratios = [1, 2, 5, 10]
    keep = [res["full(4.5K字)"]["score"] / 12, res["ext_1_2"]["score"] / 12,
            res["ext_1_5"]["score"] / 12, res["ext_1_10"]["score"] / 12]
    ax2.plot(ratios, [k * 100 for k in keep], "o-", color="#2a9d8f", label="抽取式（受控压缩比）")
    gm = sum(res[c]["score"] for c in ["summ_1_2", "summ_1_5", "summ_1_10"]) / 3 / 12 * 100
    ax2.axhline(gm, color="#e9c46a", ls="--", label=f"glm 摘要均值（实际≈1/15，{gm:.0f}%）")
    tr = res["trunc_1_5(头截)"]["score"] / 12 * 100
    ax2.axhline(tr, color="#e76f51", ls=":", label=f"截断 1/5（{tr:.0f}%）")
    for x, y in zip(ratios, keep):
        ax2.annotate(f"{y*100:.0f}%", (x, y * 100), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=9)
    ax2.set_xscale("log")
    ax2.set_xticks(ratios)
    ax2.set_xticklabels(["1×", "1/2", "1/5", "1/10"])
    ax2.set_xlabel("压缩比（原文字数/回传字数，log）")
    ax2.set_ylabel("事实保持率 %")
    ax2.set_title("蒸馏曲线：受控轴 + LLM 实际表现")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)
    fig.suptitle("E8 · 蒸馏率：sub-agent 回传 1-2K 够不够——受控压缩比 × QA 保持", fontsize=12)
    fig.tight_layout()
    p = os.path.join(os.path.dirname(RES_DIR), "e8_distill.png")
    fig.savefig(p, dpi=130)
    print("落盘:", p)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plot", action="store_true")
    a = ap.parse_args()
    if a.plot:
        plot()
    else:
        run()
