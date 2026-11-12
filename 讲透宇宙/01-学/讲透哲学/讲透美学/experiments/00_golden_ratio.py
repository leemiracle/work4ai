# -*- coding: utf-8 -*-
"""黄金比例与「审美偏好」:一个文化锚定的机制模拟(00/04 章配套实验)。

纯标准库(random/math)。assert 自验证。

模型(生成机制,不是真实数据):
  · 模拟人群:每人有一个"理想矩形比例" ideal_i ~ LogNormal(文化锚点 A, 个体离散 σ)
  · 对候选矩形 r 的偏好权重 ∝ exp(-((ln r - ln ideal_i)/w)²)——离理想越远越不选
  · 每人按权重随机投票(判断带噪声,不总选理想值)
  · 聚合票数 = 该文化的"审美偏好分布"

Part 1  Fechner 式矩形偏好模拟
  · 稳健性:锚点 ≈φ(1.62)的房间里,20 个随机种子,偏好众数全部落在黄金比矩形
  · 敏感性:文化锚点扫过 1.0/1.25/1.62/2.0,众数随锚点单调搬家
    ——方形文化选方形,"黄金比最受偏爱"忠实跟随锚点,不跟随任何"普遍人性"
Part 2  双文化混合人群(锚 1.05 与 1.62 各半)
  · 偏好分布峰值瓦解:无人过半,两个子文化的峰并存
  · 「全人类共同的最美比例」叙事在混合房间里失效

经验文献对照声明(重要,读结论前必看):
  · Fechner (1876)《美学初探》的金矩形选择实验是实验美学的起点;
  · 但后续大样本复制(综述见 Green 1995, Perception;Höge 系列等)发现:
    偏好峰值弱、跨研究跨人群不稳定,呈现方式与任务设计显著调制结果;
  · 本脚本模拟"文化锚点 + 个体噪声"这一生成机制,断言的是机制性质
    (众数的种子稳健性/文化参数敏感性),不替任何真实人群的偏好背书;
  · 解读纪律(04 章):可量的是分布,不可算的是判断——黄金比叙事的
    脆弱性恰好示范了"审美普适断言"应如何被机制模型审计。

跑法: python experiments/00_golden_ratio.py
"""

import math
import random

RATIOS = [1.0, 1.2, 1.414, 1.618, 1.75, 2.0, 2.5]   # 候选矩形(宽/高,横幅)
IDX_PHI = RATIOS.index(1.618)
SIGMA = 0.15   # 个体理想比例的离散(log 空间)
W = 0.12       # 判断噪声带宽(log 空间)
N_POP = 6000   # 每次模拟的人数
BAR = "=" * 64


def vote_share(anchor, n, rng, sigma=SIGMA, w=W):
    """一个文化锚点为 anchor 的 n 人人群对各矩形的偏好份额。"""
    counts = [0] * len(RATIOS)
    ln_anchor = math.log(anchor)
    for _ in range(n):
        ideal = math.exp(rng.gauss(ln_anchor, sigma))   # 个体理想比例
        ln_ideal = math.log(ideal)
        weights = [math.exp(-((math.log(r) - ln_ideal) / w) ** 2)
                   for r in RATIOS]
        pick = rng.choices(range(len(RATIOS)), weights=weights, k=1)[0]
        counts[pick] += 1
    return [c / n for c in counts]


def mode_index(shares):
    return max(range(len(shares)), key=lambda i: shares[i])


def show(shares, tag):
    print(f"  {tag}")
    for r, s in zip(RATIOS, shares):
        mark = "  ← 众数" if s == max(shares) else ""
        print(f"    矩形 {r:>6.3f} : {s:>6.1%}  {'█' * round(s * 100)}{mark}")


def part1_preference():
    print(BAR)
    print("Part 1 · 矩形偏好模拟:黄金比的稳健性与敏感性")
    print(BAR)

    print(f"[A] 稳健性:锚点=1.62(≈φ)的房间,{N_POP} 人 × 20 个种子")
    modes = []
    for seed in range(20):
        shares = vote_share(1.62, N_POP, random.Random(20260907 + seed))
        modes.append(mode_index(shares))
    print(f"  20 个种子的偏好众数全部落在矩形 {RATIOS[modes[0]]}"
          f"(黄金比窗口内:{modes.count(IDX_PHI)}/20)")
    shares0 = vote_share(1.62, N_POP, random.Random(20260907))
    show(shares0, "锚点 1.62 的偏好分布(种子 0):")
    assert all(m == IDX_PHI for m in modes), "锚点≈φ 时众数应种子稳健地落在黄金比"
    print("  → 机制内部,黄金比的'最受偏爱'完全稳健——只要文化锚在那里。\n")

    print("[B] 敏感性:文化锚点扫描(换文化=换众数)")
    prev = -1
    for anchor in (1.0, 1.25, 1.62, 2.0):
        shares = vote_share(anchor, N_POP, random.Random(20260907))
        m = mode_index(shares)
        print(f"  锚点 {anchor:>5.2f} → 众数 {RATIOS[m]:>6.3f}"
              f"(黄金比矩形份额 {shares[IDX_PHI]:>5.1%})")
        assert m >= prev, "众数应随锚点单调右移"
        prev = m
    assert mode_index(vote_share(1.0, N_POP, random.Random(1))) == 0, \
        "方形文化(锚 1.0)的众数应是方形"
    assert mode_index(vote_share(2.0, N_POP, random.Random(2))) == RATIOS.index(2.0), \
        "长条文化(锚 2.0)的众数应是 2.0"
    print("  → 偏好众数忠实跟随文化锚点:1.0 的房间方形称王;")
    print("    '黄金比=普遍人性'在机制层面不成立,它只是某个房间的锚。\n")

    print("[C] 文献对照(声明,非模拟结果)")
    print("  · Fechner(1876)报告金矩形在 10 个矩形中首选率约 1/3——量级与")
    print("    本模拟锚点房间的高份额同阶,原始发现并不需要'普遍人性'解释;")
    print("  · 后续大样本复制(Green 1995 综述等):峰值弱、跨研究不稳定;")
    print("  · 结论替换:把'人类天生爱黄金比'改写为'偏好分布跟随文化锚点'。")


def part2_mixture():
    print()
    print(BAR)
    print("Part 2 · 双文化混合房间:单一'最美比例'叙事的瓦解")
    print(BAR)
    rng = random.Random(42)
    half = N_POP // 2
    a = vote_share(1.05, half, rng)
    b = vote_share(1.62, half, rng)
    mixed = [(x + y) / 2 for x, y in zip(a, b)]
    show(mixed, "锚 1.05 与 1.62 各半的混合人群:")

    top = max(mixed)
    left_band = mixed[0] + mixed[1]                      # 方形带(子文化 A 的峰)
    right_band = mixed[2] + mixed[3] + mixed[4]          # 黄金比带(子文化 B 的峰)
    print(f"\n  最高份额 {top:.1%};方形带(1.0+1.2){left_band:.1%};"
          f"黄金比带(1.414~1.75){right_band:.1%};"
          f"黄金比矩形被稀释:{mixed[IDX_PHI]:.1%}(纯文化房间为 {b[IDX_PHI]:.1%})")
    assert top < 0.45, "混合房间里任何比例都不该拿到多数"
    assert left_band >= 0.35, "子文化 A 的峰带(方形带)应在场"
    assert right_band >= 0.35, "子文化 B 的峰带(黄金比带)应在场"
    assert mode_index(mixed) != IDX_PHI, "混合众数不再是黄金比——单一叙事失效"
    assert mixed[IDX_PHI] < 0.7 * b[IDX_PHI], "黄金比份额应被显著稀释"
    print("  → 两个子文化各自稳健(见 Part 1),合在一起却无王无峰值;")
    print("    趣味二律背反的统计化身:可量的是分布,不可算的是判断。")


if __name__ == "__main__":
    part1_preference()
    part2_mixture()
    print()
    print("[ALL ASSERTS PASSED] 黄金比偏好模拟:稳健性/敏感性/混合瓦解 全部命中。")
