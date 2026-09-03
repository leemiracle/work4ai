#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E5 —— Compaction 保真率：摘要丢什么、何时丢、丢在哪一层
==========================================================
设计：20 项事实嵌入"系统迁移"对话转录 → 两种压缩器（glm-4-flash / Qwen-0.5B）
     产出 compaction 摘要 → glm-4-flash 作为固定答题器，分别在
     {完整转录, glm 摘要, qwen 摘要} 上答 12 题（4 主旨 + 8 细节）。
失败分类（preprints 202605.2065 的 F1/F2/F3）：
  F1 压缩前决策错误：主旨题在摘要上答错（压缩器该保没保）
  F2 压缩中信息损失：细节题摘要错 & 全文对 & 答案串不在摘要文本里
  F3 压缩后访问失败：答案串明明在摘要文本里，答题器仍然答错
产出：results/e5_compaction.json + e5_compaction.png
对应章节：Ch05（Compaction 的艺术与三种失败）
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import local_qwen, glm, save, RES_DIR

TRANSCRIPT = """用户：下周开始订单系统迁移，先把口径对齐。
助手：好的。迁移代号"渡鸦"，整体方向是单体拆微服务，共涉及 14 个微服务。数据库从 MySQL 5.7 换到 PostgreSQL 16。
用户：节奏怎么排？
助手：冻结窗口定在 8 月 30 日到 9 月 3 日。订单服务负责人是杜衡，支付服务是白桦。库存服务这次暂缓，不迁移，这是架构组昨天的决策。
用户：网关和灰度呢？
助手：两个决策：网关超时从 3 秒调到 8 秒；灰度按流量 5% 起步放量。回滚脚本由苏晴维护，演练前她要过一遍。
用户：还有什么没解决的？
助手：两个已知 bug 未解决：优惠券双重核销；订单时间戳时区偏移 13 小时。
用户：基础设施层面的关键参数说一下。
助手：新网关 IP 段是 10.4.0.0/16；消息队列换成 RocketMQ 5.3；缓存 TTL 统一 900 秒；压测 QPS 目标 12000。
用户：演练和收尾安排？
助手：宕机演练定在 9 月 12 日。变更单编号 CHG-8841。旧库切只读模式后保留 90 天再下线。对账任务固定跑在 3 号定时节点。"""

COMPACT_PROMPT = (
    "总结以下工程对话，必须保留：架构决策、未解决的 bug、关键实施细节"
    "（负责人姓名、数字、编号、日期、参数值）。控制在 400 字以内。只输出摘要。\n\n" + TRANSCRIPT)

QUIZ = [
    # (题面, 评分关键词, 类型)
    ("这次迁移的代号是什么？只答代号。", "渡鸦", "gist"),
    ("迁移的整体方向是什么架构？答三个词以内。", "微服务", "gist"),
    ("库存服务这次迁不迁移？", "暂缓", "gist"),
    ("数据库最终换成了什么？只答产品名。", "PostgreSQL", "gist"),
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

def quiz_on(context_name, context):
    rows = []
    for q, ans, typ in QUIZ:
        prompt = f"{context}\n\n---\n问题：{q}"
        r = glm("glm-4-flash", prompt, max_tokens=24, temperature=0.0)
        reply = r["content"]
        ok = norm(ans).lower() in norm(reply)
        rows.append({"q": q, "type": typ, "ok": bool(ok), "reply": reply[:40],
                     "ans_in_ctx": norm(ans).lower() in norm(context)})
    return rows

def main():
    res = {"meta": {"date": "2026-08-26", "facts": 20, "quiz": len(QUIZ),
                    "answerer": "glm-4-flash(temp=0)"}}

    # ① 基线：完整转录
    res["full"] = quiz_on("full", TRANSCRIPT)

    # ② 两种摘要
    summ_glm = glm("glm-4-flash", COMPACT_PROMPT, max_tokens=1024, temperature=0.1)["content"]
    summ_qwen = local_qwen(COMPACT_PROMPT, max_new_tokens=640, temperature=0.2, seed=7)
    res["summary_glm"] = quiz_on("summary_glm", summ_glm)
    res["summary_qwen"] = quiz_on("summary_qwen", summ_qwen)
    res["summaries"] = {"glm": summ_glm, "qwen": summ_qwen}

    # ③ 失败分类（对每种摘要）
    def classify(rows, summary_text):
        f = {"F1_决策错": 0, "F2_信息损失": 0, "F3_访问失败": 0, "pass": 0}
        for r in rows:
            if r["ok"]:
                f["pass"] += 1
            elif r["type"] == "gist":
                f["F1_决策错"] += 1        # 主旨都丢了：该保没保
            elif r["ans_in_ctx"]:
                f["F3_访问失败"] += 1      # 答案就在摘要里却答错
            else:
                f["F2_信息损失"] += 1      # 答案不在摘要里：压掉了
        return f
    res["classify_glm"] = classify(res["summary_glm"], summ_glm)
    res["classify_qwen"] = classify(res["summary_qwen"], summ_qwen)

    # 汇总打印
    def acc(rows):
        return round(sum(r["ok"] for r in rows) / len(rows) * 100, 1)
    def acc_type(rows, t):
        sub = [r for r in rows if r["type"] == t]
        return round(sum(r["ok"] for r in sub) / len(sub) * 100, 1)
    print("=" * 70)
    for name in ("full", "summary_glm", "summary_qwen"):
        rows = res[name]
        print(f"{name:14s} 总acc={acc(rows):5.1f}%  主旨={acc_type(rows,'gist'):5.1f}%  细节={acc_type(rows,'detail'):5.1f}%")
    print("-" * 70)
    print("glm 摘要失败分类:", res["classify_glm"])
    print("qwen 摘要失败分类:", res["classify_qwen"])
    print("\n[glm 摘要全文]\n", summ_glm[:500])
    print("\n[qwen 摘要全文]\n", summ_qwen[:500])
    save("e5_compaction", res)

    # 画图
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    names = ["完整转录", "glm摘要", "qwen摘要"]
    keys = ["full", "summary_glm", "summary_qwen"]
    x = range(3); w = 0.35
    axes[0].bar([i - w/2 for i in x], [acc_type(res[k], "gist") for k in keys], w, label="主旨题", color="#55a868")
    axes[0].bar([i + w/2 for i in x], [acc_type(res[k], "detail") for k in keys], w, label="细节题", color="#dd8452")
    axes[0].set_xticks(list(x)); axes[0].set_xticklabels(names)
    axes[0].set_ylabel("答对率 %"); axes[0].set_ylim(0, 110); axes[0].legend(); axes[0].grid(alpha=0.3, axis="y")
    axes[0].set_title("主旨存活，细节阵亡：compaction 的选择性失忆")
    cls_keys = ["pass", "F1_决策错", "F2_信息损失", "F3_访问失败"]
    colors = ["#4c72b0", "#c44e52", "#dd8452", "#8172b3"]
    for ci, ck in enumerate(cls_keys):
        axes[1].bar([ci/2 - 0.25, ci/2 + 0.25],
                    [res["classify_glm"][ck], res["classify_qwen"][ck]], 0.4,
                    label=None, color=colors[ci])
        axes[1].text(ci/2 - 0.25, res["classify_glm"][ck] + 0.1, str(res["classify_glm"][ck]), ha="center", fontsize=9)
        axes[1].text(ci/2 + 0.25, res["classify_qwen"][ck] + 0.1, str(res["classify_qwen"][ck]), ha="center", fontsize=9)
    axes[1].set_xticks([i/2 for i in range(4)])
    axes[1].set_xticklabels(["通过", "F1 压缩前\n决策错", "F2 压缩中\n信息损失", "F3 压缩后\n访问失败"], fontsize=9)
    axes[1].set_ylabel("题数（glm左/qwen右）"); axes[1].grid(alpha=0.3, axis="y")
    axes[1].set_title("失败三分类（左=glm-4-flash 压缩器，右=Qwen-0.5B 压缩器）")
    fig.tight_layout()
    png = os.path.join(RES_DIR, "e5_compaction.png")
    fig.savefig(png, dpi=150)
    print(f"[saved] {png}")

if __name__ == "__main__":
    main()
