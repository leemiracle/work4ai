#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_leaderboard_gaming.py — 模拟 Bradley-Terry 排行榜, 演示"刷榜"如何扭曲排名
讲透模型宇宙 / Ch03 实验
纯标准库, 零依赖, 几秒跑完。
"""
import random, math

random.seed(42)

# 真实"内容实力" (0-100), 越高越强
N_MODELS = 12
true_skill = {i: 30 + i * 5 for i in range(N_MODELS)}  # 模型0最弱(30)...模型11最强(85)

def sigmoid(x):
    return 1 / (1 + math.exp(-x / 10.0))  # /10 让概率不那么极端

def bradley_terry_rating(skill):
    """真实实力 -> 基础 rating"""
    return skill  # 简化: rating = skill

# 给某些模型"格式加成" (style bonus): 更长、更漂亮、更自信
# 假设模型 0-3 (真实最弱) 用了刷榜技巧, 加成高
style_bonus = {i: (45 if i < 4 else 0) for i in range(N_MODELS)}

def apparent_rating(i, with_style):
    return bradley_terry_rating(true_skill[i]) + (style_bonus[i] if with_style else 0)

def simulate_leaderboard(with_style, n_battles=4000):
    """模拟对战 + 最大似然拟合 Bradley-Terry (用简单迭代)"""
    wins = {i: 0 for i in range(N_MODELS)}  # 简化: 只统计胜率作为排名代理
    for _ in range(n_battles):
        i, j = random.sample(range(N_MODELS), 2)
        ri, rj = apparent_rating(i, with_style), apparent_rating(j, with_style)
        p_i_win = sigmoid(ri - rj)
        if random.random() < p_i_win:
            wins[i] += 1
        else:
            wins[j] += 1
    # 按胜数排名
    ranked = sorted(range(N_MODELS), key=lambda x: -wins[x])
    return ranked

def main():
    print("=" * 70)
    print("排行榜刷榜模拟: 同样的真实能力, 仅加'格式/长度/style'加成")
    print("=" * 70)
    print(f"\n真实内容实力 (越高越强):")
    for i in range(N_MODELS):
        flag = "  [+45 style刷榜]" if style_bonus[i] else ""
        print(f"  模型{i:>2}: 真实实力={true_skill[i]:>3}{flag}")

    print("\n" + "-" * 70)
    fair = simulate_leaderboard(with_style=False)
    print("\n【公平榜】(无 style 加成) — 反映真实实力:")
    for rank, i in enumerate(fair, 1):
        print(f"  第{rank:>2}名: 模型{i:>2} (真实实力 {true_skill[i]})")

    print("-" * 70)
    gamed = simulate_leaderboard(with_style=True)
    print("\n【被刷榜】(弱模型加了 style 加成):")
    for rank, i in enumerate(gamed, 1):
        flag = " <-- 靠格式上位" if style_bonus[i] else ""
        print(f"  第{rank:>2}名: 模型{i:>2} (真实实力 {true_skill[i]}){flag}")

    print("\n" + "=" * 70)
    print(">>> 反直觉发现 <<<")
    # 真实最强(模型11)在两榜的排名
    rank_fair_11 = fair.index(11) + 1
    rank_gamed_11 = gamed.index(11) + 1
    # 真实最弱但刷榜(模型0)的排名
    rank_fair_0 = fair.index(0) + 1
    rank_gamed_0 = gamed.index(0) + 1
    print(f"真实最强模型11: 公平榜第{rank_fair_11}名 -> 被刷榜后第{rank_gamed_11}名")
    print(f"真实最弱模型0 (但刷榜): 公平榜第{rank_fair_0}名 -> 被刷榜后第{rank_gamed_0}名")
    print(f" => 仅靠格式/长度优化, 弱模型排名上升 {rank_fair_0 - rank_gamed_0} 位")
    print()
    print("教训: 人类对战排行榜(Arena)天然偏好更长/更漂亮的回答。")
    print("      Goodhart 定律: 当一个度量成为目标, 它就不再是好度量。")
    print("      这正是 Arena 2025 默认开启 style control 的原因。")
    print("=" * 70)

if __name__ == "__main__":
    main()
