# -*- coding: utf-8 -*-
"""演述、双语与规范本:活态史诗变异性、语言选择动力学与版本合并三幕实验。

00-体系结构.md(反直觉三律:活态史诗不是文本是事件/多语格局是两种力的均衡/
整理即选择)、03-可构造与结构.md(演述记录/语言选择/异文合并的可构造性)、
04-中国少数民族文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(random/statistics/math),无第三方依赖;每幕固定随机种子,可复现。

幕一 活态史诗的演述变异性(通说格萨尔等活态史诗艺人现象:同一艺人同一部
    的多次演述长度可差一两成而情节功能序列高度一致):
    一部史诗的某"部"拆成 23 个情节功能单元(核心 14+可选 9,功能骨架是
    传统的);6 位艺人各演述 8 晚。艺人各有:个人扩容量(程式填充的疏密,
    对数正态 σ=0.20)、掌握的可选单元子集(掌握率 0.55)、个人化的章节块
    顺序(核心 14 单元切 5 块,建艺人时相邻块换位概率 0.22);每晚演述另有
    "当晚状态"(听众/场合/体力,乘性 σ=0.15)+逐单元小抖动(σ=0.06)+
    可选单元的现场取舍(掌握者 78% 唱出)+个人顺序的偶尔翻回(3%)。
    断言:①同一艺人两晚演述的长度差中位落在 10-30% 量级,而核心功能单元
      100% 出场、功能序列 Kendall tau 中位 ≥0.95(骨架是传统的);
      ②艺人间差异大于艺人内部:长度差中位 ≥1.25 倍,功能序列 tau 中位与
        单元集 Jaccard 中位都严格更低——活态史诗不是文本是事件:
        骨架是传统的,血肉是当晚的。
幕二 双语写作的语言选择动力学(多民族文学的"母语写作/汉语写作"两栖格局):
    240 位双语作家 × 30 年创作生涯,每年 2 部作品;作品题材分两类:
    可迁移题材(份额 q,作家异质,均值 0.62)与母语不可译经验(1−q,只能
    母语承载)。可迁移题材的语言选择按收益=读者规模×表达保真 的 soft-max:
    汉语/母语读者规模比 r 从 4 增至 24(全国市场与出版传媒扩张,模型设定),
    汉语表达保真从 0.60 升至 0.82(双语能力代际提升),母语保真 ~0.92;
    作家各有收益敏感 γ(1.3±0.35)与母语依恋 κ(−1.0±0.65)。三臂:
    主臂(q 异质)/全漂臂(一切题材皆可迁移,q≡1)/全留臂(q≡0),
    三臂共享同一批作家(配对设计);增长在第 24 年后停表。
    断言:①读者规模驱动向汉语漂移:主臂生涯后期 L2 份额比前期高 ≥12 个
      百分点,个体漂移为正者过半;
      ②保留压形成均衡:全漂臂终局 ≥0.85、全留臂=0,而主臂终局严格落在
        两者之间(0.45-0.80)且增长停后份额趋平——多语文学格局是两种力
        的均衡,全漂与全留都不是均衡;
      ③均衡是"活的":主臂末期仍用两种语言写作的混写作家 ≥45%。
幕三 史诗整理的版本合并(多异文整理为"规范本"的通行工序及其两难):
    同一部史诗的 9 份口述异文,各自独立采样 46 个情节单元(核心 18 出现率
    0.96/中频 16 出现率 0.55/低频 12 出现率 0.16——异文是分布不是变体);
    规范本候选四种:并集本(凡有即收)/交集本(众本皆有)/多数本(过半
    本有)/最优异文(与诸异文平均距离最小的一份原样充当,medoid)。
    记录内容覆盖=候选所收单元按诸本见证次数加权的行数份额。
    断言:①不存在"真本":异文两两距离中位 ≥0.18,且任何一份异文(含
      最优异文)都存在与它距离 ≥0.25 的另一份,最优异文自身平均距离
      ≥0.25——异文是分布不是变体;
      ②长度-完整性两难:并集本长度 ≥1.35 倍中位异文(取并集则膨胀),
        交集本长度 ≤0.60 倍且记录内容覆盖 ≤0.65(取交集则单薄),四种
        候选无一同时做到长度 ≤1.10 倍与覆盖 ≥0.98;
      ③整理即选择:多数本对异文的平均距离四候选最小,但仍对每一份异文
        都有删削(平均删削其长度 ≥5%)——规范本是行政物不是学术物。

跑法: python -u experiments/epic_bilingual.py
"""

import math
import random
import statistics


# ==================== 幕一:活态史诗的演述变异性 ====================

N_CORE, N_OPT = 14, 9                    # 核心/可选功能单元数
N_BLOCKS = 5                             # 核心单元切成 5 个章节块
SWAP_P, FLIP_P = 0.22, 0.03              # 建艺人时块换位/演述时翻回概率
SINGER_EXPAND_SD = 0.20                  # 艺人扩容量异质性(对数正态)
MOOD_SD, JITTER_SD = 0.15, 0.06          # 当晚状态/逐单元抖动
KNOW_P, USE_P = 0.55, 0.78               # 可选单元:掌握概率/唱出概率
N_SINGERS, N_PERF = 6, 8                 # 艺人数/每人演述次数


def kendall_tau(order_a, order_b):
    """两个功能序列(共同单元的出场位次)的 Kendall tau。"""
    pos_a = {u: k for k, u in enumerate(order_a)}
    pos_b = {u: k for k, u in enumerate(order_b)}
    units = [u for u in order_a if u in pos_b]
    conc = disc = 0
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            s = (pos_b[units[i]] - pos_b[units[j]]) * (
                pos_a[units[i]] - pos_a[units[j]])
            if s > 0:
                conc += 1
            elif s < 0:
                disc += 1
    total = conc + disc
    return (conc - disc) / total if total else 1.0


def act1():
    print("=" * 84)
    print("幕一 活态史诗的演述变异:同一艺人多晚演述(种子 75044)")
    print("=" * 84)
    rng = random.Random(75044)

    core = list(range(N_CORE))                      # 核心单元 0..13
    opts = list(range(N_CORE, N_CORE + N_OPT))      # 可选单元 14..22
    base_len = {u: rng.randint(40, 180) for u in core}
    base_len.update({u: rng.randint(30, 120) for u in opts})
    block_of = {u: u * N_BLOCKS // N_CORE for u in core}   # 块号(保序)

    # 艺人:扩容量/掌握的可选单元/个人章节块顺序
    singers = []
    for _ in range(N_SINGERS):
        expand = math.exp(rng.gauss(0.0, SINGER_EXPAND_SD))
        known = [u for u in opts if rng.random() < KNOW_P]
        blocks = list(range(N_BLOCKS))
        for b in range(N_BLOCKS - 1):               # 相邻块换位=个人顺序
            if rng.random() < SWAP_P:
                blocks[b], blocks[b + 1] = blocks[b + 1], blocks[b]
        singers.append((expand, known, blocks))

    # 演述:骨架(核心块顺序,偶有翻回)+血肉(当晚状态×扩容量×抖动×取舍)
    perfs = []                                      # (艺人号, 单元集, 序列, 行数)
    for s, (expand, known, blocks) in enumerate(singers):
        for _ in range(N_PERF):
            order = list(blocks)
            for b in range(N_BLOCKS - 1):
                if rng.random() < FLIP_P:
                    order[b], order[b + 1] = order[b + 1], order[b]
            seq = [u for blk in order for u in core if block_of[u] == blk]
            used = [u for u in known if rng.random() < USE_P]
            seq = seq + used                        # 可选单元缀后
            mood = max(0.5, rng.gauss(1.0, MOOD_SD))
            total = 0
            for u in seq:
                jitter = max(0.3, rng.gauss(1.0, JITTER_SD))
                total += max(8, round(base_len[u] * expand * mood * jitter))
            perfs.append((s, set(seq), seq, total))

    def pair_stat(a, b):
        ra = abs(a[3] - b[3]) / ((a[3] + b[3]) / 2)
        jac = len(a[1] & b[1]) / len(a[1] | b[1])
        tau = kendall_tau(a[2], b[2])
        return ra, jac, tau

    intra, inter = [], []
    for i in range(len(perfs)):
        for j in range(i + 1, len(perfs)):
            (intra if perfs[i][0] == perfs[j][0] else inter).append(
                pair_stat(perfs[i], perfs[j]))
    med = lambda xs, k: statistics.median(x[k] for x in xs)
    intra_ra, inter_ra = med(intra, 0), med(inter, 0)
    intra_jac, inter_jac = med(intra, 1), med(inter, 1)
    intra_tau, inter_tau = med(intra, 2), med(inter, 2)
    core_always = all(set(core) <= p[1] for p in perfs)

    lens = [p[3] for p in perfs]
    print(f"\n一部之 {N_CORE} 核心+{N_OPT} 可选功能单元;{N_SINGERS} 位艺人"
          f"×{N_PERF} 晚,共 {len(perfs)} 场演述")
    print(f"  全场行数 {min(lens)}-{max(lens)} 行(最短/最长相差 "
          f"{max(lens) / min(lens) - 1:.0%});核心单元出场率 "
          f"{'100%' if core_always else '<100%'}")
    print(f"\n  同一艺人两晚:长度差中位 {intra_ra:.1%}(可观,10-30% 量级)")
    print(f"              单元集 Jaccard 中位 {intra_jac:.3f},"
          f"功能序列 tau 中位 {intra_tau:.3f}(骨架不动)")
    print(f"  艺人之间两晚:长度差中位 {inter_ra:.1%}(={inter_ra / intra_ra:.2f}"
          f" 倍于艺人内部),Jaccard 中位 {inter_jac:.3f},tau 中位 {inter_tau:.3f}")
    print("\n读数:")
    print("  · 同一位艺人昨晚与今晚唱同一部,行数差出一两成是常态不是事故:")
    print("    程式骨架是传统的(核心功能单元场场全出、顺序基本不动),")
    print("    填充的疏密是当晚的(听众/场合/状态)——长度是事件属性,")
    print("    不是文本属性")
    print("  · 换一位艺人,长度、可选单元、章节块顺序都换成另一副个人口音:")
    print("    艺人间差异全方位大于艺人内部——活态史诗不是文本是事件,")
    print("    '演述'是每次重新发生的一次生产")

    assert 0.10 <= intra_ra <= 0.30, (
        f"同艺人两晚长度差中位应落 10-30% 量级,实测 {intra_ra:.1%}")
    assert core_always, "核心功能单元应场场全出(骨架是传统的)"
    assert intra_tau >= 0.95, (
        f"同艺人功能序列 tau 中位应 ≥0.95,实测 {intra_tau:.3f}")
    assert inter_ra >= 1.25 * intra_ra, (
        f"艺人长度差中位应 ≥1.25 倍艺人内部,实测 {inter_ra:.1%}"
        f" vs {intra_ra:.1%}")
    assert inter_jac <= intra_jac - 0.05, (
        f"艺人单元集 Jaccard 应更低,实测 {inter_jac:.3f} vs {intra_jac:.3f}")
    assert inter_tau <= intra_tau - 0.05, (
        f"艺人功能序列 tau 应更低,实测 {inter_tau:.3f} vs {intra_tau:.3f}")
    print(f"\n✓ 幕一断言通过:同艺人长度差 {intra_ra:.0%}∈10-30% 而功能序列"
          f"tau {intra_tau:.2f}、核心单元 100% 出场;艺人长度差 {inter_ra:.0%}"
          f"={inter_ra / intra_ra:.1f} 倍内部且 tau/Jaccard 双降——活态史诗"
          f"不是文本是事件:骨架是传统的,血肉是当晚的")


# ==================== 幕二:双语写作的语言选择动力学 ====================

N_WRITERS, T_YEARS, W_PER_YEAR = 240, 30, 2
R_START, R_END = 4.0, 24.0              # 汉语/母语读者规模比(模型设定)
F2_START, F2_END = 0.60, 0.82           # 汉语表达保真的代际提升
Q_MU, Q_SD = 0.62, 0.16                 # 可迁移题材份额的作家分布
GAMMA_MU, GAMMA_SD = 1.3, 0.35          # 收益敏感
KAPPA_MU, KAPPA_SD = -1.0, 0.65         # 母语依恋(可测收益之外的留存倾向)
RAMP_YEARS = 24                         # 读者规模/双语能力的爬升期


def run_lang_arm(rng, writers, q_override):
    """一个臂:返回逐年 L2(汉语)份额、作家个体前期/后期份额。"""
    share_year = []
    first5 = {i: [0, 0] for i in range(N_WRITERS)}   # [L2 部数, 总部数]
    last5 = {i: [0, 0] for i in range(N_WRITERS)}
    for t in range(1, T_YEARS + 1):
        ramp = min(1.0, t / RAMP_YEARS)
        ratio = R_START + (R_END - R_START) * ramp
        f2 = F2_START + (F2_END - F2_START) * ramp
        n_l2 = n_tot = 0
        for i, (q_i, gamma_i, kappa_i, f1_i, f2_off) in enumerate(writers):
            q = q_i if q_override is None else q_override
            logit = gamma_i * (math.log(ratio) + math.log(
                max(0.05, (f2 + f2_off) / f1_i))) + kappa_i
            p_l2 = 1.0 / (1.0 + math.exp(-logit))
            for _ in range(W_PER_YEAR):
                n_tot += 1
                is_l2 = rng.random() < q and rng.random() < p_l2
                if is_l2:                             # 可迁移题材×选中汉语
                    n_l2 += 1
                slot = first5 if t <= 5 else (last5 if t > T_YEARS - 5 else None)
                if slot is not None:
                    slot[i][1] += 1
                    if is_l2:
                        slot[i][0] += 1
        share_year.append(n_l2 / n_tot)
    pw_early = [(a / b if b else 0.0) for a, b in first5.values()]
    pw_late = [(a / b if b else 0.0) for a, b in last5.values()]
    early = sum(a for a, _ in first5.values()) / sum(
        b for _, b in first5.values())
    return share_year, early, pw_early, pw_late


def act2():
    print("\n" + "=" * 84)
    print("幕二 双语写作的语言选择:读者规模×表达保真(种子 19800125)")
    print("=" * 84)
    rng_w = random.Random(19800125)
    clamp = lambda x, lo, hi: max(lo, min(hi, x))
    writers = []
    for _ in range(N_WRITERS):
        q = clamp(rng_w.gauss(Q_MU, Q_SD), 0.25, 0.92)
        g = clamp(rng_w.gauss(GAMMA_MU, GAMMA_SD), 0.5, 2.2)
        k = rng_w.gauss(KAPPA_MU, KAPPA_SD)
        f1 = clamp(rng_w.gauss(0.92, 0.03), 0.85, 0.98)
        f2o = rng_w.gauss(0.0, 0.04)
        writers.append((q, g, k, f1, f2o))

    share_main, early_main, ew, lw = run_lang_arm(
        random.Random(19800126), writers, None)
    share_drift, _, _, _ = run_lang_arm(
        random.Random(19800127), writers, 1.0)
    share_keep, _, _, _ = run_lang_arm(
        random.Random(19800128), writers, 0.0)

    late_main = statistics.mean(share_main[-5:])
    drift_amt = late_main - early_main
    late_drift = statistics.mean(share_drift[-5:])
    positive = sum(1 for a, b in zip(lw, ew) if a > b)
    mixed = sum(1 for x in lw if 0.05 < x < 0.95)
    tail_flat = abs(statistics.mean(share_main[-3:])
                    - statistics.mean(share_main[-6:-3]))

    print(f"\n{N_WRITERS} 位双语作家×{T_YEARS} 年,每年 {W_PER_YEAR} 部;"
          f"收益=读者规模×表达保真;读者比 {R_START:.0f}→{R_END:.0f},"
          f"汉语保真 {F2_START:.2f}→{F2_END:.2f};母语不可译题材份额均值 "
          f"{1 - Q_MU:.0%}")
    print(f"\n  {'生涯':>6} {'主臂':>8} {'全漂臂':>8} {'全留臂':>8}")
    for t in [1, 4, 8, 12, 16, 20, 24, 27, 30]:
        print(f"  第{t:>3}年 {share_main[t - 1]:>8.1%}"
              f" {share_drift[t - 1]:>8.1%} {share_keep[t - 1]:>8.1%}")
    print(f"\n  主臂汉语份额:前 5 年 {early_main:.1%} → 后 5 年 {late_main:.1%}"
          f"(漂移 +{drift_amt * 100:.1f} 个百分点;个体漂移为正 "
          f"{positive / N_WRITERS:.0%})")
    print(f"  终局:主臂 {late_main:.1%} vs 全漂臂 {late_drift:.1%} vs "
          f"全留臂 {statistics.mean(share_keep[-5:]):.1%};"
          f"末期混写作家 {mixed / N_WRITERS:.0%}")
    print(f"  增长停表(第 {RAMP_YEARS} 年)后尾段份额 3 年变动 {tail_flat:.1%}")
    print("\n读数:")
    print("  · 读者规模是持续的单向压力:全国市场与出版传媒扩张使汉语侧收益")
    print("    逐年抬升,可迁移题材的作品整体向汉语漂移,个体也多数为正")
    print("  · 但母语不可译经验形成保留压:只能母语承载的题材(谚语的音、")
    print("    史诗的程式、人情地名的质感)把每位作家的一定份额锚在母语——")
    print("    末期仍有九成作家两种语言都在写")
    print("  · 全漂臂飘到九成,全留臂纹丝不动,主臂停在两者之间且增长停后")
    print("    趋平——多语文学格局是两种力的均衡,全漂与全留都不是均衡")

    assert drift_amt >= 0.12, (
        f"主臂漂移应 ≥12 个百分点,实测 {drift_amt * 100:.1f}")
    assert positive >= 0.55 * N_WRITERS, (
        f"个体漂移为正者应过半,实测 {positive / N_WRITERS:.0%}")
    assert late_drift >= 0.85, f"全漂臂终局应 ≥0.85,实测 {late_drift:.1%}"
    assert all(s == 0.0 for s in share_keep), "全留臂应恒为 0"
    assert 0.45 <= late_main <= 0.80, (
        f"主臂终局应落在中间带 0.45-0.80,实测 {late_main:.1%}")
    assert late_main <= late_drift - 0.15, (
        f"主臂应明显低于全漂臂,实测 {late_main:.1%} vs {late_drift:.1%}")
    assert mixed >= 0.45 * N_WRITERS, (
        f"末期混写作家应 ≥45%,实测 {mixed / N_WRITERS:.0%}")
    assert tail_flat <= 0.04, (
        f"增长停后份额应趋平(3 年变动 ≤4 个点),实测 {tail_flat:.1%}")
    print(f"\n✓ 幕二断言通过:主臂漂移 +{drift_amt * 100:.0f} 个百分点而终局 "
          f"{late_main:.0%} 严格介于全留 0% 与全漂 {late_drift:.0%} 之间,"
          f"末期混写 {mixed / N_WRITERS:.0%}——多语格局是读者规模与母语"
          f"保留压的均衡,全漂与全留都不是均衡")


# ==================== 幕三:史诗整理的版本合并 ====================

N_VAR, N_UNITS = 9, 46
TIERS = [("核心", 18, 0.96), ("中频", 16, 0.55), ("低频", 12, 0.16)]
MAJORITY = 5                              # 过半本(≥5/9)视为"多数"


def act3():
    print("\n" + "=" * 84)
    print("幕三 版本合并:9 份异文整理成规范本(种子 20090928)")
    print("=" * 84)
    rng = random.Random(20090928)

    units = list(range(N_UNITS))
    base_len = {u: rng.randint(40, 160) for u in units}
    tier_p = {}
    cursor = 0
    for _, n, p in TIERS:
        for u in units[cursor:cursor + n]:
            tier_p[u] = p
        cursor += n
    presence = {u: 0 for u in units}
    variants = []
    for _ in range(N_VAR):
        s = frozenset(u for u in units if rng.random() < tier_p[u])
        variants.append(s)
        for u in s:
            presence[u] += 1

    def dist(a, b):
        return 1.0 - len(a & b) / len(a | b)

    pair_d = [dist(a, b) for i, a in enumerate(variants)
              for b in variants[i + 1:]]
    med_pair = statistics.median(pair_d)
    max_d_of = [max(dist(v, w) for w in variants if w is not v)
                for v in variants]
    mean_d = lambda v: statistics.mean(
        dist(v, w) for w in variants if w is not v)
    medoid = min(variants, key=mean_d)
    medoid_mean = mean_d(medoid)

    union = frozenset(u for u in units if presence[u] >= 1)
    inter = frozenset(u for u in units if presence[u] >= N_VAR)
    major = frozenset(u for u in units if presence[u] >= MAJORITY)

    length = lambda s: sum(base_len[u] for u in s)
    med_len = statistics.median(length(v) for v in variants)
    lr = lambda s: length(s) / med_len
    # 记录内容覆盖:候选所收单元按"诸本见证次数"加权的行数份额
    attested = sum(base_len[u] * presence[u] for u in units)
    coverage = lambda s: sum(base_len[u] * presence[u]
                             for u in s) / attested

    cand = {"并集本": union, "交集本": inter, "多数本": major,
            "最优异文": medoid}
    cand_mean_d = {k: statistics.mean(dist(s, v) for v in variants)
                   for k, s in cand.items()}
    drop_frac = [1.0 - length(v & major) / length(v) for v in variants]
    both_ok = any(lr(s) <= 1.10 and coverage(s) >= 0.98
                  for s in cand.values())

    print(f"\n{N_VAR} 份异文,各含 {statistics.mean(len(v) for v in variants):.1f}"
          f"/{N_UNITS} 个单元(核心 0.96/中频 0.55/低频 0.16 三档出现率),"
          f"单元数 {min(len(v) for v in variants)}-"
          f"{max(len(v) for v in variants)}")
    print(f"  异文两两距离中位 {med_pair:.3f};任何一份异文离最远的一份"
          f" ≥{min(max_d_of):.3f};最优异文的平均距离 {medoid_mean:.3f}")
    print(f"\n  候选        长度/中位异文  记录内容覆盖   对异文平均距离")
    for k in ("并集本", "多数本", "交集本", "最优异文"):
        print(f"  {k:6s} {lr(cand[k]):>10.2f} 倍   {coverage(cand[k]):>9.1%}"
              f"    {cand_mean_d[k]:.3f}")
    print(f"  多数本对每份异文仍平均删削其 "
          f"{statistics.mean(drop_frac):.0%} 的长度"
          f"(最少 {min(drop_frac):.0%})")
    print("\n读数:")
    print("  · 异文两两之间都有实打实的距离,连与大家最亲近的那份,也挨不着")
    print("    全部——不存在藏在九份后面的'真本',异文是分布不是变体")
    print("  · 取并集,本子比任何一位艺人唱的都长出一截(膨胀);取交集,")
    print("    只剩人人大约有的一段,记录内容的一半丢了(单薄)——长度与")
    print("    完整性不可兼得,是合并工序的结构性两难")
    print("  · 多数本是折中的行政解:平均距离最小,但仍删削每份异文近两成")
    print("    的长度——整理即选择,规范本是行政物不是学术物")

    assert med_pair >= 0.18, (
        f"异文两两距离中位应 ≥0.18,实测 {med_pair:.3f}")
    assert min(max_d_of) >= 0.25, (
        f"每份异文都应存在距离 ≥0.25 的同伴,实测最小 {min(max_d_of):.3f}")
    assert medoid_mean >= 0.25, (
        f"最优异文平均距离应 ≥0.25(无真本),实测 {medoid_mean:.3f}")
    assert lr(union) >= 1.35, (
        f"并集本膨胀应 ≥1.35 倍,实测 {lr(union):.2f}")
    assert lr(inter) <= 0.60 and coverage(inter) <= 0.65, (
        f"交集本应单薄,实测长度 {lr(inter):.2f} 倍/覆盖 {coverage(inter):.1%}")
    assert not both_ok, "不应有候选同时做到长度 ≤1.10 倍且覆盖 ≥0.98"
    assert min(cand_mean_d, key=cand_mean_d.get) == "多数本", (
        f"多数本应平均距离最小,实测 {cand_mean_d}")
    assert statistics.mean(drop_frac) >= 0.05 and min(drop_frac) >= 0.02, (
        f"多数本应删削每份异文 ≥2%(均值 ≥5%),"
        f"实测均值 {statistics.mean(drop_frac):.1%}/最小 {min(drop_frac):.1%}")
    print(f"\n✓ 幕三断言通过:异文距离中位 {med_pair:.2f} 且无'真本';并集 "
          f"{lr(union):.2f} 倍膨胀/交集覆盖仅 {coverage(inter):.0%};多数本"
          f"距离最小但仍平均删削 {statistics.mean(drop_frac):.0%}"
          f"——整理即选择,规范本是行政物不是学术物")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 演述变异:同艺人两晚长度差一两成而功能序列不动,艺人之间")
    print("     差异全方位大于艺人内部——活态史诗不是文本是事件")
    print("  ② 语言选择:读者规模驱动向汉语漂移,母语不可译经验形成保留压,")
    print("     均衡停在两者之间——全漂与全留都不是均衡")
    print("  ③ 版本合并:异文是分布不是变体,并集膨胀/交集单薄两难,多数本")
    print("     仍是删削——整理即选择,规范本是行政物不是学术物")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
