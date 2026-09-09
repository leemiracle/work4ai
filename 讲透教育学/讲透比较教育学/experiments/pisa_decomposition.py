# -*- coding: utf-8 -*-
"""PISA 式分数分解:构成效应/调整翻转/单轮高估三律检验(02/04 章配套实验)。

主题呼应 04 章走廊 1(排名重构走廊):多国学生成绩分解为
  总分 = 基准 500 + 系统效应 s_i + 背景效应×系统缓释度 b_i·SES + 噪声:
  - s_i:教育系统效应(想排的"系统水平",潜变量,排名观察者看不到);
  - SES:家庭背景(各国分布均值不同——生源构成的跨国差异);
  - b_i:各国背景斜率=系统对背景的缓释度(交互项;低 b_i=更"公平"的系统);
  - 噪声:学生层面 N(0,σ_ε);多轮模拟再加"轮间波动" u_it(每轮每国一抽,
    模拟测评轮次的共同冲击与真实波动)。
  五国为虚构国家,参数为风格化取值,不对应任何真实教育体系。

断言三律(比较教育/跨国测评方法论文献通说的结构化):
  A. 简单排名掩盖构成差异:同等系统效应、不同背景分布 → 总分排名不同
     (北洲 vs 中原同 s,SES 均值一正一负,原始分差>40 分、名次差≥2;
     配套:更强系统东屿(s=45)被更弱系统南湾(s=15)在原始榜上压过);
  B. 背景调整后排名与原始排名显著不同("排名领先≠系统有效"的统计结构):
     扣除背景的回归(各国自有截距与斜率=含交互项的完整分解)→
     东屿 3→1、南湾 2→4,Spearman<0.8,最大名次移动≥2,
     而同 s 的北洲-中原调整后差距缩到噪声量级(<8 分);
  C. 单一时点比较高估系统差异:只看一轮时,轮间波动混进"系统差距"——
     ①平均绝对差距被噪声系统性放大(单轮膨胀>1.2×,Jensen:E|d+噪声|≥|d|;
     多轮均值收缩回真值附近 <1.25×,且始终低于单轮);
     ②朴素置信区间(把多轮当独立大样本、只算学生抽样误差)过窄,
     轮间波动入账后系统效应的置信区间展宽 >5×;
     ③"显著差异"国家对数缩水,且真值相同的两国(北洲=中原)在朴素
     区间下被判"显著不同"、诚实区间下不可分。

回归为"各国自有截距+自有斜率"的完全交互模型——设计矩阵按国分块,
等价于每国一个 2×2 最小二乘(真实测评用加权多层模型+合理值,
此处朴素版足以讲清结构)。

⚠ 学科纪律(02/04 章):
  1. 参数为通说量级的风格化取值,不是任何真实测评数据的拟合;
     虚构国名,不针对任何真实国家或体系;
  2. 模拟证明「系统+构成+交互+轮间波动的简单机制足以生成三律」
     (机制充分性),不是对任何真实排名的数量断言;
  3. 通说依据:构成效应与均值比较的误读(测评方法论文献长期批评)、
     排名的测量不确定度与轮间波动、背景调整的方法争论
     (调整口径本身是价值选择)——均为综述级通说,未逐条核数;
  4. 敏感性分析:文末 Monte Carlo(120 次参数抖动)报告三律通过率
     ——换参数重跑=检验结论的结构刚性(04 章的正确用法)。

跑法: python experiments/pisa_decomposition.py
"""

import math
import random
import sys

# ----------------------------- 世界参数(基准情形,虚构五国) -----------------------------
COUNTRIES = ["北洲", "东屿", "中原", "南湾", "西原"]
SYS = [30.0, 45.0, 30.0, 15.0, -20.0]      # 系统效应 s_i(北洲=中原:断言A的同 s 对)
SES_MU = [0.7, -0.6, -0.7, 0.9, 0.0]       # 各国 SES 分布均值(构成差异的来源)
SLOPE = [35.0, 28.0, 35.0, 35.0, 40.0]     # 背景斜率 b_i(系统对背景的缓释度/交互)
BASE = 500.0                                # PISA 式量尺基准
EPS_SD = 25.0                               # 学生层面噪声 σ_ε
SES_SD = 1.0                                # 各国内 SES 波动
WAVE_SHOCK_SD = 25.0                        # 轮间波动 σ_u(每轮每国一抽)
N_CROSS = 250                               # 横截面:每国学生数(断言A/B)
N_WAVES, N_PER_WAVE = 24, 150               # 追踪:24 轮×每国 150(断言C)
Z95 = 1.96


# ----------------------------- 基础件:模拟、回归、排名 -----------------------------
def country_sufficient_stats(students, n_countries):
    """按国累计充分统计量:(n, Σses, Σses², Σy, Σses·y)——分块设计的全部输入。"""
    stats = [[0, 0.0, 0.0, 0.0, 0.0] for _ in range(n_countries)]
    for ci, ses, sc in students:
        st = stats[ci]
        st[0] += 1
        st[1] += ses
        st[2] += ses * ses
        st[3] += sc
        st[4] += ses * sc
    return stats


def fit_adjusted(students, n_countries):
    """完全交互模型的 OLS:每国自有截距(系统效应)与斜率(背景缓释度)。
    各国 2×2 正规方程闭式解:α=(Sy·Sxx−Sxy·Sx)/Δ, β=(n·Sxy−Sx·Sy)/Δ。"""
    effects = []
    for st in country_sufficient_stats(students, n_countries):
        n, sx, sxx, sy, sxy = st
        det = n * sxx - sx * sx
        alpha = (sy * sxx - sxy * sx) / det
        effects.append(alpha)          # 截距=BASE+s_i+u_it 的估计(调整后系统效应)
    return effects


def simulate(rng, params, n_per_country, shocks=None):
    """生成跨国学生数据 [(国, SES, 总分)];shocks=各国轮间波动 u_it(可 None)。"""
    sysv, ses_mu, slope = params["sys"], params["ses_mu"], params["slope"]
    eps_sd = params["eps_sd"]
    data = []
    for ci in range(len(sysv)):
        u = shocks[ci] if shocks is not None else 0.0
        for _ in range(n_per_country):
            ses = rng.gauss(ses_mu[ci], SES_SD)
            score = (BASE + sysv[ci] + slope[ci] * ses + u
                     + rng.gauss(0.0, eps_sd))
            data.append((ci, ses, score))
    return data


def raw_means(students, n_countries):
    means = [0.0] * n_countries
    counts = [0] * n_countries
    for ci, _, sc in students:
        means[ci] += sc
        counts[ci] += 1
    return [m / c for m, c in zip(means, counts)]


def ranks_desc(vals):
    """把数值变成名次(值大名次小);用于排名对比。"""
    order = sorted(range(len(vals)), key=lambda i: -vals[i])
    r = [0] * len(vals)
    for pos, i in enumerate(order):
        r[i] = pos + 1
    return r


def spearman(a, b):
    """Spearman 秩相关(无并列的朴素版,足够本实验用)。"""
    n = len(a)
    ra, rb = ranks_desc(a), ranks_desc(b)
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1.0 - 6.0 * d2 / (n * (n * n - 1))


def pairwise_gaps(vals):
    """所有国家对的(带符号)差距列表 [(i,j,Δ)]。"""
    out = []
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            out.append((i, j, vals[j] - vals[i]))
    return out


def mean_abs_gap(vals):
    return sum(abs(g) for _, _, g in pairwise_gaps(vals)) / len(
        pairwise_gaps(vals))


# ----------------------------- 断言 A/B:横截面(单轮) -----------------------------
def cross_section(rng, params):
    """单轮横截面:原始排名 vs 调整排名;返回三律 A/B 的全部读数。"""
    K = len(params["sys"])
    data = simulate(rng, params, N_CROSS)
    raw = raw_means(data, K)
    adj = fit_adjusted(data, K)
    return {"raw": raw, "adj": adj,
            "raw_ranks": ranks_desc(raw), "adj_ranks": ranks_desc(adj)}


# ----------------------------- 断言 C:多轮追踪 -----------------------------
def tracking(rng, params):
    """多轮(波次)模拟:每轮每国抽轮间波动;返回各轮的调整后系统效应估计。"""
    K = len(params["sys"])
    waves = []
    for _ in range(N_WAVES):
        shocks = [rng.gauss(0.0, params["wave_sd"]) for _ in range(K)]
        data = simulate(rng, params, N_PER_WAVE, shocks)
        waves.append(fit_adjusted(data, K))
    return waves


def ci_statistics(waves, params):
    """C②③ 置信区间与显著性:朴素 vs 诚实。
    朴素:把 W 轮当独立大样本,只算学生抽样误差 σ_ε/√(n·W)——忽略轮间
    聚类(单轮思维的极限版);诚实:从轮间实测波动入账,SE=轮间 SD/√W。"""
    K = len(waves[0])
    naive_se = params["eps_sd"] / math.sqrt(N_PER_WAVE * N_WAVES)
    naive_half = Z95 * naive_se
    track_half = []
    for k in range(K):
        col = [w[k] for w in waves]
        m = sum(col) / len(col)
        var = sum((v - m) ** 2 for v in col) / (len(col) - 1)
        track_half.append(Z95 * math.sqrt(var / len(col)))
    mean_est = [sum(col) / len(col) for col in zip(*waves)]
    naive_thr = Z95 * math.sqrt(2.0) * naive_se
    track_thr = Z95 * math.sqrt(2.0) * (sum(track_half) / len(track_half) / Z95)
    gaps = pairwise_gaps(mean_est)
    sig_naive = sum(1 for _, _, g in gaps if abs(g) > naive_thr)
    sig_track = sum(1 for _, _, g in gaps if abs(g) > track_thr)
    zero_gap = next(g for i, j, g in gaps if (i, j) == (0, 2))   # 北洲-中原
    zero_naive = abs(zero_gap) > naive_thr           # 真值相同的两国
    zero_track = abs(zero_gap) > track_thr
    return {"naive_half": naive_half,
            "track_half": sum(track_half) / len(track_half),
            "sig_naive": sig_naive, "sig_track": sig_track,
            "zero_naive": zero_naive, "zero_track": zero_track}


# ----------------------------- 报告与断言(基准情形) -----------------------------
def base_params():
    return {"sys": SYS[:], "ses_mu": SES_MU[:], "slope": SLOPE[:],
            "eps_sd": EPS_SD, "wave_sd": WAVE_SHOCK_SD}


def main():
    if hasattr(sys.stdout, "reconfigure"):           # Windows 控制台编码防御
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rng = random.Random(20260907)
    K = len(COUNTRIES)

    print("=" * 72)
    print("PISA 式分数分解:构成掩盖/调整翻转/单轮高估三律(虚构五国)")
    print("=" * 72)
    print(f"模型:总分 = {BASE:.0f} + 系统效应 s_i + 缓释斜率 b_i·SES + u(轮) + ε")
    print("国家  系统效应  SES均值  缓释斜率   ← 全部为风格化虚构参数")
    for c, s, m, b in zip(COUNTRIES, SYS, SES_MU, SLOPE):
        print(f"{c}   {s:6.1f}   {m:+5.1f}    {b:4.0f}")

    # ---- 断言 A:简单排名掩盖构成差异 ----
    cs = cross_section(rng, base_params())
    raw, adj = cs["raw"], cs["adj"]
    rr, ar = cs["raw_ranks"], cs["adj_ranks"]
    print(f"\n[断言A 构成掩盖] 同轮横截面(N={N_CROSS}/国)的原始总均值与名次:")
    print("国家  原始分  原名次  调整效应  调名次   真实系统效应")
    for k in range(K):
        print(f"{COUNTRIES[k]}  {raw[k]:6.1f}   {rr[k]}   {adj[k]:7.1f}    {ar[k]}"
              f"      {SYS[k]:+.0f}")
    gap_bm_zy = raw[0] - raw[2]                 # 北洲 vs 中原(同 s=30)
    print(f"\n  同系统效应对(北洲 s=30 vs 中原 s=30,SES 均值 {SES_MU[0]:+.1f}"
          f" vs {SES_MU[2]:+.1f}):")
    print(f"  原始分差 {gap_bm_zy:.1f} 分,名次 {rr[0]} vs {rr[2]}(差 {abs(rr[0]-rr[2])})")
    assert abs(gap_bm_zy) > 40.0, \
        f"断言A失败:同系统效应两国原始分差仅 {gap_bm_zy:.1f} 分"
    assert abs(rr[0] - rr[2]) >= 2, \
        f"断言A失败:同系统效应两国名次差仅 {abs(rr[0]-rr[2])}"
    assert rr[1] > rr[3], "配套观察失败:更强系统(东屿)未被更弱系统(南湾)压过"
    print("  ✓ 同等系统效应、不同背景分布 → 总分与名次大不相同;"
          "原始榜读作系统优劣,读的其实是生源构成")
    print(f"  ✓ 配套:更强系统东屿(s=45)原始榜第 {rr[1]},被更弱系统南湾(s=15)"
          f"第 {rr[3]} 压过——构成可以把系统差异整体倒置")

    # ---- 断言 B:调整后排名显著不同 ----
    rho = spearman(raw, adj)
    moves = [abs(a - b) for a, b in zip(rr, ar)]
    adj_gap_bm_zy = adj[0] - adj[2]
    print(f"\n[断言B 调整翻转] 扣除背景的回归(各国自有截距+斜率)后的调整名次:")
    print(f"  名次移动:东屿 {rr[1]}→{ar[1]},南湾 {rr[3]}→{ar[3]},"
          f"北洲 {rr[0]}→{ar[0]},中原 {rr[2]}→{ar[2]},西原 {rr[4]}→{ar[4]}")
    print(f"  最大名次移动 {max(moves)};Spearman(原始,调整) = {rho:.2f};"
          f"同 s 对(北洲-中原)调整后差距 {adj_gap_bm_zy:+.1f} 分(噪声量级)")
    assert ar[1] == 1, "断言B失败:调整后榜首不是真实最强系统(东屿)"
    assert max(moves) >= 2, "断言B失败:最大名次移动<2"
    assert rho < 0.8, f"断言B失败:原始与调整排名过于一致(ρ={rho:.2f})"
    assert abs(adj_gap_bm_zy) < 8.0, \
        f"断言B失败:同系统效应对调整后差距仍达 {adj_gap_bm_zy:.1f} 分"
    print("  ✓ 背景调整后,系统最强者(东屿)登顶、构成最富者(南湾)跌出前列"
          "——『排名领先≠系统有效』的统计结构")
    print("  ✓ 同 s 对调整后差距缩回噪声量级:调整还了系统效应一个公平读数"
          "(但调整口径本身是价值选择,02 章彩蛋)")

    # ---- 断言 C:单一时点高估系统差异 ----
    waves = tracking(rng, base_params())
    true_mag = mean_abs_gap(SYS)
    single_mag = sum(mean_abs_gap(w) for w in waves) / N_WAVES
    mean_est = [sum(col) / len(col) for col in zip(*waves)]
    multi_mag = mean_abs_gap(mean_est)
    inf_single = single_mag / true_mag
    inf_multi = multi_mag / true_mag
    ci = ci_statistics(waves, base_params())
    print(f"\n[断言C 单轮高估] {N_WAVES} 轮追踪(每轮每国冲击 σ_u={WAVE_SHOCK_SD}):")
    print(f"  真实平均绝对差距 {true_mag:.1f} 分(10 国对)")
    print(f"  单轮视角(每轮单看再平均):{single_mag:.1f} 分"
          f"(膨胀 {inf_single:.2f}×)")
    print(f"  多轮均值视角:{multi_mag:.1f} 分(膨胀 {inf_multi:.2f}×)")
    assert inf_single > 1.2, \
        f"C①失败:单轮差距膨胀仅 {inf_single:.2f}×"
    assert inf_multi < 1.25, \
        f"C①失败:多轮均值膨胀仍达 {inf_multi:.2f}×"
    assert single_mag > multi_mag, "C①失败:单轮未比多轮更夸大差距"
    print("  ✓ 轮间波动混进单轮差距,平均绝对差距被系统性放大"
          "(噪声让差距『看起来更大』);多轮均值把噪声除掉√T,收缩回真值附近")
    ratio = ci["track_half"] / ci["naive_half"]
    print(f"\n  置信区间:朴素(把 {N_WAVES} 轮当独立大样本,只算学生抽样误差)"
          f"半宽 {ci['naive_half']:.2f} 分")
    print(f"            vs 诚实(轮间波动入账)半宽 {ci['track_half']:.1f} 分"
          f"(展宽 ×{ratio:.0f})")
    print(f"  『显著差异』国家对数:朴素 {ci['sig_naive']}/10 对 vs"
          f" 诚实 {ci['sig_track']}/10 对")
    assert ratio > 5.0, f"C②失败:置信区间仅展宽 ×{ratio:.1f}"
    assert ci["sig_track"] < ci["sig_naive"], \
        f"C③失败:诚实区间下显著对数未缩水({ci['sig_track']} vs {ci['sig_naive']})"
    assert ci["zero_naive"] and not ci["zero_track"], \
        "C③失败:真值相同的两国未被朴素区间误判为显著不同"
    print(f"  ✓ 单轮思维只算抽样误差,区间过窄、『显著差异』满天飞——"
          f"连真实系统效应完全相同的两国(北洲=中原)都被判『显著不同』"
          f"(朴素 {ci['zero_naive']},诚实 {ci['zero_track']});")
    print("  轮间波动入账后系统效应的置信区间展宽约一个量级,边际差距"
          "(与诚实区间同量级的那部分)开始降级为『不可分』"
          "——单轮排名的确定性是错觉")

    # ---- Monte Carlo 敏感性分析 ----
    print("\n" + "=" * 72)
    print(f"Monte Carlo 敏感性分析:120 次参数抖动(系统/SES/斜率±15%;"
          f"σ_ε∈[20,30];σ_u∈[22,34])")
    n_draws, need = 120, 0.85
    passes = {"A 构成掩盖": 0, "B 调整翻转": 0, "C 单轮高估": 0}
    for _ in range(n_draws):
        def jit(x, lo=0.85, hi=1.15):
            return x * rng.uniform(lo, hi)
        sysv = [jit(s) for s in SYS]
        sysv[2] = sysv[0]                      # 保持"同系统效应对"前提
        params = {"sys": sysv,
                  "ses_mu": [jit(m) for m in SES_MU],
                  "slope": [jit(b) for b in SLOPE],
                  "eps_sd": rng.uniform(20.0, 30.0),
                  "wave_sd": rng.uniform(22.0, 34.0)}
        cs_j = cross_section(rng, params)
        ok_a = (abs(cs_j["raw"][0] - cs_j["raw"][2]) > 25.0
                and abs(cs_j["raw_ranks"][0] - cs_j["raw_ranks"][2]) >= 2)
        rho_j = spearman(cs_j["raw"], cs_j["adj"])
        moves_j = [abs(a - b) for a, b in
                   zip(cs_j["raw_ranks"], cs_j["adj_ranks"])]
        ok_b = rho_j < 0.85 and max(moves_j) >= 2
        waves_j = tracking(rng, params)
        gs_single = sum(mean_abs_gap(w) for w in waves_j) / N_WAVES
        gs_true = mean_abs_gap(params["sys"])
        mean_est_j = [sum(col) / len(col) for col in zip(*waves_j)]
        gs_multi = mean_abs_gap(mean_est_j)
        ci_j = ci_statistics(waves_j, params)
        ok_c = ((gs_single / gs_true) > 1.12
                and gs_multi < gs_single
                and (ci_j["track_half"] / ci_j["naive_half"]) > 4.0
                and ci_j["sig_track"] < ci_j["sig_naive"])
        passes["A 构成掩盖"] += ok_a
        passes["B 调整翻转"] += ok_b
        passes["C 单轮高估"] += ok_c
    for law, cnt in passes.items():
        rate = cnt / n_draws
        print(f"  {law}律通过率 {rate:.0%}")
        assert rate >= need, f"{law}律在参数抖动下不稳定({rate:.0%} < {need:.0%})"

    print("\n⚠ 学科纪律提醒:本模拟证明『系统+构成+交互+轮间波动的简单机制")
    print("  足以生成三律』,不是任何真实测评排名的数量断言;国名与参数全为虚构。")
    print("  真实读数还需:入学率与被测总体的口径(02 章口径三问)、题目跨国")
    print("  功能等价(DIF)、调整口径的价值选择——把缓释斜率 b_i 改成政策变量、")
    print("  把轮间冲击改成自相关,是使用本脚本的正确姿势(04 章 §三落点)。")


if __name__ == "__main__":
    main()
