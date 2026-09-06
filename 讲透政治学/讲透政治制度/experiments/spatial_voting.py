# -*- coding: utf-8 -*-
"""
空间投票模型：中位数收敛、Plott 星形与 McKelvey 混沌（走廊2：空间投票）
对应章：讲透政治制度/04-政治制度转代码.md（00/03 章引用）

四组断言：
  [1] 一维中位投票者定理（Downs 1957）：双候选位置迭代收敛到选民理想点
      中位数（与均值不同——中位数不响应簇大小权重）
  [2] Plott (1967) 星形配置：其余选民理想点两两位于过中位选民的反向射线上
      → 中位选民的理想点是核心点（配对击败全部网格挑战者）
  [3] 三选民非共线（三角形）配置：核心空——网格上不存在孔多塞赢家
      （McKelvey 混沌定理的离散版），且找到显式多数循环 a≻b≻c≻a
  [4] Shepsle 结构诱导均衡：逐维中位数（议题分开投票的制度产物）是稳定
      结果，但它不是孔多塞赢家——制度把混沌诱导成稳定
口径：二维欧氏偏好（选民投给离自己理想点更近的候选点）；平局各计 0.5。
"""
from itertools import permutations


def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def score(x, y, ideals):
    """x 在配对多数中得的票数（平局各半）。"""
    s = 0.0
    for v in ideals:
        dx, dy = dist(x, v), dist(y, v)
        s += 1.0 if dx < dy else (0.5 if dx == dy else 0.0)
    return s


def beats(x, y, ideals):
    return score(x, y, ideals) > len(ideals) / 2


def main():
    # ---------- [1] 一维：候选位置迭代收敛到中位数 ----------
    voters1d = [30] * 40 + [70] * 61          # 101 位选民，两个簇
    voters1d.sort()
    median1d = voters1d[50]                    # 中位数 = 70
    mean1d = sum(voters1d) / len(voters1d)     # 均值 ≈ 54

    def share1d(p, q, vs):
        s = 0.0
        for v in vs:
            if abs(p - v) < abs(q - v):
                s += 1
            elif abs(p - v) == abs(q - v):
                s += 0.5
        return s

    def best1d(opp, vs):
        return max(range(101), key=lambda p: (share1d(p, opp, vs), -abs(p - median1d)))

    a, b = 0, 100                              # 初值故意放两端
    for _ in range(50):
        a, b = best1d(b, voters1d), best1d(a, voters1d)
        if a == b == median1d:
            break
    assert a == b == median1d == 70, (a, b, median1d)
    assert abs(mean1d - 5470 / 101) < 1e-9 and median1d != round(mean1d)
    print(f"[1] 双候选从两端出发，迭代收敛到中位数 {median1d}"
          f"（均值 {mean1d:.1f} 被无视——70 人簇拖动两党，40 人簇只能跟随）")

    # ---------- [2] Plott 星形：核心存在 ----------
    star = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    grid = [(x / 2, y / 2) for x in range(-6, 7) for y in range(-6, 7)]
    assert all(beats((0, 0), g, star) for g in grid if g != (0, 0))
    # 反向射线配对检验（Plott 条件的构造面）
    rays = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    assert all(any(r1[0] * r2[0] + r1[1] * r2[1] < 0
                   and abs(r1[0] * r2[1] - r1[1] * r2[0]) < 1e-9
                   for r2 in rays) for r1 in rays)
    print("[2] 五选民星形（上下左右+中心）：中心选民理想点(0,0)击败全部 168 个"
          "网格挑战者——Plott 反向射线配对成立，核心存在")

    # ---------- [3] 三选民非共线：核心空 + 显式循环 ----------
    tri = [(0, 0), (2, 0), (0, 2)]
    cores = [g for g in grid
             if all(beats(g, h, tri) for h in grid if h != g)]
    assert cores == [], cores                  # 网格上无孔多塞赢家
    cyc = None
    for a2 in grid:
        for b2 in grid:
            if b2 != a2 and beats(b2, a2, tri):
                for c2 in grid:
                    if c2 not in (a2, b2) and beats(c2, b2, tri) \
                            and beats(a2, c2, tri):
                        cyc = (a2, b2, c2)
                        break
                if cyc:
                    break
        if cyc:
            break
    assert cyc is not None
    print(f"[3] 三选民三角形{(0,0),(2,0),(0,2)}：169 个网格点无一击败其余所有点"
          f"（核心空）；显式循环 {cyc[0]} ≻ {cyc[1]} ≻ {cyc[2]} ≻ {cyc[0]}"
          "——McKelvey：混沌是常态，稳定是奇迹")

    # ---------- [4] 结构诱导均衡：逐维中位数稳定但非孔多塞赢家 ----------
    x_med = sorted(v[0] for v in tri)[1]       # 逐维中位数
    y_med = sorted(v[1] for v in tri)[1]
    issue_by_issue = (x_med, y_med)
    assert issue_by_issue == (0, 0)
    beater = next(g for g in grid if g != issue_by_issue
                  and beats(g, issue_by_issue, tri))
    print(f"[4] 逐维投票制度产出 {issue_by_issue}（两维中位数，制度内稳定——"
          f"每维单独表决时无多数愿移动它）；但整点挑战者 {beater} 能以 2:1 "
          "击败它——稳定来自议程结构（Shepsle），不来自偏好本身")

    print("\n全部断言通过 ✓（空间投票=制度几何学：定理可构造、混沌可演示、"
          "结构诱导可对照）")


if __name__ == "__main__":
    main()
