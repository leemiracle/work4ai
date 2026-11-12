# -*- coding: utf-8 -*-
"""路径与时刻:历史社会学三个时序机制的最小实现。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(结构卡三张的样板)、
04-历史社会学转代码.md(走廊 1/2)的配套实验。
纯标准库(math/random),无第三方依赖;固定随机种子,逐幕 assert。

与同波数理社会学家族的实验(Schelling 隔离/WS 小世界/BA 优先连接)零重叠:
那边管「微观规则×聚合」的空间与网络涌现,这边管「时间中的事件」——强化、
时机与丛集。与工程宇宙标准科学技术家族 oc_curve_and_lockin.py 的锁定
实验互补:那边是份额 ODE 的确定性动力学(临界份额 s*=1/2−q/a),这边是
逐采纳者随机选择的蒙特卡洛——「锁定对象由早期随机决定」这一断言只有在
随机版里才能被提出和检验。

三律:
  幕一 Polya 罐的早期锁定(初始 1 红 1 蓝,每抽按当前比例、放回同色双份
      =净增 1,即强化;抽 200 次):
      理论锚:终局份额的极限分布 ~ Beta(初始红+抽中红, 初始蓝+抽中蓝),
      初始 (1,1) 时极限 ~ Uniform(0,1)(de Finetti 交换性;有限步的红数
      边际恰为离散均匀)。断言(MC 3000 罐):
      ①终局份额分布近似均匀(分箱频率与 1/箱数 偏差小)——「事前看,
      结局在起点上对两色公平;事后看,几乎全部份额差都是前几抽的偶然
      滚成的」②前 10 抽占多数的颜色终局份额>0.5 的概率>0.75;且「强制
      前 10 抽为某色」与「强制后 10 抽为某色」(同样 10 抽、不同位置)对
      终局份额>0.9 的概率天差地别——早期偶然优势被强化过程滚成压倒格局
      (路径依赖的最小机器)。
      如实标注:观测意义上「前 10 抽多数」与「后 10 抽多数」对终局份额
      同样有预测力(交换序列的必然,实验同步打印对照)——不对称只存在于
      干预意义:搬得动的前 10 抽改写整个终局分布,搬不动的后 10 抽只是往
      已经形成的格局里加 10 个球。路径依赖的本体在干预,不在预测。
  幕二 Arthur 收益递增与技术锁定(两技术对称:质量相同,采纳者收益=
      基础+α×该技术已采纳份额,内在偏好±ξ 异质,逐采纳者 logit 选择,
      α=1、ξ=±0.2、β=6、n=800):
      断言①对称设定下锁定 A 或 B 各约 50%——锁定对象由早期随机决定,
      而不是由质量决定(质量本来也相同)②早期份额落后 10 与 40 个百分点
      的翻盘曲线(δ 网格扫描):同一价码 δ=0.15 浅坑翻得动、深坑翻不动,
      深坑价码 δ* 约为浅坑的 3 倍;且同样的价码越晚出手翻盘概率越低
      (领先会被强化继续滚大:10pp 的领先 300 个采纳者后涨到约 0.70,
      40pp 涨到约 0.89)——坑越深填坑越贵,越晚翻盘越贵。
  幕三 危机的时间聚集(社会压力做带漂移的随机游走,非负地板,超越承载力
      阈值 T=危机爆发并按比例部分释放;漂移分承平(微负,压力耗散)/高压
      两纪元慢切换):断言危机计数的丛集指数(每箱计数方差/均值,逐历史
      计算后平均,泊松对照=1)>1(过度散布),且高压纪元漂移越大聚集越强
      ——大变动的年代不是均匀撒在历史里,是丛集在压力纪元的临界段
      (「时代的一粒灰」的时间结构)。
      如实标注:单一恒定强漂移不产生丛集,产生「定时器」式的规律爆发
      (欠散布≪1)——丛集的统计指纹指向的是纪元结构,不是漂移本身;
      这正是断续均衡(长期稳态+快速变迁)的最小机器。

跑法: python -X utf8 experiments/path_and_moment.py
"""

import math
import random

SEED_BASE = 20260909  # 建族日固定种子;各幕/各档逐格加号,可复现


# ==================== 幕一:Polya 罐的早期锁定 ====================

N_DRAWS = 200     # 每罐抽 200 次
RUNS1 = 3000      # 蒙特卡洛罐数
NBINS = 10        # 终局份额分箱数


def polya_run(rng, n_draws=N_DRAWS, force_first=None, force_last=None):
    """一次 Polya 罐:初始 1 红 1 蓝;每抽按当前红蓝比例抽 1 球、放回
    同色 2 球(净增 1=强化)。force_first/force_last 可强制首/末 10 抽的
    颜色(干预实验)。返回 (前10抽红数, 后10抽红数, 终局红份额)。"""
    r = b = 1
    red_first = red_last = 0
    for t in range(1, n_draws + 1):
        if force_first is not None and t <= 10:
            color = force_first
        elif force_last is not None and t > n_draws - 10:
            color = force_last
        elif rng.random() < r / (r + b):
            color = "R"
        else:
            color = "B"
        if color == "R":
            r += 1
            if t <= 10:
                red_first += 1
            if t > n_draws - 10:
                red_last += 1
        else:
            b += 1
    return red_first, red_last, r / (r + b)


def act1():
    print("=" * 84)
    print("幕一 Polya 罐的早期锁定(初始 1 红 1 蓝,按比例放回双份,抽 200 次,"
          f"MC {RUNS1} 罐)")
    print("=" * 84)
    print("\n理论锚:终局份额极限 ~ Beta(1+红, 1+蓝);初始 (1,1) 时极限 ~ "
          "Uniform(0,1)")
    print("       (de Finetti:可交换序列的参数混合;有限步的红数边际恰为离散均匀)")

    # ① 终局份额分布的均匀性
    bins = [0] * NBINS
    early_majority_win = early_total = 0
    late_majority_win = late_total = 0
    for k in range(RUNS1):
        rf, rl, share = polya_run(random.Random(SEED_BASE + k))
        bins[min(int(share * NBINS), NBINS - 1)] += 1
        if rf != 5:  # 前 10 抽有多数色(排除 5:5 平局)
            early_total += 1
            if (share > 0.5) == (rf > 5):
                early_majority_win += 1
        if rl != 5:  # 后 10 抽有多数色(观测对称对照)
            late_total += 1
            if (share > 0.5) == (rl > 5):
                late_majority_win += 1
    freqs = [c / RUNS1 for c in bins]
    max_dev = max(abs(f - 1 / NBINS) for f in freqs)
    print(f"\n① 终局份额分箱({NBINS} 箱)频率:")
    print("   " + " ".join(f"{f:.3f}" for f in freqs))
    print(f"   与均匀线 1/{NBINS}={1 / NBINS:.1f} 的最大偏差 {max_dev:.4f}"
          f"(均匀性断言)")
    p_early = early_majority_win / early_total
    p_late = late_majority_win / late_total
    print(f"\n② 前 10 抽多数色的终局份额>0.5 的概率:{p_early:.4f}"
          f"(排除平局后 {early_total} 罐;断言>0.75)")
    print(f"   对照:后 10 抽多数色对终局>0.5 的概率:{p_late:.4f}"
          f"(两数接近是交换性的必然,见读数)")

    # ③ 干预实验:强制首 10 抽 vs 强制末 10 抽(同样 10 抽,不同位置)
    win_first = sum(polya_run(random.Random(SEED_BASE + 100000 + k),
                              force_first="R")[2] > 0.9
                    for k in range(RUNS1))
    win_last = sum(polya_run(random.Random(SEED_BASE + 200000 + k),
                             force_last="R")[2] > 0.9
                   for k in range(RUNS1))
    pf, pl = win_first / RUNS1, win_last / RUNS1
    print(f"\n③ 干预:强制首 10 抽全红 → 终局红份额>0.9 的概率 {pf:.4f}")
    print(f"   干预:强制末 10 抽全红 → 终局红份额>0.9 的概率 {pl:.4f}"
          f"(理论锚:Beta(11,1) 右尾 1−0.9^11≈0.686 vs 均匀尾≈0.10)")
    print(f"   同样 10 抽,放在开头比放在结尾对终局的杠杆高 "
          f"{pf / pl:.1f} 倍")
    print("\n读数:")
    print("  · 事前与事后是两个世界:抽之前,任何一罐的终局份额都对两色公平")
    print("    (边际均匀);抽完之后,几乎每个罐都长出悬殊的份额——「结局在")
    print("    起点上是对称的」,对称的破缺全部由早段的偶然完成")
    print(f"  · 前 10 抽的多数以 {p_early:.0%} 的把握押中终局多数")
    print("    ——早期偶然优势被「按当前比例强化」滚成压倒格局")
    print(f"  · 如实标注:观测意义上后 10 抽的多数同样押中 {p_late:.0%}"
          "(可交换性,先后不可分辨);")
    print("    但干预意义完全不对称——把 10 抽从末段搬到首段,终局>0.9 的概率")
    print(f"    从 {pl:.2f} 跳到 {pf:.2f}:路径依赖的本体在「搬得动过去」,")
    print("    不在「猜得中结局」——这是观测/干预两层的教科书分离")

    # 断言 1:早期锁定
    assert max_dev < 0.02, f"终局份额分箱应近似均匀,最大偏差 {max_dev:.4f}"
    assert p_early > 0.75, f"前 10 抽多数应>0.75 把握押中终局,实测 {p_early:.4f}"
    assert abs(p_early - p_late) < 0.05, "观测意义的前/后 10 抽应对称(交换性)"
    assert pf > 0.6, f"强制首 10 抽的终局>0.9 概率应>0.6,实测 {pf:.4f}"
    assert pl < 0.3, f"强制末 10 抽的终局>0.9 概率应<0.3,实测 {pl:.4f}"
    assert pf > 3 * pl, f"首段干预杠杆应>3 倍,实测 {pf:.4f}/{pl:.4f}"
    print(f"\n✓ 幕一断言通过:终局份额近似均匀(最大偏差 {max_dev:.4f});"
          f"前 10 抽多数押中终局 {p_early:.2f}>0.75;")
    print(f"  强制首 10 抽 vs 末 10 抽,终局>0.9 概率 {pf:.2f} vs {pl:.2f}"
          f"({pf / pl:.1f} 倍)——早期偶然被强化滚成压倒格局")
    return dict(p_early=p_early, pf=pf, pl=pl)


# ==================== 幕二:Arthur 收益递增与技术锁定 ====================

N_ADP = 800       # 采纳者总数
M_LEAD = 100      # 领先格局钉死的采纳者位置
ALPHA = 1.0       # 收益递增强度(网络效应)
XI = 0.2          # 采纳者内在偏好幅度(±,等概率,异质性)
BETA = 6.0        # logit 尺度(选择噪声的倒数)
RUNS2 = 500       # 对称实验罐数
RUNS2G = 200      # δ 网格扫描每档罐数


def arthur_run(rng, n=N_ADP, m0=0, s_init=None, delta=0.0,
               delta_from=None, alpha=ALPHA, beta=BETA, xi=XI):
    """Arthur 采纳模型:收益_A = pref + alpha×A 份额,收益_B = −pref +
    alpha×B 份额 − delta(pref=±xi 异质内在偏好;delta 为 B 的持续质量
    优势,自第 delta_from 个采纳者起生效)。前 m0 个采纳者按 s_init 钉成
    早期份额。返回 A 的终局份额。"""
    if m0:
        na = int(round(s_init * m0))
        nb = m0 - na
    else:
        na = nb = 0
    for t in range(m0, n):
        tot = na + nb
        pref = xi if rng.random() < 0.5 else -xi
        d = delta if (delta and (delta_from is None or t >= delta_from)) else 0.0
        if tot == 0:
            gap = pref - d
        else:
            gap = pref + alpha * (2 * na / tot - 1) - d
        z = -beta * gap
        if z > 60.0:
            z = 60.0
        elif z < -60.0:
            z = -60.0
        if rng.random() < 1.0 / (1.0 + math.exp(z)):
            na += 1
        else:
            nb += 1
    return na / (na + nb)


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 Arthur 收益递增与技术锁定(两技术对称,收益=基础+α×已采纳"
          f"份额,logit 选择,α={ALPHA},ξ=±{XI},β={BETA},n={N_ADP})")
    print("=" * 84)

    # ① 对称设定:锁定对象由早期随机决定
    finals = [arthur_run(random.Random(SEED_BASE + 300000 + k))
              for k in range(RUNS2)]
    lock_a = sum(1 for s in finals if s >= 0.8)
    lock_b = sum(1 for s in finals if s <= 0.2)
    p_a = lock_a / RUNS2
    print(f"\n① 对称 MC({RUNS2} 次):锁定 A(终局份额≥0.8){p_a:.1%},"
          f"锁定 B {lock_b / RUNS2:.1%},")
    print(f"   未及锁定(0.2<份额<0.8){1 - (lock_a + lock_b) / RUNS2:.1%}"
          "——锁定对象约五五开,由早期随机决定")

    # ② 翻盘成本:早期落后 10pp vs 40pp 的 δ 扫描
    deltas = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
    probs = {}
    print(f"\n② B 持续质量优势 δ 与翻盘概率(B 终局份额>0.5,"
          f"早期格局钉在第 {M_LEAD} 个采纳者):")
    print(f"   {'δ':>5} {'落后10pp':>9} {'落后40pp':>9}")
    for i, d in enumerate(deltas):
        row = []
        for j, lead in enumerate((10, 40)):
            s_a = 0.5 + lead / 200.0
            win = sum(arthur_run(random.Random(SEED_BASE + 400000 + i * 7919
                                               + j * 397 + k),
                                 m0=M_LEAD, s_init=s_a, delta=d) < 0.5
                      for k in range(RUNS2G))
            row.append(win / RUNS2G)
        probs[d] = row
        print(f"   {d:>5.2f} {row[0]:>9.1%} {row[1]:>9.1%}")

    def dstar(idx, target=0.75):
        for d in deltas:
            if probs[d][idx] >= target:
                return d
        return None

    d10, d40 = dstar(0), dstar(1)
    p15_10, p15_40 = probs[0.15]
    print(f"   δ*(翻盘概率≥75% 的最小持续质量优势):落后 10pp → {d10},"
          f"落后 40pp → {d40}(深坑价码约 {d40 / d10:.1f} 倍)")
    print(f"   同一价码 δ=0.15:落后 10pp 翻盘 {p15_10:.0%},"
          f"落后 40pp 翻盘 {p15_40:.0%}——价码没变,坑深了就翻不动")

    # ③ 越晚翻盘越贵:领先会被强化继续滚大,再出手同一价码
    snap10 = [ ]  # 10pp 领先放任至 t=400 的份额
    snap40 = [ ]
    for k in range(100):
        rng = random.Random(SEED_BASE + 510000 + k)
        for lead, sink in ((10, snap10), (40, snap40)):
            na = int(round((0.5 + lead / 200.0) * M_LEAD))
            nb = M_LEAD - na
            for t in range(M_LEAD, 400):
                pref = XI if rng.random() < 0.5 else -XI
                gap = pref + ALPHA * (2 * na / (na + nb) - 1)
                if rng.random() < 1.0 / (1.0 + math.exp(-BETA * gap)):
                    na += 1
                else:
                    nb += 1
            sink.append(na / (na + nb))
    m10, m40 = sum(snap10) / len(snap10), sum(snap40) / len(snap40)
    d_demo = 0.35
    p_now = sum(arthur_run(random.Random(SEED_BASE + 600000 + k),
                           m0=M_LEAD, s_init=0.70, delta=d_demo) < 0.5
                for k in range(RUNS2G)) / RUNS2G
    p_late = sum(arthur_run(random.Random(SEED_BASE + 700000 + k),
                            m0=M_LEAD, s_init=0.70, delta=d_demo,
                            delta_from=400) < 0.5
                 for k in range(RUNS2G)) / RUNS2G
    print(f"\n③ 时机对照:10pp 领先放任 300 个采纳者涨到 {m10:.2f},"
          f"40pp 涨到 {m40:.2f}(强化的复利);")
    print(f"   落后 40pp、价码 δ={d_demo} 固定:立即出手翻盘 {p_now:.0%},"
          f"晚 300 个采纳者出手 {p_late:.0%}")
    print("    ——坑不仅在变深,还在自己长深:同样的价码,越晚出手越翻不动")
    print("\n读数:")
    print("  · 对称世界里胜者是掷出来的:两个质量相同的技术,市场不会停在")
    print("    五五开,而是滚向单边锁定;锁的是谁,由早段的随机摇摆决定")
    print("    (实验幕一 Polya 罐的连续版)")
    print("  · 「好技术终将获胜」在收益递增下没有保证:翻盘要的不是一次性")
    print("    优势,是持续的质量差距;且领先越深、出手越晚,价码越高")
    print("    ——这正是 QWERTY 叙事的机制本体(注:QWERTY 相对劣势的幅度")
    print("    在文献中有 Liebowitz-Margolis 争议,按通说处理:机制成立,")
    print("    史实幅度另议)")

    # 断言 2:锁定与翻盘成本
    assert 0.42 < p_a < 0.58, f"对称 MC 锁 A 应约 50%,实测 {p_a:.3f}"
    assert (lock_a + lock_b) / RUNS2 > 0.85, "绝大多数游程应滚向单边锁定"
    assert probs[0.0][0] < 0.25, "δ=0 时落后方翻盘应困难(强化在起作用)"
    assert d10 is not None and d10 > 0, "浅坑也应有正的翻盘价码"
    assert d40 is not None and d40 >= 2.5 * d10, (
        f"深坑 δ* 应≥2.5 倍浅坑,实测 {d40} vs {d10}")
    assert p15_10 - p15_40 > 0.5, (
        f"同一价码 δ=0.15 浅坑/深坑翻盘率应差>0.5,实测 {p15_10:.2f} vs {p15_40:.2f}")
    assert 0.6 < m10 < 0.8 and m40 > 0.8, (
        f"领先应被强化滚大(10pp→{m10:.2f},40pp→{m40:.2f})")
    assert p_now - p_late > 0.5, (
        f"同样的 δ 立即出手应显著优于晚出手,实测 {p_now:.2f} vs {p_late:.2f}")
    print(f"\n✓ 幕二断言通过:对称锁定 A/B {p_a:.0%}/{lock_b / RUNS2:.0%}"
          f"(对象由早期随机决定);δ* {d40}≥2.5×{d10},")
    print(f"  δ=0.15 翻盘 {p15_10:.0%} vs {p15_40:.0%};10pp/40pp 领先 300 人后"
          f"滚到 {m10:.2f}/{m40:.2f},同一价码立即 {p_now:.0%} vs 晚出手 "
          f"{p_late:.0%}——越晚翻盘越贵")
    return dict(p_a=p_a, d10=d10, d40=d40, m10=m10, m40=m40,
                p_now=p_now, p_late=p_late)


# ==================== 幕三:危机的时间聚集 ====================

STEPS = 24000     # 时间轴步数
BINW = 240        # 计数箱宽(步)
T = 50.0          # 承载力阈值
PHI = 0.20        # 危机后压力按比例部分释放的保留系数
SIGMA = 1.5       # 噪声幅度
MU_LOW = -0.15    # 承平纪元漂移(压力耗散,非负地板)
P_LH = 0.002      # 承平→高压 切换率(每步)
P_HL = 0.0035     # 高压→承平 切换率(每步)
RUNS3 = 40        # 每配置游程数


def crisis_times(rng, steps=STEPS, const_mu=None, mu_high=0.6):
    """压力 S 做带漂移随机游走:S += μ + σε,S<0 取 0(压力非负);S≥T
    记一次危机并按比例部分释放(S←φ·S)。纪元版:μ 在承平(MU_LOW,耗散)
    与高压(mu_high)间按慢马尔可夫切换;定时器版:const_mu 恒定。
    返回危机时刻列表。"""
    s = 0.0
    high = False
    times = []
    for t in range(steps):
        if const_mu is not None:
            mu = const_mu
        else:
            if high:
                if rng.random() < P_HL:
                    high = False
            elif rng.random() < P_LH:
                high = True
            mu = mu_high if high else MU_LOW
        s += mu + SIGMA * rng.gauss(0.0, 1.0)
        if s < 0.0:
            s = 0.0
        if s >= T:
            times.append(t)
            s = PHI * s
    return times


def fano(times, steps=STEPS, bin_w=BINW):
    """一条历史的丛集指数:每箱危机计数的方差/均值(泊松=1)。"""
    nbin = steps // bin_w
    counts = [0] * nbin
    for t in times:
        counts[t // bin_w] += 1
    m = sum(counts) / nbin
    v = sum((c - m) ** 2 for c in counts) / (nbin - 1)
    return v / m


def act3():
    print("\n" + "=" * 84)
    print("幕三 危机的时间聚集(压力=带漂移随机游走,阈值 T=50 爆发并按"
          f"比例释放 φ={PHI};承平 μ={MU_LOW} 耗散/高压纪元慢切换;"
          f"{RUNS3} 条历史×{STEPS} 步)")
    print("=" * 84)

    runs_lo = [crisis_times(random.Random(SEED_BASE + 800000 + k), mu_high=0.6)
               for k in range(RUNS3)]
    runs_hi = [crisis_times(random.Random(SEED_BASE + 900000 + k), mu_high=1.2)
               for k in range(RUNS3)]
    runs_clk = [crisis_times(random.Random(SEED_BASE + 960000 + k), const_mu=1.2)
                for k in range(RUNS3)]
    f_lo = sum(fano(ts) for ts in runs_lo) / RUNS3
    f_hi = sum(fano(ts) for ts in runs_hi) / RUNS3
    f_clk = sum(fano(ts) for ts in runs_clk) / RUNS3
    # 泊松对照:每条历史按同总数把危机时刻均匀重撒
    rng = random.Random(SEED_BASE + 970000)
    f_po = 0.0
    for ts in runs_lo + runs_hi:
        uni = [rng.randrange(STEPS) for _ in range(len(ts))]
        f_po += fano(uni)
    f_po /= 2 * RUNS3
    n_lo = sum(len(ts) for ts in runs_lo) / RUNS3
    n_hi = sum(len(ts) for ts in runs_hi) / RUNS3

    print(f"\n纪元版(高压 μ=0.6):场均危机 {n_lo:.1f} 次,"
          f"平均丛集指数(方差/均值)={f_lo:.2f}")
    print(f"纪元版(高压 μ=1.2):场均危机 {n_hi:.1f} 次,"
          f"平均丛集指数={f_hi:.2f}")
    print(f"泊松对照(同总数均匀重撒):平均丛集指数={f_po:.2f}(理论 1)")
    print(f"定时器版(恒定强漂移 μ=1.2,无纪元):平均丛集指数={f_clk:.2f}")
    # 样例历史的时间条(直观看到丛集)
    strip = [0] * (STEPS // BINW)
    for t in runs_hi[0]:
        strip[t // BINW] += 1
    line = "".join("." if c == 0 else ("o" if c == 1 else "*") for c in strip)
    print(f"\n一条样例时间轴(高压 μ=1.2,每字符 {BINW} 步;"
          f".=平静 o=1 次 *=≥2 次):")
    for i in range(0, len(line), 100):
        print(f"   {line[i:i + 100]}")
    print("\n读数:")
    print("  · 危机不是均匀撒在时间轴上:压力在承平纪元耗散归零,在高压纪元")
    print("    爬升、越过临界段后连环爆发——丛集指数>1 是「大变动的年代」")
    print("    的统计指纹")
    print(f"  · 高压纪元漂移从 0.6 提到 1.2,丛集指数 {f_lo:.2f}→{f_hi:.2f}:")
    print("    纪元内重建越快,每簇越密,聚集越强")
    print(f"  · 如实标注:恒定强漂移(无纪元)给出 {f_clk:.2f}≪1——「定时器」")
    print("    式的规律爆发;丛集指向的是纪元结构而非漂移本身。这正是断续")
    print("    均衡的最小机器:长期稳态(承平)+快速变迁(高压纪元临界段)")
    print("  · 与 Goldstone 的人口-结构论同构:压力(人口/财政/生计)累积到")
    print("    承载力附近,小扰动连环触发——革命浪潮丛集在 17 世纪危机、")
    print("    一战后的年代之类的「世界时间」里,不是均匀分布的背景噪声")

    # 断言 3:丛集
    assert f_lo > 1.15, f"纪元版丛集指数应明显>1,实测 {f_lo:.3f}"
    assert f_hi > f_lo + 0.3, (
        f"高压漂移更大应聚集更强,实测 {f_hi:.3f} vs {f_lo:.3f}")
    assert 0.8 < f_po < 1.2, f"泊松对照应在 1 附近,实测 {f_po:.3f}"
    assert f_clk < 0.6, f"定时器版应欠散布(<1),实测 {f_clk:.3f}"
    assert n_hi > n_lo, "高压更强时危机总数应更多(压力注入更快)"
    print(f"\n✓ 幕三断言通过:丛集指数 纪元版 {f_lo:.2f}/{f_hi:.2f}>1"
          f"(高压更强→聚集更强),泊松对照 {f_po:.2f}≈1,定时器 {f_clk:.2f}≪1")
    print("  ——大变动的年代丛集在压力纪元的临界段,不是均匀撒在历史里")
    return dict(f_lo=f_lo, f_hi=f_hi, f_po=f_po, f_clk=f_clk)


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① Polya 早期锁定:终局份额边际近似均匀(起点对称),前 10 抽多数")
    print("     以>0.75 把握押中终局;强制首 10 抽 vs 末 10 抽,终局>0.9 概率")
    print("     差约一个数量级——早期偶然被强化滚成压倒格局(路径依赖的")
    print("     最小机器);观测对称/干预不对称如实分离")
    print("  ② Arthur 收益递增:对称技术锁定对象约五五开(由早期随机决定);")
    print("     深坑翻盘价码 δ*≥2.5 倍浅坑,领先还在被强化滚大,同样的价码")
    print("     越晚出手越翻不动——胜者不必是优者,早到本身就是优势")
    print("  ③ 危机时间聚集:危机计数过度散布(丛集指数>1,泊松=1),聚集强度")
    print("     随高压纪元漂移增大;恒定漂移只出定时器(≪1)——大事件的丛集")
    print("     是压力纪元的指纹(断续均衡的最小机器)")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
