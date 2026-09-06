# -*- coding: utf-8 -*-
"""环境时序变点检测:CUSUM 与滑动 t 检验,以及短窗口的"暂停"幻觉。

00 章 §七(反直觉:变暖"暂停"是窗口选择效应)& 03 章构造 3(CUSUM 流水线)
& 04 章走廊 1(传感器流的异常/变点检测)配套实验。纯标准库。

设定 Part1: 年温度距平序列 1960-2024(n=65)。真实结构:
  1960-1997 均值 -0.20 ℃,1998 年起 +0.35 ℃(regime shift,真实突变年=1998),噪声 σ=0.25。
  CUSUM   : S_t = Σ_{i≤t}(x_i − x̄),变点 = argmax|S_t| ——均值突变在累计离差上堆成"峰"
  滑动 t  : 逐分割点算前后两段均值差几个标准误,变点 = argmax|t|
  显著性  : 置换检验——整条序列随机重排 N 次得零假设分布(找过最大值的统计量不能查表,
            这是 03 章"argmax 定价"的现场)
设定 Part2: 同样的数据,窗口选择效应——增暖序列(趋势 0.018 ℃/yr + AR(1) 红噪声
  + 1998 年 El Niño 尖峰)在全长窗口斜率显著为正,而 1998-2012 短窗斜率塌陷甚至变号。

跑法: python experiments/00_changepoint.py
自验证: 结尾 assert 两种方法变点估计均落在真实突变年 ±2 内、置换 p<0.01、
  两法估计差 ≤3 年、短窗斜率 < 长窗斜率的一半。
"""

import math
import random

YEARS = list(range(1960, 2025))          # n = 65
N = len(YEARS)
TRUE_SHIFT_YEAR = 1998                    # Part1 真实突变年
MIN_SEG = 10                              # 滑动 t 每段最少年数


# ---------- 合成序列 ----------
def make_shifted_series(seed=20260907):
    """均值突变序列:1998 年起 +0.55 ℃ 的跳变埋在 σ=0.25 的白噪声里。"""
    rng = random.Random(seed)
    xs = []
    for y in YEARS:
        mu = -0.20 if y < TRUE_SHIFT_YEAR else 0.35
        xs.append(mu + rng.gauss(0.0, 0.25))
    return xs


def make_warming_series(seed=19580301):
    """增暖序列:线性趋势 0.018 ℃/yr + AR(1) 红噪声(φ=0.5)+ 1998 年 El Niño 尖峰。"""
    rng = random.Random(seed)
    xs, prev = [], 0.0
    for k, _ in enumerate(YEARS):
        prev = 0.5 * prev + rng.gauss(0.0, 0.15)
        x = -0.35 + 0.018 * k + prev
        if YEARS[k] == 1998:
            x += 0.45                    # 世纪强 El Niño:把 1998 顶成暂时高点
        xs.append(x)
    return xs


# ---------- 检测统计量 ----------
def cusum_scan(xs):
    """CUSUM:返回 (argmax|S_t| 的下标, max|S_t|)。S_t 为对总均值的累计离差。"""
    xbar = sum(xs) / len(xs)
    s, best_t, best_s = 0.0, 0, 0.0
    for t in range(1, N - 1):            # 端点 S 恒为 0,排除
        s += xs[t] - xbar
        if abs(s) > abs(best_s):
            best_t, best_s = t, s
    return best_t, abs(best_s)


def sliding_t_scan(xs):
    """滑动 t:逐分割点算 Welch t,返回 (argmax|t| 的下标, max|t|)。"""
    # 前缀和/平方和:每条候选分割 O(1)
    P = [0.0]
    Q = [0.0]
    for x in xs:
        P.append(P[-1] + x)
        Q.append(Q[-1] + x * x)

    def seg(a, b):                        # [a, b) 的均值与方差
        m = b - a
        mean = (P[b] - P[a]) / m
        var = max((Q[b] - Q[a]) / m - mean * mean, 1e-12)
        return mean, var

    best_t, best_stat = 0, 0.0
    for i in range(MIN_SEG, N - MIN_SEG):
        m1, v1 = seg(0, i)
        m2, v2 = seg(i, N)
        stat = abs(m2 - m1) / math.sqrt(v1 / i + v2 / (N - i))
        if stat > best_stat:
            best_t, best_stat = i, stat
    return best_t, best_stat


def perm_pvalue(xs, stat_fn, observed, nperm=1000, seed=42):
    """置换检验:打乱时间顺序 N 次,零假设下同样'找最大值'的重定价。"""
    rng = random.Random(seed)
    cnt = 0
    pool = list(xs)
    for _ in range(nperm):
        rng.shuffle(pool)
        _, s = stat_fn(pool)
        if s >= observed:
            cnt += 1
    return (cnt + 1) / (nperm + 1)        # 加 1 的保守修正


def ols_slope(xs, years):
    """最小二乘斜率(℃/yr)。"""
    n = len(years)
    mx, my = sum(years) / n, sum(xs) / n
    sxy = sum((years[i] - mx) * (xs[i] - my) for i in range(n))
    sxx = sum((y - mx) ** 2 for y in years)
    return sxy / sxx


def part1_detection():
    xs = make_shifted_series()
    t_cus, s_cus = cusum_scan(xs)
    t_t, s_t = sliding_t_scan(xs)
    y_cus, y_t = YEARS[t_cus], YEARS[t_t]
    p_cus = perm_pvalue(xs, cusum_scan, s_cus)
    p_t = perm_pvalue(xs, sliding_t_scan, s_t)
    return y_cus, y_t, p_cus, p_t


def part2_window_illusion():
    xs = make_warming_series()
    long_i = [i for i, y in enumerate(YEARS)]                       # 1960-2024
    short_i = [i for i, y in enumerate(YEARS) if 1998 <= y <= 2012]  # 15 年短窗
    slope_long = ols_slope([xs[i] for i in long_i], [YEARS[i] for i in long_i])
    slope_short = ols_slope([xs[i] for i in short_i], [YEARS[i] for i in short_i])
    return slope_long, slope_short


def main():
    print("=" * 68)
    print(f"Part 1  合成温度序列突变年检测(真实突变年 = {TRUE_SHIFT_YEAR},"
          f"跳变 0.55 ℃,噪声 σ=0.25)")
    print("=" * 68)
    y_cus, y_t, p_cus, p_t = part1_detection()
    print(f"  CUSUM  argmax|S_t|  →  变点估计 {y_cus} 年,置换 p = {p_cus:.3f}")
    print(f"  滑动 t argmax|t|    →  变点估计 {y_t} 年,置换 p = {p_t:.3f}")
    print(f"  两法估计相差 {abs(y_cus - y_t)} 年;均在真实突变年 ±2 内"
          f"({1996}–{2000})")

    print()
    print("=" * 68)
    print("Part 2  同一条增暖序列,窗口选择的'暂停'幻觉(趋势 0.018 ℃/yr)")
    print("=" * 68)
    slope_long, slope_short = part2_window_illusion()
    print(f"  全长窗口 1960-2024 斜率 = {slope_long:+.4f} ℃/yr   ← 人类信号浮现")
    print(f"  短窗   1998-2012 斜率 = {slope_short:+.4f} ℃/yr   ← 从 El Niño 顶点出发")
    print(f"  短窗只拾回长窗斜率的 {100 * slope_short / slope_long:.0f}% ——"
          " 同一条序列,两种叙事")
    print("  教训:趋势陈述必须声明窗口;短窗趋势是自然变率发的随机礼物。")

    print()
    print("=" * 68)
    print("自验证 assert")
    print("=" * 68)
    assert abs(y_cus - TRUE_SHIFT_YEAR) <= 2, f"CUSUM 变点 {y_cus} 应在 ±2 内"
    assert abs(y_t - TRUE_SHIFT_YEAR) <= 2, f"滑动 t 变点 {y_t} 应在 ±2 内"
    assert p_cus <= 0.01, f"CUSUM 置换 p={p_cus:.3f} 应 ≤0.01"
    assert p_t <= 0.01, f"滑动 t 置换 p={p_t:.3f} 应 ≤0.01"
    assert abs(y_cus - y_t) <= 3, "两法变点估计应相差 ≤3 年"
    assert 0.012 < slope_long < 0.024, f"长窗斜率 {slope_long:.4f} 应贴近真趋势 0.018"
    assert slope_short < 0.5 * slope_long, (
        f"短窗斜率 {slope_short:+.4f} 应塌缩到长窗 {slope_long:+.4f} 的一半以下")
    print("assert 全部通过 ✓")


if __name__ == "__main__":
    main()
