# -*- coding: utf-8 -*-
"""
联盟形成：最小获胜联盟、权力指数与分赃定律（走廊2：联盟形成）
对应章：讲透国际政治学/04-国际政治学转代码.md（00/03 章引用）

对象：加权投票游戏 [quota; w1..wn]（席位/实力=权重，多数规则）。
四组断言：
  [1] 经典局 [51; 48,47,3,2]：最小获胜联盟恰为 {48+47} 与 {48+3}；
      Banzhaf 摆动数恰为 [5,3,3,1]——47 席大党与 3 席小党权力相等
      （权力≠席位，政党联盟政府的算术真相）
  [2] 独裁者局 [3; 3,1,1]：归一化 Banzhaf = [1,0,0]（权重幂等的反例）
  [3] Riker (1962) 规模原理：随机局中"随机组队+贪婪瘦身"形成的
      联盟恒为最小获胜联盟（300 局全检），且平均规模严格小于大联盟
      （多带人=多分赃，理性联盟不会过度扩张）
  [4] Gamson (1961) 定律：形成联盟内部按权重比例分赃，份额和为 1
口径：纯多数规则（无意识形态距离成本——练习 1 加入后的变体见 04 章）。
"""
import random
from itertools import combinations


def winning(members, weights, quota):
    return sum(weights[i] for i in members) >= quota


def minimal_winning(weights, quota):
    """全部最小获胜联盟（MWC）：获胜且去掉任一成员即败。"""
    n = len(weights)
    mwcs = set()
    for size in range(1, n + 1):
        for S in combinations(range(n), size):
            if winning(S, weights, quota) and all(
                    not winning(T, weights, quota) for T in combinations(S, size - 1)):
                mwcs.add(frozenset(S))
    return mwcs


def banzhaf(weights, quota):
    """绝对摆动数与归一化 Banzhaf 权力指数。"""
    n = len(weights)
    swings = [0] * n
    for size in range(1, n + 1):
        for S in combinations(range(n), size):
            if winning(S, weights, quota):
                for i in S:
                    if not winning(tuple(x for x in S if x != i), weights, quota):
                        swings[i] += 1
    total = sum(swings)
    return swings, [s / total for s in swings]


def form_coalition(weights, quota, rng):
    """随机组队至获胜，再贪婪瘦身（先踢大权重）——恒收敛到 MWC。"""
    order = list(range(len(weights)))
    rng.shuffle(order)
    S = []
    for i in order:
        S.append(i)
        if winning(S, weights, quota):
            break
    assert winning(S, weights, quota)
    changed = True
    while changed:
        changed = False
        for i in sorted(S, key=lambda j: -weights[j]):
            rest = [x for x in S if x != i]
            if rest and winning(rest, weights, quota):
                S.remove(i)
                changed = True
                break
    return frozenset(S)


def main():
    rng = random.Random(20260907)

    # ---------- [1] 权力≠席位 ----------
    w, q = [48, 47, 3, 2], 51
    mwcs = minimal_winning(w, q)
    assert mwcs == {frozenset({0, 1}), frozenset({0, 2}),
                    frozenset({1, 2, 3})}, mwcs
    swings, norm = banzhaf(w, q)
    assert swings == [5, 3, 3, 1], swings
    assert abs(norm[1] - norm[2]) < 1e-12 and norm[1] == 0.25
    assert norm[0] > norm[1] > norm[3] > 0
    print(f"[1] [51; 48,47,3,2]：MWC = {{48+47}}, {{48+3}}, {{47+3+2}}；"
          f"Banzhaf = {norm}")
    print("    → 47 席党与 3 席党权力同为 0.25：关键在'让联盟过线的最后一票'"
          "而非体量——造王者≠大块头（且三家小党可组 52 联盟踢开老大）")

    # ---------- [2] 独裁者局 ----------
    _, norm2 = banzhaf([3, 1, 1], 3)
    assert norm2 == [1.0, 0.0, 0.0], norm2
    print(f"[2] [3; 3,1,1]：Banzhaf = {norm2}——一人过线，其余皆零"
          "（权力指数对'名义平等、实际独裁'的照妖镜）")

    # ---------- [3] Riker 规模原理 ----------
    sizes = []
    N_GAMES = 300
    for _ in range(N_GAMES):
        wts = [rng.randint(1, 20) for _ in range(5)]
        quota = sum(wts) * 51 // 100 + 1          # 严格过半
        formed = form_coalition(wts, quota, rng)
        assert formed in minimal_winning(wts, quota)   # 恒为 MWC
        sizes.append(len(formed))
        # Gamson 分赃自检
        total_w = sum(wts[i] for i in formed)
        shares = [wts[i] / total_w for i in sorted(formed)]
        assert abs(sum(shares) - 1.0) < 1e-9
    mean_size = sum(sizes) / len(sizes)
    assert mean_size < 5.0
    assert all(1 <= s <= 5 for s in sizes)   # 规模 1=单独过半的巨无霸党
    print(f"[3] {N_GAMES} 局随机加权游戏（n=5）：形成的联盟 300/300 为最小"
          f"获胜联盟；平均规模 {mean_size:.2f} < 5（大联盟）——"
          "Riker 规模原理：赢够了就停，多带人是纯分赃")

    # ---------- [4] Gamson 定律展示 ----------
    wts = [40, 35, 15, 10]
    quota = sum(wts) // 2 + 1
    formed = form_coalition(wts, quota, random.Random(1))
    total_w = sum(wts[i] for i in formed)
    shares = {i: wts[i] / total_w for i in sorted(formed)}
    assert abs(sum(shares.values()) - 1.0) < 1e-9 and len(formed) <= 3
    print(f"[4] 展示局 [51; {wts}] 形成 {sorted(formed)} 号联盟："
          f"Gamson 分赃 = {{{', '.join(f'{i}:{s:.0%}' for i, s in shares.items())}}}"
          "——席位比例即部长席位比例（议会联合政府的标准经验律）")

    print("\n全部断言通过 ✓（联盟=合作博弈的政治方言：可枚举、可算权、"
          "可验律）")


if __name__ == "__main__":
    main()
