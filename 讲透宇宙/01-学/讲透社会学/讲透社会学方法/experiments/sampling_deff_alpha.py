# -*- coding: utf-8 -*-
"""社会学方法三律实验:精度账单 / 整群设计效应 / 量表信度 Cronbach α。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(抽样方案卡、结构引擎 1
随机化引擎)与 04-社会学方法转代码.md(走廊 1/2)的配套实验。
纯标准库(math/random/statistics),固定随机种子,assert 自验证。

三幕:
  幕一 精度账单(样本量的边际递减):SE = σ/√n。
      断言:n=4→16 时 SE 减半、16→64 再减半(理论比恰为 2);
      蒙特卡洛互证:经验 SE(样本均值的标差)与理论 SE 相对偏差 < 5%。
      打印:样本量翻 4 倍,精度只翻 1 倍——民调的钱花在 √n 上。
  幕二 整群抽样的设计效应:deff = 1 + (m−1)ρ。
      断言:m=20、ρ=0.05 → deff = 1.95(等效样本近乎减半)。
      蒙特卡洛互证:个体值 = 类共同冲击(方差 τ²)+ 个体噪声(方差 σ²),
      ICC ρ = τ²/(τ²+σ²);整群样本均值的实际方差比同规模简单随机样本
      高约 (m−1)ρ 倍——"抽了 1000 人不等于有 1000 人的信息"。
  幕三 量表信度 Cronbach α 与题目数:α = k·r̄ / (1 + (k−1)·r̄)。
      三律:
      ① 锚值:r̄=0.30 时 k=4 → α≈0.632、k=8 → α≈0.774(容差 1e-3);
      ② 加题边际递减:k 从 2→4→8 时 α 增量逐段缩小(数值打印);
      ③ r̄ 低时到达 0.9 需要不现实题量:r̄=0.30 时最小整数 k=21 才使
      α≥0.90(代数解 0.3k=0.9(1+0.3(k−1))→k=21,数值扫描互证);
      对照 r̄=0.50 时 k=9 即达(0.5k=0.9(1+0.5(k−1))→k=9)。
      点题:加题能到但要付题量代价;r̄ 才是信度的第一杠杆——
      题目间相关烂,加题是饮鸩止渴。
      蒙特卡洛互证:单因子题目模型(题 = √r̄·潜特质 + √(1−r̄)·噪声),
      经验 α 与闭式解一致;经验题间平均相关 ≈ r̄。

跑法: python -u experiments/sampling_deff_alpha.py
"""

import math
import random
import statistics

MU = 50.0          # 幕一总体均值
SIGMA = 10.0       # 幕一总体标差(已知)


# ==================== 幕一:精度账单(样本量的边际递减) ====================

def act1():
    print("=" * 84)
    print("幕一 精度账单:SE = σ/√n(样本量翻 4 倍,精度只翻 1 倍)")
    print("=" * 84)
    grid = ((4, 20_000), (16, 20_000), (64, 8_000), (256, 4_000))
    rows = {}
    print(f"\n总体 μ={MU}, σ={SIGMA}(已知);蒙特卡洛重复见括号")
    print(f"{'n':>5} {'理论SE':>9} {'经验SE(MC)':>12} {'相对偏差':>9} "
          f"{'95%误差(1.96SE)':>15}")
    for k, (n, reps) in enumerate(grid):
        rng = random.Random(20260901 + k)
        means = []
        for _ in range(reps):
            s = 0.0
            for _ in range(n):
                s += rng.gauss(MU, SIGMA)
            means.append(s / n)
        emp = statistics.stdev(means)
        theo = SIGMA / math.sqrt(n)
        rel = abs(emp - theo) / theo
        rows[n] = (theo, emp, rel)
        print(f"{n:>5} {theo:>9.4f} {emp:>12.4f} {rel:>8.2%} "
              f"{1.96 * theo:>15.4f}")

    print("\n读数:")
    print("  · n: 4→16(钱×4):SE 5.000→2.500——恰减半;16→64(再×4):再减半")
    print("  · 精度按 √n 爬:想把误差砍半,预算翻 4 倍;砍到 1/4,翻 16 倍")
    print("  · 换算成比例问题(p=0.5):n=1000 → ±3.1 个百分点;")
    print("    n=4000(钱×4)→ ±1.55 个百分点(精度×2)——这就是民调的定价表")
    print("  · SE 与总体大小无关:1000 人对 100 万与对 3 亿总体,SE 同价")

    # 断言 1a:理论减半律(精确);n 每 ×4,SE ×1/2
    assert abs(rows[4][0] / rows[16][0] - 2.0) < 1e-12, "4→16 理论 SE 应减半"
    assert abs(rows[16][0] / rows[64][0] - 2.0) < 1e-12, "16→64 理论 SE 应再减半"
    assert abs(rows[64][0] / rows[256][0] - 2.0) < 1e-12, "64→256 理论 SE 应再减半"
    # 断言 1b:MC 互证——经验 SE 与理论 SE 相对偏差 < 5%
    for n in (4, 16, 64, 256):
        assert rows[n][2] < 0.05, f"n={n}:经验 SE 偏差 {rows[n][2]:.2%} 应 <5%"
    # 断言 1c:经验减半律(采样噪声内)
    assert abs(rows[4][1] / rows[16][1] - 2.0) < 0.10, "MC 经验 SE 4→16 应≈减半"
    assert abs(rows[16][1] / rows[64][1] - 2.0) < 0.10, "MC 经验 SE 16→64 应≈减半"
    print(f"\n✓ 幕一断言通过:理论 SE 逐级减半精确成立;"
          f"MC 经验 SE 最大偏差 {max(rows[n][2] for n in rows):.2%} < 5%")
    return rows


# ================ 幕二:整群抽样的设计效应 deff = 1+(m−1)ρ ================

def act2():
    print("\n" + "=" * 84)
    print("幕二 整群抽样的设计效应:deff = 1 + (m−1)ρ")
    print("=" * 84)
    m = 20            # 每群人数(班级/居委会/住户群)
    rho = 0.05        # 组内相关 ICC
    g = 50            # 群数
    n = g * m         # 总样本 1000
    v_total = 1.0     # 个体总方差
    tau2 = rho * v_total        # 类共同冲击方差 0.05
    sig2 = v_total - tau2       # 个体噪声方差 0.95
    reps = 3_000
    theo_deff = 1.0 + (m - 1) * rho

    print(f"\n个体值 = 类共同冲击(方差 τ²={tau2}) + 个体噪声(方差 σ²={sig2});"
          f"ICC ρ = τ²/(τ²+σ²) = {rho}")
    print(f"抽样方案:g={g} 群 × 每群 m={m} 人 = n={n};简单随机对照同 n\n")
    print(f"{'方案':<10} {'均值方差(MC)':>13} {'理论方差':>10} {'相对偏差':>9}")
    print(f"{'(理论 SRS':<10} {'—':>13} {v_total / n:>10.6f} {'—':>9})")

    # 整群臂:先抽共同冲击,再加个体噪声
    rng = random.Random(20260905)
    means_c = []
    for _ in range(reps):
        s = 0.0
        for _ in range(g):
            c = rng.gauss(0.0, math.sqrt(tau2))
            for _ in range(m):
                s += c + rng.gauss(0.0, math.sqrt(sig2))
        means_c.append(s / n)
    var_c = statistics.variance(means_c)
    theo_var_c = theo_deff * v_total / n

    # 简单随机臂:同 n 独立抽样
    rng2 = random.Random(20260906)
    means_s = []
    for _ in range(reps):
        s = 0.0
        for _ in range(n):
            s += rng2.gauss(0.0, math.sqrt(v_total))
        means_s.append(s / n)
    var_s = statistics.variance(means_s)
    theo_var_s = v_total / n

    rel_c = abs(var_c - theo_var_c) / theo_var_c
    rel_s = abs(var_s - theo_var_s) / theo_var_s
    deff_emp = var_c / var_s
    print(f"{'整群':<10} {var_c:>13.6f} {theo_var_c:>10.6f} {rel_c:>8.2%}")
    print(f"{'简单随机':<10} {var_s:>13.6f} {theo_var_s:>10.6f} {rel_s:>8.2%}")
    print(f"\n经验 deff(整群方差/SRS方差)= {deff_emp:.3f};"
          f"理论 deff = 1+(m−1)ρ = {theo_deff:.2f}")
    print(f"方差膨胀 = deff−1 = {deff_emp - 1:.3f};理论 (m−1)ρ = {(m - 1) * rho:.2f}")
    print(f"等效样本量 = n/deff = {n}/{theo_deff:.2f} ≈ {n / theo_deff:.0f} 人")
    print("\n读数:")
    print("  · 同样抽 1000 人,整群方案的抽样方差高约 95%((m−1)ρ 倍膨胀)")
    print("  · 等效样本 1000→约 513 人:『抽了 1000 人』≠『有 1000 人的信息』")
    print("  · 群越大(m↑)、群内越像(ρ↑),deff 越惨:班级/居委会抽样必须预算")
    print("  · 工程口诀:多阶段整群设计之后,样本量先乘 deff 再报价(幕一账单翻页)")

    # 断言 2:deff 理论值;MC 互证两个臂+膨胀倍数
    assert abs(theo_deff - 1.95) < 1e-12, "m=20, ρ=0.05 → deff 应=1.95"
    assert rel_c < 0.08, f"整群臂 MC 方差偏差 {rel_c:.2%} 应 <8%"
    assert rel_s < 0.08, f"SRS 臂 MC 方差偏差 {rel_s:.2%} 应 <8%"
    assert abs(deff_emp - theo_deff) / theo_deff < 0.10, \
        f"经验 deff {deff_emp:.3f} 与理论 {theo_deff:.2f} 偏差应 <10%"
    assert abs((deff_emp - 1) - (m - 1) * rho) < 0.20, \
        f"方差膨胀应≈(m−1)ρ={(m - 1) * rho:.2f},实测 {deff_emp - 1:.3f}"
    assert n / theo_deff < 0.55 * n, "等效样本应近乎减半"
    print(f"\n✓ 幕二断言通过:deff=1.95;MC 两臂各自对上理论方差;"
        f"膨胀 {deff_emp - 1:.3f}≈{(m - 1) * rho:.2f};等效样本≈{n / theo_deff:.0f} 人")
    return deff_emp


# ============== 幕三:Cronbach α 与题目数(信度的兑换率) ==============

def alpha_closed(k, rbar):
    """等方差等题间相关假设下的 Spearman-Brown 式 α 闭式解。"""
    return k * rbar / (1.0 + (k - 1) * rbar)


def alpha_empirical(k, rbar, resp, seed):
    """单因子题目模型模拟经验 α:题 = √r̄·潜特质 + √(1−r̄)·噪声。
    逐题累加 Σx、Σx²,总分累加 Σt、Σt²;α = k/(k−1)·(1−Σvar_i/var_T)。"""
    rng = random.Random(seed)
    lam = math.sqrt(rbar)
    e = math.sqrt(1.0 - rbar)
    sx = [0.0] * k
    sx2 = [0.0] * k
    st = st2 = 0.0
    for _ in range(resp):
        f = rng.gauss(0.0, 1.0)
        tot = 0.0
        for j in range(k):
            x = lam * f + e * rng.gauss(0.0, 1.0)
            tot += x
            sx[j] += x
            sx2[j] += x * x
        st += tot
        st2 += tot * tot
    sum_vi = sum(sx2[j] / resp - (sx[j] / resp) ** 2 for j in range(k))
    var_t = st2 / resp - (st / resp) ** 2
    return k / (k - 1) * (1.0 - sum_vi / var_t), sum_vi, var_t


def min_items(target, rbar):
    """达到 α≥target 所需最少题数(闭式扫描)。"""
    k = 2
    while alpha_closed(k, rbar) < target:
        k += 1
    return k


def act3():
    print("\n" + "=" * 84)
    print("幕三 量表信度 Cronbach α 与题目数:α = k·r̄/(1+(k−1)·r̄)")
    print("=" * 84)
    rbar = 0.30
    print(f"\n闭式解(r̄=题间平均相关={rbar}):")
    print(f"{'k(题数)':>7} {'α':>7} {'每翻倍增益':>9}")
    prev = None
    for k in (4, 8, 16, 32, 64):
        a = alpha_closed(k, rbar)
        d = "" if prev is None else f"+{a - prev:.3f}"
        print(f"{k:>7} {a:>7.3f} {d:>9}")
        prev = a

    a2, a4, a8 = alpha_closed(2, rbar), alpha_closed(4, rbar), alpha_closed(8, rbar)
    d24, d48 = a4 - a2, a8 - a4
    lim = alpha_closed(1_000_000, rbar)
    k90 = min_items(0.90, rbar)
    k90_hi = min_items(0.90, 0.50)
    print(f"\n读数:")
    print(f"  · 加题边际递减:k 2→4 增量 +{d24:.3f},4→8 增量 +{d48:.3f}"
          f"(逐段缩小);继续 8→16 +{alpha_closed(16, rbar) - a8:.3f}")
    print(f"  · 理论上限:k→∞ 时 kr̄ 与 1+(k−1)r̄ 同阶,α→1"
          f"(10⁶ 题时 α={lim:.7f})")
    print(f"  · 到达 0.9 的题量代价:r̄=0.30 时最小整数 k={k90} 才使 α≥0.90")
    print(f"    (代数解 0.3k=0.9(1+0.3(k−1))→k=21,数值扫描互证,α(21)=0.900);")
    print(f"    对照 r̄=0.50 时 k={k90_hi} 即达(α(9)=0.900)")
    print(f"  · r̄ 才是信度的第一杠杆:同样 4 题,r̄=0.3/0.5/0.7 → "
          f"α={alpha_closed(4, 0.3):.3f}/{alpha_closed(4, 0.5):.3f}/"
          f"{alpha_closed(4, 0.7):.3f};")
    print(f"    把 α 从 0.632 提到 0.800:提题质 r̄ 0.3→0.5(4 题不动),"
          f"或加题 4→{min_items(0.80, rbar)} 题")
    print(f"  · 点题:加题能到但要付题量代价;题目间相关烂,加题是饮鸩止渴")

    # 断言 3a:闭式锚值(容差 1e-3)
    assert abs(a4 - 0.632) < 1e-3, f"k=4 应 α≈0.632,得 {a4:.4f}"
    assert abs(a8 - 0.774) < 1e-3, f"k=8 应 α≈0.774,得 {a8:.4f}"
    # 断言 3b:加题边际递减(2→4→8 增量逐段缩小)
    assert 0 < d48 < d24, \
        f"k 2→4 增量 {d24:.4f} 应大于 4→8 增量 {d48:.4f}"
    # 断言 3c:阈值题数——r̄=0.30 时最小整数 k=21(α(21)=0.900 恰达);
    #          对照 r̄=0.50 时 k=9 即达
    assert k90 == 21 and abs(alpha_closed(k90, rbar) - 0.90) < 1e-9, \
        f"r̄=0.3 时最小整数 k 应=21 且 α(21)=0.900,得 k={k90}"
    assert k90_hi == 9 and abs(alpha_closed(k90_hi, 0.50) - 0.90) < 1e-9, \
        f"r̄=0.5 时最小整数 k 应=9 且 α(9)=0.900,得 k={k90_hi}"
    # 断言 3d:上限算准(k→∞ 的 α 上限 = 1,分子分母同阶)
    assert abs(lim - 1.0) < 1e-4, f"k=10⁶ 应逼近上限 1,得 {lim:.7f}"
    # 断言 3e:MC 互证——经验 α 对上闭式解,经验题间平均相关 ≈ r̄
    resp = 40_000
    a_emp, sum_vi, var_t = alpha_empirical(8, rbar, resp, seed=20260915)
    rbar_emp = (var_t - sum_vi) / (8 * 7)     # 等方差≈1 时,题间平均协方差≈平均相关
    print(f"\n蒙特卡洛互证:单因子模型,受访者 {resp:,},k=8:")
    print(f"  经验 α = {a_emp:.4f};闭式 α = {a8:.4f};"
          f"经验题间平均相关 ≈ {rbar_emp:.4f}(设定 {rbar})")
    assert abs(a_emp - a8) < 0.01, f"经验 α {a_emp:.4f} 与闭式 {a8:.4f} 应差<0.01"
    assert abs(rbar_emp - rbar) < 0.01, f"经验 r̄ {rbar_emp:.4f} 应≈{rbar}"
    print(f"\n✓ 幕三断言通过:α(4)={a4:.4f}≈0.632、α(8)={a8:.4f}≈0.774;"
          f"增量 2→4({d24:.3f})>4→8({d48:.3f});"
          f"达 0.9 需 k=21(r̄=0.3)vs k=9(r̄=0.5);MC 经验 α={a_emp:.4f} 对上闭式解")
    return a4, a8, a_emp


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口(三律):")
    print("  ① 精度账单:SE=σ/√n——样本量翻 4 倍精度只翻 1 倍(MC 互证<5%)")
    print("  ② 设计效应:deff=1+(m−1)ρ——m=20、ρ=0.05 → 1.95,等效样本近乎")
    print("     减半;整群方差比简单随机高约 (m−1)ρ 倍(MC 互证)")
    print("  ③ 信度兑换率:α=kr̄/(1+(k−1)r̄)——加题边际递减(k 2→4→8 增量")
    print("     逐段缩小);到 0.9 需 k=21(r̄=0.30)vs k=9(r̄=0.50)——")
    print("     r̄ 才是信度的第一杠杆:题目间相关烂,加题是饮鸩止渴(MC 互证)")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
