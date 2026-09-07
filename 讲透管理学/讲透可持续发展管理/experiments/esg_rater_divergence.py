# -*- coding: utf-8 -*-
"""ESG 评级分歧仿真:方法学偏移+噪声 ⟹ 聚合困惑(aggregate confusion)。

00-体系结构.md(反直觉 1/美之时刻 3)、02-语言特征.md(三栏之二:评级分歧)
与 04-可持续管理转代码.md(走廊 3/4)的配套实验。纯标准库(random/math)。

模型(02 章「测量/范围/权重」三分解的参数化,Berg-Kölbel-Rigobon 2022 的最小可计算版):
  企业 i 的真实可持续水平藏在三支柱里 E/S/G ∈ [0,100]:
      T_p = 100·(0.5·F + 0.5·u_p)    F=企业共同因子,u_p=支柱独立因子
  ⟹ 支柱间相关 ≈ 0.5;总水平 T=三支柱均值(不可直接观测的构念——无金标准)。
  企业另有披露姿态 D_p = T_p + g_p,g_p ~ N(0, σ_g):披露-实质缺口的个体差异;
  漂绿(greenwash)= 只抬 g 不动 T(可观测披露信号变好,实质水平不变)。
  机构 j 的评级 = 真实水平经三层方法学偏移 + 抽样噪声:
      ① 权重差  w_p   :三支柱配比不同(weight divergence,Berg 分解 ~6%)
      ② 范围差  λ     :披露通道 D_p 与实质通道 T_p 的混合比(scope divergence)
      ③ 测量差  m_ij  :机构对企业的持久方法学偏差,~N(0,σ_m),
                        跨波持久、跨机构独立(measurement divergence,Berg 分解 ~56%,占大头)
      ④ 非线性  γ     :分位拉伸的幂变换
      ⑤ 抽样噪声 n_ij :~N(0,σ_j),每波独立
      r_ij = 100·(x_ij/100)^γ + m_ij + n_ij,其中 x_ij = Σ_p w_p·((1−λ)·T_p + λ·D_p)

三组断言:
  ① 分歧是结构性的:同机构跨波自相关(可靠性)显著高于两两跨机构相关;
     把抽样噪声归零后跨机构相关仍远离 1(分歧来自方法学,不来自噪声)。
  ② 排序不稳定:同一企业在不同机构处的分位差很大(40+ 分位带、上下半区翻转)。
  ③ 漂绿可度量:只抬披露姿态(+15,实质不动)时,披露型机构(λ≥0.7)评级显著抬升、
     实质型机构(λ≤0.2)几乎不动;披露-实质评级缺口对漂绿组的增量远大于对照组,
     按缺口增量排序可把漂绿组筛出(precision@K ≥ 0.8)。

跑法: python3 -u experiments/esg_rater_divergence.py
"""

import math
import random

N_FIRMS = 300
N_WAVES_SAMPLES = 2          # 两个独立评级波(测同机构自相关)
SIGMA_G = 12.0               # 披露-实质缺口的个体差异
SIGMA_M = 8.0                # 测量差:机构-企业持久方法学偏差
GREENWASH_DELTA = 15.0       # 漂绿:披露姿态抬升幅度(实质不动)
GREENWASH_N = 60             # 漂绿组企业数

# 机构名 / 权重 w(E,S,G) / 通道混合比 λ / 非线性 γ / 抽样噪声 σ
AGENCIES = [
    ("A·环重披露型", (0.50, 0.30, 0.20), 0.85, 0.90, 3.0),
    ("B·社重实质型", (0.25, 0.50, 0.25), 0.10, 1.10, 3.5),
    ("C·治重均衡型", (0.20, 0.30, 0.50), 0.45, 1.00, 4.0),
    ("D·披露型    ", (0.35, 0.35, 0.30), 0.75, 1.15, 4.0),
    ("E·实质型    ", (0.30, 0.25, 0.45), 0.15, 0.85, 3.0),
]
DISCLOSURE_IDX = (0, 3)      # λ≥0.7 的披露型机构(A/D)
SUBSTANCE_IDX = (1, 4)       # λ≤0.2 的实质型机构(B/E)


def clamp(v, lo=0.0, hi=100.0):
    return lo if v < lo else (hi if v > hi else v)


def make_firms(rng, n):
    """真实三支柱 T_p 与披露姿态 D_p;返回 (T, D) 两个 n×3 矩阵(列表的列表)。"""
    true_p, disc = [], []
    for _ in range(n):
        f = rng.uniform(0.0, 1.0)
        t_row = [clamp(100.0 * (0.5 * f + 0.5 * rng.uniform(0.0, 1.0)))
                 for _ in range(3)]
        d_row = [clamp(t + rng.gauss(0.0, SIGMA_G)) for t in t_row]
        true_p.append(t_row)
        disc.append(d_row)
    return true_p, disc


def rate(true_p, disc, agency, firm_i, m_ij, n_ij, disclosure=None):
    """评级函数:x=Σw·((1−λ)T+λ·D) → γ 幂变换 → +测量差+抽样噪声。"""
    _, w, lam, gamma, _ = agency
    d_row = disc[firm_i] if disclosure is None else disclosure[firm_i]
    x = sum(w[p] * ((1.0 - lam) * true_p[firm_i][p] + lam * d_row[p])
            for p in range(3))
    y = 100.0 * (x / 100.0) ** gamma
    return clamp(y + m_ij + n_ij)


def panel(true_p, disc, m_bias, noises):
    """整张评级面板:r[j][i];m_bias/noises 为 n机构×n企业 的持久偏差/当波噪声。"""
    return [[rate(true_p, disc, AGENCIES[j], i, m_bias[j][i], noises[j][i])
             for i in range(len(true_p))] for j in range(len(AGENCIES))]


def draw_noises(rng, n):
    return [[rng.gauss(0.0, AGENCIES[j][4]) for _ in range(n)]
            for j in range(len(AGENCIES))]


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy)


def percentile_ranks(vals):
    """0-100 分位(秩法);评级有界可能截断并列,秩法对并列不敏感,够用。"""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    for pos, i in enumerate(order):
        ranks[i] = 100.0 * pos / (len(vals) - 1)
    return ranks


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs)


def main():
    rng = random.Random(20260907)
    n_ag, n = len(AGENCIES), N_FIRMS
    true_p, disc = make_firms(rng, n)
    # 持久测量差(方法学,跨波不变、跨机构独立)+ 两波独立抽样噪声
    m_bias = [[rng.gauss(0.0, SIGMA_M) for _ in range(n)] for _ in range(n_ag)]
    noise1 = draw_noises(rng, n)
    noise2 = draw_noises(rng, n)
    r1 = panel(true_p, disc, m_bias, noise1)
    r2 = panel(true_p, disc, m_bias, noise2)

    print("=" * 86)
    print("ESG 评级分歧:方法学偏移(权重/通道/非线性/测量差)+噪声 —— 聚合困惑仿真")
    print(f"参数:{n} 家企业 × {n_ag} 家机构;σ_g={SIGMA_G}(披露缺口),"
          f"σ_m={SIGMA_M}(测量差),漂绿 δ=+{GREENWASH_DELTA}")
    print("=" * 86)

    # ---- 断言 ①:分歧的结构性 ----
    within = [pearson(r1[j], r2[j]) for j in range(n_ag)]      # 同机构跨波=可靠性
    cross = [(j, k, pearson(r1[j], r1[k]))                     # 两两跨机构
             for j in range(n_ag) for k in range(j + 1, n_ag)]
    zero = [[0.0] * n for _ in range(n_ag)]
    r_nz = panel(true_p, disc, m_bias, zero)                   # 抽样噪声归零
    cross_nz = [pearson(r_nz[j], r_nz[k])
                for j in range(n_ag) for k in range(j + 1, n_ag)]
    print("\n① 分歧的结构性(同机构跨波自相关 vs 两机构两两相关):")
    for j, name in enumerate(a[0] for a in AGENCIES):
        print(f"  {name}  自相关 {within[j]:.3f}")
    for j, k, rv in cross:
        print(f"  {AGENCIES[j][0].strip()} × {AGENCIES[k][0].strip()}: {rv:.3f}")
    print(f"  ── 自相关均值 {mean(within):.3f} | 两两均值 {mean([c[2] for c in cross]):.3f}"
          f" | 噪声归零后两两均值 {mean(cross_nz):.3f}(区间 "
          f"{min(cross_nz):.3f}~{max(cross_nz):.3f})")
    print("  对照:信用评级机构间相关 ≈ 0.99(Berg 等 2022 通说)——ESG 评级的分歧是量级差")
    assert min(within) - max(c[2] for c in cross) > 0.05, \
        "断言①失败:跨机构相关未显著低于同机构自相关"
    assert 0.5 < mean(c[2] for c in cross) < 0.92, "断言①失败:分歧量级不合理"
    assert mean(within) > 0.90, "断言①失败:同机构可靠性应高(对照信用评级)"
    assert max(cross_nz) < 0.95, \
        "断言①失败:噪声归零后仍应分歧——方法学差异独存是结构性的"

    # ---- 断言 ②:排序不稳定(同一企业跨机构分位差)----
    pcts = [percentile_ranks(r1[j]) for j in range(n_ag)]      # 各机构内的分位
    spreads = [max(pcts[j][i] for j in range(n_ag))
               - min(pcts[j][i] for j in range(n_ag)) for i in range(n)]
    flips = sum(1 for i in range(n)                            # 上下半区翻转
                if max(pcts[j][i] for j in range(n_ag)) >= 50.0
                > min(pcts[j][i] for j in range(n_ag)))
    wide = sum(1 for s in spreads if s > 40.0)
    print(f"\n② 排序不稳定:同一企业跨机构分位带")
    print(f"  分位带(最高分位−最低分位)均值 {mean(spreads):.1f} | "
          f">40 分位带的企业 {wide}/{n} ({wide / n:.0%}) | "
          f"上下半区翻转企业 {flips}/{n} ({flips / n:.0%})")
    assert mean(spreads) > 15.0, "断言②失败:分位带应显著为宽"
    assert wide > 0.05 * n, "断言②失败:应存在 40+ 分位带的企业"
    assert flips > 0.10 * n, "断言②失败:上下半区翻转应常见"

    # ---- 断言 ③:漂绿的披露-实质缺口可度量 ----
    # 漂绿干预:抽 GREENWASH_N 家,披露姿态 +δ(实质 T 不动);噪声与测量差冻结,
    # 评级变化只来自披露通道——隔离"只改信号不改实质"的效应。
    gw_set = set(rng.sample(range(n), GREENWASH_N))
    disc_gw = [[clamp(d + (GREENWASH_DELTA if i in gw_set else 0.0))
                for d in row] for i, row in enumerate(disc)]
    r1g = panel(true_p, disc_gw, m_bias, noise1)

    def delta(j, i):
        return r1g[j][i] - r1[j][i]

    d_disc = mean([delta(j, i) for j in DISCLOSURE_IDX for i in gw_set])
    d_sub = mean([delta(j, i) for j in SUBSTANCE_IDX for i in gw_set])

    def gap(i):
        return (mean([r1[j][i] for j in DISCLOSURE_IDX])
                - mean([r1[j][i] for j in SUBSTANCE_IDX]))

    def gap_gw(i):
        return (mean([r1g[j][i] for j in DISCLOSURE_IDX])
                - mean([r1g[j][i] for j in SUBSTANCE_IDX]))

    inc_gw = mean([gap_gw(i) - gap(i) for i in gw_set])
    inc_rest = mean([gap_gw(i) - gap(i) for i in range(n) if i not in gw_set])
    ranked = sorted(range(n), key=lambda i: gap_gw(i) - gap(i), reverse=True)
    hits = sum(1 for i in ranked[:GREENWASH_N] if i in gw_set)
    print(f"\n③ 漂绿(披露+{GREENWASH_DELTA:.0f}、实质不动)的披露-实质缺口:")
    print(f"  披露型机构(A/D,λ≥0.7)平均评级变化 {d_disc:+.2f} | "
          f"实质型机构(B/E,λ≤0.2)平均变化 {d_sub:+.2f}")
    print(f"  缺口增量:漂绿组 {inc_gw:+.2f} vs 对照组 {inc_rest:+.2f} | "
          f"按缺口增量取前 {GREENWASH_N} 名:命中漂绿组 {hits}/{GREENWASH_N} "
          f"(precision@K={hits / GREENWASH_N:.2f})")
    assert d_disc > 4 * abs(d_sub) and d_disc > 6.0, \
        "断言③失败:披露型机构应显著抬升"
    assert abs(d_sub) < 3.0, "断言③失败:实质型机构应几乎不动"
    assert inc_gw - inc_rest > 5.0, "断言③失败:缺口增量应区分漂绿组与对照组"
    assert hits >= 0.8 * GREENWASH_N, "断言③失败:缺口排序应筛出漂绿组"

    print("\n✓ 自验证通过:① 两两相关显著低于同机构自相关,噪声归零后仍分歧"
          "(结构性,方法学独存) | ② 分位带均值 %.1f、%d 家 40+ 分位带、"
          "%d 家上下半区翻转(排序不稳定) | ③ 漂绿使披露型评级 +%.1f 而实质型 "
          "%+.1f,缺口增量 %.1f vs %.1f,precision@K=%.2f"
          % (mean(spreads), wide, flips, d_disc, d_sub, inc_gw, inc_rest,
             hits / GREENWASH_N))
    print("  读法:分歧不是谁不认真——测量差/范围差/权重差都是『口径的合法选择』;")
    print("  而缺口(披露通道−实质通道)恰是漂绿的候选信号:测量失败反转成检测器。")


if __name__ == "__main__":
    main()
