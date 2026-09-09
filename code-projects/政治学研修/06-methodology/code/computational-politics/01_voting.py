#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""计算政治学代码 1：投票与社会选择
演示：Condorcet 悖论、中位选民定理、不同投票规则的差异（阿罗不可能定理的直观）
纯 Python 标准库，无需第三方依赖。运行：python3 01_voting.py
"""

# === 1. Condorcet 悖论：循环多数 ===
voters = {
    1: ['A', 'B', 'C'],   # 选民1: A>B>C
    2: ['B', 'C', 'A'],   # 选民2: B>C>A
    3: ['C', 'A', 'B'],   # 选民3: C>A>B
}

def pairwise(a, b, voters):
    aw = sum(1 for v in voters.values() if v.index(a) < v.index(b))
    return aw, len(voters) - aw

print("=" * 55)
print("1. Condorcet 悖论：3 选民的循环多数")
print("=" * 55)
for a, b in [('A', 'B'), ('B', 'C'), ('A', 'C')]:
    aw, bw = pairwise(a, b, voters)
    print(f"  {a} vs {b}: {a}={aw}票, {b}={bw}票 → {(a if aw > bw else b)}胜")
print("  → A>B, B>C, C>A 循环！无 Condorcet 赢家（悖论）\n")

# === 2. 中位选民定理 ===
print("=" * 55)
print("2. 中位选民定理：两党向中点收敛")
print("=" * 55)
positions = [i / 10 for i in range(11)]
median = sorted(positions)[len(positions) // 2]
print(f"  选民位置(均匀): {positions}")
print(f"  中位选民位置 = {median}")
pL, pR = 0.2, 0.8
print(f"  初始: 左党={pL}, 右党={pR}")
for s in range(1, 4):
    pL, pR = (pL + median) / 2, (pR + median) / 2
    print(f"  第{s}步调整: 左党={pL:.3f}, 右党={pR:.3f}")
print(f"  → 两党收敛到中位点 {median}（Hotelling 中位选民定理）\n")

# === 3. 同一偏好，不同规则 → 不同赢家（阿罗的直观）===
print("=" * 55)
print("3. 同一 Profile，不同投票规则 → 不同赢家")
print("=" * 55)
profile = {'ABC': 60, 'BCA': 40}   # 60人 A>B>C；40人 B>C>A

def plurality(pf):
    first = {}
    for pref, n in pf.items():
        first[pref[0]] = first.get(pref[0], 0) + n
    return max(first, key=first.get), first

def borda(pf):
    sc = {}
    for pref, n in pf.items():
        for i, c in enumerate(reversed(pref)):
            sc[c] = sc.get(c, 0) + i * n
    return max(sc, key=sc.get), sc

pw, ps = plurality(profile)
bw, bs = borda(profile)
print(f"  Profile: 60 人(A>B>C), 40 人(B>C>A)")
print(f"  Plurality(多数制,看第一): {ps} → 赢家 = {pw}")
print(f"  Borda(波达计数):        {bs} → 赢家 = {bw}")
aw, _ = pairwise('A', 'B', {k: list(v) for k, v in enumerate(['ABC'] * 60 + ['BCA'] * 40)})
print(f"  Condorcet(两两):        A vs B = {aw}:{100 - aw} → {'A' if aw > 50 else 'B'}胜")
print("  → 不同规则可能选出不同赢家！这正是阿罗不可能定理的直观。")
