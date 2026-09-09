#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""计算政治学代码 5：Axelrod 合作演化锦标赛
演示：在重复囚徒困境中，"以牙还牙"（Tit-for-Tat）为何胜出。
基于 Robert Axelrod《合作的演化》（The Evolution of Cooperation, 1984）。
纯 Python 标准库。运行：python3 05_axelrod.py
"""
import random

random.seed(42)  # 可复现

# === 收益矩阵（T>R>P>S）===
T, R, P, S = 5, 3, 1, 0
ROUNDS = 200  # 每场比赛轮数

# === 策略定义 ===
def always_cooperate(hist_me, hist_them):
    return 'C'

def always_defect(hist_me, hist_them):
    return 'D'

def tit_for_tat(hist_me, hist_them):
    """第一轮合作，之后模仿对方上一轮"""
    if not hist_them:
        return 'C'
    return hist_them[-1]

def grim_trigger(hist_me, hist_them):
    """永久报复：一旦对方背叛，永久背叛"""
    if 'D' in hist_them:
        return 'D'
    return 'C'

def random_strat(hist_me, hist_them):
    return random.choice('CD')

def pavlov(hist_me, hist_them):
    """赢留输变：上轮合作则重复，背叛则切换"""
    if not hist_me:
        return 'C'
    last_me, last_them = hist_me[-1], hist_them[-1]
    # 上轮得分
    payoff = {( 'C','C'): R, ('C','D'): S, ('D','C'): T, ('D','D'): P}
    if payoff[(last_me, last_them)] >= R:
        return last_me  # 赢了（或平R），保持
    else:
        return 'D' if last_me == 'C' else 'C'  # 输了，变

STRATEGIES = {
    'AllCooperate':   always_cooperate,
    'AllDefect':      always_defect,
    'TitForTat':      tit_for_tat,
    'GrimTrigger':    grim_trigger,
    'Pavlov':         pavlov,
    'Random':         random_strat,
}

def play_match(strat_a, strat_b, rounds=ROUNDS):
    ha, hb = [], []
    sa = sb = 0
    for _ in range(rounds):
        a = strat_a(ha, hb)
        b = strat_b(hb, ha)
        if a == 'C' and b == 'C':
            sa += R; sb += R
        elif a == 'C' and b == 'D':
            sa += S; sb += T
        elif a == 'D' and b == 'C':
            sa += T; sb += S
        else:
            sa += P; sb += P
        ha.append(a); hb.append(b)
    return sa, sb

# === 锦标赛 ===
print("=" * 60)
print(f"Axelrod 重复囚徒困境锦标赛（每对对打 {ROUNDS} 轮，循环赛）")
print("=" * 60)

names = list(STRATEGIES)
totals = {n: 0 for n in names}
n_matches = {n: 0 for n in names}

for i in range(len(names)):
    for j in range(i, len(names)):
        a, b = names[i], names[j]
        sa, sb = play_match(STRATEGIES[a], STRATEGIES[b])
        totals[a] += sa; n_matches[a] += 1
        totals[b] += sb; n_matches[b] += 1
        winner = "平" if sa == sb else (a if sa > sb else b)
        print(f"  {a:16s} vs {b:16s}: {sa:4d} - {sb:4d}  → {winner}")

print("\n" + "=" * 60)
print("总排名（按平均分/场）")
print("=" * 60)
ranking = sorted(totals.items(), key=lambda x: -x[1] / n_matches[x[0]])
for rank, (name, score) in enumerate(ranking, 1):
    avg = score / n_matches[name]
    print(f"  #{rank} {name:16s}: 总分 {score:5d}  平均/场 {avg:.1f}")

winner = ranking[0][0]
print(f"\n→ 冠军：{winner}！")
print("\nAxelrod 的洞见（1984）：")
print("  最优策略的四个特征：")
print("  ① 善良（nice）—— 不先背叛")
print("  ② 可激怒（retaliatory）—— 被背叛就报复")
print("  ③ 宽容（forgiving）—— 对方恢复合作就原谅")
print("  ④ 清晰（clear）—— 规则简单可预测")
print("\n  政治学含义：合作可以在无政府状态中自发涌现——")
print("  只要博弈是重复的、双方有长期关系（呼应[03 自由主义 IR](../../03-international-relations/ir-theories/02-自由主义.md)）")
