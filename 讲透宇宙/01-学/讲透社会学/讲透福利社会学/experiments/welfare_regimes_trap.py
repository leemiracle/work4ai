# -*- coding: utf-8 -*-
"""体制、多元与陷阱:福利社会学实验三律。

00-体系结构.md(反直觉三发现)、03-可构造与结构.md(三具结构引擎的严格
可构造性)、04-福利社会学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random),无第三方依赖。

三律:
  律一 三体制的去商品化指数(艾斯平-安德森方法的教学版):
      对失业/医疗/养老三个项目,各按「覆盖率×替代率×持续时间」合成项目
      指数,再加总为体制总分;三体制代表性参数取社会民主/保守/自由三档
      (档位在三个项目间排序一致);每体制 6 个风格化国家,项目指数带
      体制内异质性(体制内国家互有强弱,通说)。
      断言:①三体制总分严格分层(社会民主>保守>自由,18 国无一越层);
      ②任一单项目上相邻体制的国家分布重叠——不存在单项目阈值把三体制
      分开:体制是多维组合,不是单指标。
  律二 福利多元的挤出与互补(国家-市场-家庭-社会的分账):
      总保障 G(P)=公共供给 P+非公共供给 S(P);S(P)=N·(1−σ(P/N)²/2),
      边际挤出率=σ·P/N(每单位公共扩张挤掉的非公共供给,随公共份额线性
      上升;σ=替代弹性档位:σ 大→强挤出,σ 小→互补)。
      断言:σ<1 时 dG/dP=1−σ·P/N 在全域为正(互补主导);σ>1 时越过
      临界份额 P*=N/σ 后转负(挤出主导)——挤出不是福利的定律,
      是弹性的问题。
  律三 贫困陷阱的 METR(家计调查型福利的退坡几何):
      低收入家庭领取社会救助+住房补贴两项家计调查型福利,收入上升福利
      按退坡率 taper 退出;个人所得税免征额以上课 15%。
      METR=(Δ税+Δ福利退坡)/Δ收入。
      断言:①存在 METR>60% 的收入区间(打印陷阱宽度);②退坡率上调使
      陷阱区间加宽加深(最高段越过 100%:多挣反而少得),且加宽后的陷阱
      恰好覆盖「最低工资到中位工资」段——工作的贫困陷阱是制度的几何,
      不是个人的懒惰。

跑法: python -X utf8 experiments/welfare_regimes_trap.py
"""

import math
import random

# ==================== 律一:三体制的去商品化指数 ====================

REGIMES = ("社会民主", "保守主义", "自由主义")
PROGRAMS = ("失业保险", "医疗保险", "养老金")

# 代表性参数(教学示意口径,非实测):(覆盖率, 替代率, 持续时间)
# 三档档位在三个项目间排序一致:每一档都比下一档覆盖更广/替代更高/持续更久
BASE_FACTORS = {
    "社会民主": {
        "失业保险": (0.92, 0.74, 0.88),
        "医疗保险": (0.97, 0.80, 0.94),
        "养老金": (0.96, 0.75, 0.90),
    },
    "保守主义": {
        "失业保险": (0.84, 0.50, 0.54),
        "医疗保险": (0.93, 0.71, 0.92),
        "养老金": (0.92, 0.66, 0.87),
    },
    "自由主义": {
        "失业保险": (0.42, 0.30, 0.30),
        "医疗保险": (0.52, 0.42, 0.86),
        "养老金": (0.82, 0.38, 0.64),
    },
}
N_COUNTRIES = 6   # 每体制的风格化国家数
HET = 0.085       # 体制内国家异质性(单项目指数的绝对扰动)


def build_countries():
    """生成 18 个风格化国家的项目指数与总分(固定种子,可复现)。

    项目指数 = 覆盖率×替代率×持续时间(体制基准),再加体制内国家异质性
    扰动(同一体制的国家在单项目上互有强弱——现实通说:体制内国家互有高低,
    体制是多项目的组合,不是单指标的档位)。
    """
    rng = random.Random(840673)
    idx = {r: {p: [] for p in PROGRAMS} for r in REGIMES}
    for r in REGIMES:
        for _ in range(N_COUNTRIES):
            for p in PROGRAMS:
                cov, rep, dur = BASE_FACTORS[r][p]
                v = cov * rep * dur + rng.gauss(0.0, HET)
                idx[r][p].append(max(v, 0.005))
    totals = {r: [sum(idx[r][p][c] for p in PROGRAMS)
                  for c in range(N_COUNTRIES)] for r in REGIMES}
    return idx, totals


def act1():
    print("=" * 84)
    print("律一 三体制的去商品化指数(项目指数=覆盖率×替代率×持续时间;"
          "总分=三项目之和)")
    print("=" * 84)
    idx, totals = build_countries()
    print(f"\n每体制 {N_COUNTRIES} 个风格化国家(体制内异质性 σ={HET});"
          "先看单项目,再看总分:\n")
    print(f"{'项目':>6} {'社会民主(区间)':>20} {'保守主义(区间)':>20}"
          f" {'自由主义(区间)':>20}  相邻重叠")
    overlap_ok = {}
    for p in PROGRAMS:
        cols = []
        for r in REGIMES:
            xs = idx[r][p]
            cols.append((min(xs), max(xs)))
        # 相邻体制(低档 vs 高档)的分布是否重叠:max(低) > min(高)
        ov_sdc = cols[1][1] > cols[0][0]   # 保守 max > 社会 min
        ov_cl = cols[2][1] > cols[1][0]    # 自由 max > 保守 min
        overlap_ok[p] = ov_sdc or ov_cl
        mark = []
        if ov_sdc:
            mark.append("社会-保守")
        if ov_cl:
            mark.append("保守-自由")
        print(f"{p:>6} {fmt_range(cols[0]):>20} {fmt_range(cols[1]):>20}"
              f" {fmt_range(cols[2]):>20}  {'/'.join(mark)}")
    print(f"\n{'体制':>6} {'总分均值':>9} {'总分区间':>18}  单项目均值(失业/医疗/养老)")
    means = {}
    for r in REGIMES:
        ts = totals[r]
        m = sum(ts) / len(ts)
        means[r] = m
        proj = [sum(idx[r][p]) / len(idx[r][p]) for p in PROGRAMS]
        print(f"{r:>6} {m:>9.3f} "
              f"[{min(ts):.3f}, {max(ts):.3f}]  "
              f"{proj[0]:.3f}/{proj[1]:.3f}/{proj[2]:.3f}")
    layer1 = max(totals["自由主义"]) < min(totals["保守主义"])
    layer2 = max(totals["保守主义"]) < min(totals["社会民主"])
    print("\n读数:")
    print("  · 总分把三体制干净分层:社会民主 %.3f > 保守主义 %.3f > 自由主义 %.3f,"
          % (means["社会民主"], means["保守主义"], means["自由主义"]))
    print("    且 18 国无一越层(自由最大 %.3f < 保守最小 %.3f < 保守最大 %.3f"
          " < 社会最小 %.3f);"
          % (max(totals["自由主义"]), min(totals["保守主义"]),
             max(totals["保守主义"]), min(totals["社会民主"])))
    print("  · 但每个单项目上,都存在相邻体制对分布重叠——体制内国家互有")
    print("    强弱(自由体制也有单项强项,社会民主体制也有单项弱项);")
    print("  · 单指标读体制必翻车:体制是多维组合,不是单指标——这正是")
    print("    去商品化指数要跨项目合成的原因(艾斯平-安德森方法的教学版)")

    # 断言 1:总分严格分层(均值+全对分层);单项目相邻重叠
    assert means["社会民主"] > means["保守主义"] > means["自由主义"], \
        "体制总分应严格排序:社会民主>保守>自由"
    assert means["社会民主"] - means["保守主义"] > 0.5, "相邻体制总分差距应显著"
    assert means["保守主义"] - means["自由主义"] > 0.5, "相邻体制总分差距应显著"
    assert layer1 and layer2, "18 国总分应无一越层(自由<保守<社会,全对分层)"
    for p in PROGRAMS:
        assert overlap_ok[p], f"单项目 {p} 应存在相邻体制分布重叠(不能单指标分体制)"
    print("\n✓ 律一断言通过:总分严格分层且 18 国无一越层;而失业/医疗/养老"
          "每个单项目上都存在相邻体制对的国家分布重叠——体制是多维组合,"
          "不是单指标")


def fmt_range(col):
    return "[%.2f, %.2f]" % (col[0], col[1])


# ==================== 律二:福利多元的挤出与互补 ====================

NEED = 100.0        # 风格化需求总量 N(公共+非公共共同应对的保障需求)
SIGMAS = (0.5, 0.8, 1.25, 1.6)   # 替代弹性档位:σ 大=强挤出,σ 小=互补
GRID = list(range(0, 101))       # 公共供给 P 的扫描格点(步长 1)


def s_of(p, sigma):
    """非公共供给(市场/家庭/社会):公共为 0 时全额自担,随公共扩张撤退。

    S(P) = N·(1 − σ(P/N)²/2);边际挤出率 = σ·P/N(随公共份额线性上升)。
    """
    return NEED * (1.0 - sigma * (p / NEED) ** 2 / 2.0)


def g_of(p, sigma):
    return p + s_of(p, sigma)


def act2():
    print("\n" + "=" * 84)
    print("律二 福利多元的挤出与互补(总保障 G=公共 P+非公共 S(P);"
          "边际挤出率=σ·P/N)")
    print("=" * 84)
    print(f"\n需求 N={NEED:.0f};公共供给 P 从 0 扫到 N;"
          "临界份额 P*=N/σ(σ<1 时 P*>N,全域互补):\n")
    print(f"{'σ':>5} {'临界份额N/σ':>10} {'G(0)':>7} {'G(50)':>7} {'G(100)':>8}"
          f" {'峰值位置':>8} {'峰值G':>8}  净效应形态")
    results = {}
    for sigma in SIGMAS:
        gs = [g_of(p, sigma) for p in GRID]
        amax = max(range(len(GRID)), key=lambda i: gs[i])
        results[sigma] = (gs, amax)
        pstar = NEED / sigma
        if sigma < 1.0:
            shape = "全域互补:处处递增"
        else:
            shape = "先升后降:过 P* 转负"
        print(f"{sigma:>5.2f} {pstar:>10.1f} {gs[0]:>7.1f} {gs[50]:>7.1f}"
              f" {gs[100]:>8.1f} {GRID[amax]:>8d} {gs[amax]:>8.1f}  {shape}")
    print("\n读数:")
    print("  · 边际净效应 dG/dP = 1 − σ·(P/N):公共扩张既加一单位公共,")
    print("    又挤掉 σ·P/N 单位非公共(市场撤保/家庭卸责/互助退场);")
    print("  · σ=0.5/0.8(<1):临界份额 N/σ>N,公共扩张全程加总保障——互补")
    print("    主导(公共在做非公共不做的事:兜底与再分配);")
    print("  · σ=1.25/1.6(>1):公共份额越过 1/σ 后,边际挤出超过公共增量,")
    print("    总保障不升反降——挤出主导(公共在做非公共本来会做的事);")
    print("  · 同一个公共扩张,总账是正是负,由弹性 σ 说了算——挤出不是")
    print("    福利的定律,是弹性的问题")

    # 断言 2:σ<1 全域为正;σ>1 过临界点转负;S≥0;净效应随 σ 单调恶化
    for sigma in (0.5, 0.8):
        gs, amax = results[sigma]
        diffs = [b - a for a, b in zip(gs, gs[1:])]
        assert all(d > 0 for d in diffs), \
            f"σ={sigma}:互补主导,总保障应全域递增"
        assert gs[100] > gs[0], f"σ={sigma}:公共扩张应加总保障"
    for sigma in (1.25, 1.6):
        gs, amax = results[sigma]
        pstar = NEED / sigma
        assert abs(GRID[amax] - pstar) <= 1.5, \
            f"σ={sigma}:峰值应贴临界份额 N/σ={pstar:.1f},实测 {GRID[amax]}"
        assert gs[100] < gs[amax], \
            f"σ={sigma}:越过临界点后总保障应转降(挤出主导)"
        tail = [b - a for a, b in zip(gs[80:], gs[81:])]
        assert all(d < 0 for d in tail), \
            f"σ={sigma}:高公共份额段净效应应恒为负"
    for sigma in SIGMAS:
        ss = [s_of(p, sigma) for p in GRID]
        assert min(ss) >= 0.0, f"σ={sigma}:非公共供给不应为负"
    d_low = results[0.5][0][91] - results[0.5][0][90]
    d_high = results[1.6][0][91] - results[1.6][0][90]
    assert d_low > 0 and d_high < 0, \
        "同一点的净效应应随 σ 由正转负(P=90 处对照)"
    print(f"\n✓ 律二断言通过:σ=0.5/0.8 时 G 全域递增(G(100) 分别 "
          f"{results[0.5][0][100]:.0f}/{results[0.8][0][100]:.0f});"
          f"σ=1.25/1.6 时峰值贴临界份额 N/σ(80/62.5)且 G(100) < 峰值"
          "——挤出不是福利的定律,是弹性的问题")


# ==================== 律三:贫困陷阱的 METR ====================

W_MIN, W_MED = 1800.0, 3600.0   # 最低工资 / 中位工资(风格化月收入)
TAX_FREE, TAX_RATE = 1000.0, 0.15
EXIT1, EXIT2 = 2400.0, 3600.0   # 社会救助 / 住房补贴的退坡退出点
STEP = 10.0
Y_MAX = 5000.0
TAPER_BASE, TAPER_HIGH = 0.35, 0.50


def tax(y):
    return TAX_RATE * max(0.0, y - TAX_FREE)


def benefit(y, taper):
    b1 = max(0.0, taper * (EXIT1 - y))   # 社会救助
    b2 = max(0.0, taper * (EXIT2 - y))   # 住房补贴(退出更晚)
    return b1 + b2


def net(y, taper):
    return y - tax(y) + benefit(y, taper)


def metr_profile(taper):
    """按收入段 [y, y+STEP) 计算有效边际税率 METR=(Δ税+Δ福利退坡)/Δ收入。"""
    prof = []
    y = 0.0
    while y + STEP <= Y_MAX:
        d_tax = tax(y + STEP) - tax(y)
        d_cut = benefit(y, taper) - benefit(y + STEP, taper)
        prof.append((y, (d_tax + d_cut) / STEP))
        y += STEP
    return prof


def trap_zone(prof, thresh=0.60):
    """METR>thresh 的最长连续区间(起止毛收入)。"""
    best = None
    cur = None
    for y, m in prof:
        if m > thresh:
            if cur is None:
                cur = [y, y + STEP]
            else:
                cur[1] = y + STEP
            if best is None or (cur[1] - cur[0]) > (best[1] - best[0]):
                best = list(cur)
        else:
            cur = None
    return best


def act3():
    print("\n" + "=" * 84)
    print("律三 贫困陷阱的 METR(两项家计调查型福利:社会救助退坡退出 "
          f"{EXIT1:.0f}/住房补贴 {EXIT2:.0f};税=免征额 {TAX_FREE:.0f} 以上 {TAX_RATE:.0%})")
    print("=" * 84)
    for taper, tag in ((TAPER_BASE, "基准退坡率 0.35"),
                       (TAPER_HIGH, "上调退坡率 0.50")):
        prof = metr_profile(taper)
        zone = trap_zone(prof)
        mmax = max(m for _, m in prof)
        print(f"\n[{tag}] 最低工资 {W_MIN:.0f} / 中位工资 {W_MED:.0f}")
        segs = []
        for lo, hi, rate in ((0, TAX_FREE, None), (TAX_FREE, EXIT1, None),
                             (EXIT1, EXIT2, None)):
            ms = [m for y, m in prof if lo <= y < hi]
            if ms:
                segs.append("y∈(%d,%d):%.2f" % (lo, hi, sum(ms) / len(ms)))
        print("  分段 METR(平均):" + ";".join(segs))
        print(f"  陷阱区间(METR>60%):[{zone[0]:.0f}, {zone[1]:.0f}),"
              f"宽度 {zone[1] - zone[0]:.0f};最高 METR={mmax:.2f}"
              f"({'悬崖:多挣反而少得' if mmax > 1.0 else '未越 100%'})")
        edge = ("恰压中位工资 %d" % W_MED if abs(zone[1] - W_MED) <= STEP
                else "未及中位工资 %d" % W_MED)
        print(f"  覆盖检查:最低工资 {W_MIN:.0f} "
              f"{'∈' if zone[0] <= W_MIN < zone[1] else '∉'} 陷阱;"
              f"上沿 {zone[1]:.0f} {edge}")
        print("  净收入:net(0)=%.0f net(%.0f)=%.0f net(%.0f)=%.0f net(%.0f)=%.0f"
              % (net(0, taper), W_MIN, net(W_MIN, taper), W_MED, net(W_MED, taper),
                 Y_MAX, net(Y_MAX, taper)))
        if taper == TAPER_BASE:
            base_zone, base_mmax = zone, mmax
        else:
            high_zone, high_mmax = zone, mmax
    # 具体走一步:陷阱段中央挣 10 元净得多少
    y_mid = (TAX_FREE + EXIT1) / 2
    dn_base = net(y_mid + STEP, TAPER_BASE) - net(y_mid, TAPER_BASE)
    dn_high = net(y_mid + STEP, TAPER_HIGH) - net(y_mid, TAPER_HIGH)
    print("\n读数:")
    print("  · 陷阱段中央(毛收入 %.0f→%.0f):基准退坡下挣 10 元净得 %+.1f 元"
          " (METR=%.0f%%);"
          % (y_mid, y_mid + STEP, dn_base, 100 * (1 - dn_base / STEP)))
    print("    上调退坡率后挣 10 元净得 %+.1f 元(METR=%.0f%%,越过 100%%:"
          % (dn_high, 100 * (1 - dn_high / STEP)))
    print("    净收入不升反降——退坡率把『多劳多得』改成『多劳多扣』);")
    print("  · 退坡率 0.35→0.50:陷阱宽度 %d→%d(加宽),最高 METR "
          "%.2f→%.2f(加深," % (base_zone[1] - base_zone[0],
                               high_zone[1] - high_zone[0],
                               base_mmax, high_mmax))
    print("    且越过 100%:本已低于陷阱线的『仅剩住房补贴』段也被抬过线);")
    print("  · 加宽后的陷阱恰好覆盖最低工资 %.0f 到中位工资 %.0f 段——"
          % (W_MIN, W_MED))
    print("    拿全日制最低工资的人全程踩在陷阱里:这不是个人的懒惰,")
    print("    是退坡率×退出点×税线的几何")

    # 断言 3:陷阱存在且够宽;上调加宽加深;覆盖最低-中位工资段;扫描单调
    assert base_zone is not None and base_zone[1] - base_zone[0] >= 2000, \
        "基准参数下应存在宽度≥2000 的 METR>60% 陷阱区间"
    assert base_mmax >= 0.84, f"基准最高 METR 应达 0.85 量级,实测 {base_mmax:.3f}"
    assert base_zone[0] <= W_MIN < base_zone[1], "最低工资应落在基准陷阱内"
    w_base = base_zone[1] - base_zone[0]
    w_high = high_zone[1] - high_zone[0]
    assert w_high > w_base, f"退坡率上调应加宽陷阱({w_base}→{w_high})"
    assert high_mmax > base_mmax and high_mmax > 1.0, \
        f"退坡率上调应加深陷阱且越过 100%(实测 {high_mmax:.3f})"
    assert high_zone[0] <= W_MIN and high_zone[1] >= W_MED, \
        "加宽后的陷阱应覆盖最低工资到中位工资段"
    assert abs(high_zone[1] - W_MED) <= STEP, \
        f"陷阱上沿应恰好压在中位工资 {W_MED:.0f} 处,实测 {high_zone[1]:.0f}"
    widths, mmaxes = [], []
    for taper in (0.30, 0.35, 0.45, 0.50):
        prof = metr_profile(taper)
        zone = trap_zone(prof)
        widths.append(zone[1] - zone[0])
        mmaxes.append(max(m for _, m in prof))
    assert all(a <= b for a, b in zip(widths, widths[1:])), \
        f"陷阱宽度应随退坡率非降,实测 {widths}"
    assert all(a < b for a, b in zip(mmaxes, mmaxes[1:])), \
        f"陷阱深度应随退坡率严格加深,实测 {mmaxes}"
    assert dn_base > 0 and dn_high < 0, \
        "陷阱段中央:基准下净增为正,上调后退坡率应把净增收打成负数"
    print(f"\n✓ 律三断言通过:基准陷阱宽度 {w_base:.0f}(最高 METR "
          f"{base_mmax:.2f});退坡率上调后宽度 {w_high:.0f}、最高 {high_mmax:.2f}"
          f"(悬崖),上沿恰好压在中位工资 {W_MED:.0f}——工作的贫困陷阱是"
          "制度的几何,不是个人的懒惰")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 去商品化:总分严格分层(社会民主>保守>自由,18 国无一越层),")
    print("     但每个单项目上都存在相邻体制对分布重叠——体制是多维组合,不是单指标")
    print("  ② 福利多元:σ<1 时公共扩张全程加总保障(互补主导);σ>1 时越过")
    print("     临界份额 N/σ 后转负(挤出主导)——挤出不是福利的定律,")
    print("     是弹性的问题")
    print("  ③ 贫困陷阱:METR>60% 的区间存在且随退坡率加宽加深(可越过 100%),")
    print("     加宽后恰好覆盖最低工资到中位工资段——陷阱是制度的几何,")
    print("     不是个人的懒惰")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
