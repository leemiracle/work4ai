#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""计算政治学代码 4：博弈论与演化仿真
演示：囚徒困境、演化博弈（合作如何崩溃 / 需何条件才能维持）
纯 Python 标准库。运行：python3 04_game.py
"""
# 囚徒困境收益：T(诱惑) > R(奖励) > P(惩罚) > S(吃亏)
T, R, P, S = 5, 3, 1, 0

def payoff(a, b):
    if a == 'C' and b == 'C':
        return R
    if a == 'C' and b == 'D':
        return S
    if a == 'D' and b == 'C':
        return T
    return P

def evolve(p0, steps=15):
    p = p0
    print(f"  初始合作者比例 p = {p:.2f}")
    for s in range(steps):
        payC = p * R + (1 - p) * S      # 合作者期望收益
        payD = p * T + (1 - p) * P      # 背叛者期望收益
        avg = p * payC + (1 - p) * payD
        p_new = (p * payC / avg) if avg > 0 else 0
        if s < 4 or s >= steps - 2:
            tag = "← 合作占优" if payC > payD else "← 背叛占优"
            print(f"  第{s + 1:2d}代: p={p_new:.3f} (合作 {payC:.1f} vs 背叛 {payD:.1f}) {tag}")
        p = p_new
    return p

print("=" * 55)
print("1. 囚徒困境收益矩阵（T>R>P>S）")
print("=" * 55)
print("           对方合作C    对方背叛D")
print(f"  我合作C   R={R} (奖励)   S={S} (吃亏)")
print(f"  我背叛D   T={T} (诱惑)   P={P} (惩罚)")
print(f"  → 无论对方如何，我'背叛'收益都更高 → 理性导致双方 P={P}，而非 R={R}（悲剧）\n")

print("=" * 55)
print("2. 演化博弈：初始合作者 70%，合作能否维持？")
print("=" * 55)
final = evolve(0.7, 15)
print(f"\n  最终合作者比例 = {final:.3f}")
print("  → 因 T > R（背叛诱惑），背叛者收益更高 → 合作逐步崩溃至 0")
print("  → 这就是'公地悲剧'/集体行动难题（奥尔森《集体行动的逻辑》）")
print("  → 现实中合作能维持，靠的是：①重复博弈（以牙还牙）；②制度惩罚背叛；③声誉\n")

print("=" * 55)
print("3. 政治学含义：为什么需要国家/制度？")
print("=" * 55)
print("  霍布斯：自然状态 = 囚徒困境 → 需'利维坦'强制合作（[01 霍布斯](../../../01-political-theory/social-contract/01-霍布斯.md)）")
print("  奥尔森：大集团难集体行动 → 需选择性激励")
print("  制度主义：制度=降低交易成本、惩罚背叛的机制（[02 福山/Acemoglu](../../../02-comparative-politics/comparative-politics/03-国家能力与制度.md)）")
