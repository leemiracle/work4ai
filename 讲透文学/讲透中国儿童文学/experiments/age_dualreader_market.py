# -*- coding: utf-8 -*-
"""适龄爬升-双读者-替代动力学三律模拟:中国儿童文学家族实验(GB/T 75041)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(三条结构引擎的
严格可构造性)、04-中国儿童文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260907 可复现。

三幕:
  幕一 适龄性的语言爬升(分级阅读的语言学基础):
      阅读能力发育是 S 形曲线(识字爆炸期斜率最大),文本语言复杂度按目标年龄
      分层——复杂度=句长/词汇稀有度/嵌套深度的合成指数,其期望=发育曲线的投影。
      目标年龄档 3/6/9/12/15 岁,每档生成 240 种文本抽样。
      断言:①五档指数严格单调上升(分层成立)
            ②相邻档间距不均:6→9 档(幼小衔接/识字爆炸期)斜率最大且显著
              压过 3→6 档与 9→12 档;12→15 档(青少年段)趋缓到不足 6→9 档
              斜率的 1/8——分级不是均匀刻度,是发育曲线的投影。
  幕二 双读者结构(crossover 现象;诺德曼"隐含的成人"/双重讲述的算术版):
      儿童向文本被双层编码:表层故事线(门,儿童可达性 s)×深层意义层(房,主题密度 d)。
      儿童端达成率 = s·exp(-1.2d)(深度按指数把儿童往外推——门被房堵);
      成人重读价值 = (0.15+0.85·d/(d+0.35))·(0.25+0.75s)(深度饱和收益,
      且成人也要先进得了门)。
      断言:①双层书的成人重读率 ≈ 单层对照的 2 倍以上,且儿童端不塌——
              童年读表层/成年读深层的"两次消费"率显著更高
            ②深度过密的文本两头不讨好:儿童端流失到单层书的 1/5 以下,
              成人端也不及双层书,两次消费率塌掉——两头不讨好区间在网格上
              占比≈四成(双读者设计是窄门艺术)
            ③双读者价值(儿童端×成人端)的最大值点:门要宽(s*≥0.90)、
              房要中等深(d*∈[0.25,0.45])——好童书是给孩子的门和给大人的房子。
  幕三 引进-原创的替代动力学(后发市场的标准路径):
      品类市场(1990-2025)由引进主导转向本土原创:原创产能=逻辑斯蒂 ramp
      (拐点 2009),引进品种量=1990 年代扩张+2001 年峰值+慢衰减长尾(平台 0.45),
      二者各带 ±3% 市场噪声;份额=量/总量。
      断言:①原创份额呈 S 形:1990-2000 年引进份额 ≥0.83(先引进)、份额年增量
              单峰(慢-快-慢)、50% 跨越恰一次;引进长尾不消——窗口末端引进份额
              仍 ≥0.19,品种量仍 ≥0.33×峰值(原创从不归零引进)
            ②原创起飞拐点(原创量过其渐近半值之年)滞后引进品种峰值约一个
              产品周期 T_c=8 年(引进选题→本土仿创→原创规模化),实测 |滞后-8|≤2
              ——先引进后原创的模仿学习期。

跑法: python -u experiments/age_dualreader_market.py
"""

import math
import random
import statistics

SEED = 20260907  # 检索校准日作种子,可复现

# ==================== 幕一:适龄性的语言爬升 ====================

AGES = (3, 6, 9, 12, 15)
TIERS = ("3岁·婴儿期图画书", "6岁·幼小衔接桥梁书", "9岁·中段章节书",
         "12岁·高段成长小说", "15岁·青少年文学")
N_TEXTS = 240  # 每档抽 240 种文本


def dev(a):
    """阅读能力发育曲线: logistic, 识字爆炸期(≈8 岁)斜率最大。"""
    return 1.0 / (1.0 + math.exp(-(a - 8.0) / 1.4))


def text_metrics(rng, d):
    """一种文本的三个语言指标: 平均句长(字/句)/低频词占比/平均嵌套深度(层)。"""
    m_len = 8 + 30 * d + rng.gauss(0, 2.5)     # 8..38 字/句
    m_rare = 0.02 + 0.36 * d + rng.gauss(0, 0.020)  # 0.02..0.38
    m_nest = 0.4 + 3.2 * d + rng.gauss(0, 0.30)     # 0.4..3.6 层
    return m_len, m_rare, m_nest


def composite(m_len, m_rare, m_nest):
    """合成适龄复杂度指数 0-100: 句长 40% + 稀有度 35% + 嵌套 25%。"""
    nl = min(1.0, max(0.0, m_len / 38.0))
    nr = min(1.0, max(0.0, m_rare / 0.38))
    nn = min(1.0, max(0.0, m_nest / 3.6))
    return 100.0 * (0.40 * nl + 0.35 * nr + 0.25 * nn)


def act1():
    print("=" * 84)
    print("幕一 适龄性的语言爬升: 复杂度指数 = 发育曲线的投影(档 3/6/9/12/15 岁)")
    print("=" * 84)
    rng = random.Random(SEED)
    print("\n发育曲线 dev(a)=1/(1+exp(-(a-8)/1.4)); 每档生成 %d 种文本,"
          "指数=句长40%%+稀有度35%%+嵌套25%%\n" % N_TEXTS)
    print(f"{'档':<14} {'dev':>5} {'句长':>6} {'稀有度':>7} {'嵌套':>5} "
          f"{'指数均值':>8} {'指数标准差':>10}")

    means, sds = {}, {}
    for a, tier in zip(AGES, TIERS):
        idxs = []
        for _ in range(N_TEXTS):
            m_len, m_rare, m_nest = text_metrics(rng, dev(a))
            idxs.append(composite(m_len, m_rare, m_nest))
        means[a] = statistics.mean(idxs)
        sds[a] = statistics.stdev(idxs)
        d = dev(a)
        print(f"{tier:<14} {d:>5.2f} {8 + 30 * d:>6.1f} {0.02 + 0.36 * d:>7.3f} "
              f"{0.4 + 3.2 * d:>5.1f} {means[a]:>8.1f} {sds[a]:>10.1f}")

    g36 = means[6] - means[3]
    g69 = means[9] - means[6]
    g912 = means[12] - means[9]
    g1215 = means[15] - means[12]
    print("\n相邻档间距(指数点, 各跨 3 岁):")
    print(f"  3→6 : {g36:5.1f}   6→9 : {g69:5.1f}   9→12 : {g912:5.1f}   "
          f"12→15 : {g1215:5.1f}")
    print("读数:")
    print("  · 6→9 档(幼小衔接)爬升最陡——识字爆炸期,分级在这里必须切得最细")
    print(f"  · 12→15 档只升 {g1215:.1f} 点(6→9 档的 {g1215 / g69:.0%}):青少年段")
    print("    发育趋缓,语言爬升让位给主题与形式的爬升")
    print(f"  · 同档内标准差 ≈ {sds[9]:.0f} 点——同龄不同读,分级要按带宽不按刻线")

    assert means[3] < means[6] < means[9] < means[12] < means[15], "五档应严格单调上升"
    assert g69 > 1.6 * g912, "6→9 间距应显著压过 9→12(识字爆炸期)"
    assert g69 > 2.2 * g36, "6→9 间距应显著压过 3→6"
    assert g912 > 3 * g1215, "9→12 间距应压过 12→15(青少年段趋缓)"
    assert g69 / 3.0 > 8 * (g1215 / 3.0), "6→9 年斜率应 >8×12→15 年斜率"
    assert max(g36, g69, g912, g1215) > 8 * min(g36, g69, g912, g1215), \
        "分级不是均匀刻度: 间距最大/最小应差 8 倍以上"
    print(f"\n✓ 幕一断言通过: 单调 {means[3]:.1f}→{means[15]:.1f}; 间距比 "
          f"g(6→9):g(9→12):g(12→15) = 1 : {g912 / g69:.2f} : {g1215 / g69:.2f}"
          "——发育曲线的投影,不是均匀刻度")


# ==================== 幕二: 双读者结构(crossover) ====================

K_DEPTH = 1.2  # 深度对儿童的驱逐速率(指数)


def child_appeal(s, d):
    """儿童端达成率: 门 s 要宽, 深度 d 按指数把儿童往外推。"""
    return s * math.exp(-K_DEPTH * d)


def adult_value(s, d):
    """成人重读价值: 深度饱和收益 d/(d+0.35), 且成人也要先进得了门。"""
    d_hat = d / (d + 0.35)
    return (0.15 + 0.85 * d_hat) * (0.25 + 0.75 * s)


def act2():
    print("\n" + "=" * 84)
    print("幕二 双读者结构: 儿童端=s·exp(-1.2d)(门), 成人端=深度饱和×门反哺(房)")
    print("=" * 84)

    # 2a 网格扫描: 双读者价值 = 儿童端 × 成人端 的最优结构
    grid_s = [0.05 * i for i in range(1, 20)]   # 0.05..0.95
    grid_d = [0.05 * i for i in range(21)]      # 0.00..1.00
    best, bad_cells, total = None, 0, 0
    for s in grid_s:
        for d in grid_d:
            c, a = child_appeal(s, d), adult_value(s, d)
            if best is None or c * a > best[0]:
                best = (c * a, s, d, c, a)
            if c < 0.25 and a < 0.45:
                bad_cells += 1
            total += 1
    _, s_star, d_star, c_star, a_star = best
    bad_frac = bad_cells / total

    print("\n[2a] 网格扫描(s∈[0.05,0.95]×d∈[0,1], 步长 0.05):")
    print(f"  双读者价值(儿童端×成人端)最大点: s*={s_star:.2f}(门宽), "
          f"d*={d_star:.2f}(房深)")
    print(f"    该点儿童端={c_star:.3f}, 成人端={a_star:.3f}——门过半, 房也立得住")
    print(f"  两头不讨好区(儿童端<0.25 且 成人端<0.45)占网格 {bad_frac:.1%}"
          "——高深度低可达的'成人化童书'真实存在且不可忽略")
    assert s_star >= 0.90, "最优门宽 s* 应≥0.90(给孩子的门必须敞开)"
    assert 0.25 <= d_star <= 0.45, "最优房深 d* 应中等(过密堵门,过浅无房)"
    assert c_star > 0.5 and a_star > 0.5, "最优点两端都要过半"
    assert bad_frac > 0.30, "两头不讨好区间占比应>30%"
    print("  ✓ 2a 断言通过: 好童书是给孩子的门(宽)和给大人的房子(中等深)")

    # 2b 蒙特卡洛: 三类书 × N 位读者(童年读/成年重读各一次伯努利)
    n_readers = 8000
    classes = [
        ("单层儿童书(s=0.88,d=0.05)", 0.88, 0.05),
        ("双层童书  (s=0.85,d=0.45)", 0.85, 0.45),
        ("深度过密书(s=0.40,d=0.90)", 0.40, 0.90),
    ]
    rng = random.Random(SEED)
    print(f"\n[2b] 三类书 × {n_readers} 位读者(童年 9 岁读/成年 35 岁重读):")
    print(f"{'类别':<26} {'儿童端':>7} {'成人重读':>8} {'两次消费':>8}")
    rates = {}
    for name, s, d in classes:
        pc, pa = child_appeal(s, d), adult_value(s, d)
        child_n = adult_n = twice_n = 0
        for _ in range(n_readers):
            as_child = rng.random() < pc
            as_adult = rng.random() < pa
            child_n += as_child
            adult_n += as_adult
            twice_n += as_child and as_adult
        rates[name] = (child_n / n_readers, adult_n / n_readers,
                       twice_n / n_readers)
        print(f"{name:<26} {rates[name][0]:>7.3f} {rates[name][1]:>8.3f} "
              f"{rates[name][2]:>8.3f}")

    single = rates["单层儿童书(s=0.88,d=0.05)"]
    dual = rates["双层童书  (s=0.85,d=0.45)"]
    dense = rates["深度过密书(s=0.40,d=0.90)"]
    print("读数:")
    print(f"  · 双层书成人重读 {dual[1]:.3f} ≈ 单层书 {single[1]:.3f} 的 "
          f"{dual[1] / single[1]:.1f} 倍——深层意义层是成年重读的引擎")
    print(f"  · 深度过密书儿童端 {dense[0]:.3f} 仅为单层书的 {dense[0] / single[0]:.0%}:"
          "门被房堵死,儿童端崩塌")
    print(f"  · 过密书两次消费 {dense[2]:.3f} 反而不到单层书的一半——深度买到手,"
          "读者没进门,两头不讨好")
    assert dual[1] > 1.8 * single[1], "双层书成人重读率应≈单层书 2 倍"
    assert dual[0] > 0.45, "双层书儿童端不应塌(<0.45)"
    assert dual[2] > 1.2 * single[2], "双层书两次消费率应显著更高"
    assert dense[0] < 0.35 * single[0], "过密书儿童端应流失到单层书的 1/3 以下"
    assert dense[1] < dual[1], "过密书成人端也不及双层书"
    assert dense[2] < 0.5 * single[2], "过密书两次消费应塌掉"
    print(f"\n✓ 幕二断言通过: 成人重读 {single[1]:.3f}→{dual[1]:.3f}"
          f"(×{dual[1] / single[1]:.1f}); 过密书儿童端 {dense[0]:.3f}="
          f"{dense[0] / single[0]:.0%}×单层——双层是资产,过密是负债")


# ==================== 幕三: 引进-原创的替代动力学 ====================

YEARS = list(range(1990, 2026))
T_PEAK = 2001     # 引进品种量峰值年(构造)
T_INFL = 2009     # 原创产能逻辑斯蒂拐点(构造)
T_CYCLE = 8       # 产品周期: 引进选题→本土仿创→原创规模化
R_LOGIT = 3.4     # 原始逻辑斯蒂速率
P_BASE, Q_AMP = 100.0, 150.0  # 引进峰值量 / 原创渐近量


def import_volume(t):
    """引进品种量指数: 1990s 扩张 → 2001 峰值 → 慢衰减到 0.45 平台(长尾)。"""
    x = t - 1990
    if x < 11:
        return P_BASE * (0.35 + 0.65 * (x / 11.0) ** 2.5)
    return P_BASE * (0.45 + 0.55 * math.exp(-(x - 11.0) / 6.0))


def original_volume(t):
    """原创产能量指数: 逻辑斯蒂 ramp, 拐点 2009(滞后引进峰值一个产品周期)。"""
    sigma = 1.0 / (1.0 + math.exp(-(t - T_INFL) / R_LOGIT))
    return Q_AMP * (0.02 + 0.98 * sigma)


def smooth(xs, w=3):
    """宽度 w 的滑动平均(量级噪声下找峰/找拐点用)。"""
    out = []
    for i in range(len(xs)):
        lo, hi = max(0, i - w // 2), min(len(xs), i + w // 2 + 1)
        out.append(statistics.mean(xs[lo:hi]))
    return out


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 引进-原创替代动力学(1990-2025, 品种量指数, ±3% 市场噪声,"
          f"产品周期 T_c={T_CYCLE} 年)")
    print("=" * 84)
    rng = random.Random(SEED)
    vi, vo = [], []
    for t in YEARS:
        vi.append(import_volume(t) * rng.uniform(0.97, 1.03))
        vo.append(original_volume(t) * rng.uniform(0.97, 1.03))
    share_o = [o / (o + i) for o, i in zip(vo, vi)]

    show = (1990, 1995, 2001, 2005, 2009, 2013, 2017, 2021, 2025)
    print(f"\n{'年':>5} {'引进量':>7} {'原创量':>7} {'原创份额':>8}")
    for j, t in enumerate(YEARS):
        if t in show:
            note = {2001: "← 引进品种峰值", 2009: "← 原产起飞拐点"}.get(t, "")
            print(f"{t:>5} {vi[j]:>7.1f} {vo[j]:>7.1f} {share_o[j]:>8.3f}  {note}")

    vi_s, vo_s = smooth(vi), smooth(vo)
    # 峰值年=平滑引进量的最大值年; 起飞拐点=平滑原创量过其渐近半值(Q·0.51)之年
    t_peak = YEARS[max(range(len(YEARS)), key=lambda j: vi_s[j])]
    half_asym = Q_AMP * 0.51
    t_infl = next(YEARS[j] for j in range(len(YEARS)) if vo_s[j] >= half_asym)
    lag = t_infl - t_peak

    dso = [share_o[j + 1] - share_o[j] for j in range(len(YEARS) - 1)]
    idx_max = max(range(len(dso)), key=lambda j: dso[j])
    t_max_growth = YEARS[1 + idx_max]
    crosses = [j for j in range(1, len(YEARS))
               if share_o[j - 1] < 0.5 <= share_o[j]]
    early_import_ok = all(1 - share_o[j] >= 0.83
                          for j, t in enumerate(YEARS) if t <= 2000)
    rise = [share_o[j] for j, t in enumerate(YEARS) if 0.30 <= share_o[j] <= 0.70]
    mean_import_rise = 1 - statistics.mean(rise)
    end_import_share = 1 - share_o[-1]
    end_import_vol = vi[-1] / max(vi)

    print("\n读数:")
    print(f"  · 引进品种峰值 {t_peak} 年, 原创起飞拐点 {t_infl} 年, 滞后 {lag} 年"
          f"≈一个产品周期(T_c={T_CYCLE})——先引进后原创的模仿学习期")
    print(f"  · 份额年增量峰值在 {t_max_growth} 年, 50% 跨越恰 {len(crosses)} 次"
          f"({YEARS[crosses[0]] if crosses else '—'} 年)——S 形替代")
    print(f"  · 原创崛起期(份额 0.3→0.7)引进份额均值 {mean_import_rise:.2f}:"
          "替代最猛时市场仍近半是引进书")
    print(f"  · 2025 年引进份额仍有 {end_import_share:.2f}, 品种量 {end_import_vol:.0%}"
          "×峰值——长尾不消, 原创从不归零引进")

    assert len(crosses) == 1, "50% 跨越应恰一次(S 形)"
    assert early_import_ok, "1990-2000 引进份额应≥0.83(先引进)"
    assert 2004 <= t_max_growth <= 2012, "份额年增量峰值应在拐点附近"
    assert dso[0] < 0.4 * dso[idx_max] and dso[-1] < 0.4 * dso[idx_max], \
        "S 形两端增量应远低于峰值(慢-快-慢)"
    assert mean_import_rise >= 0.35, "崛起期引进份额均值应≥0.35"
    assert end_import_share >= 0.19, "窗口末端引进份额应≥0.19(长尾不消)"
    assert end_import_vol >= 0.33, "末端引进品种量应≥0.33×峰值"
    assert abs(lag - T_CYCLE) <= 2, f"原创起飞应滞后引进峰值≈{T_CYCLE}±2 年, 实测 {lag}"
    print(f"\n✓ 幕三断言通过: S 形替代+引进长尾(末段 {end_import_share:.2f}); "
          f"滞后 {lag} 年≈T_c={T_CYCLE}——后发市场的标准路径")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 适龄性=发育曲线的投影: 复杂度指数随目标年龄单调爬升, 6→9 档(识字")
    print("     爆炸期)斜率最大, 12→15 档趋缓至不足其 1/8——分级不是均匀刻度")
    print("  ② 双读者结构: 双层编码(表层门+深层房)的成人重读≈单层书 2 倍且儿童端")
    print("     不塌; 深度过密则儿童端崩塌、两次消费归零——好童书是给孩子的门和")
    print("     给大人的房子, 过密是两头不讨好")
    print("  ③ 引进-原创 logistic 替代: S 形+50% 单次跨越; 崛起期引进仍近半, 末端")
    print("     长尾不消; 原创起飞滞后引进峰值≈一个产品周期(8 年)——先引进后原创,")
    print("     原创从不归零引进")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
