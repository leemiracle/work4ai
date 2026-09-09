# -*- coding: utf-8 -*-
"""布朗运动模拟 + 重对数律(LIL)数值探测。

04 章·转代码 配套实验(走廊 2 造过程 + 走廊 1 估期望) | 03 章 刚性定理数值实拍。纯标准库。

重对数律(Kolmogorov 1929): limsup_{t→∞} B_t / √(2t·loglog t) = 1   (a.s.)
—— 随机游走看似自由,包络被钉死到常数因子。本实验:
  ① 造布朗运动(高斯增量随机游走,"采样即构造"落地)
  ② 每条路径统计 R = sup_{k≥n_min} S_k / √(2k·loglog k),看分布是否聚在 1 附近
  ③ 数包络越界比例:|S_k| > c·包络 的时间点占比(应很小)

跑法: python experiments/00_brownian_lil.py
"""
import math
import random


def simulate_path(n, rng):
    """高斯增量随机游走: S_k = B_1 + ... (每步 ~N(0,1), 即单位时间布朗的整数时刻采样)。"""
    s = 0.0
    path = [0.0] * (n + 1)
    for k in range(1, n + 1):
        s += rng.gauss(0.0, 1.0)
        path[k] = s
    return path


def lil_stats(path, n_min):
    """返回 (sup R_k, 越界比例): R_k = S_k/√(2k·loglog k), 越界 = |S_k|>1.2·包络。"""
    sup = 0.0
    viol = 0
    cnt = 0
    for k in range(n_min, len(path)):
        env = math.sqrt(2.0 * k * math.log(math.log(k)))
        r = path[k] / env
        if r > sup:
            sup = r
        if abs(path[k]) > 1.2 * env:
            viol += 1
        cnt += 1
    return sup, viol / cnt


def main():
    rng = random.Random(20260906)
    N, M, N_MIN = 100_000, 48, 100

    print("=" * 64)
    print("布朗运动 + 重对数律: 随机游走的精确跑道")
    print(f"  路径数 M={M}, 步数 N={N}, 统计起点 n_min={N_MIN}")
    print("=" * 64)

    # ① 一条样本路径的包络速览(03 章"自由中的必然")
    p0 = simulate_path(N, rng)
    print(f"{'k':>10} {'S_k':>10} {'±√(2k·loglog k)':>18} {'R_k':>8}")
    for k in (100, 1_000, 10_000, 100_000):
        env = math.sqrt(2.0 * k * math.log(math.log(k)))
        print(f"{k:>10} {p0[k]:>10.2f} {env:>18.2f} {p0[k]/env:>8.3f}")
    print("  → |S_k| 被包络 ±√(2k·loglog k) 夹住, 且 R_k = O(1) 不发散\n")

    # ② M 条路径的 sup R 统计(LIL: limsup = 1)
    sups, viol_rates = [], []
    for _ in range(M):
        sup, vr = lil_stats(simulate_path(N, rng), N_MIN)
        sups.append(sup)
        viol_rates.append(vr)
    sups_sorted = sorted(sups)
    med = sups_sorted[M // 2]
    print("=" * 64)
    print(f"sup_k R_k   (理论上 limsup = 1):  min={sups_sorted[0]:.3f} "
          f"median={med:.3f} max={sups_sorted[-1]:.3f}")
    print(f"|S_k| > 1.2·包络 的时间占比:      mean={sum(viol_rates)/M:.4f}")
    print("=" * 64)
    print("读数:")
    print("  · sup R 聚在 1 的上方附近(收敛极慢, 从上方逼近 1)——LIL 的「恰好夹住」")
    print("  · 越界占比个位数百分比:轨道几乎总在 1.2 倍包络之内活动")
    print("  · 对照:若换成 √(2k·log k) 包络(多了个 log),R 会压向 0——loglog 的第二个")
    print("    log 正是「精确跑道」的精妙之处, 多一分太紧, 少一分太松")

    # ③ 自验证断言(容差诚实: LIL 收敛极慢, n=1e5 处 sup 从上方缓降)
    assert 0.6 < med < 1.6, f"LIL sup 中位数 {med:.3f} 偏离理论值 1 过远"
    frac_ok = sum(1 for s in sups if s <= 2.2) / M
    assert frac_ok >= 0.9, f"sup≤2.2 的路径比例仅 {frac_ok:.2f}"
    assert sum(viol_rates) / M < 0.10, "包络越界比例异常"
    print("\n[自验证断言] 全部通过 ✓  (median∈(0.6,1.6); sup≤2.2 比例≥90%; 越界<10%)")


if __name__ == "__main__":
    main()
