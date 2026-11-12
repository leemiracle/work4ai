# -*- coding: utf-8 -*-
"""军事社会学家族实验:组织、信任与再融入的三个最小模型(纯社会面)。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(三张结构卡)、
04-军事社会学转代码.md(三条走廊)的配套实验。纯标准库
(math/random/statistics),无第三方依赖。**写作红线的技术版:一切参数
皆为玩具参数,不建模任何真实军队的人事、编制或政策数据。**

三幕:
  幕一 规则化晋升的社会流动(Stouffer/Moskos 线通说:军队作为社会
      流动通道的组织机制):
      两臂对照,同一批人(能力共享)、同一机会总量(每轮晋升配额相同):
        军队臂=规则化晋升——按「绩效+资历」的透明队列打分,出身权重 0;
        民间臂=网络化晋升——得分含社交网络中心度,出身通过网络分层
        间接起效,且晋升反过来扩张网络(累积优势)。
      断言:底层出身个体在军队臂的期望终秩显著高于民间臂、方差更小,
      出身对终秩的解释力(组间 R²)军队臂≈0 而民间臂可观——
      「规则把出身从机会分配里挤出去」;总机会不变,变的是分配。
  幕二 军民接触与信任(接触假说的最小模型):
      军民两群体,接触率 c(志愿役社会 c 下降);态度更新=直接接触
      (向合作性接触的高信任锚移动)+媒体框架(两群体异质框架锚),
      按 c 与 1-c 加权。断言:c 高时两群体信任收敛到高值;c→0 时
      信任分化取决于框架差(框架同质则不分化但到不了高信任)——
      「信任的来源从握手换成屏幕」;平均信任随 c 单调上升。
  幕三 退伍再融入的关键期(四状态马尔可夫链):
      状态=未就业/教育进修/就业/稳定(吸收态);上行转移概率随退役后
      年份 t 衰减(技能贴现/网络冷却)。支持性干预(上行概率×1.6)
      同为两年:头两年(t=1,2) vs 第 3-4 年(t=3,4)。
      断言:头两年干预的 5 年稳定率>第 3-4 年才干预,且其对基线的
      边际贡献更大;晚干预仍优于基线——「政策杠杆支点在头两年」。
      解析递归(分布层)与蒙特卡洛队列双证。

跑法: python3 -u experiments/org_and_reintegration.py
"""

import math
import random
import statistics

RNG_SEED = 20260947   # 固定随机种子(家族建族日风格)


# ==================== 幕一:规则化晋升的社会流动 ====================


def act1():
    print("=" * 84)
    print("幕一 规则化晋升的社会流动:规则把出身从机会分配里挤出去")
    print("=" * 84)
    rng = random.Random(RNG_SEED)

    n = 6000                      # 同一批人,两臂共用能力
    origins = ["底层", "中间", "高层"]
    weights = [0.40, 0.35, 0.25]  # 出身结构(玩具参数)
    origin_of = []
    for name, w in zip(origins, weights):
        origin_of.extend([name] * int(n * w))
    origin_of.extend(["底层"] * (n - len(origin_of)))   # 补齐
    ability = [rng.gauss(0.0, 1.0) for _ in range(n)]   # 能力两臂共享
    origin_center = {"底层": -0.7, "中间": 0.0, "高层": +0.7}

    rounds, quota_frac = 10, 0.30

    def run_arm(arm):
        """arm='military':得分=能力+资历队列(透明规则);arm='civilian':
        得分=能力+网络中心度(起点由出身分层,且网络随机遇与晋升累积)。"""
        rank = [0] * n
        wait = [0] * n                       # 资历:未获晋升的等待年数(军队臂透明队列)
        centrality = [origin_center[o] for o in origin_of]  # 网络起点由出身分层(民间臂)
        quota = int(quota_frac * n)
        for _ in range(rounds):
            if arm == "military":
                # 规则化:绩效+资历(等待越久优先越高),小噪声(规则透明)
                score = [ability[i] + 0.30 * wait[i] + rng.gauss(0.0, 0.20)
                         for i in range(n)]
            else:
                # 网络化:机遇冲击使网络漂移(偶发的联系与引荐)
                score = [ability[i] + 0.85 * centrality[i] + rng.gauss(0.0, 0.35)
                         for i in range(n)]
            order = sorted(range(n), key=lambda i: score[i], reverse=True)
            promoted = set(order[:quota])
            for i in range(n):
                if arm == "civilian":
                    centrality[i] += rng.gauss(0.0, 0.30)   # 网络随机漂移
                if i in promoted:
                    rank[i] += 1
                    wait[i] = 0
                    if arm == "civilian":
                        centrality[i] += 0.15      # 晋升扩张网络:累积优势
                else:
                    wait[i] += 1
        return rank

    rank_mil = run_arm("military")
    rank_civ = run_arm("civilian")

    def stats(rank, name):
        sub = [rank[i] for i in range(n) if origin_of[i] == name]
        return statistics.mean(sub), statistics.pvariance(sub), len(sub)

    # 出身对终秩的解释力:单因素方差分析的组间 R²(eta²)
    def origin_r2(rank):
        grand = statistics.mean(rank)
        ss_total = sum((r - grand) ** 2 for r in rank)
        ss_between = 0.0
        for name in origins:
            sub = [rank[i] for i in range(n) if origin_of[i] == name]
            m = statistics.mean(sub)
            ss_between += len(sub) * (m - grand) ** 2
        return ss_between / ss_total

    r2_mil, r2_civ = origin_r2(rank_mil), origin_r2(rank_civ)
    print(f"\n同一批 {n} 人(能力共享),每轮晋升配额同为 {quota_frac:.0%},"
          f"{rounds} 轮后终秩(0-{rounds}):")
    print(f"  {'出身':>4} {'n':>5} │ {'军队臂 均值':>10} {'方差':>8} │ "
          f"{'民间臂 均值':>10} {'方差':>8} │ 军-民差")
    diffs = {}
    for name in origins:
        mm, vm, k = stats(rank_mil, name)
        mc, vc, k2 = stats(rank_civ, name)
        diffs[name] = mm - mc
        print(f"  {name:>4} {k:>5} │ {mm:>12.3f} {vm:>8.3f} │ "
              f"{mc:>13.3f} {vc:>8.3f} │ {mm - mc:+.3f}")
    total_mil = sum(rank_mil)
    total_civ = sum(rank_civ)
    print(f"\n  终秩总和:军队臂 {total_mil} vs 民间臂 {total_civ}(同一机会总量)")
    print(f"  出身对终秩的解释力 R²:军队臂 {r2_mil:.4f} vs 民间臂 {r2_civ:.4f}")

    # 断言 1a:底层出身——军队臂期望终秩显著更高,方差更小
    assert diffs["底层"] > 0.5, f"底层军-民差应显著为正,实测 {diffs['底层']:+.3f}"
    vm_low = stats(rank_mil, "底层")[1]
    vc_low = stats(rank_civ, "底层")[1]
    assert vm_low < vc_low, (
        f"底层方差军队臂({vm_low:.3f})应小于民间臂({vc_low:.3f})")
    # 断言 1b:高层出身反向吃亏——规则双向挤压(零和重分配,总机会不变)
    assert diffs["高层"] < -0.3, f"高层军-民差应显著为负,实测 {diffs['高层']:+.3f}"
    assert total_mil == total_civ, "两臂晋升配额相同,总机会必须相等"
    # 断言 1c:出身解释力被规则压到近零
    assert r2_mil < 0.02, f"军队臂出身 R² 应≈0(<0.02),实测 {r2_mil:.4f}"
    assert r2_civ > 0.10, f"民间臂出身 R² 应可观(>0.10),实测 {r2_civ:.4f}"

    print("\n读数:")
    print("  · 机会总量被两臂锁死相等——军队臂不是「机会更多」,是「同一锅饭")
    print("    换了一种分法」:规则化晋升把底层应得的那份从网络手里赎回来")
    print(f"  · 底层军-民差 {diffs['底层']:+.2f} 级,高层 {diffs['高层']:+.2f} 级,")
    print("    方向相反——「规则把出身从机会分配里挤出去」是双向的挤压")
    print("  · 军队臂方差更小:资历队列是补偿性的(等得越久优先越高),")
    print("    压缩了纯运气的放大;民间臂的网络累积优势放大早期偶然")
    print(f"  · 出身解释力 R²:军队臂 {r2_mil:.4f}(≈0)vs 民间臂 {r2_civ:.4f}——")
    print("    出身在军队臂几乎预测不了终秩,在民间臂是重要预测变量")
    print(f"\n✓ 幕一断言通过:底层军-民差 {diffs['底层']:+.3f}(方差 {vm_low:.3f}"
          f"<{vc_low:.3f});高层 {diffs['高层']:+.3f};总机会相等;"
          f"R² {r2_mil:.4f} vs {r2_civ:.4f}")
    return diffs, r2_mil, r2_civ


# ==================== 幕二:军民接触与信任 ====================


def act2():
    print("\n" + "=" * 84)
    print("幕二 军民接触与信任:信任的来源从握手换成屏幕")
    print("=" * 84)
    rng = random.Random(RNG_SEED + 1)

    n_group = 800        # 每群体人数
    steps = 600          # 更新步数(到均衡附近)
    a_contact, alpha = 0.80, 0.05   # 接触:向合作性接触的高信任锚移动
    beta = 0.02                      # 媒体:向本群体框架锚移动(较慢)
    frames = {"军": 0.55, "民": 0.30}   # 异质框架:军内媒体框社会/社会媒体框军队

    def run(c, frames_used):
        """返回 (军对民信任, 民对军信任) 的终值均值。"""
        att = {"军": [rng.uniform(0.3, 0.5) for _ in range(n_group)],
               "民": [rng.uniform(0.3, 0.5) for _ in range(n_group)]}
        anchor = {g: [frames_used[g] + rng.gauss(0.0, 0.05)
                      for _ in range(n_group)] for g in ("军", "民")}
        for _ in range(steps):
            for g in ("军", "民"):
                for i in range(n_group):
                    x = att[g][i]
                    if rng.random() < c:                     # 直接接触(正)
                        att[g][i] = x + alpha * (a_contact - x)
                    else:                                    # 媒体框架
                        att[g][i] = x + beta * (anchor[g][i] - x)
        return statistics.mean(att["军"]), statistics.mean(att["民"])

    def eq(c, f):
        """均值场解析均衡:两股拉力的加权锚点。"""
        num_m = c * alpha * a_contact + (1 - c) * beta * f["军"]
        num_c = c * alpha * a_contact + (1 - c) * beta * f["民"]
        den = c * alpha + (1 - c) * beta
        return num_m / den, num_c / den

    # 情景 S1 高接触 / S2 低接触·异质框架 / S3 低接触·同质框架
    s1_m, s1_c = run(0.50, frames)
    s2_m, s2_c = run(0.02, frames)
    same = {"军": 0.45, "民": 0.45}
    s3_m, s3_c = run(0.02, same)

    print(f"\n接触更新:以概率 c 向高信任锚 {a_contact} 移动(步长 {alpha});")
    print(f"媒体更新:以概率 1-c 向本群体框架锚移动(步长 {beta});")
    print(f"异质框架:军内媒体框「社会」= {frames['军']},"
          f"社会媒体框「军队」= {frames['民']}")
    print(f"每群体 n={n_group},更新 {steps} 步(固定种子):\n")
    print(f"  {'情景':<26} {'军对民':>8} {'民对军':>8} {'差距':>7} {'均值场':>16}")
    for label, (tm, tc) in (("S1 高接触 c=0.50", (s1_m, s1_c)),
                            ("S2 低接触 c=0.02 异框架", (s2_m, s2_c)),
                            ("S3 低接触 c=0.02 同框架", (s3_m, s3_c))):
        c_val = 0.50 if label.startswith("S1") else 0.02
        fr = frames if "异" in label else same
        em, ec = eq(c_val, fr)
        print(f"  {label:<26} {tm:>8.3f} {tc:>8.3f} {abs(tm - tc):>7.3f}"
              f"   ({em:.3f},{ec:.3f})")

    # 断言 2a:c 高——两群体信任收敛到高值,差距小
    assert s1_m > 0.60 and s1_c > 0.60, (
        f"高接触下两群体信任应>0.60,实测 军{s1_m:.3f}/民{s1_c:.3f}")
    assert abs(s1_m - s1_c) < 0.12, f"高接触差距应<0.12,实测 {abs(s1_m - s1_c):.3f}"
    # 断言 2b:c→0·异质框架——信任分化,且双双低于高接触情景
    gap2 = abs(s2_m - s2_c)
    assert gap2 > 0.15, f"低接触+异框架应分化(差距>0.15),实测 {gap2:.3f}"
    assert s2_m < s1_m and s2_c < s1_c, "接触率塌陷后两群体信任都应下降"
    assert s2_m > s2_c, "框架占优方(军内框架更高)应保留更高信任"
    # 断言 2c:c→0·同质框架——不分化,但也到不了高信任
    gap3 = abs(s3_m - s3_c)
    assert gap3 < 0.04, f"同框架即使零接触也不应分化(<0.04),实测 {gap3:.3f}"
    assert s3_m < 0.55 and s3_c < 0.55, "无接触时信任应停在框架锚附近(<0.55)"
    # 断言 2d:接触率扫描——平均信任随 c 单调上升
    print("\n  接触率扫描(异质框架):")
    prev_avg = -1.0
    for c in (0.0, 0.05, 0.10, 0.20, 0.35, 0.50):
        tm, tc = run(c, frames)
        avg, gap = (tm + tc) / 2, abs(tm - tc)
        em, ec = eq(c, frames)
        print(f"    c={c:.2f}:军对民 {tm:.3f} 民对军 {tc:.3f} 差距 {gap:.3f} "
              f"│ 均值场 ({em:.3f},{ec:.3f})")
        assert avg > prev_avg, f"平均信任应随 c 单调上升(c={c:.2f} 回退)"
        assert abs(tm - em) < 0.02 and abs(tc - ec) < 0.02, (
            f"MC 应贴住均值场均衡(c={c:.2f}: {tm:.3f} vs {em:.3f})")
        prev_avg = avg

    print("\n读数:")
    print("  · c 高:接触的拉力压过框架的拉力,两群体一起被拉向高信任锚——")
    print("    「握手」在场时,媒体说什么不重要")
    print(f"  · c→0+异质框架:均衡退化为各自的框架锚,差距 {gap2:.2f}——")
    print("    信任的来源从握手换成屏幕,而两块屏幕讲的不是同一个故事")
    print(f"  · c→0+同质框架:差距 {gap3:.2f},不分化但也停在 {s3_m:.2f}——")
    print("    分化要靠框架差,高信任却只能靠接触,二者不可互相替代")
    print("  · 志愿役社会的结构性含义:服役者占比下降=接触率 c 下降,")
    print("    军民差距(civil-military gap)由此内生——不是谁变了心,")
    print("    是接触的通道收窄了(通说 contact hypothesis 的组织版)")
    print(f"\n✓ 幕二断言通过:S1 双高({s1_m:.3f}/{s1_c:.3f},差距 "
          f"{abs(s1_m - s1_c):.3f});S2 分化 {gap2:.3f} 且双降;S3 不分化 "
          f"({gap3:.3f})但低信任;平均信任随 c 单调上升且贴住均值场")
    return s1_m, s1_c, s2_m, s2_c, gap2, gap3


# ==================== 幕三:退伍再融入的关键期 ====================


def act3():
    print("\n" + "=" * 84)
    print("幕三 退伍再融入的关键期:政策杠杆支点在头两年")
    print("=" * 84)
    rng = random.Random(RNG_SEED + 2)

    # 状态:0 未就业 / 1 教育进修 / 2 就业 / 3 稳定(吸收态)
    states = ["未就业", "教育进修", "就业", "稳定"]
    years = 10
    tau = 3.2                    # 上行转移的衰减时间常数(技能贴现/网络冷却)
    boost = 1.6                  # 支持性干预对上行概率的乘子
    base_up = {(0, 1): 0.18, (0, 2): 0.30, (1, 2): 0.45, (2, 3): 0.25}
    drop = {(1, 0): 0.10, (2, 0): 0.12}   # 中断率(不随 t 衰减)

    def matrix(t, window):
        """第 t 年(1 起)的转移矩阵;window=受干预的年份集合。"""
        d = math.exp(-(t - 1) / tau)
        m = [[0.0] * 4 for _ in range(4)]
        m[3][3] = 1.0                                   # 吸收态
        up = {k: v * d * (boost if t in window else 1.0)
              for k, v in base_up.items()}
        m[0][1], m[0][2] = up[(0, 1)], up[(0, 2)]
        m[0][0] = 1.0 - m[0][1] - m[0][2]
        m[1][0] = drop[(1, 0)]
        m[1][2] = up[(1, 2)]
        m[1][1] = 1.0 - m[1][0] - m[1][2]
        m[2][0] = drop[(2, 0)]
        m[2][3] = up[(2, 3)]
        m[2][2] = 1.0 - m[2][0] - m[2][3]
        for r in range(4):                              # 行随机性自检
            assert abs(sum(m[r]) - 1.0) < 1e-12, f"第 {r} 行不是分布(和={sum(m[r])})"
        return m

    def simulate(window):
        """分布层递归:退役时分布 → 逐年转移,返回逐年状态分布。"""
        dist = [0.55, 0.20, 0.20, 0.05]                 # 退役瞬间的分布
        traj = [dist]
        for t in range(1, years + 1):
            m = matrix(t, window)
            dist = [sum(dist[i] * m[i][j] for i in range(4)) for j in range(4)]
            traj.append(dist)
        return traj

    traj_base = simulate(set())
    traj_early = simulate({1, 2})                       # 头两年干预
    traj_late = simulate({3, 4})                        # 第 3-4 年才干预

    stable = lambda tr, t: tr[t][3]
    s5_base, s5_early, s5_late = (stable(traj_base, 5), stable(traj_early, 5),
                                  stable(traj_late, 5))
    s10_early, s10_late = stable(traj_early, 10), stable(traj_late, 10)

    print(f"\n四状态(未就业/教育进修/就业/稳定),上行转移概率按 "
          f"exp(-(t-1)/{tau}) 衰减(技能贴现/网络冷却);")
    print(f"干预=上行概率×{boost} 持续两年。退役瞬间分布:"
          f"未就业 55%/教育 20%/就业 20%/稳定 5%\n")
    print(f"  {'方案':<18} {'5 年稳定率':>9} {'10 年稳定率':>10}")
    print(f"  {'基线(不干预)':<18} {s5_base:>10.4f} {stable(traj_base, 10):>11.4f}")
    print(f"  {'头两年干预':<18} {s5_early:>10.4f} {s10_early:>11.4f}")
    print(f"  {'第 3-4 年干预':<18} {s5_late:>10.4f} {s10_late:>11.4f}")

    # 蒙特卡洛队列互证(固定种子):头两年干预臂,5 年稳定率
    cohort = 50000
    mc_stable = 0
    for _ in range(cohort):
        u = rng.random()
        s = 0 if u < 0.55 else (1 if u < 0.75 else (2 if u < 0.95 else 3))
        for t in range(1, 6):
            m = matrix(t, {1, 2})
            r, acc = rng.random(), 0.0
            s2 = s
            for j in range(4):
                acc += m[s][j]
                if r < acc:
                    s2 = j
                    break
            s = s2
        mc_stable += (s == 3)
    mc_rate = mc_stable / cohort
    print(f"\n  蒙特卡洛队列(n={cohort},固定种子):头两年干预 5 年稳定率 "
          f"{mc_rate:.4f}(解析递归 {s5_early:.4f},偏差 "
          f"{abs(mc_rate - s5_early):+.4f})")

    # 断言 3a:头两年干预的 5 年稳定率 > 第 3-4 年才干预
    assert s5_early > s5_late + 0.03, (
        f"5 年稳定率:头两年 {s5_early:.4f} 应比第 3-4 年 {s5_late:.4f} 高 3pp+")
    # 断言 3b:边际贡献比较(各自减基线)
    gain_early = s5_early - s5_base
    gain_late = s5_late - s5_base
    assert gain_early > gain_late, (
        f"头两年边际贡献 {gain_early:.4f} 应大于第 3-4 年 {gain_late:.4f}")
    # 断言 3c:晚干预仍优于不干预(不是「晚干预没用」,是「杠杆更小」)
    assert s5_late > s5_base, "第 3-4 年干预也应优于基线"
    # 断言 3d:MC 与解析递归一致
    assert abs(mc_rate - s5_early) < 0.012, (
        f"MC({mc_rate:.4f})应贴住解析递归({s5_early:.4f})")

    print("\n读数:")
    print(f"  · 同样的钱(两年×{boost} 倍上行概率):放头两年 5 年稳定率 "
          f"{s5_early:.1%},放到第 3-4 年只有 {s5_late:.1%}——差 "
          f"{(s5_early - s5_late) * 100:.1f} 个百分点")
    print(f"  · 边际贡献:头两年 {gain_early:+.4f} vs 第 3-4 年 {gain_late:+.4f}"
          f"(晚干预仍有效,只是杠杆小)")
    print("  · 两个机制叠加:①上行概率本身随 t 衰减——技能在贴现、网络在")
    print("    冷却,同样的推动力放在衰减前最值钱;②「稳定」是吸收态——")
    print("    早进入的人后续年份一直在累积,复利效应偏向早干预")
    print(f"  · 10 年稳定率 {s10_early:.1%} vs {s10_late:.1%}:差距仍在但收窄")
    print("    ——晚干预最终能追回一部分(衰减归零后大家都在慢通道),")
    print("    可失去的头两年机会不回来;过渡期研究的「关键期」即此")
    print(f"\n✓ 幕三断言通过:头两年 {s5_early:.4f} > 第 3-4 年 {s5_late:.4f}"
          f"(+{(s5_early - s5_late) * 100:.1f}pp);边际贡献 "
          f"{gain_early:.4f}>{gain_late:.4f};晚干预仍优于基线({s5_late:.4f}"
          f">{s5_base:.4f});MC 偏差 {abs(mc_rate - s5_early):.4f}")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 规则化晋升:机会总量锁死相等,军队臂底层期望终秩更高、方差更小、")
    print("     出身解释力 R²≈0(民间臂可观)——规则把出身从机会分配里挤出去;")
    print("     高层反向吃亏:双向挤压,零和重分配")
    print("  ② 军民接触与信任:接触率高→两群体收敛到高信任;接触率塌陷→分化")
    print("     取决于框架差(同框架不分化但到不了高信任);平均信任随 c 单调")
    print("     上升且贴住均值场均衡——信任的来源从握手换成屏幕")
    print("  ③ 退伍再融入关键期:同样的两年干预,头两年对 5 年稳定率的贡献")
    print("     大于第 3-4 年(上行概率随时间衰减+吸收态复利)——政策杠杆")
    print("     支点在头两年;晚干预有效但杠杆更小")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
