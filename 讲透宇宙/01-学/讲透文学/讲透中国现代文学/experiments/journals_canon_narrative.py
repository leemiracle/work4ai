# -*- coding: utf-8 -*-
"""阵地、选本与白话:期刊阵地网络、经典化漏斗与语言替换三幕实验。

00-体系结构.md(反直觉三律:阵地即身份论战即接触/文学史写的常常是选本选过的/
白话赢的不是辩论是网络效应)、03-可构造与结构.md(阵地网络/经典化漏斗/语言
份额动力学的可构造性)、04-中国现代文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(random/statistics/math),无第三方依赖;每幕固定随机种子,可复现。

幕一 五四文坛的组织生态:社团的期刊阵地网络(1917-1937 通说口径的社团谱系):
    七大社团(文学研究会/创造社/语丝社/现代评论派/新月派/左联/上海现代派)
    各有阵地期刊;作家有「阵地惯性+固定的跨社渠道」:每篇作品 72% 落本社团
    期刊;多数作家另有一至两个固定的第二阵地(跨社发表全部走这些渠道),
    第二阵地的抽取按论战对(为人生vs为艺术/语丝vs现代评论/新月vs左联/
    左翼vs《现代》周边)权重 5、其余 1。随机期望用社团标签置换检验
    (400 次置换),论战集中度以「同边际均匀期望」为基线。
    断言:①本社团阵地发表份额 ≥ 置换期望中位数的 3 倍(阵地即身份);
      ②跨社发表落向论战对家的份额 ≥ 均匀期望的 1.8 倍,且「两栖作家」
        (有固定第二阵地者)的主第二阵地落向论战对家的比例 ≥ 均匀期望的
        1.8 倍(互动以论战形式——论战即接触);
      ③同社期刊对的作者重合度(Jaccard) ≥ 跨社期刊对中位数的 3 倍。
幕二 经典化的滞后与固化:发表→选本→文学史的三级漏斗(1935《中国新文学
    大系》为锚,通说;1951/1963/1980/1987/1998 五部文学史):
    300 位作家,创作峰值按五四/三十年代/四十年代三代分布,天赋异质性
    s=exp(0.5·gauss);大系(1935,限峰值≤1932)按天赋入选;此后五部选本
    (1947/1956/1979/1988/1998)与五部文学史接力——大系成员高概率存续,
    非成员小概率凭天赋与「重写文学史」开口进入。对照臂:无大系无选本,
    文学史各版独立按天赋抽签。
    断言:①入选作家的「首次文学史化」中位滞后于创作峰值 ≥25 年(约一代人);
      ②大系成员进入 1987 文学史的概率 ≥ 非成员(同龄段)的 2 倍,且
        1987 文学史同龄段名单中大系成员覆盖率 ≥0.60(早选本的路径依赖);
      ③有锚臂「1951 入选者仍入 1987」的概率 ≥ 无锚对照臂的 1.3 倍
        (选本锚把文学史名录从「逐版重抽」变成「逐版存续」)。
幕三 白话对文言的替换曲线(1917-1927):出版物语言选择的从众演化:
    每年 M=600 条新出版物,选白话的概率 p=σ(K·(f−0.5)+A+e),f=当期白话
    份额(网络效应:收益随使用者份额上升,σ=逻辑斯蒂,K=6.5),
    A=0.35 白话内生优势(易学/读者面/印刷),e=年度扰动 σ=0.28;权威
    转向冲击 e:{1918:《新青年》全部改白话;1919:五四后白话报刊涌现;
    1920:教育部令小学国文改国语;1921:《小说月报》全面革新}(通说
    节点)。对照臂无冲击。无冲击系统有三个不动点:低均衡≈0.10(文言
    侧)→不稳定临界点≈0.32→高均衡≈0.97(白话侧):份额被压在临界点
    以下时从众拉回文言,越过则自增强到白话。
    断言:①有冲击臂呈 S 形:增量先增后减,最大增量年落在 1919-1921,
        且临界穿越发生在权威冲击窗口(1918-1919)内;
      ②替换相变:有冲击臂 ≥95% 实现终局白话份额 ≥0.9,对照臂跨越 0.5
        的实现 ≤2% 且终局中位 ≤0.20(卡在低均衡)——临界点在少数权威
        刊物转向后被迅速穿过(≤2 年,精英带动从众);
      ③不可逆:有冲击臂中,份额首次达 0.6 后回落破 0.5 的实现 ≤2%。

跑法: python -u experiments/journals_canon_narrative.py
"""

import math
import random
import statistics


# ==================== 幕一:社团的期刊阵地网络 ====================

# (社团, 期刊阵地, 作家数) —— 通说文学史口径的 1917-1937 主要社团谱系
SOCIETIES = [
    ("文学研究会", ("小说月报", "文学旬刊"), 34),
    ("创造社", ("创造季刊", "创造周报", "洪水"), 20),
    ("语丝社", ("语丝",), 12),
    ("现代评论派", ("现代评论",), 10),
    ("新月派", ("新月", "诗镌"), 12),
    ("左联", ("萌芽", "拓荒者", "北斗", "文学月报"), 22),
    ("上海现代派", ("现代", "新文艺"), 10),
]
N_SOC = len(SOCIETIES)
# 论战对(通说):文研会vs创造社(1922 为人生/为艺术之争);语丝vs现代评论
# (1925-26 女师大诸案);新月vs左联(1929-30 人性论/文学的阶级性);
# 左翼vs《现代》周边(1932-33 与"自由人""第三种人"论争)
POLEMIC_PAIRS = {(0, 1), (2, 3), (4, 5), (5, 6)}
P_PUB = 14          # 每位作家的发表条数
P_HOME = 0.72       # 阵地惯性:落本社团期刊的概率
W_POLEMIC = 5.0     # 论战对家的吸引力权重(第二阵地抽取)
W_OTHER = 1.0
P_SECOND = 0.60     # 有一位固定第二阵地的作家比例
P_THIRD = 0.28      # 再多一位第二阵地的比例
W_SEC1, W_SEC2 = 2.0, 1.0   # 两渠道间的流量权重(第一渠道加倍)
N_PERM = 400        # 置换检验次数


def is_polemic(a, b):
    return (min(a, b), max(a, b)) in POLEMIC_PAIRS


def weighted_choice(rng, weights):
    total = sum(weights)
    x = rng.random() * total
    acc = 0.0
    for i, w in enumerate(weights):
        acc += w
        if x <= acc:
            return i
    return len(weights) - 1


def draw_secondary(rng, home):
    """抽一个第二阵地:论战对家权重 3,其余社团 1。"""
    w = [0.0] * N_SOC
    for t in range(N_SOC):
        if t != home:
            w[t] = W_POLEMIC if is_polemic(home, t) else W_OTHER
    return weighted_choice(rng, w)


def act1():
    print("=" * 84)
    print("幕一 社团的期刊阵地网络:阵地即身份,论战即接触(种子 75031)")
    print("=" * 84)
    rng = random.Random(75031)

    # 生成作家与发表记录:阵地惯性 + 固定跨社渠道(第二阵地)
    writers = []                       # (home, [piece_society...], [第二阵地...])
    journal_writers = {}               # 期刊名 -> 发表过该刊的作家序号集合
    for s_idx, (_, journals, n_mem) in enumerate(SOCIETIES):
        for _ in range(n_mem):
            w_id = len(writers)
            seconds = []
            if rng.random() < P_SECOND:
                seconds.append(draw_secondary(rng, s_idx))
                if rng.random() < P_THIRD / P_SECOND:
                    extra = draw_secondary(rng, s_idx)
                    if extra != seconds[0]:
                        seconds.append(extra)
            pieces = []
            for _ in range(P_PUB):
                if rng.random() < P_HOME or not seconds:
                    js = s_idx
                else:
                    k = weighted_choice(
                        rng, [W_SEC1 if k == 0 else W_SEC2
                              for k in range(len(seconds))])
                    js = seconds[k]
                pieces.append(js)
                target_journals = SOCIETIES[js][1]
                journal_writers.setdefault(
                    target_journals[rng.randrange(len(target_journals))],
                    set()).add(w_id)
            writers.append((s_idx, pieces, seconds))

    total_pieces = sum(len(p) for _, p, _ in writers)
    home_share = sum(1 for h, ps, _ in writers for p in ps if p == h) / total_pieces
    size_share = [sum(1 for h, _, _ in writers if h == s) / len(writers)
                  for s in range(N_SOC)]

    # ①随机期望:置换社团标签(作家数与期刊分布不动),重算阵地份额
    homes = [h for h, _, _ in writers]
    perm_stats = []
    for _ in range(N_PERM):
        perm = homes[:]
        rng.shuffle(perm)
        perm_stats.append(sum(1 for (h, ps, _), ph in zip(writers, perm)
                              for p in ps if p == ph) / total_pieces)
    perm_med = statistics.median(perm_stats)

    # ②论战集中度:跨社发表落向论战对家的份额 vs 同边际均匀期望
    cross_obs, cross_exp = 0, 0.0
    cross_total = 0
    for h, ps, _ in writers:
        n_polemic_deg = sum(1 for t in range(N_SOC)
                            if t != h and is_polemic(h, t))
        for p in ps:
            if p != h:
                cross_total += 1
                cross_obs += is_polemic(h, p)
                cross_exp += n_polemic_deg / (N_SOC - 1)
    pole_frac_obs = cross_obs / cross_total
    pole_frac_exp = cross_exp / cross_total

    # 两栖作家:有固定第二阵地者;主第二阵地=跨社篇数最多的渠道
    amphib_total, amphib_polemic = 0, 0
    for h, ps, seconds in writers:
        if not seconds:
            continue
        amphib_total += 1
        counts = {t: ps.count(t) for t in seconds}
        second = max(seconds, key=lambda t: counts[t])
        amphib_polemic += is_polemic(h, second)
    amphib_frac = amphib_polemic / amphib_total

    # ③期刊对作者重合度:同社 vs 跨社(Jaccard)
    jnames = list(journal_writers)
    jac_same, jac_cross = [], []
    for i in range(len(jnames)):
        for j in range(i + 1, len(jnames)):
            a, b = journal_writers[jnames[i]], journal_writers[jnames[j]]
            union = len(a | b)
            jac = len(a & b) / union if union else 0.0
            soc = [k for k in range(N_SOC) if jnames[i] in SOCIETIES[k][1]]
            soc2 = [k for k in range(N_SOC) if jnames[j] in SOCIETIES[k][1]]
            (jac_same if soc == soc2 else jac_cross).append(jac)
    jac_same_med = statistics.median(jac_same)
    jac_cross_med = statistics.median(jac_cross)

    print(f"\n七大社团 {sum(n for _, _, n in SOCIETIES)} 位作家,每人 {P_PUB} 篇发表;"
          f"阵地惯性 {P_HOME:.0%};{int(P_SECOND * 100)}% 作家有一个固定第二阵地"
          f"(论战对家权重 {W_POLEMIC:.0f}:其余 {W_OTHER:.0f})")
    print(f"论战对:" + ";".join(
        f"{SOCIETIES[a][0]}-{SOCIETIES[b][0]}" for a, b in sorted(POLEMIC_PAIRS)))
    print(f"\n  本社团阵地发表份额(实测)      {home_share:.1%}")
    print(f"  置换期望中位数({N_PERM} 次)      {perm_med:.1%}"
          f"(社团规模份额平方和 {sum(x * x for x in size_share):.1%})")
    print(f"  实测/置换期望                {home_share / perm_med:.1f} 倍")
    print(f"\n  跨社发表落向论战对家(实测)    {pole_frac_obs:.1%}"
          f"  均匀期望 {pole_frac_exp:.1%}  集中度 {pole_frac_obs / pole_frac_exp:.1f} 倍")
    print(f"  两栖作家(有固定第二阵地)     {amphib_total} 人,"
          f"主第二阵地为论战对家占 {amphib_frac:.1%}"
          f"(均匀期望 {pole_frac_exp:.1%} 的 {amphib_frac / pole_frac_exp:.1f} 倍)")
    print(f"\n  期刊对作者重合度 Jaccard 中位:同社 {jac_same_med:.3f}"
          f" vs 跨社 {jac_cross_med:.3f}({jac_same_med / jac_cross_med:.0f} 倍)"
          if jac_cross_med > 0 else "")
    print("\n读数:")
    print("  · 发表不是撒网,是站队:八成多发表落在自家阵地——置换社团标签后")
    print("    只剩一成多,「在哪个刊物上写」与「属于哪个社团」不是两件事")
    print("  · 跨社流动不是随机的:跨出去的发表以约两三倍于均匀的浓度落向")
    print("    论战对家;两栖作家的主第二阵地同样向论战对家集中——五四文坛")
    print("    的社团间接触,大量以论战的形式发生(为人生vs为艺术/语丝vs")
    print("    现代评论/新月vs左联)")
    print("  · 组织生态一句话:阵地即身份,论战即接触")

    assert home_share >= 3.0 * perm_med, (
        f"阵地份额应 ≥3 倍置换期望,实测 {home_share:.3f} vs {perm_med:.3f}")
    assert pole_frac_obs >= 1.8 * pole_frac_exp, (
        f"论战集中度应 ≥1.8 倍,实测 {pole_frac_obs:.3f} vs 均匀 {pole_frac_exp:.3f}")
    assert amphib_frac >= 1.8 * pole_frac_exp, (
        f"两栖作家主第二阵地论战占比应 ≥1.8 倍均匀期望,"
        f"实测 {amphib_frac:.3f} vs {pole_frac_exp:.3f}")
    assert jac_same_med >= 3.0 * jac_cross_med, (
        f"同社期刊对 Jaccard 应 ≥3 倍跨社,实测 {jac_same_med:.3f}"
        f" vs {jac_cross_med:.3f}")
    print(f"\n✓ 幕一断言通过:阵地份额 {home_share:.0%}≈置换期望 "
          f"{perm_med:.0%} 的 {home_share / perm_med:.1f} 倍;跨社发表论战集中度 "
          f"{pole_frac_obs / pole_frac_exp:.1f} 倍;两栖作家主第二阵地论战集中度 "
          f"{amphib_frac / pole_frac_exp:.1f} 倍——阵地即身份,论战即接触")


# ==================== 幕二:经典化的滞后与固化 ====================

N_WRITERS = 300
DAXI_YEAR = 1935                       # 《中国新文学大系》(通说:1935-36 影印成书)
DAXI_ELIGIBLE = 1932                   # 大系收录段的创作峰值上限(1917-1927 卷)
ANTHOLOGIES = [(1947, 0.00), (1956, 0.00), (1979, 0.10),
               (1988, 0.18), (1998, 0.22)]   # (年份, 非大系直入开口)
HISTORIES = [(1951, 0.00), (1963, 0.00), (1980, 0.05),
             (1987, 0.12), (1998, 0.16)]     # (年份, 无选本直入开口)


def draw_peak(rng):
    """创作峰值:五四代 40% / 三十年代代 35% / 四十年代代 25%(通说代群比例)。"""
    u = rng.random()
    if u < 0.40:
        return rng.randint(1918, 1927)
    if u < 0.75:
        return rng.randint(1928, 1937)
    return rng.randint(1938, 1948)


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 经典化的滞后与固化:发表→选本→文学史三级漏斗(种子 19350715)")
    print("=" * 84)
    rng = random.Random(19350715)

    peaks = [draw_peak(rng) for _ in range(N_WRITERS)]
    statures = [math.exp(rng.gauss(0.0, 0.5)) for _ in range(N_WRITERS)]
    order = sorted(range(N_WRITERS), key=lambda i: statures[i])
    rank = [0.0] * N_WRITERS
    for pos, i in enumerate(order):
        rank[i] = pos / (N_WRITERS - 1)          # 天赋分位 r∈[0,1]

    # —— 主臂:大系(1935)→ 选本接力 → 文学史接力 ——
    in_daxi = [False] * N_WRITERS
    for i in range(N_WRITERS):
        if peaks[i] <= DAXI_ELIGIBLE:
            in_daxi[i] = rng.random() < min(0.94, 0.10 + 0.62 * rank[i])
    anthol_year = [None] * N_WRITERS             # 首次进入任一后续选本
    hist_year = [None] * N_WRITERS               # 首次文学史化
    anthol_rosters = {}
    for year, opening in ANTHOLOGIES:
        roster = []
        for i in range(N_WRITERS):
            if in_daxi[i]:
                p = 0.80
            elif anthol_year[i] is not None:
                p = 0.68
            else:
                p = 0.04 + 0.12 * rank[i] + opening
            if rng.random() < p:
                roster.append(i)
                if anthol_year[i] is None:
                    anthol_year[i] = year
        anthol_rosters[year] = set(roster)
    hist_rosters = {}
    for year, opening in HISTORIES:
        roster = []
        for i in range(N_WRITERS):
            if in_daxi[i]:
                p = 0.88
            elif anthol_year[i] is not None and anthol_year[i] <= year:
                p = 0.66
            else:
                p = 0.03 + 0.06 * rank[i] + opening
            if rng.random() < p:
                roster.append(i)
                if hist_year[i] is None:
                    hist_year[i] = year
        hist_rosters[year] = set(roster)

    # —— 对照臂:无大系无选本,各版文学史独立按天赋抽签,且逐版有时代口味
    #    摆动(无锚,名录随每一代批评风尚漂移) ——
    ctrl_in = {}
    for year, _ in HISTORIES:
        taste = rng.gauss(0.0, 0.20)
        ctrl_in[year] = {i for i in range(N_WRITERS)
                         if rng.random() < min(0.95, max(0.02,
                              0.10 + 0.50 * rank[i] + taste))}

    # ①滞后:首次文学史化 − 创作峰值
    canonized = [i for i in range(N_WRITERS) if hist_year[i] is not None]
    lags = [hist_year[i] - peaks[i] for i in canonized]
    med_lag = statistics.median(lags)
    cohort = lambda p: ("五四代" if p <= 1927 else
                        ("三十年代代" if p <= 1937 else "四十年代代"))
    cohort_lags = {}
    for c in ("五四代", "三十年代代", "四十年代代"):
        xs = [hist_year[i] - peaks[i] for i in canonized if cohort(peaks[i]) == c]
        cohort_lags[c] = (statistics.median(xs), len(xs)) if xs else (0, 0)

    # ②路径依赖:大系成员 vs 同龄段非成员的文学史进入率 + 名单覆盖率
    eligible = [i for i in range(N_WRITERS) if peaks[i] <= DAXI_ELIGIBLE]
    daxi_set = {i for i in eligible if in_daxi[i]}
    nondaxi_elig = [i for i in eligible if not in_daxi[i]]
    h87 = hist_rosters[1987]
    p_daxi = sum(1 for i in daxi_set if i in h87) / len(daxi_set)
    p_non = sum(1 for i in nondaxi_elig if i in h87) / len(nondaxi_elig)
    elig87 = [i for i in h87 if peaks[i] <= DAXI_ELIGIBLE]
    coverage = sum(1 for i in elig87 if in_daxi[i]) / len(elig87)

    # ③固化:有锚臂 vs 对照臂的跨版存续率
    persist_main = len(h87 & hist_rosters[1951]) / len(hist_rosters[1951])
    persist_ctrl = len(ctrl_in[1987] & ctrl_in[1951]) / len(ctrl_in[1951])

    # 1998 版边际增量:既不在大系也不在任何选本的"重写文学史"新增
    h98 = hist_rosters[1998]
    marginal = sum(1 for i in h98
                   if not in_daxi[i] and anthol_year[i] is None) / len(h98)

    print(f"\n{N_WRITERS} 位作家(峰值:五四代 40%/三十年代 35%/四十年代 25%;"
          f"天赋 s=exp(0.5·σ));漏斗:{DAXI_YEAR} 大系(限峰值≤{DAXI_ELIGIBLE})"
          f"→选本 {'/'.join(str(y) for y, _ in ANTHOLOGIES)}→文学史 "
          f"{'/'.join(str(y) for y, _ in HISTORIES)}")
    print(f"  大系成员 {len(daxi_set)} 人(同龄段 {len(eligible)} 人中 "
          f"{len(daxi_set) / len(eligible):.0%})")
    print(f"\n  ①首次文学史化滞后于创作峰值:全体中位 {med_lag:.0f} 年"
          f"(一代人≈25-30 年)")
    for c, (m, n) in cohort_lags.items():
        print(f"      {c:7s} 中位滞后 {m:.0f} 年(n={n})")
    print(f"  ②进入 1987 文学史的概率:大系成员 {p_daxi:.0%} vs 同龄段非成员 "
          f"{p_non:.0%}({p_daxi / p_non:.1f} 倍);1987 名单同龄段大系覆盖率 "
          f"{coverage:.0%}")
    print(f"  ③跨版存续(1951 入选者仍入 1987):有锚臂 {persist_main:.0%} vs "
          f"无锚对照臂 {persist_ctrl:.0%}({persist_main / persist_ctrl:.1f} 倍)")
    print(f"  1998 文学史中「既无大系亦无选本」的边际新增仅 {marginal:.0%}")
    print("\n读数:")
    print("  · 经典化是漏斗不是直通车:作品发表后先过选本(1935 大系一代人的")
    print("    筛),再过文学史(又一代人的筛)——首次文学史化落后创作峰值约")
    print("    一代人,中间隔着选本的时滞与筛选")
    print("  · 早选本是锚:1987 名单里同龄段作家六成以上就是 1935 大系那批人")
    print("    ——文学史写的常常是选本选过的;「重写文学史」能开新口子,")
    print("    但到 1998 版,绕过全部选本直接入史的边际新增仍是一小撮")
    print("  · 对照臂说明锁是谁上的:没有大系锚,各版文学史逐版重抽,存续率")
    print("    骤降——路径依赖不是「好作家自然留名」,是选本把名录焊住了")

    assert med_lag >= 25, f"首次文学史化中位滞后应 ≥25 年,实测 {med_lag:.0f}"
    assert p_daxi >= 2.0 * p_non, (
        f"大系成员入史率应 ≥2 倍非成员,实测 {p_daxi:.3f} vs {p_non:.3f}")
    assert coverage >= 0.60, f"1987 名单同龄段大系覆盖率应 ≥0.60,实测 {coverage:.3f}"
    assert persist_main >= 1.3 * persist_ctrl, (
        f"有锚臂存续率应 ≥1.3 倍对照臂,实测 {persist_main:.3f} vs {persist_ctrl:.3f}")
    print(f"\n✓ 幕二断言通过:中位滞后 {med_lag:.0f} 年≈一代人;大系成员入史率 "
          f"{p_daxi / p_non:.1f} 倍于非成员且名单覆盖率 {coverage:.0%};有锚臂存续 "
          f"{persist_main:.0%} vs 无锚 {persist_ctrl:.0%}——文学史写的常常是选本选过的")


# ==================== 幕三:白话对文言的替换曲线 ====================

YEARS = list(range(1917, 1928))
M_SLOTS = 600                          # 每年新出版物条数
K_CONF = 6.5                           # 从众响应锐度(网络效应)
ADV_NEW = 0.35                         # 白话内生优势(易学/读者面/印刷成本)
SIGMA_E = 0.28                         # 年度扰动
F0 = 0.04                              # 1917 起点:白话在新出版物中的份额
# 权威转向冲击(通说节点):1918《新青年》全部改白话;1919 五四后白话报刊
# 涌现;1920 教育部令国民学校一二年级国文改国语;1921《小说月报》全面革新
ELITE_SHOCKS = {1918: 1.1, 1919: 1.0, 1920: 2.2, 1921: 0.4}
N_REAL3 = 1500


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def run_lang(rng, shocks_on):
    """一次实现:返回逐年末白话份额列表。"""
    f = F0
    path = []
    for year in YEARS:
        e = ELITE_SHOCKS.get(year, 0.0) if shocks_on else 0.0
        p = sigmoid(K_CONF * (f - 0.5) + ADV_NEW + e + rng.gauss(0, SIGMA_E))
        n_new = sum(1 for _ in range(M_SLOTS) if rng.random() < p)
        f = n_new / M_SLOTS
        path.append(f)
    return path


def fixed_points():
    """无冲击系统 σ(K(f−0.5)+A)=f 的三个不动点:低均衡/临界点/高均衡。"""
    def bisect(lo, hi, rising_low):
        for _ in range(80):
            mid = (lo + hi) / 2
            above = sigmoid(K_CONF * (mid - 0.5) + ADV_NEW) > mid
            if above == rising_low:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    low_eq = bisect(0.05, 0.12, True)      # 下方 g>0 → 低稳定均衡
    crit = bisect(0.15, 0.45, False)       # 下方 g<0 → 不稳定临界点
    high_eq = bisect(0.90, 0.99, True)     # 下方 g>0 → 高稳定均衡
    return low_eq, crit, high_eq


def act3():
    print("\n" + "=" * 84)
    print("幕三 白话对文言的替换:从众演化的相变(种子 19170504)")
    print("=" * 84)
    rng = random.Random(19170504)
    elite_paths = [run_lang(rng, True) for _ in range(N_REAL3)]
    ctrl_paths = [run_lang(rng, False) for _ in range(N_REAL3)]

    mean_path = [statistics.mean(p[t] for p in elite_paths) for t in range(len(YEARS))]
    ctrl_mean = [statistics.mean(p[t] for p in ctrl_paths) for t in range(len(YEARS))]
    incs = [mean_path[t] - (F0 if t == 0 else mean_path[t - 1])
            for t in range(len(YEARS))]
    takeoff = max(range(len(YEARS)), key=lambda t: incs[t])

    f87 = mean_path[-1]
    reach90 = sum(1 for p in elite_paths if p[-1] >= 0.90) / N_REAL3
    ctrl_cross50 = sum(1 for p in ctrl_paths
                       if max(p) >= 0.50) / N_REAL3
    ctrl_final_med = statistics.median(p[-1] for p in ctrl_paths)

    # 穿越速度:从首达 0.35 到首达 0.70 的年数(有冲击臂)
    speeds = []
    for p in elite_paths:
        a = next((t for t, f in enumerate(p) if f >= 0.35), None)
        b = next((t for t, f in enumerate(p) if f >= 0.70), None)
        if a is not None and b is not None:
            speeds.append(b - a)
    speed_med = statistics.median(speeds) if speeds else 99

    # 不可逆:首达 0.6 后回落破 0.5 的实现
    reversals = 0
    for p in elite_paths:
        first6 = next((t for t, f in enumerate(p) if f >= 0.60), None)
        if first6 is not None and min(p[first6:]) < 0.50:
            reversals += 1
    rev_rate = reversals / N_REAL3

    low_eq, x_star, high_eq = fixed_points()
    print(f"\n每年 {M_SLOTS} 条新出版物;p(白话)=σ({K_CONF}·(f−0.5)+{ADV_NEW}+e),"
          f"起点 f={F0:.0%};冲击:1918 新青年/1919 五四报刊/1920 国语令/"
          f"1921 小说月报;{N_REAL3} 实现/臂")
    print(f"无冲击系统有三个不动点:低均衡 {low_eq:.2f}(文言侧)→ 不稳定临界点 "
          f"{x_star:.2f} → 高均衡 {high_eq:.2f}(白话侧);份额被从众压在临界点"
          f"以下时,拉回文言")
    print(f"\n  {'年份':>6} {'有冲击(均值)':>12} {'对照(均值)':>10}  冲击事件")
    events = {1918: "《新青年》全部改白话", 1919: "五四后白话报刊涌现",
              1920: "教育部令小学国文改国语", 1921: "《小说月报》全面革新"}
    for t, y in enumerate(YEARS):
        ev = f" ←{events[y]}" if y in events else ""
        print(f"  {y:>6} {mean_path[t]:>12.1%} {ctrl_mean[t]:>10.1%}{ev}")
    print(f"\n  最大增量年 {YEARS[takeoff]}(+{incs[takeoff]:.0%})∈1919-1921;"
          f"增量序列先增后减(S 形)")
    print(f"  1917 均值 {mean_path[0]:.0%} → 1921 均值 {mean_path[4]:.0%}"
          f" → 1927 均值 {f87:.0%}")
    print(f"  终局 ≥90% 的实现:{reach90:.0%};对照臂跨 0.5 的实现 "
          f"{ctrl_cross50:.0%},终局中位 {ctrl_final_med:.0%}")
    print(f"  穿越 0.35→0.70 的年数中位 {speed_med:.0f} 年;"
          f"首达 0.6 后回落破 0.5 的实现 {rev_rate:.1%}")
    print("\n读数:")
    print("  · 1917-1919 慢爬,1920-1921 一年接管,1922 后平台——教科书说的")
    print("    「白话文运动几年内胜利」是一条 S 曲线,不是一场辩论的裁决")
    print("  · 临界点是结构参数:无冲击时从众演化把白话按在低均衡;四记权威")
    print("    冲击(一份杂志/一场运动/一道政令/一本老牌大刊改版)把份额推过")
    print("    临界点,从众效应反转为自增强——白话赢的不是辩论,是网络效应")
    print("  · 过了 0.6 之后回落破 0.5 的实现不足百分之二:临界点之后不可逆")

    assert 1919 <= YEARS[takeoff] <= 1921, (
        f"最大增量年应落在 1919-1921,实测 {YEARS[takeoff]}")
    pre = incs[:takeoff]
    post = incs[takeoff:]
    assert all(pre[i] < pre[i + 1] + 0.005 for i in range(len(pre) - 1)), (
        f"起飞前增量应大体递增:{['%.3f' % x for x in pre]}")
    assert all(post[i] > post[i + 1] - 0.005 for i in range(len(post) - 1)), (
        f"起飞后增量应大体递减:{['%.3f' % x for x in post]}")
    assert mean_path[0] <= 0.12 and f87 >= 0.90, (
        f"起点应低/终点应高,实测 {mean_path[0]:.3f}→{f87:.3f}")
    assert reach90 >= 0.95, f"有冲击臂终局 ≥90% 的实现应 ≥95%,实测 {reach90:.1%}"
    assert ctrl_cross50 <= 0.02 and ctrl_final_med <= 0.20, (
        f"对照臂应卡低均衡,实测跨越率 {ctrl_cross50:.1%},终局中位 {ctrl_final_med:.3f}")
    assert speed_med <= 2, f"穿越 0.35→0.70 应 ≤2 年,实测中位 {speed_med}"
    assert rev_rate <= 0.02, f"首达 0.6 后回落率应 ≤2%,实测 {rev_rate:.1%}"
    assert mean_path[1] < x_star < mean_path[2], (
        f"临界点({x_star:.2f})应被穿越于 1918-1919 的权威冲击窗口,"
        f"实测 {mean_path[1]:.2f}→{mean_path[2]:.2f}")
    print(f"\n✓ 幕三断言通过:S 形(最大增量 {YEARS[takeoff]},先增后减);有冲击臂 "
          f"{reach90:.0%} 实现终局 ≥90% 而对照臂终局中位 {ctrl_final_med:.0%};"
          f"临界穿越中位 {speed_med:.0f} 年且回落率 {rev_rate:.1%}"
          f"——白话赢的不是辩论,是网络效应")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 期刊阵地网络:社团内部同刊密度远高于跨社随机期望,两栖作家集中")
    print("     于论战对立阵营——阵地即身份,论战即接触(五四文坛的组织生态)")
    print("  ② 经典化漏斗:首次文学史化滞后创作峰值约一代人,早期选本对后续")
    print("     文学史覆盖率高且存续有锚——文学史写的常常是选本选过的")
    print("  ③ 语言替换相变:白话份额 S 形接管,临界点在少数权威刊物转向后被")
    print("     迅速穿过,越点不可逆——白话赢的不是辩论,是网络效应")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
