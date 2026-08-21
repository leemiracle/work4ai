#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_family_timeline.py — 量化"新瓶装旧酒"：模型架构的回流间隔
讲透模型宇宙 / Ch01 实验
纯标准库，零依赖，几秒跑完。
"""
import statistics

# (架构名, 流行年, 起源年, 起源出处)
# 起源年取"最常被引的最早公开文献"，流行年取"大规模普及年"。
ARCHES = [
    ("Transformer Attention", 2017, 2014, "Bahdanau attention"),
    ("Mamba / SSM",           2023, 2020, "HiPPO (Gu & Dao)"),
    ("MoE 混合专家",            2024, 1991, "Jacobs et al. mixtures-of-experts"),
    ("Diffusion 生成",          2022, 2011, "score matching (Vincent)"),
    ("ResNet 残差",             2015, 2015, "Highway Networks (Srivastava)"),
    ("LoRA 微调",              2021, 2019, "adapters (Houlsby)"),
    ("世界模型 JEPA",           2022, 2018, "World Models (Ha & Schmidhuber)"),
    ("Test-time scaling",     2024, 2016, "AlphaGo MCTS"),
    ("对比学习 SimCLR",         2020, 2006, "contrastive divergence (Hinton)"),
    ("GPT 自回归 LM",          2018, 2003, "Bengio neural prob. LM"),
    ("Dropout",               2012, 1995, "贝叶斯神经网络近似"),
    ("BatchNorm",             2015, 1998, "内部协变量平移/归一化思想"),
]

def main():
    print("=" * 68)
    print("模型架构回流分析：'新'架构 vs 它真正的学术起源")
    print("=" * 68)
    print(f"{'架构':<22}{'流行年':>7}{'起源年':>8}{'回流间隔':>10}  起源出处")
    print("-" * 68)

    gaps = []
    truly_new = []
    for name, hot, origin, src in ARCHES:
        gap = hot - origin
        gaps.append(gap)
        mark = "  <-- 真新" if gap <= 1 else ""
        if gap <= 1:
            truly_new.append(name)
        print(f"{name:<20}{hot:>9}{origin:>9}{gap:>9}年  {src}{mark}")

    print("-" * 68)
    n = len(ARCHES)
    recycled = n - len(truly_new)
    print(f"\n样本数: {n}")
    print(f"真正'新'(间隔<=1年): {len(truly_new)} 个  -> {truly_new}")
    print(f"'新瓶装旧酒'(间隔>1年): {recycled} 个")
    print(f"\n>>> 反直觉发现 <<<")
    print(f"新瓶装旧酒比例: {recycled}/{n} = {recycled/n*100:.1f}%")
    print(f"回流间隔: 中位 {statistics.median(gaps):.0f} 年, 均值 {statistics.mean(gaps):.1f} 年, 最长 {max(gaps)} 年")
    print()
    print("结论: AI 架构创新的 ~{:.0%} 是'老想法+新规模/数据/理论'的组合创新，".format(recycled/n))
    print("      真正的'新原理'(如反向传播/注意力/残差)几十年一遇。")
    print("      研究者的目光: 看穿名字, 找到骨架。")
    print("=" * 68)

if __name__ == "__main__":
    main()
