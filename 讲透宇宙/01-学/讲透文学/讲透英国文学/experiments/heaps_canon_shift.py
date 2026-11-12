# -*- coding: utf-8 -*-
"""Heaps-正典-混合三律实验:英国文学(GB/T 75057)三个机制的最小可计算化身。

00-体系结构.md(§七反直觉三律)、03-可构造与结构.md(可构造谱系左端)、
04-英国文学转代码.md(走廊 1/2/3)的配套实验。纯标准库(math/random/statistics),
无第三方依赖,固定种子 20260909 全程可复现。参数为通说代表性案例的风格化参数
(见各幕题注),模拟不冒充文学史计量。

三幕:
  幕一 Heaps 词汇增长律(莎士比亚词汇之谜的定量面)
      模拟作者写作:每个新 token 以概率 p_new(N)=0.5k(N+N0)^(-1/2) 成为
      "新词"(新词率随篇幅递减),否则按当前词频成比例复用(优先连接——
      Simon 1955 的词频生成机制,频谱呈 Zipf 型)。词汇量 |V|(N) 随篇幅 N
      按 Heaps 律 |V|=k·N^β(β≈0.5)增长(Heaps 1978,通说)。
      通说锚:莎士比亚现存文本约 88 万词、不同词形约 3.15 万(常引
      884,647/31,534,依版本与词形归并口径而异);Efron-Thisted 1976 用
      "未见物种"法估计若再有同篇幅新作,新词约 1.1 万+,总词汇约 6.6 万。
      断言:①模拟曲线与 k·N^β 拟合 R²>0.99 且 β̂∈(0.45,0.55)
      ②"再写一批剧本"的新词增量严格递减(同篇幅增量下新词率单调下降)
      ——莎士比亚两三万词表不是记性好,是幂律增长的自然段位。
  幕二 正典席位的马太动力学
      正典候选池(120 部作品,分 8 代入场,自带质量与两种"范式契合度"
      ——旧范式/新范式),每个时代 600 份注意力(选本/课程/论文份额)按
      (存量声望+4)^1.05 × exp(0.8×契合) 分配(超线性=累计优势);第 12 代
      发生"批评范式转移"(风格化:文化研究重估),契合函数由旧切新。
      席位=按声望排名。
      通说锚:Leavis《伟大的传统》(1948)式正典名单;1970-80 年代后
      文化研究与后殖民批评对正典的重估(通说综述口径)。
      断言:①早期声望差距随时间放大——固定早期队列的声望基尼系数
      严格上升、领先组/落后组的绝对差放大≥1.5×且组间比上升(马太效应)
      ②范式转移后,中游席位
      (11-70 名)平均位移≥顶尖席位(前 10 名)的 3 倍,而两代间前 10 名
      重叠≥7/10——正典的马太与重估分层:顶尖几乎不动,中游一两代换血。
      (与世界文学史家族层积实验分工:那边管多时代跨国层积,本家族管
      单一正典内的席位动力学)
  幕三 移民作家的语言混合(拉什迪现象)
      移民作者文本=英语底+母语迁移特征:按代际(第一代成年移民/一点五代
      幼年随迁/第二代英国出生)设定混合率与"未译片段"结构,生成风格化
      文本;评论界打分=差异化收益 1.2·m/(m+0.10) − 可读性代价 1.5m²+噪声。
      通说锚:拉什迪《午夜之子》(1981 布克奖;1993"布克中的布克"/2008
      "布克四十年最佳",通说)的"酸辣酱化"英语;石黑一雄(2017 诺奖,
      通说)的低混合迁移英语;布克奖 2013 年向全球英语开放(通说)。
      断言:①混合率与未译片段长度随代际严格递减(第一代 vs 第二代
      Welch t>4)②"混合风格"接受度存在最优区间:二次拟合凹,峰值
      混合率 m*∈(0.15,0.42),峰顶高出全同化端与全混合端各≥0.15
      ——当代英国文学的中心已移到语言接触带。

跑法: python3 -u experiments/heaps_canon_shift.py
"""

import math
import random
import statistics as stats

SEED = 20260909  # 建族日,固定种子全程可复现

# ==================== 幕一:Heaps 词汇增长律 ====================

N_TOTAL = 884_647          # 通说锚:莎士比亚现存总词数(常引 884,647)
HEAPS_K = 33.5             # 校准:V(884647)≈31.5k → k=V/√N≈33.5(风格化)
N0 = (HEAPS_K / 2) ** 2    # 平移量,使 p_new(0)=1(起步全是新词)
CAP = 60_000               # 词表容量(远超期望词形数≈3.2 万)
PERIOD = N_TOTAL // 8      # 一个"创作期"≈11 万词≈4-5 部戏(通说均篇幅≈2.3 万)


class Fenwick:
    """树状数组:词频前缀和,支持"按频比例抽词"(优先连接)的 O(log V) 落点。"""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, v):
        j = i + 1
        while j <= self.n:
            self.t[j] += v
            j += j & -j

    def find(self, w):
        """最小 i 使前缀和(0..i) > w:树上下界搜索,w∈[0,total)。"""
        pos = 0
        p = 1 << self.n.bit_length()
        while p:
            np_ = pos + p
            if np_ <= self.n and self.t[np_] <= w:
                pos = np_
                w -= self.t[np_]
            p >>= 1
        return pos


def simulate_writer(rng):
    """模拟一位多产作者的写作生涯:新词率递减 + 按频复用(优先连接)。

    返回 (词频表, 增长曲线)。增长曲线在固定检查点记录 (N, |V|)。
    """
    fen = Fenwick(CAP)
    counts = []                       # counts[i] = 第 i 个词形的频次
    n_words = 0
    total = 0
    marks = sorted({10_000, 100_000} |
                   {PERIOD * j // 2 for j in range(2, 17)})  # 每 1/16 检查
    curve = []
    half_k = 0.5 * HEAPS_K
    sqrt = math.sqrt
    rnd = rng.random
    for n in range(1, N_TOTAL + 1):
        if total == 0 or rnd() < half_k / sqrt(n + N0):
            idx = n_words
            n_words += 1
            counts.append(1)
        else:
            idx = fen.find(rnd() * total)
            counts[idx] += 1
        fen.add(idx, 1)
        total += 1
        if n in marks:
            curve.append((n, n_words))
    return counts, curve


def linreg(xs, ys):
    """最小二乘 y=a+b·x;返回 (a, b, r2)。"""
    mx, my = stats.mean(xs), stats.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    b = sxy / sxx
    a = my - b * mx
    r2 = (sxy * sxy) / (sxx * syy)
    return a, b, r2


def act1():
    print("=" * 84)
    print("幕一 Heaps 词汇增长律(莎士比亚词汇之谜的定量面,Simon 优先连接风格化)")
    print("=" * 84)
    print(f"模拟生涯:{N_TOTAL:,} token(通说锚:莎翁现存文本常引 884,647 词,")
    print(f"      词形约 3.15 万,依版本与词形归并口径而异);每个创作期≈{PERIOD:,} 词≈4-5 部戏")
    counts, curve = simulate_writer(random.Random(SEED + 1))
    v_end = curve[-1][1]
    print(f"\n词形总数 |V|={v_end:,}(期望≈31,500);词表容量 {CAP:,} 未触顶")

    # 断言 1:Heaps 律拟合(对数-对数线性回归,弃掉前 1 万词的起步段)
    pts = [(math.log(n), math.log(v)) for n, v in curve if n >= 10_000]
    xs, ys = zip(*pts)
    a, b, r2 = linreg(xs, ys)
    k_fit = math.exp(a)
    beta = b
    print(f"\nHeaps 拟合(检查点 {len(pts)} 个,N≥10k):|V|={k_fit:.1f}·N^{beta:.3f},R²={r2:.5f}")
    assert r2 > 0.99, f"Heaps 拟合 R² 应>0.99:{r2}"
    assert 0.45 < beta < 0.55, f"β̂ 应∈(0.45,0.55):{beta}"
    ttr = [(n, v / n) for n, v in curve]
    print(f"  类型-token 比(TTR)随篇幅下降:10k 处 {ttr[0][1]:.3f} →"
          f" 100k 处 {ttr[1][1]:.3f} → {N_TOTAL:,} 处 {ttr[-1][1]:.3f}")
    print(f"\n✓ 幕一断言①通过:k·N^β 幂律拟合 R²={r2:.3f}>0.99,β̂={beta:.3f}≈0.5")

    # 断言 2:同篇幅增量下,新词增量严格递减
    marks_p = [PERIOD * j for j in range(1, 9)]
    v_at = dict(curve)
    incs = [v_at[marks_p[0]]] + [v_at[marks_p[j]] - v_at[marks_p[j - 1]]
                                for j in range(1, 8)]
    print(f"\n八个创作期(每期 {PERIOD:,} 词)的新词形增量:")
    for j, inc in enumerate(incs, 1):
        print(f"  期 {j}(累计 {marks_p[j-1]:>7,} 词):新增词形 {inc:>6,}")
    assert all(a_ > b_ for a_, b_ in zip(incs, incs[1:])), f"新词增量应严格递减:{incs}"
    drop = incs[0] / incs[-1]
    print(f"\n✓ 幕一断言②通过:首期 {incs[0]:,} → 末期 {incs[-1]:,},严格单调下降"
          f"(首期为末期的 {drop:.1f} 倍)——写更多,新词越来越少")

    # 附:倍增外推 vs Efron-Thisted;Zipf 频谱核查
    extra = k_fit * (N_TOTAL ** beta) * (2 ** beta - 1)
    print(f"\n倍增外推:若再写同篇幅,新词形 ≈ {extra:,.0f}"
          f"(Efron-Thisted 1976 通说估计约 1.14 万,同量级)")
    srt = sorted(counts, reverse=True)
    ranks = [r for r in range(1, 3001)]
    freqs = srt[:3000]
    _, slope, r2z = linreg([math.log(r) for r in ranks], [math.log(f) for f in freqs])
    print(f"频谱核查:前 3000 名 log-log 斜率 {slope:.3f}(Zipf 型幂律,截距不计)"
          f",R²={r2z:.4f};单现词占比 {sum(1 for c in counts if c == 1) / len(counts):.1%}")
    assert -1.7 < slope < -0.6, f"频谱应呈 Zipf 型幂律(-1.7, -0.6):{slope}"
    print("  ——按频复用(优先连接)造出 Zipf 频谱;新词率递减造出 Heaps 增长:"
          "莎士比亚词表是幂律系统的自然段位,不是记忆奇迹")
    return {"beta": beta, "r2": r2, "incs": incs, "v_end": v_end,
            "extra": extra, "slope": slope, "drop": drop}


# ==================== 幕二:正典席位的马太动力学 ====================

M_WORKS = 120
DECADES = 20
ENTRY_DECADES = 8        # 每代 15 部入场
ATT = 600                # 每时代注意力 token 数(选本/课程/论文份额)
THETA = 1.05             # 马太指数:注意力∝存量声望^θ(超线性=累计优势)
LAM = 0.8                # 范式契合强度
SHIFT_AT = 12            # 第 12 代:批评范式转移(风格化:文化研究重估)
WORLDS = 40              # 蒙特卡洛世界数(断言打在均值上)


def bsearch(cum, w):
    """最小 i 使 cum[i] > w(自写二分,不用 bisect)。"""
    lo, hi = 0, len(cum) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if cum[mid] <= w:
            lo = mid + 1
        else:
            hi = mid
    return lo


def one_world(rng):
    """跑一个正典世界;返回 (作品表, 逐代声望快照, 逐代流量份额)。"""
    works = []
    for d in range(1, ENTRY_DECADES + 1):
        for _ in range(15):
            q = rng.lognormvariate(math.log(3.0), 0.45)
            u = rng.random()
            if u < 0.25:
                old, new = -1.0, 1.0      # 新范式受益者(风格化:文化研究抬)
            elif u < 0.50:
                old, new = 1.0, -1.0      # 旧范式受益者(风格化:细读传统抬)
            else:
                old, new = 0.0, 0.0
            works.append({"entry": d, "q": q, "old": old, "new": new, "S": 0.0})
    snaps = {}
    for t in range(1, DECADES + 1):
        active = [w for w in works if w["entry"] <= t]
        for w in active:
            if w["S"] == 0.0:
                w["S"] = w["q"]
        weights = []
        for w in active:
            fit = w["old"] if t < SHIFT_AT else w["new"]
            weights.append((w["S"] + 4.0) ** THETA * math.exp(LAM * fit))
        tot = sum(weights)
        cum, s = [], 0.0
        for wt in weights:
            s += wt
            cum.append(s)
        gains = [0] * len(active)
        for _ in range(ATT):
            i = bsearch(cum, rng.random() * tot)
            gains[i] += 1
        for w, g in zip(active, gains):
            w["S"] += g
        if t in (3, 6, 9, 11, 12, 20):
            snaps[t] = [w["S"] for w in works]
    return works, snaps


def ranks_of(ss):
    """声望→席位(1=最高;并列按序,本模拟几乎无并列)。"""
    order = sorted(range(len(ss)), key=lambda i: -ss[i])
    rk = [0] * len(ss)
    for pos, i in enumerate(order, 1):
        rk[i] = pos
    return rk


def gini(xs):
    """基尼系数(0=完全均等,1=完全集中):马太读数。"""
    xs = sorted(xs)
    n = len(xs)
    tot = sum(xs)
    cum = sum(i * x for i, x in enumerate(xs, 1))
    return (2.0 * cum) / (n * tot) - (n + 1.0) / n


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 正典席位的马太动力学({M_WORKS} 部作品×{DECADES} 代,注意力∝声望^{THETA},"
          f"{WORLDS} 个蒙特卡洛世界)")
    print("=" * 84)
    print("通说锚:Leavis《伟大的传统》(1948)式名单靠选本/课程/论文再生产;1970-80")
    print("      年代后文化研究与后殖民批评的重估(风格化为第 12 代范式切换)")
    ginis = {t: [] for t in (3, 6, 9, 12)}
    gaps3, gaps12, ratios3, ratios12 = [], [], [], []
    top_moves, mid_moves, overlaps, top_sp = [], [], [], []
    for w_ in range(WORLDS):
        works, snaps = one_world(random.Random(SEED + 100 + w_))
        # 马太:固定早期队列(入场≤3 代的 45 部,无入场稀释混杂)的基尼系数
        c3 = [i for i, w in enumerate(works) if w["entry"] <= 3]
        for t in (3, 6, 9, 12):
            ginis[t].append(gini([snaps[t][i] for i in c3]))
        srt = sorted(c3, key=lambda i: -snaps[3][i])
        lead, lag = srt[:11], srt[-11:]
        gaps3.append(stats.mean(snaps[3][i] for i in lead)
                     - stats.mean(snaps[3][i] for i in lag))
        gaps12.append(stats.mean(snaps[12][i] for i in lead)
                      - stats.mean(snaps[12][i] for i in lag))
        ratios3.append(sum(snaps[3][i] for i in lead) / sum(snaps[3][i] for i in lag))
        ratios12.append(sum(snaps[12][i] for i in lead) / sum(snaps[12][i] for i in lag))
        # 重估分层:第 11 代(转移前)→ 第 20 代(转移后)的席位位移
        r11, r20 = ranks_of(snaps[11]), ranks_of(snaps[20])
        t11 = [i for i in range(M_WORKS) if r11[i] <= 10]
        m11 = [i for i in range(M_WORKS) if 11 <= r11[i] <= 70]
        top_moves.append(stats.mean(abs(r11[i] - r20[i]) for i in t11))
        mid_moves.append(stats.mean(abs(r11[i] - r20[i]) for i in m11))
        overlaps.append(len(set(i for i in range(M_WORKS) if r11[i] <= 10) &
                            set(i for i in range(M_WORKS) if r20[i] <= 10)))
        # 顶尖内部序的稳定:Spearman(前 10 在 11/20 两代的名次)
        xs = [r11[i] for i in t11]
        ys = [r20[i] for i in t11]
        mx, my = stats.mean(xs), stats.mean(ys)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        top_sp.append(sxy / math.sqrt(sxx * syy))

    gi3, gi6, gi9, gi12 = (stats.mean(ginis[t]) for t in (3, 6, 9, 12))
    g3m, g12m = stats.mean(gaps3), stats.mean(gaps12)
    r3m, r12m = stats.mean(ratios3), stats.mean(ratios12)
    tmv, mmv = stats.mean(top_moves), stats.mean(mid_moves)
    ovl, tsp = stats.mean(overlaps), stats.mean(top_sp)
    print(f"\n马太读数 1:固定早期队列(45 部)声望的基尼系数")
    print(f"  第 3 代 {gi3:.3f} → 第 6 代 {gi6:.3f} → 第 9 代 {gi9:.3f} → 第 12 代 {gi12:.3f}")
    print(f"马太读数 2:早期领先组−落后组的平均声望差:第 3 代 {g3m:.1f} →"
          f" 第 12 代 {g12m:.1f}(组间比 {r3m:.1f}→{r12m:.1f})")
    # 断言 1:马太效应——队列内不平等上升,早期差距放大
    assert gi3 < gi6 < gi9 < gi12, f"队列基尼应严格上升:{gi3}/{gi6}/{gi9}/{gi12}"
    assert g12m > 1.5 * g3m, f"领先/落后绝对差应放大≥1.5×:{g3m:.1f}→{g12m:.1f}"
    assert r12m > r3m, f"组间比应上升:{r3m:.2f}→{r12m:.2f}"
    print(f"\n✓ 幕二断言①通过:队列基尼严格上升({gi3:.2f}→{gi12:.2f}),"
          f"早期绝对差 ×{g12m / g3m:.1f}、组间比 {r3m:.1f}→{r12m:.1f}"
          "——存量优势被注意力再生产放大(马太效应)")

    print(f"\n范式转移(第 12 代)前后席位位移(第 11 代 → 第 20 代):")
    print(f"  顶尖席位(前 10 名)平均位移 {tmv:.2f} 位;中游席位(11-70 名)"
          f"平均位移 {mmv:.2f} 位")
    print(f"  前 10 名集合重叠 {ovl:.1f}/10;顶尖内部序 Spearman ρ={tsp:.3f}")
    # 断言 2:重估分层——中游大动,顶尖几乎不动
    assert mmv >= 3.0 * tmv, f"中游位移应≥顶尖 3 倍:{mmv:.2f} vs {tmv:.2f}"
    assert mmv >= 10.0, f"中游平均位移应≥10 位:{mmv:.2f}"
    assert ovl >= 7.0, f"前 10 名重叠应≥7/10:{ovl:.1f}"
    assert tsp >= 0.85, f"顶尖内部序应高度稳定:{tsp:.3f}"
    print(f"\n✓ 幕二断言②通过:中游位移 {mmv:.1f} 位≈顶尖 {tmv:.1f} 位的"
          f" {mmv / tmv:.1f} 倍,而前 10 名重叠 {ovl:.1f}/10、内部序 ρ={tsp:.2f}"
          "——顶尖几乎不动,中游换血(马太与重估分层)")
    print("  ——与世界文学史家族层积实验分工:那边管多时代跨国层积,"
          "本家族管单一正典内的席位动力学")
    return {"gi3": gi3, "gi12": gi12, "gap_x": g12m / g3m, "tmv": tmv,
            "mmv": mmv, "ovl": ovl, "tsp": tsp}


# ==================== 幕三:移民作家的语言混合 ====================

T_TOKENS = 8000                                   # 每位作者的风格化文本长度
GENS = (  # (代际名, 混合率均值, 混合率sd, 未译片段均长, 片段sd, 每代人数)
    ("第一代(成年移民,拉什迪/奈保尔型)", 0.30, 0.10, 3.8, 0.9, 15),
    ("一点五代(幼年随迁,库雷西型)", 0.17, 0.07, 2.2, 0.5, 15),
    ("第二代(英国出生,史密斯型)", 0.085, 0.04, 1.15, 0.25, 15),
)
# 接受度模型:差异化收益 − 可读性代价 + 噪声
A_GAIN, M_HALF, B_COST, NOISE = 1.2, 0.10, 1.5, 0.10


def gen_author(rng, mu, sd, span_mu, span_sd):
    """生成一位作者的文本统计:英语底 + 母语"未译片段"插入。"""
    m_t = min(0.60, max(0.01, rng.gauss(mu, sd)))
    target = int(round(m_t * T_TOKENS))
    l1, spans = 0, []
    while l1 < target:
        length = max(1, min(target - l1, round(rng.gauss(span_mu, span_sd))))
        spans.append(length)
        l1 += length
    return l1 / T_TOKENS, stats.mean(spans), sum(1 for s in spans if s >= 2) / len(spans)


def score(m, rng):
    return (A_GAIN * m / (m + M_HALF)) - B_COST * m * m + rng.gauss(0.0, NOISE)


def welch_t(a, b):
    sa, sb = stats.stdev(a), stats.stdev(b)
    return (stats.mean(a) - stats.mean(b)) / math.sqrt(sa * sa / len(a) + sb * sb / len(b))


def act3():
    print("\n" + "=" * 84)
    print("幕三 移民作家的语言混合(拉什迪现象:英语底+母语迁移,风格化)")
    print("=" * 84)
    print("通说锚:《午夜之子》1981 布克奖、2008\"布克四十年最佳\"(通说)的\"酸辣酱化\"")
    print("      英语;石黑一雄 2017 诺奖(通说)的低混合英语;布克奖 2013 向全球英语")
    print("      开放后的短名单构成(通说综述口径)——每代 15 位作者×8000 token")
    rng = random.Random(SEED + 300)
    groups = []
    for name, mu, sd, smu, ssd, n in GENS:
        rows = [gen_author(rng, mu, sd, smu, ssd) for _ in range(n)]
        ms = [r[0] for r in rows]
        groups.append((name, rows))
        multi = stats.mean(r[2] for r in rows)
        print(f"\n  {name}:混合率均值 {stats.mean(ms):.3f}(sd {stats.stdev(ms):.3f}),"
              f"未译片段均长 {stats.mean(r[1] for r in rows):.2f} 词,"
              f"多词片段占 {multi:.0%}")
    ms0 = [r[0] for r in groups[0][1]]
    ms1 = [r[0] for r in groups[1][1]]
    ms2 = [r[0] for r in groups[2][1]]
    t12 = welch_t(ms0, ms2)
    # 断言 1:混合率与片段长度随代际严格递减,且组间分离显著
    assert stats.mean(ms0) > stats.mean(ms1) > stats.mean(ms2), \
        f"混合率应随代际递减:{stats.mean(ms0)}/{stats.mean(ms1)}/{stats.mean(ms2)}"
    sp0 = stats.mean(r[1] for r in groups[0][1])
    sp1 = stats.mean(r[1] for r in groups[1][1])
    sp2 = stats.mean(r[1] for r in groups[2][1])
    assert sp0 > sp1 > sp2, f"未译片段均长应随代际递减:{sp0}/{sp1}/{sp2}"
    assert t12 > 4.0, f"第一代 vs 第二代 Welch t 应>4:{t12:.2f}"
    print(f"\n✓ 幕三断言①通过:混合率 {stats.mean(ms0):.2f}>{stats.mean(ms1):.2f}>"
          f"{stats.mean(ms2):.2f},片段长 {sp0:.1f}>{sp1:.1f}>{sp2:.1f},"
          f"一代 vs 二代 Welch t={t12:.1f}——代际递变不是修辞,是可测梯度")

    # 断言 2:接受度最优区间(混合率网格 × 12 位评论者,二次拟合)
    grid = [0.02 + 0.0125 * j for j in range(57)]     # m∈[0.02,0.72]
    means = []
    for m in grid:
        means.append(stats.mean(score(m, rng) for _ in range(12)))
    # 最小二乘二次拟合 mean = c0 + c1·m + c2·m²
    n = len(grid)
    s = [sum(m ** k for m in grid) for k in range(5)]
    t0 = sum(means)
    t1 = sum(m * v for m, v in zip(grid, means))
    t2 = sum(m * m * v for m, v in zip(grid, means))
    # 解 3×3 正规方程(Cramer)
    a11, a12, a13 = float(n), s[1], s[2]
    a21, a22, a23 = s[1], s[2], s[3]
    a31, a32, a33 = s[2], s[3], s[4]
    det = (a11 * (a22 * a33 - a23 * a32) - a12 * (a21 * a33 - a23 * a31)
           + a13 * (a21 * a32 - a22 * a31))
    c0 = ((t0 * (a22 * a33 - a23 * a32) - a12 * (t1 * a33 - a23 * t2)
           + a13 * (t1 * a32 - a22 * t2)) / det)
    c1 = ((a11 * (t1 * a33 - a23 * t2) - t0 * (a21 * a33 - a23 * a31)
           + a13 * (a21 * t2 - t1 * a31)) / det)
    c2 = ((a11 * (a22 * t2 - t1 * a32) - a12 * (a21 * t2 - t1 * a31)
           + t0 * (a21 * a32 - a22 * a31)) / det)
    m_star = -c1 / (2 * c2)
    peak = c0 + c1 * m_star + c2 * m_star * m_star
    v_low = c0 + c1 * 0.05 + c2 * 0.0025
    v_high = c0 + c1 * 0.72 + c2 * 0.5184
    print(f"\n接受度二次拟合:score = {c0:.3f} + {c1:.3f}·m - {abs(c2):.3f}·m²"
          f"(二次项为负,凹)")
    print(f"  峰值混合率 m*={m_star:.3f},峰顶 {peak:.3f};"
          f"全同化端(0.05){v_low:.3f} / 全混合端(0.72){v_high:.3f}")
    assert c2 < -1.0, f"二次项应显著为负:{c2}"
    assert 0.15 < m_star < 0.42, f"峰值混合率应∈(0.15,0.42):{m_star}"
    assert peak - v_low >= 0.15 and peak - v_high >= 0.15, \
        f"峰顶应高出两端各≥0.15:{peak - v_low:.3f}/{peak - v_high:.3f}"
    print(f"\n✓ 幕三断言②通过:接受度中间峰 m*={m_star:.2f}——全同化(石黑型)"
          f"无差异点、全混合伤可读性,峰顶高出两端 {peak - max(v_low, v_high):.2f}"
          " 分——当代英国文学的中心已移到语言接触带")
    return {"m": [stats.mean(x) for x in (ms0, ms1, ms2)],
            "t12": t12, "m_star": m_star, "peak": peak,
            "gap_low": peak - v_low, "gap_high": peak - v_high}


def main():
    r1 = act1()
    r2 = act2()
    r3 = act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print(f"  ① Heaps 律:|V|={r1['v_end']:,} 词形拟合 k·N^{r1['beta']:.3f}"
          f" R²>0.99,β≈0.5;创作期新词 {r1['incs'][0]:,}→{r1['incs'][-1]:,}"
          f" 严格递减(首/末 {r1['drop']:.1f}×)——词表是幂律段位不是记忆奇迹")
    print(f"  ② 正典席位:队列基尼 {r2['gi3']:.2f}→{r2['gi12']:.2f} 上升、"
          f"早期绝对差 ×{r2['gap_x']:.1f}(马太);范式转移后中游位移"
          f" {r2['mmv']:.1f} 位≈顶尖 {r2['tmv']:.1f} 位的 {r2['mmv'] / r2['tmv']:.0f} 倍,"
          f"前 10 重叠 {r2['ovl']:.0f}/10——顶尖不动,中游换血")
    print(f"  ③ 语言混合:混合率 {r3['m'][0]:.2f}/{r3['m'][1]:.2f}/{r3['m'][2]:.2f}"
          f" 随代际递减(Welch t={r3['t12']:.1f});接受度中间峰 m*={r3['m_star']:.2f},"
          f"峰顶高出两端 {min(r3['gap_low'], r3['gap_high']):.2f}——中心移到接触带")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
