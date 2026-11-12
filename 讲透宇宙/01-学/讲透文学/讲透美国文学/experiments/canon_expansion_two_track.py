# -*- coding: utf-8 -*-
"""正典扩张-畅销正典双轨-族裔双市场三律模拟:美国文学家族实验(GB/T 75071)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(三条结构引擎的
严格可构造性)、04-美国文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260909 可复现。

风格化声明:席位份额、市场参数、生涯风险均为机制研究用的风格化设定,
断言针对"机制模式"(棘轮再分配/双轨筛选/双市场对冲),不是史实拟合;
作家作品评述一律通说文学史口径(运动年代与正典化标志按通说)。

三幕:
  幕一 正典战争的席位再分配(选本/课程正典随批评运动重排):
      以 1940-2020 九个十年观察点模拟一部"美国文学选本"的 100 席份额:
      旧正典(白人男性核心)初始 0.78 席;多元主义运动强度 M(t) 自 1960s
      升起(民权与族裔研究),1990s 达峰(正典战争通说峰值),其后回落;
      运动越强,白人男性板块按运动强度放出席位(但旧正典有不破防线,
      布鲁姆《西方正典》1994 一系的抵抗,通说);边缘群体按"组织化推力×
      席位缺口"竞争新席位;已得席位因课程与招聘建制而惯性保有。
      棘轮模型(泄漏 4%/十年)对照钟摆模型(泄漏 40%,运动退潮即回吐)。
      断言:①旧正典份额大幅下降但不清零(全程≥防线 0.42——被置换不阵亡)
            ②新增席位集中于此前零席位群体(非裔/亚裔/拉丁裔/原住民合计
              增量占边缘总增量≥70%),且运动峰值后一代(1990-2020)仍
              继续增长(制度化惯性:招聘与课程表的滞后传递)
            ③棘轮非钟摆:棘轮模型下零席位群体份额近单调不减,终值≥
              钟摆模型终值的 1.6 倍;钟摆模型峰值后真实回吐。
  幕二 畅销-正典双轨制(同期销量 vs 长期在版):
      600 部风格化书目:质量 q 与市场契合 m 独立;"当年销量指数"
      spike=0.10q+0.90m+噪声(市场主要投题材与时机);在版以每十年存活率
      p=0.55+0.35q 追踪(存续主要靠质量);正典化
      P=σ(−5.0+2.6q+0.38·在版十年数)(选目委员会看得见质量与存续,
      看不见当年橱窗)。
      断言:①同期畅销对正典席位预测力弱:corr(spike, 入典)≤0.30,当年
              畅销前十组的入典率≤其余组的 1.6 倍,入典者中当年畅销前十
              占比≤0.20——当年畅销≠入典
            ②长期在版与正典化强相关:corr(在版, 入典)≥0.50,在版最久
              四分位入典率≥最短四分位的 3.5 倍,在版满十年组入典率≥
              当年畅销前十组的 1.8 倍——正典筛选的不是销量是存续:
              市场投短期票,正典投长期票。
  幕三 族裔文学的双市场(主流市场×族裔社群市场):
      两个世代各 1200 位族裔背景作家×6 期(每期五年)生涯:封闭期
      (开放度 0.15)与开放期(开放度 0.85,承接幕一);策略三种——
      双市场(拥抱族裔标签,双渠道发行)/去标签主流(淡化标签入主流)/
      族裔单市场;主流渠道收入高但每期 14% 被弃,族裔渠道稳但薄
      (每期 5% 被弃);双市场精力分流(各按 0.8q);资源转负即生涯终止。
      存活者正典化:带标签 P=σ(−3.6+3.0q+2.4·开放度),去标签
      P=σ(−2.75+3.0q)——开放期标签是资本,封闭期标签是债务。
      断言:①双市场作者生涯存续率≥两类单市场+0.08(两个世代皆然)——对冲
            ②标签双面性:封闭期带标签入典率<去标签(标签=债务);开放期
              带标签≥去标签的 1.6 倍(标签=资本)——莫里森路径(拥抱标签
              成正典)与汤婷路径(淡化标签入主流)并存,谁优取决于正典
              的开放期。

实验分工声明:英国文学家族实验管单一正典内的马太动力学(放大+范式
转移只动中游),本家族管正典的再分配(席位在群体间怎么流);法国文学
家族管场域建制(宣言/加冕/级联)——三层不同题,互不重复。

跑法: python -u experiments/canon_expansion_two_track.py
"""

import math
import random
import statistics

SEED = 20260909  # 建族日作种子,可复现


# ==================== 幕一:正典战争的席位再分配 ====================

DECADES = list(range(1940, 2021, 10))
# 多元主义运动强度(风格化):1960s 民权与族裔研究起,1990s 正典战争峰值(通说),后回落
M_MOVE = [0.00, 0.00, 0.15, 0.45, 0.75, 1.00, 0.60, 0.40, 0.25]
INIT = {"旧正典": 0.78, "外围白男": 0.10, "白人女性": 0.12,
        "非裔": 0.00, "亚裔": 0.00, "拉丁裔": 0.00, "原住民": 0.00}
W_PUSH = {"白人女性": 0.55, "非裔": 0.95, "亚裔": 0.45,
          "拉丁裔": 0.40, "原住民": 0.30}      # 组织化推力(风格化)
EDGE = list(W_PUSH)
ZERO = ["非裔", "亚裔", "拉丁裔", "原住民"]    # 1940 年零席位群体
FLOOR_OLD, FLOOR_PER = 0.42, 0.06              # 旧正典防线 / 外围底线
RELEASE = 0.16                                 # 白男板块每十年按运动强度放出的份额
LEAK_RATCHET, LEAK_PENDULUM = 0.04, 0.40       # 棘轮惯性保有 / 钟摆回吐系数


def decade_step(shares, M, leak, rng):
    """推进十年:白男板块按运动强度放出席位(不破防线),边缘按压力竞争;
    运动退潮时已得席位按 leak 比例回吐(棘轮小泄,钟摆大泄)。"""
    old, per = shares["旧正典"], shares["外围白男"]
    block = old + per
    don_old, don_per = max(0.0, old - FLOOR_OLD), max(0.0, per - FLOOR_PER)
    release = min(RELEASE * M * block * rng.uniform(0.92, 1.08),
                  don_old + don_per)
    take_old = release * don_old / (don_old + don_per) if don_old + don_per > 0 else 0.0
    take_per = release - take_old
    pres = {g: W_PUSH[g] * max(0.05, 1.0 - shares[g]) * rng.uniform(0.90, 1.10)
            for g in EDGE}
    tot = sum(pres.values())
    new = dict(shares)
    new["旧正典"] = old - take_old
    new["外围白男"] = per - take_per
    give_back = 0.0
    for g in EDGE:
        gain = release * pres[g] / tot
        leak_amt = leak * (1.0 - M) * max(0.0, shares[g] - INIT[g])
        new[g] = shares[g] + gain - leak_amt
        give_back += leak_amt
    new["旧正典"] += give_back          # 回吐的席位由旧正典收回
    new["旧正典"] = min(new["旧正典"], INIT["旧正典"])  # 不超过初始
    return new


def trajectory(leak, rng):
    shares = dict(INIT)
    traj = [dict(shares)]
    for M in M_MOVE[1:]:
        shares = decade_step(shares, M, leak, rng)
        traj.append(dict(shares))
    return traj


def act1():
    print("=" * 84)
    print("幕一 正典战争的席位再分配: 100 席选本份额 1940-2020, 运动强度 M(t) 1990s 达峰")
    print("=" * 84)
    rng = random.Random(SEED)
    traj = trajectory(LEAK_RATCHET, rng)
    pend = trajectory(LEAK_PENDULUM, random.Random(SEED))  # 同随机流, 纯机制对照

    print(f"\n{'年份':>4} {'运动M':>5} {'旧正典':>7} {'外围白男':>7} {'白人女性':>7} "
          f"{'非裔':>6} {'亚裔':>6} {'拉丁裔':>6} {'原住民':>6}  零席位组合计")
    for t, y in enumerate(DECADES):
        s = traj[t]
        z = sum(s[g] for g in ZERO)
        print(f"{y:>4} {M_MOVE[t]:>5.2f} {s['旧正典']:>7.3f} {s['外围白男']:>7.3f} "
              f"{s['白人女性']:>7.3f} {s['非裔']:>6.3f} {s['亚裔']:>6.3f} "
              f"{s['拉丁裔']:>6.3f} {s['原住民']:>6.3f}  {z:.3f}")

    core = [s["旧正典"] for s in traj]
    zero = [sum(s[g] for g in ZERO) for s in traj]
    zero_pend = [sum(s[g] for g in ZERO) for s in pend]
    t_peak = M_MOVE.index(max(M_MOVE))
    edge_gain = sum(traj[-1][g] - INIT[g] for g in EDGE)
    zero_gain = zero[-1] - zero[0]

    print(f"\n[1a] 旧正典(白人男性核心): 0.780 → {core[-1]:.3f} "
          f"(让出 {core[0] - core[-1]:.3f}, 全程最低 {min(core):.3f}, 防线 {FLOOR_OLD})")
    print("读数: 大幅让位但不清零——席位被置换, 名单没阵亡(布鲁姆防线:")
    print("      《西方正典》1994 一系的抵抗把跌幅钉在防线上, 通说口径)")
    print(f"\n[1b] 零席位群体(非裔/亚裔/拉丁裔/原住民): 0.000 → {zero[-1]:.3f}, "
          f"占边缘总增量 {zero_gain / edge_gain:.1%}")
    print(f"      峰值年({DECADES[t_peak]})读数 {zero[t_peak]:.3f} → "
          f"2020 读数 {zero[-1]:.3f}: 峰值后一代({DECADES[t_peak]}-2020)仍增 "
          f"{zero[-1] - zero[t_peak]:.3f}, 为峰值前增量({zero[t_peak]:.3f})的 "
          f"{(zero[-1] - zero[t_peak]) / zero[t_peak]:.0%}")
    print("读数: 新席位集中于此前零席位群体;运动退潮后增长靠课程与招聘的")
    print("      滞后传递续命一代——正典扩张的引擎是建制惯性, 不只风口")
    print(f"\n[1c] 棘轮 vs 钟摆(零席位群体份额, 峰值后轨迹):")
    print(f"      棘轮(泄漏4%/十年): 1990 {zero[t_peak]:.3f} → 2000 {zero[t_peak+1]:.3f} "
          f"→ 2010 {zero[t_peak+2]:.3f} → 2020 {zero[-1]:.3f}(近单调不减)")
    print(f"      钟摆(泄漏40%/十年): 1990 {zero_pend[t_peak]:.3f} → 2020 {zero_pend[-1]:.3f}"
          f"(真实回吐 {zero_pend[-1] - zero_pend[t_peak]:+.3f})")
    print(f"      终值比 棘轮/钟摆 = {zero[-1] / zero_pend[-1]:.2f}×")
    print("读数: 若正典是钟摆, 退潮即回 1970s;实测形状是棘轮——席位到手")
    print("      便建制化(课表/教职/选目), 回吐几乎不发生")

    # 断言 ①: 旧正典下降但不清零
    assert core[0] - core[-1] >= 0.28, f"旧正典应大幅让位≥0.28, 实测 {core[0]-core[-1]:.3f}"
    assert min(core) >= FLOOR_OLD - 0.005, \
        f"旧正典任意十年都不应破防线 0.42, 实测最低 {min(core):.3f}"
    # 断言 ②: 新增席位集中于零席位群体, 峰值后仍延续一代
    assert zero_gain / edge_gain >= 0.70, \
        f"零席位群体应占边缘增量≥70%, 实测 {zero_gain/edge_gain:.1%}"
    assert zero[-1] - zero[t_peak] >= 0.30 * zero[t_peak], \
        "峰值后一代仍应增长(≥峰值增量的 30%)"
    assert all(zero[t + 1] > zero[t] - 0.004 for t in range(t_peak, len(zero) - 1)), \
        "棘轮模型下零席位群体份额应近单调不减"
    # 断言 ③: 棘轮非钟摆
    assert zero[-1] >= 1.6 * zero_pend[-1], \
        f"棘轮终值应≥钟摆的 1.6 倍, 实测 {zero[-1]/zero_pend[-1]:.2f}×"
    assert zero_pend[-1] < zero_pend[t_peak], "钟摆模型峰值后应真实回吐"
    print(f"\n✓ 幕一断言通过: 旧正典 0.780→{core[-1]:.3f} 不清零;零席位群体 "
          f"0→{zero[-1]:.3f}(占增量 {zero_gain/edge_gain:.0%}, 峰值后仍+"
          f"{zero[-1]-zero[t_peak]:.3f});棘轮/钟摆={zero[-1]/zero_pend[-1]:.1f}×"
          "——正典扩张是棘轮不是钟摆")


# ==================== 幕二:畅销-正典双轨制 ====================

N_BOOKS2 = 600
HORIZON2 = 10          # 在版追踪十个十年
B0C, BQC, BSC = -5.0, 2.6, 0.38   # 正典化 logits: 截距/质量/在版十年数


def pearson(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    sy = math.sqrt(sum((b - my) ** 2 for b in ys))
    return cov / (sx * sy)


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 畅销-正典双轨制: {N_BOOKS2} 部书目, spike=0.10q+0.90m+噪声, "
          f"在版 p=0.55+0.35q, 入典 P=σ({B0C}+{BQC}q+{BSC}·在版)")
    print("=" * 84)
    rng = random.Random(SEED)
    books = []
    for _ in range(N_BOOKS2):
        q = rng.random()                            # 作品质量(风格化)
        m = rng.random()                            # 市场契合(题材/时机/可读性)
        spike = 0.10 * q + 0.90 * m + rng.gauss(0.0, 0.05)   # 当年销量指数
        alive, inprint = True, 0
        for _ in range(HORIZON2):                   # 逐十年在版追踪
            if alive and rng.random() < 0.55 + 0.35 * q:
                inprint += 1
            else:
                alive = False
        canon = rng.random() < 1.0 / (1.0 + math.exp(
            -(B0C + BQC * q + BSC * inprint)))
        books.append({"q": q, "spike": spike, "inp": inprint, "canon": canon})

    spikes = [b["spike"] for b in books]
    inps = [b["inp"] for b in books]
    canons = [1 if b["canon"] else 0 for b in books]
    r_spike = pearson(spikes, canons)
    r_inp = pearson(inps, canons)
    n_canon = sum(canons)

    order_s = sorted(range(N_BOOKS2), key=lambda i: -spikes[i])
    top_s = set(order_s[:N_BOOKS2 // 10])           # 当年销量前十组
    order_i = sorted(range(N_BOOKS2), key=lambda i: -inps[i])
    q4 = N_BOOKS2 // 4
    top_i, bot_i = set(order_i[:q4]), set(order_i[-q4:])   # 在版最久/最短四分位
    full_i = {i for i in range(N_BOOKS2) if inps[i] == HORIZON2}  # 在版满十年组

    rate = lambda idx: (sum(canons[i] for i in idx) / len(idx)) if idx else 0.0
    r_top_s, r_rest_s = rate(top_s), rate(set(range(N_BOOKS2)) - top_s)
    r_top_i, r_bot_i = rate(top_i), rate(bot_i)
    r_full_i = rate(full_i)
    frac_canon_top_s = sum(1 for i in top_s if canons[i]) / n_canon

    print(f"\n入典率总体: {n_canon / N_BOOKS2:.3f} ({n_canon}/{N_BOOKS2})")
    print(f"[2a] 同期销量 vs 入典:")
    print(f"  corr(当年销量, 入典) = {r_spike:+.3f}")
    print(f"  当年畅销前十组入典率 {r_top_s:.3f} vs 其余 {r_rest_s:.3f} "
          f"(加成 ×{r_top_s / r_rest_s:.2f})")
    print(f"  入典者中当年进畅销前十的占比 {frac_canon_top_s:.1%}")
    print("读数: 当年橱窗几乎不带正典票——市场主要投题材与时机(m 占 spike 九成),")
    print("      而选目委员会看得见的是质量与存续, 看不见当年销量")
    print(f"\n[2b] 长期在版 vs 入典:")
    print(f"  corr(在版十年数, 入典) = {r_inp:+.3f}")
    print(f"  在版最久四分位入典率 {r_top_i:.3f} vs 最短四分位 {r_bot_i:.3f} "
          f"(×{r_top_i / max(r_bot_i, 1e-9):.1f})")
    print(f"  在版满十年组({len(full_i)} 部)入典率 {r_full_i:.3f} vs "
          f"当年畅销前十组 {r_top_s:.3f} (×{r_full_i / r_top_s:.2f})")
    print("读数: 正典筛选的不是销量是存续——在版就是被一代代读者与课堂持续")
    print("      投票;市场投短期票, 正典投长期票(《了不起的盖茨比》式: 初版")
    print("      平平, 二战军队版广发, 身后入典, 通说口径)")

    assert abs(r_spike) <= 0.30, f"corr(spike,入典)应≤0.30, 实测 {r_spike:+.3f}"
    assert r_top_s <= 1.60 * r_rest_s, "当年畅销前十组加成应≤1.6×(预测力弱)"
    assert frac_canon_top_s <= 0.20, "入典者中当年畅销前十占比应≤20%"
    assert r_inp >= 0.50, f"corr(在版,入典)应≥0.50, 实测 {r_inp:+.3f}"
    assert r_top_i >= 3.5 * r_bot_i, \
        f"在版最久四分位加成应≥3.5×, 实测 {r_top_i/max(r_bot_i,1e-9):.1f}×"
    assert r_full_i >= 1.8 * r_top_s, \
        f"满十年在版组入典率应≥当年畅销前十组的 1.8×, 实测 {r_full_i/r_top_s:.2f}×"
    print(f"\n✓ 幕二断言通过: corr(当年销量,入典)={r_spike:+.2f} vs "
          f"corr(在版,入典)={r_inp:+.2f};在版最久/最短四分位 "
          f"{r_top_i/r_bot_i:.1f}× vs 当年畅销加成 {r_top_s/r_rest_s:.2f}×"
          "——市场投短期票, 正典投长期票")


# ==================== 幕三:族裔文学的双市场 ====================

N_AUTH, N_PERIODS = 1200, 6          # 每世代作家数 / 生涯期数(五年一期)
OPEN_CLOSED, OPEN_OPEN = 0.15, 0.85  # 封闭期/开放期正典开放度(承接幕一)
DROP_MAIN, DROP_ETH = 0.14, 0.05     # 主流/族裔渠道每期被弃概率
SPEND = 2.0                          # 每期生涯开销
B0L, BQL, BOL = -3.6, 3.0, 2.4       # 带标签正典化: 截距/质量/开放度
B0D, BQD = -2.75, 3.0                # 去标签正典化: 截距/质量


def career(strategy, q, rng):
    """一个生涯: 返回 (存续?, 带标签?, 质量)。资源转负即终止。
    双市场精力分流: 两渠道各按 0.8q;单市场全速。"""
    res, main_on, eth_on = 3.0, strategy != "族裔单市场", strategy != "去标签主流"
    labeled = strategy != "去标签主流"
    for _ in range(N_PERIODS):
        if main_on and rng.random() < DROP_MAIN:
            main_on = False
        if eth_on and rng.random() < DROP_ETH:
            eth_on = False
        income = 0.0
        if main_on:
            qm = 0.8 * q if strategy == "双市场" else q
            income += rng.gauss(1.3 + 2.2 * qm, 1.2)
        if eth_on:
            qe = 0.8 * q if strategy == "双市场" else q
            income += rng.gauss(1.1 + 1.3 * qe, 0.6)
        res += income - SPEND
        if res < 0 or not (main_on or eth_on):
            return False, labeled, q
    return True, labeled, q


def one_cohort(openness, de_label_share, dual_share, rng):
    """一个世代: 按份额分配策略, 跑生涯, 存活者掷正典化。"""
    lab_c = lab_n = del_c = del_n = 0
    surv = {"双市场": [0, 0], "去标签主流": [0, 0], "族裔单市场": [0, 0]}
    for _ in range(N_AUTH):
        u = rng.random()
        strategy = ("去标签主流" if u < de_label_share
                    else "双市场" if u < de_label_share + dual_share else "族裔单市场")
        q = rng.random()
        alive, labeled, q = career(strategy, q, rng)
        surv[strategy][1] += 1
        surv[strategy][0] += alive
        if not alive:
            continue
        if labeled:
            p = 1.0 / (1.0 + math.exp(-(B0L + BQL * q + BOL * openness)))
            lab_n += 1
            lab_c += rng.random() < p
        else:
            p = 1.0 / (1.0 + math.exp(-(B0D + BQD * q)))
            del_n += 1
            del_c += rng.random() < p
    return surv, (lab_c, lab_n), (del_c, del_n)


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 族裔文学的双市场: 两世代×{N_AUTH} 作家×{N_PERIODS} 期生涯, "
          f"主流渠道被弃{DROP_MAIN:.0%}/期 vs 族裔{DROP_ETH:.0%}/期")
    print(f"      带标签入典 P=σ({B0L}+{BQL}q+{BOL}·开放度) vs "
          f"去标签 P=σ({B0D}+{BQD}q)")
    print("=" * 84)
    rng = random.Random(SEED)
    cohorts = [
        ("封闭期(开放度0.15, 去标签62%·双市场23%·单市场15%)",
         OPEN_CLOSED, 0.62, 0.23),
        ("开放期(开放度0.85, 去标签35%·双市场45%·单市场20%)",
         OPEN_OPEN, 0.35, 0.45),
    ]
    results = {}
    for name, open_, de_share, dual_share in cohorts:
        surv, (lab_c, lab_n), (del_c, del_n) = one_cohort(open_, de_share, dual_share, rng)
        results[open_] = {"surv": surv, "lab": lab_c / lab_n, "del": del_c / del_n,
                          "lab_n": lab_n, "del_n": del_n}
        print(f"\n[{name.split('(', 1)[0]}]")
        for s in ("双市场", "去标签主流", "族裔单市场"):
            a, n = surv[s]
            print(f"  {s:<6} 存续率 {a / n:.3f} ({a}/{n})")
        print(f"  带标签入典率 {lab_c / lab_n:.3f} ({lab_c}/{lab_n}) vs "
              f"去标签 {del_c / del_n:.3f} ({del_c}/{del_n}) "
              f"(×{lab_c / lab_n / (del_c / del_n):.2f})")

    for key, tag in ((OPEN_CLOSED, "封闭期"), (OPEN_OPEN, "开放期")):
        s = results[key]["surv"]
        dual = s["双市场"][0] / s["双市场"][1]
        best_single = max(s["去标签主流"][0] / s["去标签主流"][1],
                          s["族裔单市场"][0] / s["族裔单市场"][1])
        assert dual >= best_single + 0.08, \
            f"{tag}: 双市场存续率应≥单市场最优+0.08, 实测 {dual:.3f} vs {best_single:.3f}"
    lc, dc = results[OPEN_CLOSED]["lab"], results[OPEN_CLOSED]["del"]
    lo, do = results[OPEN_OPEN]["lab"], results[OPEN_OPEN]["del"]
    assert lc < dc, "封闭期标签应是债务(带标签入典率<去标签)"
    assert lo >= 1.6 * do, \
        f"开放期标签应是资本(带标签入典率≥去标签 1.6×), 实测 {lo/do:.2f}×"
    print("\n读数:")
    print("  · 双市场=对冲: 两条渠道一条被弃仍有饭吃, 两个世代存续率都高出")
    print("    单市场最优 8 个百分点以上——族裔社群市场是生涯保险")
    print(f"  · 标签双面性: 封闭期带标签 {lc:.3f} < 去标签 {dc:.3f}(标签=债务,")
    print(f"    风格化去标记的动机);开放期带标签 {lo:.3f} ≥ 去标签 {do:.3f} 的 "
          f"{lo/do:.1f} 倍(标签=资本)")
    print("  · 莫里森路径(拥抱标签成正典)与汤婷路径(淡化标签入主流)并存,")
    print("    谁优不取决于作家, 取决于正典处在开放期还是封闭期(承接幕一)")
    print(f"\n✓ 幕三断言通过: 双市场对冲(两世代存续差≥0.08);标签双面性"
          f"(封闭期 {lc:.2f}<{dc:.2f} 债务, 开放期 {lo:.2f}={lo/do:.1f}×{do:.2f} 资本)")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 席位再分配: 旧正典大幅让位但不清零(防线之上——被置换不阵亡);")
    print("     新增席位集中于此前零席位群体且峰值后仍延续一代——正典扩张")
    print("     是棘轮不是钟摆(与英国文学马太实验分工: 那边管单一正典放大,")
    print("     本家族管席位在群体间的再分配)")
    print("  ② 畅销-正典双轨: 当年销量对入典预测力弱(corr≤0.30), 长期在版")
    print("     强相关(≥0.50)且加成数倍于同期畅销——市场投短期票, 正典投")
    print("     长期票: 正典筛选的不是销量是存续")
    print("  ③ 族裔双市场: 双市场存续率对冲性高于两类单市场;标签在封闭期是")
    print("     债务、开放期是资本——莫里森路径与汤婷路径并存, 胜负取决于")
    print("     正典的开放期")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
