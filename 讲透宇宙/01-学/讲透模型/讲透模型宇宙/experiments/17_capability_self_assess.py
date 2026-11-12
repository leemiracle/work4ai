#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
17_capability_self_assess.py — 模型工作能力 8 维自评 + 瓶颈分析
讲透模型宇宙 / Ch17 工具
纯标准库, 零依赖。
用法: 改下面 SELF_SCORE 为你的真实自评(0-3), 重跑。
  L0=不会 L1=跟着做 L2=独立做 L3=创新教
"""
import math

# 8 个能力维度: (key, 名称, 一句话, 默认画像分, 补缺章节)
# 默认画像: Python工程级/PyTorch入门/ML零基础起步的工作者 (典型本项目用户)
DIMS = [
    ("build",   "建",  "为工作问题搭出模型方案(数据/架构/目标决策链)", 1,
     "Ch18建与选 + 讲透基础模型/讲透PyTorch"),
    ("tune",    "调",  "系统化调参+微调, 不炼丹",                      1,
     "Ch19调与改 + 讲透微调"),
    ("modify",  "改",  "改造模型: steering/剪枝/蒸馏/adapter",          0,
     "Ch19调与改 + 讲透复用权重/讲透端侧AI压缩"),
    ("use",     "用",  "部署+调用: vLLM/Ollama/API接入业务",            2,
     "Ch18+Ch20 + 讲透RAG/讲透Agent"),
    ("optimize","优化","推理优化: 量化/KV cache/服务化, 快省稳",        1,
     "Ch20优化与部署 + 讲透KV Cache/讲透GPU与系统级"),
    ("reproduce","复现","把握+复现论文: 抓核心+跑通代码",               0,
     "Ch21复现论文 (本系列独有)"),
    ("communicate","沟通","领域专业对话: 听懂术语+准确表达",           1,
     "Ch22沟通与拓展 (本系列独有)"),
    ("extend",  "拓展","用模型扩宽工作边界, 迁移到新场景",              1,
     "Ch22沟通与拓展 + 讲透AI应用全景"),
]

def radar_bar(level):
    """L0-L3 -> 文本进度条"""
    blocks = int(level * 2)  # 每级2格, 满6格
    return "[" + "█" * (blocks) + "·" * (6 - blocks) + "]"

def main():
    print("=" * 72)
    print("模型工作能力 8 维自评 (L0不会 / L1跟着做 / L2独立做 / L3创新教)")
    print("=" * 72)
    print("默认画像: Python工程级 / PyTorch入门 / ML零基础起步的工作者")
    print("(改脚本顶部 SELF_SCORE 为你的真实自评, 重跑)\n")

    total = 0
    scores = []
    print(f"{'维度':<8}{'等级':<6}{'进度':<10}  含义")
    print("-" * 72)
    for key, name, desc, score, fix in DIMS:
        scores.append((name, score, desc, fix))
        total += score
        lvl_name = ["L0不会", "L1跟着做", "L2独立做", "L3创新教"][score]
        print(f"{name:<6}  {lvl_name:<8}{radar_bar(score):<10}  {desc}")

    max_score = len(DIMS) * 3
    print("-" * 72)
    print(f"\n总分: {total}/{max_score}  ({total/max_score*100:.0f}%)")
    # 等级判定
    pct = total / max_score
    if pct < 0.30:
        verdict = "起步期: 重点补'建'和'用', 先能搭出可跑的东西"
    elif pct < 0.55:
        verdict = "成长期: 补最短板, 让木桶均衡"
    elif pct < 0.80:
        verdict = "熟练期: 补'复现/沟通/拓展', 把能力放大"
    else:
        verdict = "成熟期: 追求 L3 创新, 或拓展新领域"
    print(f"阶段: {verdict}")

    # 木桶: 最短板
    scores_sorted = sorted(scores, key=lambda x: x[1])
    print("\n" + "=" * 72)
    print(">>> 木桶分析: 你的短板决定实际天花板 <<<\n")
    print("最该补的 3 块板 (从最短开始):")
    for i, (name, score, desc, fix) in enumerate(scores_sorted[:3], 1):
        print(f"  {i}. [{name}] 当前 L{score}")
        print(f"     缺口: {desc}")
        print(f"     怎么补: {fix}")

    # 强项
    print("\n你的强项 (可放大/可教别人):")
    for name, score, desc, fix in sorted(scores, key=lambda x: -x[1])[:2]:
        if score >= 2:
            print(f"  · [{name}] L{score} — {desc}")

    print("\n" + "=" * 72)
    print("记住: 能力是【验证】出来的, 不是看教程看出来的。")
    print("      每补一块板, 回到工作里【独立完成】一个真任务来验证。")
    print("      短板补到 L2 (独立做) >> 强项刷到 L3。木桶效应。")
    print("=" * 72)

if __name__ == "__main__":
    main()
