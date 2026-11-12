# -*- coding: utf-8 -*-
"""断代的定量检验(教学版):知识生产模拟序列、分段趋势拟合与换锚敏感性。

00 章 §四假设一(断代即史观)+ 04 章 C1(断代定量检验走廊)的配套实验。

构造两条模拟序列(1665-2020,种子固定可复现;覆盖"科学革命/学院化/
大科学"三节点所需的最短窗口——截取任一两百年窗口断裂结构不完整):
  A 科学出版物年产量——指数增长+三节点增速跳变+对数正态噪声
  B 学会成立年数——分段强度泊松计数
三个断代节点(增速结构断点,叙事锚=通说事件):
  1687 牛顿《原理》——科学革命段合拢(期刊-学会体制成型,1665 Phil.
     Trans. 创刊为序列起点)
  1832 学院化——柏林大学 1810 之后的实验室革命与专业科学体制成型
     (BAAS 1831/惠威尔造词 scientist 1833)
  1945 大科学——战时动员转平时建制(Bush 报告→NSF 1950)
增速段标定到 Price 式指数增长直觉(《小科学,大科学》1963:科学文献
十余年翻一番);节点间用 ±15 年线性过渡——历史断点从来不是一夜跳变。

三组断言(04 章 C1 走廊的教学版结论):
  ① 断代有统计收益:三断点分段趋势拟合的总残差平方(SSE)显著小于
    单一趋势拟合——"切时代"在数据上有收益
  ② 换锚敏感性:断点整体移动 ±15 年,拟合收益保留(>80%)——断代
    作为一种分割是稳健的;但窗口内 SSE 曲线近乎平坦(起伏 <总收益
    的 5%),叙事年与数据最优年统计上不可区分——精确到年的断点
    叙事不稳健(断点年=叙事构造;呼应 BJHS 1993→2024"大图景
    叙事为何困难"圆桌母题,01 章热线一)
  ③ 双代理同向:三节点之后学会成立速率均显著高于之前——两条独立
    代理序列对同一断代给出同向证据

⚠ 史学纪律:本实验数据是模拟的教学版(参数标定到通说直觉,非实测
数据库);它检验的是"断代方法论的统计性质",不产出任何历史结论。
真实数据的走廊见 04 章 C2/C3;真实量化研究的样板见 01 章热线五
(Nature HSSC 2025:350+ 学科领域起源)。

跑法: python experiments/periodization_bursts.py
"""

import math
import random

SPAN = (1665, 2020)                              # 起=Phil. Trans. 创刊
NODES = [1687, 1832, 1945]                       # 三断代节点(叙事锚)
NODE_LABELS = ["科学革命(原理 1687)", "学院化(实验室革命 1830s)", "大科学(1945 建制化)"]
RAMP = 15                                        # 节点过渡带宽(年)
SEG_RATES = [0.010, 0.022, 0.030, 0.055]         # 各段对数年增速(教学版标定)
BASE_1665 = 40.0                                 # 起点年出版量(模拟)
NOISE_SIGMA = 0.08                               # 对数尺度噪声
SEED_PUB = 20260907                              # 出版物序列种子
SEG_LAMBDAS = [0.5, 1.0, 2.4, 6.0]               # 学会成立泊松强度(段均值)
SEED_SOC = 19621963                              # 学会序列种子(结构年致敬)


def seg_interp(t, values, nodes, ramp):
    """分段常值+节点±ramp 线性过渡:t 年所在段位的插值(增速/强度共用)。"""
    i = 0
    for k in nodes:
        if t > k + ramp:
            i += 1
    if i >= len(nodes):
        return values[-1]
    if t <= nodes[i] - ramp:
        return values[i]
    frac = (t - (nodes[i] - ramp)) / (2.0 * ramp)
    frac = min(max(frac, 0.0), 1.0)
    return values[i] + (values[i + 1] - values[i]) * frac


def gen_publications():
    """序列 A:年出版量。对数水平按增速梯形积分,叠加对数正态噪声。"""
    rng = random.Random(SEED_PUB)
    years = list(range(SPAN[0], SPAN[1] + 1))
    counts, logy = [], []
    log_level, prev_r = math.log(BASE_1665), None
    for t in years:
        r = seg_interp(t, SEG_RATES, NODES, RAMP)
        if prev_r is not None:
            log_level += (r + prev_r) / 2.0
        prev_r = r
        noisy = log_level + rng.gauss(0.0, NOISE_SIGMA)
        counts.append(round(math.exp(noisy)))
        logy.append(math.log(max(counts[-1], 1)))
    return years, counts, logy


def gen_societies():
    """序列 B:年学会成立数。泊松计数,强度与增速段同步跳变。"""
    rng = random.Random(SEED_SOC)
    foundings = {}
    for t in range(SPAN[0], SPAN[1] + 1):
        lam = seg_interp(t, SEG_LAMBDAS, NODES, RAMP)
        L, k, p = math.exp(-lam), 0, 1.0
        while True:
            p *= rng.random()
            if p <= L:
                break
            k += 1
        foundings[t] = k
    return foundings


def solve_normal(cols, y):
    """最小二乘:解 (A^T A)x = A^T y。高斯消元+部分主元,纯标准库。"""
    m, n = len(cols), len(y)
    M = [[sum(cols[i][r] * cols[j][r] for r in range(n)) for j in range(m)] +
         [sum(cols[i][r] * y[r] for r in range(n))] for i in range(m)]
    for c in range(m):
        piv = max(range(c, m), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        for r in range(c + 1, m):
            f = M[r][c] / M[c][c]
            for cc in range(c, m + 1):
                M[r][cc] -= f * M[c][cc]
    x = [0.0] * m
    for r in range(m - 1, -1, -1):
        s = M[r][m] - sum(M[r][c] * x[c] for c in range(r + 1, m))
        x[r] = s / M[r][r]
    return x


def sse_of(cols, y, x):
    """残差平方和。"""
    tot = 0.0
    for r in range(len(y)):
        pred = sum(cols[i][r] * x[i] for i in range(len(x)))
        tot += (y[r] - pred) ** 2
    return tot


def fit_single(years, logy):
    """单一趋势:log y ~ a + b·t(Price 式单指数,2 参数)。"""
    ones = [1.0] * len(years)
    tc = [float(t - 1900) for t in years]
    x = solve_normal([ones, tc], logy)
    return sse_of([ones, tc], logy, x), x


def fit_piecewise(years, logy, knots):
    """分段趋势:连续折线,log y ~ a + b·t + Σ c·relu(t-k)(2+|knots| 参数)。"""
    ones = [1.0] * len(years)
    tc = [float(t - 1900) for t in years]
    cols = [ones, tc] + [[max(0.0, t - k) for t in years] for k in knots]
    x = solve_normal(cols, logy)
    return sse_of(cols, logy, x), x


def fitted_slope(x, t):
    """折线拟合在 t 年的斜率 = b + Σ(过了的节点贡献)。"""
    s = x[1]
    for j, k in enumerate(NODES):
        if t > k:
            s += x[2 + j]
    return s


def main():
    print("=" * 76)
    print("断代的定量检验(教学版):知识生产模拟序列 1665-2020(356 年)")
    print("=" * 76)

    years, counts, logy = gen_publications()
    for probe in (1665, 1687, 1832, 1945, 2020):
        print(f"  {probe} 年:模拟出版量 ≈ {counts[probe - SPAN[0]]:>9,} 种"
              f"(对数 {math.log(counts[probe - SPAN[0]]):.2f})")
    print("  增速段(标定值):" + " → ".join(f"{r*100:.1f}%/年" for r in SEG_RATES)
          + "(节点 ±15 年线性过渡)")

    # ── 断言 ①:断代有统计收益(分段 SSE 显著小于单一趋势)──────────
    sse_single, x_single = fit_single(years, logy)
    sse_narr, x_pw = fit_piecewise(years, logy, NODES)
    ratio = sse_narr / sse_single
    print(f"\n单一趋势拟合 SSE  = {sse_single:9.3f}(单指数,2 参数,"
          f"斜率 {x_single[1]:.4f}/年)")
    print(f"三断点分段拟合 SSE = {sse_narr:9.3f}(连续折线,5 参数)→ "
          f"残差降至 {ratio:.1%}")
    assert sse_narr < 0.5 * sse_single, "断代统计收益:分段 SSE 应显著小于单一趋势"
    print("断言 ① 通过:断代有统计收益——'切时代'把残差砍掉一半以上 ✓")

    # 分段斜率(断代买到的可解释性:每段一个增速)
    probes = [1680, 1800, 1900, 2000]
    slopes = [fitted_slope(x_pw, t) for t in probes]
    print("\n分段拟合斜率(断代买到的可解释性):")
    for t, s in zip(probes, slopes):
        print(f"  探针年 {t}:增速 ≈ {s:.4f}/年(倍增期 ≈ {math.log(2)/s:5.1f} 年)"
              f"  [Price 1963:现代科学十余年翻一番]")
    assert all(a < b for a, b in zip(slopes, slopes[1:])), "增速应逐段抬升"
    print("          ——增速逐段抬升 ✓(通史版加速律:知识生产增速结构向上)")

    # ── 断言 ②:换锚敏感性(±15 年扫描)──────────────────────────
    print("\n换锚敏感性:三断点整体平移,重拟合")
    print(f"  {'平移':>5} {'断点年组':<22} {'SSE':>8} {'保留收益':>8}")
    scan = {}
    for d in range(-15, 16, 5):
        knots = [k + d for k in NODES]
        s, _ = fit_piecewise(years, logy, knots)
        scan[d] = s
        kept = (sse_single - s) / (sse_single - sse_narr)
        print(f"  {d:>+5} {str(knots):<22} {s:>8.3f} {kept:>8.1%}")
    gain_full = sse_single - sse_narr
    for d, s in scan.items():
        assert (sse_single - s) > 0.8 * gain_full, \
            f"换锚 ±15 内拟合收益应保留(平移 {d} 失败)"
    flat = max(scan.values()) - min(scan.values())
    best_d = min(scan, key=scan.get)
    assert flat < 0.05 * gain_full, "窗口内起伏应远小于断代总收益"
    print(f"断言 ② 通过:断代稳健,断点年不稳健 ✓")
    print(f"  ②a 收益保留:窗口内所有平移保留 >80% 的断代收益——'切三段'")
    print(f"     这个分割本身对 ±15 年的锚移动不敏感(断代稳健)")
    print(f"  ②b 精确年不稳健:窗口内 SSE 起伏仅 {flat:.3f}"
          f"(总收益的 {flat/gain_full:.1%});本种子")
    print(f"     数据最优平移 {best_d:+d} 年——1687 与 1682 在统计上"
          f"不可区分;")
    print("     教科书'1687 年转折'的年份精度是叙事构造,不是数据输出")

    # ── 断言 ③:双代理同向(学会成立速率三节点前后)────────────────
    foundings = gen_societies()
    print("\n双代理检验:学会成立速率(独立种子)在三节点前后")
    ok3 = True
    for k, label in zip(NODES, NODE_LABELS):
        # 前窗起点不越过序列起点(首节点前窗自动截短为 1665 起)
        pre = [foundings[t] for t in range(max(SPAN[0], k - 35), k - 4)]
        post = [foundings[t] for t in range(k + 5, k + 36)]
        m_pre, m_post = sum(pre) / len(pre), sum(post) / len(post)
        ok3 = ok3 and m_post > 1.25 * m_pre
        print(f"  {label}:节点前 30 年均值 {m_pre:.2f} 家/年 → "
              f"节点后 {m_post:.2f} 家/年(×{m_post/m_pre:.1f})")
    assert ok3, "三节点之后学会成立速率应显著高于之前"
    total_soc = sum(foundings.values())
    print(f"断言 ③ 通过:双代理同向 ✓(全期学会成立共 {total_soc} 家——"
          f"出版物与")
    print("  学会成立两条独立模拟序列对同一断代给出同向证据;真实研究中"
          "双代理")
    print("  同向是断代合法性的最低证据标准,单代理断代默认存疑")

    print("\n" + "=" * 76)
    print("三组断言全部通过:断代统计收益 / 换锚稳健而断点年不稳健 / 双代理同向 ✓")
    print("\n⚠ 史学纪律提醒:本脚本数据为教学版模拟(参数标定到通说直觉);")
    print("  它演示的是断代方法论的统计性质——①断代有收益②精确断点年是")
    print("  叙事构造③单代理不足信——不产出任何历史结论。真实数据的断代")
    print("  检验须:换真实数据库重跑+代理指标声明(出版量≠知识量)+选样")
    print("  声明(04 章 §5 换锚重跑是使用断代的正确姿势)。")


if __name__ == "__main__":
    main()
