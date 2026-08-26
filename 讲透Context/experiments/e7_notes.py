#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E7 —— NOTES.md 双会话接力：结构化笔记 vs 线性摘要的交接对决
================================================================
设计：与 E5 同一份 20 事实转录、同一套 12 题、同一答题器（glm-4-flash temp=0）。
     会话 1 让 glm-4-flash 写交接笔记（两种引导）：
       N1 自由笔记："写下接手需要的备忘"（≈ 自由摘要）
       N2 结构化模板：给定字段骨架（决策/未解决bug/负责人/参数/时间点/编号）
     会话 2 全新上下文只读笔记答题。
对照：E5 的 compaction 线性摘要（400 字预算压缩对话流）。
假设（Factory.ai 2026：结构化 3.70 vs 自由 3.44）：N2 > N1 ≈ 线性摘要。
产出：results/e7_notes.json + e7_notes.png（含 token 成本对照）
对应章节：Ch07（记忆：窗口之外的持久化）
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import glm, _get_qwen, save, load, RES_DIR

TRANSCRIPT = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "e5_compaction.py"), encoding="utf-8").read().split('TRANSCRIPT = """')[1].split('"""')[0]

PROMPT_N1 = ("你是值班的工程师，明天有位全新同事接手你的工作。请写一份交接备忘（NOTES.md），"
             "包含他认为接手需要的全部信息。只输出备忘内容。\n\n" + TRANSCRIPT)

PROMPT_N2 = ("你是值班的工程师，明天有位全新同事接手你的工作。请严格按以下模板写交接备忘（NOTES.md），"
             "每个字段都必须填，数字/编号/姓名/日期一字不差：\n"
             "## 迁移概览（代号/方向/规模/数据库）\n## 组织与负责人\n## 架构决策\n"
             "## 未解决 bug\n## 关键参数（IP/队列/缓存/压测）\n## 时间点与编号\n"
             "## 交接清单（回滚/演练/变更单/旧库/对账）\n只输出备忘内容。\n\n" + TRANSCRIPT)

QUIZ = [
    ("这次迁移的代号是什么？只答代号。", "渡鸦", "gist"),
    ("迁移的整体方向是什么架构？答三个词以内。", "微服务", "gist"),
    ("库存服务这次迁不迁移？", "暂缓", "gist"),
    ("数据库最终换成了什么？只答产品名。", "postgresql", "gist"),
    ("灰度放量从百分之几起步？只答数字。", "5", "detail"),
    ("网关超时调到了几秒？只答数字。", "8", "detail"),
    ("回滚脚本由谁维护？只答姓名。", "苏晴", "detail"),
    ("变更单编号是多少？只答编号。", "8841", "detail"),
    ("优惠券那个未解决 bug 的现象是什么？八个字以内。", "核销", "detail"),
    ("时间戳 bug 偏移了多少小时？只答数字。", "13", "detail"),
    ("旧库只读模式保留多少天？只答数字。", "90", "detail"),
    ("对账任务跑在几号定时节点？只答数字。", "3", "detail"),
]

def norm(s):
    for ch in " ：:，,。.、":
        s = s.replace(ch, "")
    return s.lower()

def quiz_on(context):
    rows = []
    for q, ans, typ in QUIZ:
        r = glm("glm-4-flash", f"{context}\n\n---\n以下是接手备忘。问题：{q}", max_tokens=24, temperature=0.0)
        ok = norm(ans) in norm(r["content"])
        rows.append({"q": q, "type": typ, "ok": bool(ok), "reply": r["content"][:40]})
    return rows

def main():
    tok, _ = _get_qwen()
    def ntok(s): return len(tok(s, add_special_tokens=False).input_ids)

    res = {"meta": {"date": "2026-08-26", "answerer": "glm-4-flash(temp=0)", "quiz": len(QUIZ)}}

    notes_n1 = glm("glm-4-flash", PROMPT_N1, max_tokens=1024, temperature=0.1)["content"]
    notes_n2 = glm("glm-4-flash", PROMPT_N2, max_tokens=1280, temperature=0.1)["content"]
    res["notes"] = {"n1_freeform": notes_n1, "n2_structured": notes_n2}

    res["n1"] = quiz_on(notes_n1)
    res["n2"] = quiz_on(notes_n2)

    # 拉 E5 的对照数据
    try:
        e5 = load("e5_compaction")
        comp = e5["summary_glm"]; comp_tok = ntok(e5["summaries"]["glm"])
    except Exception:
        comp = None; comp_tok = None

    def acc(rows, t=None):
        sub = [r for r in rows if t is None or r["type"] == t]
        return round(sum(r["ok"] for r in sub) / len(sub) * 100, 1)

    rows_plot = [("compaction线性摘要", comp, comp_tok), ("N1 自由笔记", res["n1"], ntok(notes_n1)),
                 ("N2 结构化模板笔记", res["n2"], ntok(notes_n2))]
    print("=" * 72)
    for name, rows, tk in rows_plot:
        if rows is None:
            print(f"{name:18s} （E5 未跑，跳过）"); continue
        print(f"{name:18s} 总acc={acc(rows):5.1f}%  主旨={acc(rows,'gist'):5.1f}%  细节={acc(rows,'detail'):5.1f}%  成本={tk} tok")
    print("\n[N2 结构化笔记全文]\n", notes_n2)
    res["rows_plot"] = [{"name": n, "acc": acc(r) if r else None, "acc_gist": acc(r, "gist") if r else None,
                         "acc_detail": acc(r, "detail") if r else None, "tok": t} for n, r, t in rows_plot]
    save("e7_notes", res)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    labels = [n for n, r, t in rows_plot if r]
    gist_v = [acc(r, "gist") for n, r, t in rows_plot if r]
    det_v = [acc(r, "detail") for n, r, t in rows_plot if r]
    toks = [t for n, r, t in rows_plot if r]
    x = range(len(labels)); w = 0.35
    ax.bar([i - w/2 for i in x], gist_v, w, label="主旨题", color="#55a868")
    ax.bar([i + w/2 for i in x], det_v, w, label="细节题", color="#dd8452")
    for i, (g, d, t) in enumerate(zip(gist_v, det_v, toks)):
        ax.text(i - w/2, g + 2, f"{g:.0f}", ha="center", fontsize=10)
        ax.text(i + w/2, d + 2, f"{d:.0f}", ha="center", fontsize=10)
        ax.text(i, -14, f"成本 {t} tok", ha="center", fontsize=9, color="#666")
    ax.set_xticks(list(x)); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("会话2 答对率 %"); ax.set_ylim(0, 115); ax.legend(); ax.grid(alpha=0.3, axis="y")
    ax.set_title("E7 双会话接力：同一转录，三种交接介质（答题器固定 glm-4-flash）")
    fig.tight_layout()
    png = os.path.join(RES_DIR, "e7_notes.png")
    fig.savefig(png, dpi=150)
    print(f"[saved] {png}")

if __name__ == "__main__":
    main()
