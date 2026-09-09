# -*- coding: utf-8 -*-
"""
孔多塞循环：投票悖论模拟（走廊1：社会选择）
对应章：讲透政治学理论/04-政治学理论转代码.md（00/03 章引用）

四组断言：
  [1] 经典 3 选民×3 方案循环 profile：多数规则产生 A>B>C>A 循环（无孔多塞赢家）
  [2] n=3 精确枚举：216 个等概率 profile 中恰 12 个循环 = 1/18 ≈ 5.56%
      （Gehrlein 系列首项，2026-09 推导核对：循环 3-子集恰为 {ABC,BCA,CAB} 与其逆转）
  [3] 蒙特卡洛（固定种子）：无偏文化下循环概率随选民数上升，
      n=999 时落入 Guilbaud (1952) 极限 1-0.9123≈0.0877 的邻域 [0.075, 0.10]
  [4] 议程操纵：循环 profile 下，换议程顺序可让任意方案当选（孔多塞第二暗面）；
      规则敏感性：存在 profile 使多数决胜的赢家 ≠ 孔多塞赢家 = 博尔达赢家
口径：无偏文化=每个选民排序均匀独立取自全部排列；奇数选民保证无平局。
"""
import itertools
import random

ALTS = "ABC"


def defeats(profile, x, y):
    """多数规则：profile（排序字符串列表）中 x 配对击败 y。"""
    return sum(1 for r in profile if r.index(x) < r.index(y)) * 2 > len(profile)


def condorcet_winner(profile):
    """返回同时配对击败所有对手的方案；无则 None。"""
    for x in set("".join(profile)):
        if all(defeats(profile, x, y) for y in set("".join(profile)) if y != x):
            return x
    return None


def majority_cycle(profile):
    """配对多数关系成环（等价于无孔多塞赢家，3 方案奇数选民时）。"""
    return condorcet_winner(profile) is None


def agenda_winner(profile, order):
    """顺序二选一议程：先比 order[0] 与 order[1]，胜者对阵 order[2]。"""
    w0 = order[0] if defeats(profile, order[0], order[1]) else order[1]
    return w0 if defeats(profile, w0, order[2]) else order[2]


def borda_scores(profile):
    """博尔达计数：排名第 k 得 (m-1-k) 分。"""
    m = len(profile[0])
    sc = {a: 0 for a in profile[0]}
    for r in profile:
        for k, a in enumerate(r):
            sc[a] += m - 1 - k
    return sc


def main():
    rng = random.Random(20260907)

    # ---------- [1] 经典循环 profile ----------
    classic = ["ABC", "BCA", "CAB"]  # 三选民：轮换偏好
    assert defeats(classic, "A", "B") and defeats(classic, "B", "C") \
        and defeats(classic, "C", "A"), "应成环 A>B>C>A"
    assert condorcet_winner(classic) is None, "循环 profile 无孔多塞赢家"
    print("[1] profile {ABC, BCA, CAB}: A>B 2-1, B>C 2-1, C>A 2-1 → 循环，"
          "集体无赢家（个体偏好完全理性，集体'非理性'）")

    # ---------- [2] n=3 精确枚举 ----------
    all_orders = ["".join(p) for p in itertools.permutations(ALTS)]  # 6 种排序
    profiles3 = list(itertools.product(all_orders, repeat=3))        # 216 个 profile
    n_cycle = sum(majority_cycle(list(t)) for t in profiles3)
    assert len(profiles3) == 6 ** 3 == 216
    assert n_cycle == 12, n_cycle
    assert n_cycle / 216 == 1 / 18
    print(f"[2] n=3 精确枚举：216 profile 中 {n_cycle} 个循环 = "
          f"{n_cycle/216:.4f}（Gehrlein 首项 1/18）")

    # ---------- [3] 蒙特卡洛：循环概率随 n 上升 → Guilbaud 极限 ----------
    perms = ["".join(p) for p in itertools.permutations(ALTS)]
    TRIALS = 30000
    probs = {}
    for n in (3, 51, 999):
        hits = 0
        for _ in range(TRIALS):
            prof = [rng.choice(perms) for _ in range(n)]
            if majority_cycle(prof):
                hits += 1
        probs[n] = hits / TRIALS
    assert probs[3] < probs[999] < 0.10, probs          # 单调上升且未超限
    assert 0.075 <= probs[999] <= 0.10, probs           # 逼近 0.0877（±~5σ 容差）
    print(f"[3] 无偏文化蒙特卡洛（{TRIALS} 次/组，固定种子）：")
    for n, p in probs.items():
        print(f"      n={n:>4}: 循环概率 {p:.4f}")
    print("      → 随选民增多趋近 Guilbaud 极限 0.0877：'人民意志'有近 9% "
          "的概率在数学上不存在（Riker 1982 的武器）")

    # ---------- [4] 议程操纵 + 规则敏感性 ----------
    winners = {agenda_winner(classic, o)
               for o in map("".join, itertools.permutations(ALTS))}
    assert winners == {"A", "B", "C"}, winners
    print("[4a] 同一循环 profile，六种议程选出 {A,B,C} 全部三方案——"
          "议程设置者想让谁赢谁就赢（Black 1958 悖论）")

    # 规则敏感性：孔多塞赢家 B 在多数决胜下落败，博尔达恢复 B
    sens = ["ABC"] * 4 + ["BCA"] * 3 + ["CBA"] * 2
    assert condorcet_winner(sens) == "B"
    assert borda_scores(sens)["B"] == 12 and borda_scores(sens)["A"] == 8
    assert borda_scores(sens)["B"] > max(borda_scores(sens)[a] for a in "AC")
    print("[4b] profile (4×ABC, 3×BCA, 2×CBA)：多数决胜赢家=A（4 票首好），"
          "孔多塞赢家=博尔达赢家=B（配对 5:4 击败 A）——规则换，结果换")

    print("\n全部断言通过 ✓（社会选择=纯组合对象：悖论率可枚举、可模拟、可复现）")


if __name__ == "__main__":
    main()
