# -*- coding: utf-8 -*-
"""宣言脉冲-加冕双通道-奖项级联三律模拟:法国文学家族实验(GB/T 75061)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(三条结构引擎的
严格可构造性)、04-法国文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260907 可复现。

风格化声明:运动参数、网络规模、奖项序列均为机制研究用的风格化设定,
断言针对"机制模式"(先升后降/两路加冕/级联趋避),不是史实拟合;
作家作品评述一律通说文学史口径(宣言年份按通说)。

三幕:
  幕一 宣言脉冲的兴衰(宣言驱动的文学运动):
      法国文学的流派多以宣言开局(1886 象征主义宣言/1924 超现实主义宣言/
      1950-58 新小说檄文,通说)。凝聚力=各次宣言脉冲的叠加:
      I(s)=A·(s/τ)·exp(1−s/τ)(s=距宣言年数),每条脉冲在 s=τ 处达峰后衰减;
      宣言越多(k 越大),单条脉冲的衰减时标越短 τ=τ0/(1+0.85(k−1)),
      且后续宣言振幅递减(0.85·0.45^i)——多宣言=内部分裂的信号。
      断言:①宣言后运动凝聚力先升后降(经典 S+衰退):平滑曲线上升开局、
              峰值年落在窗口前 1/4、高原期(≥峰值 85%)跨度≤8 年、
              窗口后 1/3 全面跌破峰值 35%(衰退不可逆)、且半衰期长于
              半升期(衰退比爬升缓)——一条运动的完整生命周期
            ②宣言产量高的运动生命周期更短:寿命(平滑凝聚力≥0.30 的末年)
              按 k 分组均值严格递减,Pearson r(k,寿命)≤−0.90——
              宣言是运动的起跑枪也是解散令。
  幕二 文学与理论的共生网络(作家-理论家二部网络):
      理论家为作家提供概念资本(连接按优先连接 ∝ 度数,概念资本随理论家
      度数增长),作家为理论家提供分析对象;正典化概率
      P=sigmoid(β0+βq·q+βC·C+βP·prize)——理论资本与奖项是两条可替代通道。
      断言:①高度数理论家连接的作家形成"经典簇"(正典化共振):同连顶级
              理论家的作家对共同正典率 ≥ 无共享理论家对的 2.2 倍
            ②无理论中介的作家更依赖奖项通道进入正典:正典化的无理论作家
              中获奖率显著高于有理论作家(差≥0.12),且纯理论(无奖)正典率
              ≥ 纯天赋(无奖无理论)的 2.5 倍——法国式的正典化有两条路:
              理论加冕与奖项加冕。
  幕三 奖项场域的级联(十月-十一月 cascade):
      每年秋季五大奖(龚古尔/雷诺多/费米娜/梅迪西/联盟,位次 1-5,通说序列)
      依时间先后颁出;候选书 14 种带评审吸引力;级联模型:后续奖项在
      评分上对当年已获奖图书扣分 δ(差异化默契),独立基线:各奖独立取最优。
      获奖销量脉冲=P0·ρ^(位次−1)(龚古尔效应量级为构造值)。
      断言:①评审趋避:级联模型"龚古尔得主同年再获后续大奖"的年份率远低于
              独立基线(≤0.10 vs ≥0.75,联合概率<基线的 0.15 倍);任一重复
              年率同步大降——差异化默契是准绳不是法律(默契破例仍偶发双奖)
            ②销量脉冲随奖项序列位次递减:位次 1→5 严格单调降,头两位
              (龚古尔+雷诺多)捕获总脉冲 ≥0.78,位次 1 ≥ 位次 3 的 3 倍——
              法国文学奖是十一月的天气预报,头几个风标决定整个冬季。

跑法: python -u experiments/manifesto_field_cascade.py
"""

import math
import random
import statistics

SEED = 20260907  # 检索校准日作种子,可复现

# ==================== 幕一:宣言脉冲的兴衰 ====================

# 运动×宣言年(建派年=首宣言年;宣言年份按通说,动力学参数为风格化构造)
MOVES = [
    # (名称,               建派年, 宣言相对年 offsets, 旗手备注)
    ("帕尔纳斯派", 1866, (0,),              "1866《当代帕尔纳斯》创刊集结(通说)"),
    ("象征主义",   1886, (0, 5),            "1886 莫雷亚斯宣言;1891 另立罗马派(通说)"),
    ("乌力波",     1960, (0, 3),            "1960 建派;后续纲领文选(通说)"),
    ("超现实主义", 1924, (0, 5, 18),        "1924/1929 宣言;1942 三次宣言前言(通说)"),
    ("新小说",     1950, (0, 6, 8),         "1950 萨洛特/1956-58 罗伯-格里耶(通说)"),
]
TAU0 = 6.5      # 单宣言运动的脉冲衰减时标(年)
K_SPLIT = 0.85  # 每多一次宣言,时标压缩系数(内部分裂信号)
A0 = 0.85       # 首宣言振幅
DECAY_I = 0.45  # 后续宣言振幅衰减率
TH_C = 0.30     # 凝聚力阈值(低于即视为运动消散)
HORIZON = 46    # 观测窗口(年)


def impulse(s, tau, amp):
    """单次宣言脉冲: s=距宣言年数, 峰值在 s=tau 处(经典 S+衰退核)。"""
    if s < 0:
        return 0.0
    x = s / tau
    return amp * x * math.exp(1.0 - x)


def cohesion_series(offsets, rng):
    """运动凝聚力年序列=各宣言脉冲叠加+±3% 噪声。"""
    k = len(offsets)
    taus = [TAU0 / (1.0 + K_SPLIT * (k - 1))] * k
    amps = [A0 * (DECAY_I ** i) for i in range(k)]
    series = []
    for t in range(HORIZON):
        c = sum(impulse(t - off, tau, amp)
                for off, tau, amp in zip(offsets, taus, amps))
        series.append(max(0.0, c * rng.uniform(0.97, 1.03)))
    return series


def smooth(xs, w=5):
    """宽度 w 的滑动平均(滤掉年度噪声与脉冲交叠的小鼓包)。"""
    out = []
    for i in range(len(xs)):
        lo, hi = max(0, i - w // 2), min(len(xs), i + w // 2 + 1)
        out.append(statistics.mean(xs[lo:hi]))
    return out


def act1():
    print("=" * 84)
    print("幕一 宣言脉冲的兴衰: I(s)=A·(s/τ)·e^(1−s/τ), τ=6.5/(1+0.85(k−1)), 后续振幅×0.45")
    print("=" * 84)
    rng = random.Random(SEED)
    print(f"\n{'运动':<8} {'k':>2} {'τ':>5} {'峰值':>6} {'峰值年':>6} {'高原期':>6} "
          f"{'寿命':>5}   备注")
    results = []
    for name, founding, offsets, note in MOVES:
        k = len(offsets)
        raw = cohesion_series(offsets, rng)
        sm = smooth(raw)
        gmax = max(sm)
        t_peak = sm.index(gmax)
        plateau = [t for t, c in enumerate(sm) if c >= 0.85 * gmax]
        span = max(plateau) - min(plateau)
        life = max(t for t, c in enumerate(sm) if c >= TH_C)
        rise_half = next(t for t, c in enumerate(sm) if c >= 0.5 * gmax)
        fall_half = next(t for t in range(t_peak, HORIZON)
                         if sm[t] <= 0.5 * gmax)
        results.append({"name": name, "k": k, "life": life})
        tau = TAU0 / (1.0 + K_SPLIT * (k - 1))
        print(f"{name:<8} {k:>2} {tau:>5.1f} {gmax:>6.2f} {t_peak:>6} "
              f"{span:>4}年 {life:>5}   {note}")
        # 断言 1: 先升后降(经典 S+衰退 的五项形状检查)
        assert sm[2] > sm[0], f"{name}: 宣言后凝聚力应上升(起跑枪)"
        assert t_peak <= HORIZON // 4, f"{name}: 峰值年应落在窗口前 1/4"
        assert span <= 8, f"{name}: 高原期跨度应≤8 年, 实测 {span}"
        assert max(sm[2 * HORIZON // 3:]) < 0.35 * gmax, \
            f"{name}: 窗口后 1/3 应跌破峰值 35%(衰退不可逆)"
        assert fall_half - t_peak > t_peak - rise_half, \
            f"{name}: 半衰期应长于半升期(衰退比爬升缓)"

    # 断言 2: 宣言越多, 寿命越短
    ks = [r["k"] for r in results]
    lifes = [r["life"] for r in results]
    mk, ml = statistics.mean(ks), statistics.mean(lifes)
    cov = sum((a - mk) * (b - ml) for a, b in zip(ks, lifes))
    sk = math.sqrt(sum((a - mk) ** 2 for a in ks))
    sl = math.sqrt(sum((b - ml) ** 2 for b in lifes))
    r_kl = cov / (sk * sl)
    life_by_k = {}
    for r in results:
        life_by_k.setdefault(r["k"], []).append(r["life"])
    print("\n按宣言数分组(寿命=平滑凝聚力≥0.30 的末年, 建派年计 0):")
    for k in sorted(life_by_k):
        print(f"  k={k}: 寿命 {life_by_k[k]} (均值 {statistics.mean(life_by_k[k]):.1f} 年)")
    print(f"  Pearson r(k, 寿命) = {r_kl:.3f}")
    print("读数:")
    print("  · 每次新宣言都把脉冲时标压缩一档(τ: 6.5→3.5→2.4)——宣言越多,")
    print("    运动越像连续起跑, 旧脉冲越快耗尽")
    print("  · 后续宣言振幅只剩 0.45^i: 二次宣言是分裂的信号, 不是再生的燃料")
    assert r_kl <= -0.90, f"r(k,寿命) 应≤−0.90, 实测 {r_kl:.3f}"
    means_by_k = [statistics.mean(life_by_k[k]) for k in sorted(life_by_k)]
    assert all(means_by_k[i] > means_by_k[i + 1]
               for i in range(len(means_by_k) - 1)), \
        "寿命分组均值应随 k 严格递减"
    print("\n✓ 幕一断言通过: S+衰退形状五项全过+宣言越多寿命越短"
          f"(分组均值 {means_by_k[0]:.1f}→{'→'.join(f'{m:.1f}' for m in means_by_k[1:])}, "
          f"r={r_kl:.2f})——宣言是运动的起跑枪也是解散令")


# ==================== 幕二:作家-理论家共生网络 ====================

N_AUTHORS = 24
N_THEORISTS = 8
N_MC = 4000     # 蒙特卡洛场次数
B0, BQ, BC, BP = -2.8, 2.0, 2.4, 1.6   # 正典化 logits: 截距/质量/理论资本/奖项


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def one_field(rng):
    """生成一个文学场: 24 作家×质量×理论链接(优先连接)×奖项, 返回记录。"""
    links = [set() for _ in range(N_AUTHORS)]
    degree = [0] * N_THEORISTS
    recs = []
    for i in range(N_AUTHORS):
        q = rng.random()                       # 作品质量(风格化)
        # 理论链接: 概率 0.55 获得 1-2 个理论家, 按度数优先连接(概念资本集中)
        if rng.random() < 0.55:
            n_link = 1 + (1 if rng.random() < 0.35 else 0)
            for _ in range(n_link):
                weights = [d + 1 for d in degree]
                tot = sum(weights)
                pick, acc = 0, rng.random() * tot
                for j, w in enumerate(weights):
                    acc -= w
                    if acc <= 0:
                        pick = j
                        break
                links[i].add(pick)
                degree[pick] += 1
        prize = rng.random() < min(0.50, 0.12 + 0.38 * q)   # 奖项通道(随质量开)
        recs.append({"q": q, "links": links[i], "prize": prize})
    # 概念资本=所连理论家的最终度数之和(归一)
    for r in recs:
        r["C"] = min(1.0, sum(degree[j] for j in r["links"]) / 3.0)
    return recs, degree


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 作家-理论家共生网络: {N_AUTHORS}作家×{N_THEORISTS}理论家, "
          f"{N_MC} 个文学场(优先连接;P(正典)=σ(−2.8+2.0q+2.4C+1.6奖))")
    print("=" * 84)
    rng = random.Random(SEED)

    n_pairs_same_top = n_canon_same_top = 0
    n_pairs_far = n_canon_far = 0
    cnt = {"c_noT": 0, "c_noT_prize": 0, "c_T": 0, "c_T_prize": 0,
           "n_noT": 0, "n_noT_noprize_canon": 0, "n_T": 0, "n_T_noprize_canon": 0,
           "n_noT_noprize": 0, "n_T_noprize": 0,
           "n_canon": 0, "n_canon_prize": 0}
    deg_top_cnt = [0] * N_THEORISTS

    for _ in range(N_MC):
        recs, degree = one_field(rng)
        top2 = sorted(range(N_THEORISTS), key=lambda j: -degree[j])[:2]
        for j in top2:
            deg_top_cnt[j] += 1
        canon = []
        for i, r in enumerate(recs):
            p = sigmoid(B0 + BQ * r["q"] + BC * r["C"] + BP * r["prize"])
            c = rng.random() < p
            canon.append(c)
            cnt["n_canon"] += c
            cnt["n_canon_prize"] += c and r["prize"]
            if r["C"] > 0:
                cnt["n_T"] += 1
                cnt["c_T"] += c
                cnt["c_T_prize"] += c and r["prize"]
                cnt["n_T_noprize"] += not r["prize"]
                cnt["n_T_noprize_canon"] += (not r["prize"]) and c
            else:
                cnt["n_noT"] += 1
                cnt["c_noT"] += c
                cnt["c_noT_prize"] += c and r["prize"]
                cnt["n_noT_noprize"] += not r["prize"]
                cnt["n_noT_noprize_canon"] += (not r["prize"]) and c
        # 经典簇共振: 同连顶级理论家的作家对 vs 无共享理论家的作家对
        for a in range(N_AUTHORS):
            for b in range(a + 1, N_AUTHORS):
                same_top = bool(recs[a]["links"] & recs[b]["links"] & set(top2))
                if same_top:
                    n_pairs_same_top += 1
                    n_canon_same_top += canon[a] and canon[b]
                elif not (recs[a]["links"] & recs[b]["links"]):
                    n_pairs_far += 1
                    n_canon_far += canon[a] and canon[b]

    pair_rate_top = n_canon_same_top / n_pairs_same_top
    pair_rate_far = n_canon_far / n_pairs_far
    print(f"\n理论家度数分布(被列入 top2 的次数): {deg_top_cnt}")
    print("  → 概念资本高度集中: 少数理论家垄断'加冕通道'(优先连接的马太效应)")
    print(f"\n[2a] 经典簇共振(共同正典率):")
    print(f"  同连顶级理论家的作家对: {pair_rate_top:.3f} ({n_pairs_same_top} 对)")
    print(f"  无共享理论家的作家对:   {pair_rate_far:.3f} ({n_pairs_far} 对)")
    print(f"  共振比 = {pair_rate_top / pair_rate_far:.2f}×")

    p_canon_T = cnt["c_T"] / cnt["n_T"]
    p_canon_noT = cnt["c_noT"] / cnt["n_noT"]
    prize_rate_canon_T = cnt["c_T_prize"] / cnt["c_T"]
    prize_rate_canon_noT = cnt["c_noT_prize"] / cnt["c_noT"]
    p_theory_noprize = cnt["n_T_noprize_canon"] / cnt["n_T_noprize"]
    p_noT_noprize = cnt["n_noT_noprize_canon"] / cnt["n_noT_noprize"]

    print(f"\n[2b] 两条加冕通道(正典化率):")
    print(f"  有理论中介作家: {p_canon_T:.3f}   无理论中介作家: {p_canon_noT:.3f}")
    print(f"  正典化作家中的获奖率: 有理论 {prize_rate_canon_T:.3f} vs "
          f"无理论 {prize_rate_canon_noT:.3f}")
    print(f"  无奖通道的正典化率: 纯理论(有C无奖) {p_theory_noprize:.3f} vs "
          f"纯天赋(无C无奖) {p_noT_noprize:.3f}")
    print("读数:")
    print("  · 无理论中介而正典化的作家, 获奖率显著更高——他们靠奖项补票上车")
    print("  · 有理论中介的作家即使无奖, 正典化率仍数倍于纯天赋组——理论加冕")
    print("    是独立于奖项的第二通道(萨特式-巴特式加冕的算术版)")

    assert pair_rate_top >= 2.2 * pair_rate_far, \
        f"经典簇共振比应≥2.2×, 实测 {pair_rate_top / pair_rate_far:.2f}"
    assert prize_rate_canon_noT - prize_rate_canon_T >= 0.12, \
        "无理论正典作家应显著更依赖奖项通道(差≥0.12)"
    assert p_theory_noprize >= 2.5 * p_noT_noprize, \
        "纯理论通道正典化率应≥纯天赋的 2.5 倍"
    assert p_canon_T >= 2.0 * p_canon_noT, "理论中介应总体抬高正典化率"
    print(f"\n✓ 幕二断言通过: 共振比 {pair_rate_top / pair_rate_far:.1f}×; "
          f"奖项依赖差 {prize_rate_canon_noT - prize_rate_canon_T:.2f}; "
          f"纯理论/纯天赋 {p_theory_noprize / p_noT_noprize:.1f}×"
          "——理论加冕与奖项加冕双通道")


# ==================== 幕三:奖项场域的级联 ====================

YEARS3 = list(range(1993, 2025))
PRIZES = ("龚古尔", "雷诺多", "费米娜", "梅迪西", "联盟")  # 位次 1-5(通说序列)
N_BOOKS = 14
P_OBEY = 0.97    # 差异化默契强度: 后续评审以 0.97 只在未获奖书中选
EPS = 0.05       # 评审噪声
P0, RHO = 380.0, 0.42   # 龚古尔销量脉冲(千册, 构造量级)与位次衰减


def autumn(appeal, rng, cascade):
    """颁出一个秋季。

    级联模型: 首奖取全场地最优; 后续奖项以 P_OBEY 的默契只在"当年未获奖"
    的书中选(差异化默契), 以 1−P_OBEY 破例回到全局最优(准绳不是法律)。
    独立基线: 各奖独立取全场地最优(无默契)。
    """
    winners = []
    for pos in range(len(PRIZES)):
        if cascade and winners and rng.random() < P_OBEY:
            pool = [i for i in range(N_BOOKS) if i not in winners]
        else:
            pool = list(range(N_BOOKS))
        w = max(pool, key=lambda i: appeal[i] + rng.gauss(0, EPS))
        winners.append(w)
    return winners


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 奖项场域的级联({YEARS3[0]}-{YEARS3[-1]}, 五大奖位次 1-5, "
          f"候选 {N_BOOKS} 种, 差异化默契 P_obey={P_OBEY}, 销量脉冲 P0·ρ^(位次−1))")
    print("=" * 84)
    rng = random.Random(SEED)

    dup_cas = dup_ind = pair_cas = pair_ind = 0
    pulses = [0.0] * len(PRIZES)
    for y in YEARS3:
        appeal = [rng.random() for _ in range(N_BOOKS)]
        w_cas = autumn(appeal, rng, cascade=True)
        w_ind = autumn(appeal, rng, cascade=False)
        dup_cas += len(w_cas) != len(set(w_cas))     # 级联: 五奖中有无同书重复
        dup_ind += len(w_ind) != len(set(w_ind))     # 基线: 同上
        pair_cas += w_cas[0] in w_cas[1:]            # 龚古尔得主同年再获后续大奖
        pair_ind += w_ind[0] in w_ind[1:]
        for pos in range(len(PRIZES)):
            pulses[pos] += P0 * (RHO ** pos) * rng.uniform(0.85, 1.15)

    n_y = len(YEARS3)
    pair_rate_cas, pair_rate_ind = pair_cas / n_y, pair_ind / n_y
    dup_rate_cas, dup_rate_ind = dup_cas / n_y, dup_ind / n_y
    print(f"\n[3a] 评审趋避(差异化默契, {n_y} 个秋季):")
    print(f"  龚古尔得主同年再获后续大奖: 级联 {pair_rate_cas:.2f} "
          f"({pair_cas}/{n_y}) vs 独立基线 {pair_rate_ind:.2f} ({pair_ind}/{n_y})")
    print(f"  五奖任一同书重复的年份率:   级联 {dup_rate_cas:.2f} "
          f"({dup_cas}/{n_y}) vs 独立基线 {dup_rate_ind:.2f} ({dup_ind}/{n_y})")
    print(f"  顶级对联合概率比 = {pair_rate_cas / pair_rate_ind:.3f}(级联/独立)")
    print("读数: 独立评审几乎必撞车——评分相近时五个评审团全涌向同一本;")
    print("  级联评审的差异化默契把撞车压到零星(首奖一出, 后续各奔东西),")
    print("  但默契破例仍偶发——准绳不是法律")

    tot = sum(pulses)
    shares = [p / tot for p in pulses]
    print(f"\n[3b] 销量脉冲按位次(千册, 32 年合计):")
    for pos, name in enumerate(PRIZES):
        print(f"  位次{pos + 1} {name}: {pulses[pos]:>7.1f}  (份额 {shares[pos]:.3f})")
    print("读数:")
    print(f"  · 头两位(龚古尔+雷诺多)捕获总脉冲 {shares[0] + shares[1]:.1%}——")
    print("    十一月的头两个风标决定整个冬季的书店橱窗")
    print(f"  · 位次 1 脉冲为位次 3 的 {pulses[0] / pulses[2]:.1f} 倍——"
          "级联越靠后, 加冕的含金量按几何率折旧")

    assert pair_rate_cas <= 0.10, \
        f"级联顶级对撞车率应≤0.10, 实测 {pair_rate_cas:.2f}"
    assert pair_rate_ind >= 0.75, \
        f"独立基线顶级对撞车率应≥0.75, 实测 {pair_rate_ind:.2f}"
    assert pair_rate_cas <= 0.15 * pair_rate_ind, \
        "级联顶级对联合概率应<基线的 0.15 倍(趋避默契)"
    assert dup_rate_cas <= 0.25, "级联任一重复年率应≤0.25"
    assert dup_rate_ind >= 0.90, "独立基线任一重复年率应≥0.90"
    assert all(pulses[i] > pulses[i + 1] for i in range(len(pulses) - 1)), \
        "销量脉冲应随位次严格单调降"
    assert shares[0] + shares[1] >= 0.78, "头两位份额应≥0.78"
    assert pulses[0] >= 3.0 * pulses[2], "位次 1 脉冲应≥位次 3 的 3 倍"
    print(f"\n✓ 幕三断言通过: 顶级对撞车 {pair_rate_ind:.2f}→{pair_rate_cas:.2f}; "
          f"头两位份额 {shares[0] + shares[1]:.1%}; 位次1/位次3="
          f"{pulses[0] / pulses[2]:.1f}×——法国文学奖是十一月的天气预报")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 宣言脉冲: 宣言后凝聚力先升后降(S+衰退形状五项检查全过), 宣言")
    print("     越多时标越压缩、寿命越短(分组均值严格递减, r≤−0.90)")
    print("     ——宣言是运动的起跑枪也是解散令")
    print("  ② 共生网络: 高度数理论家连接的作家成'经典簇'(共振≥2.2×);无理论")
    print("     中介的作家更依赖奖项通道(获奖率差≥0.12), 纯理论通道正典化≥纯")
    print("     天赋 2.5×——理论加冕与奖项加冕双通道")
    print("  ③ 奖项级联: 评审趋避把龚古尔得主的同年双大奖率压到独立基线的 0.15")
    print("     倍以下;销量脉冲随位次几何递减, 头两位捕获≥78%——法国文学奖是")
    print("     十一月的天气预报, 头几个风标决定整个冬季")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
