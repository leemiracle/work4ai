#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
21_paper_repro_checklist.py — 论文复现 checklist + 准备度分析
讲透模型宇宙 / Ch21 工具
纯标准库, 零依赖。
用法: 改下面 PROGRESS 为你的真实进度(0=未做 1=做了 2=已验证), 重跑。
"""
import math

# 六阶段, 每阶段关键检查项: (阶段, 检查项, 默认进度)
# 默认: 一个刚开始复现的典型进度
CHECKLIST = [
    ("1.理解", "用四问(解决什么/怎么解决/怎么验证/边界)写下答案", 1),
    ("1.理解", "能用一段话(无术语)讲清核心机制 — 费曼检验", 0),
    ("1.理解", "推导了关键公式, 不只是看懂", 0),

    ("2.环境", "找到并下载官方代码(GitHub/paperswithcode)", 1),
    ("2.环境", "用作者指定版本锁依赖(python/cuda/torch)", 1),
    ("2.环境", "用 conda/docker 隔离环境", 0),

    ("3.数据", "拿到作者用的同一数据集(同版本)", 0),
    ("3.数据", "完全照抄作者的数据预处理", 0),
    ("3.数据", "确认训练/测试集无泄漏", 0),

    ("4.训练", "先用作者 checkpoint 验证推理能复现(若有)", 0),
    ("4.训练", "完全照抄超参(lr/batch/epoch/seed)", 0),
    ("4.训练", "先在小数据子集跑通 pipeline", 0),

    ("5.评估", "用作者的评估脚本 + 同一测试集", 0),
    ("5.评估", "对比论文报告的数字(差距<5%=成功)", 0),
    ("5.评估", "报多 seed 均值±方差", 0),

    ("6.对比改", "复现成功后改一个变量看影响", 0),
    ("6.对比改", "记录改动的因果到经验库", 0),
]

def main():
    print("=" * 70)
    print("论文复现 Checklist + 准备度分析")
    print("=" * 70)
    print("进度: 0=未做  1=做了  2=已验证")
    print("(改脚本顶部 PROGRESS 为你的真实进度, 重跑)\n")

    # 按阶段统计
    stages = {}
    for stage, item, prog in CHECKLIST:
        stages.setdefault(stage, []).append(prog)

    print(f"{'阶段':<10}{'检查项':<48}{'进度'}")
    print("-" * 70)
    cur_stage = ""
    for stage, item, prog in CHECKLIST:
        s = stage if stage != cur_stage else ""
        cur_stage = stage
        bar = ["  未做 ", " 做了 ", " 已验证"][prog]
        print(f"{s:<10}{item:<46}{bar}")

    # 准备度: 每阶段完成度 = 该阶段项的平均/2
    print("\n" + "=" * 70)
    print(">>> 各阶段准备度 <<<\n")
    total_ready = 0
    bottleneck_stage = None
    min_ready = 1.1
    for stage, progs in stages.items():
        ready = sum(progs) / (len(progs) * 2)  # 0-1
        total_ready += ready
        bar_len = int(ready * 20)
        print(f"  {stage:<10} [{'█'*bar_len}{'·'*(20-bar_len)}] {ready*100:>5.0f}%")
        if ready < min_ready:
            min_ready = ready
            bottleneck_stage = stage

    overall = total_ready / len(stages)
    print(f"\n  总体准备度: {overall*100:.0f}%")
    if overall < 0.3:
        verdict = "起步: 先把'理解'和'环境'做扎实, 别急着训"
    elif overall < 0.6:
        verdict = "进行中: 补最缺的阶段, 顺序推进(别跳)"
    elif overall < 0.85:
        verdict = "接近完成: 补'评估'的严谨性(多seed/对比数字)"
    else:
        verdict = "可复现: 进入'对比改'阶段, 从复现走向研究"
    print(f"  阶段: {verdict}")

    print("\n" + "-" * 70)
    print(f">>> 当前瓶颈: {bottleneck_stage} (准备度最低) <<<")
    print(f"    先把这个阶段的检查项全部做到'已验证', 再推进下一阶段。")
    print(f"    复现铁律: 顺序不能乱 — 前一阶段没扎实, 后面会反复返工。")

    print("\n" + "=" * 70)
    print("复现的真正价值:")
    print("  · 复现一遍 > 读十遍 (动手逼出真理解)")
    print("  · 复现后你能改, 改了能用于工作")
    print("  · 复现5-10篇后, 你有调包侠永远没有的第一手直觉")
    print("  研究者口号: '没有复现过的论文, 不算真读过。'")
    print("=" * 70)

if __name__ == "__main__":
    main()
