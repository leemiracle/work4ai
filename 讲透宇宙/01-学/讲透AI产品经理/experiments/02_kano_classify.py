#!/usr/bin/env python3
# -*- coding: utf-8: utf-8 -*-
"""
Kano 模型问卷模拟器（AI 功能版）
================================
Kano（狩野纪昭 1984）：用正反两问把功能分为五类——
  魅力(Attractive)/期望(One-dimensional)/必备(Must-be)/无差异(Indifferent)/反向(Reverse)
AI 产品的特殊性（讲透AI产品经理/02-方法论武器库.md §02.1③）：
  AI 功能的 Kano 位置漂移极快（AI 摘要 2023=魅力，2026=必备）——按季度重测。

实验内容：
  A. 标准 Kano 评估矩阵：正反问答案对 -> 分类
  B. 模拟同一功能在两个时点的调查结果（2023 vs 2026），展示 Kano 漂移
运行：python3 02_kano_classify.py
"""
from collections import Counter

# 用户对每个问题的回答选项（Kano 标准五选一）
# 正问："如果有 X 功能，你的感受？"
# 反问："如果没有 X 功能，你的感受？"
# A=喜欢 B=理所当然 C=无所谓 D=勉强接受 E=不喜欢
EVAL_MATRIX = {
    # (正问, 反问) -> 分类
    ("A", "E"): "期望 (One-dimensional)   越多越满意",
    ("A", "A"): "魅力 (Attractive)        有惊喜，没有也不怪",
    ("A", "B"): "魅力 (Attractive)",
    ("A", "C"): "魅力 (Attractive)",
    ("A", "D"): "无差异 (Indifferent)     可有可无",
    ("B", "E"): "必备 (Must-be)           没有就不满意，有了不加分",
    ("B", "A"): "无差异 (Indifferent)",
    ("B", "B"): "无差异 (Indifferent)",
    ("B", "C"): "无差异 (Indifferent)",
    ("B", "D"): "无差异 (Indifferent)",
    ("C", "E"): "期望 (One-dimensional)",
    ("C", "A"): "无差异 (Indifferent)",
    ("C", "B"): "无差异 (Indifferent)",
    ("C", "C"): "无差异 (Indifferent)",
    ("C", "D"): "反向 (Reverse)           不要更好",
    ("D", "E"): "期望 (One-dimensional)",
    ("D", "A"): "反向 (Reverse)",
    ("D", "B"): "反向 (Reverse)",
    ("D", "C"): "反向 (Reverse)",
    ("D", "D"): "反向 (Reverse)",
    ("E", "A"): "反向 (Reverse)",
    ("E", "B"): "反向 (Reverse)",
    ("E", "C"): "反向 (Reverse)",
    ("E", "D"): "反向 (Reverse)",
    ("E", "E"): "可疑 (Questionable)",
}

def classify(poll: Counter) -> str:
    """poll: Counter of (正问答案, 反问答案) -> 人数；返回众数分类"""
    buckets = Counter()
    for (pos, neg), n in poll.items():
        buckets[EVAL_MATRIX[(pos, neg)]] += n
    top = buckets.most_common()
    winner, votes = top[0]
    share = votes / sum(buckets.values())
    return f"{winner}  [众数占比 {share:.0%}]"


# ---------------- 模拟数据（教学示例；真实场景=问卷回收 100-300 份） ----------------
# 时点1：2023，"AI 摘要"还是新鲜事物
survey_2023 = Counter({
    ("A", "C"): 35,  # 喜欢，没有无所谓 -> 魅力
    ("A", "B"): 20,  # 魅力
    ("A", "E"): 10,  # 期望
    ("B", "E"): 5,   # 必备
    ("C", "C"): 25,  # 无差异
    ("C", "D"): 5,
})

# 时点2：2026，竞品都有了，用户预期已建立
survey_2026 = Counter({
    ("A", "C"): 5,
    ("A", "B"): 5,
    ("A", "E"): 15,
    ("B", "E"): 45,  # 理所当然+没有就不爽 -> 必备
    ("B", "A"): 5,
    ("C", "C"): 20,
    ("E", "E"): 5,
})

# 反向功能示例：过度智能（自动帮你发邮件）
survey_reverse = Counter({
    ("C", "C"): 15,
    ("D", "C"): 20,  # 正问=勉强接受 -> 反向倾向
    ("E", "A"): 25,  # 正问=不喜欢 -> 反向
    ("E", "B"): 10,
    ("C", "A"): 10,
    ("B", "C"): 10,
    ("A", "C"): 10,
})

def main():
    print("== Kano 分类（同一功能'AI 摘要'，两个时点）==\n")
    print(f"2023 调查：\n  -> {classify(survey_2023)}")
    print(f"2026 调查：\n  -> {classify(survey_2026)}")
    print(f"\n反面示例：'AI 自动代发邮件'（过度自主）\n  -> {classify(survey_reverse)}")

    print("""
结论：
1. Kano 漂移实证：AI 摘要从 2023 的'魅力'漂到 2026 的'必备'——
   魅力属性会衰减成必备属性（竞品普及 + 预期建立），
   AI 功能的 Kano 位置必须按季度重测，否则 roadmap 会继续投资
   已不加分的功能、或漏掉即将变必备的。
2. 反向功能警示：自主性不是越多越好——'自动代发邮件'落在反向区，
   印证 04 章 HITL 决策树（写操作要确认门）。
3. 方法要点：Kano 问卷是正反问对（不是单问），无差异区超过 40%
   说明该功能根本不值得做——比魅力/必备分类更早杀死坏主意。""")


if __name__ == "__main__":
    main()
