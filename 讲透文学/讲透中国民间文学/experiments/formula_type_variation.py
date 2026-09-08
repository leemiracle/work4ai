# -*- coding: utf-8 -*-
"""程式-类型-变异三律实验:中国民间文学(GB/T 75037)三个机制的最小可计算化身。

00-体系结构.md(§七反直觉三律)、03-可构造与结构.md(可构造谱系左端三对象)、
04-中国民间文学转代码.md(走廊 1/2/3)的配套实验。纯标准库(math/random/statistics),
无第三方依赖,固定种子 20260909 全程可复现。参数为通说代表性案例的风格化参数
(见各幕题注),模拟不冒充田野计量。

三幕:
  幕一 程式密度与口头性(帕里-洛德口头程式理论)
      风格化对照:口传史诗生成器(程式库三槽位组合:开头/中段/结尾程式,
      帕里定义「在相同的格律条件下,通常用来表达一个给定基本观念的一组词」)
      vs 书面文本生成器(自由取词+少量书面套语)。同一歌手两场表演。
      通说锚:帕里-洛德 1933-1935 南斯拉夫田野(古斯勒歌手;文盲歌手阿夫多
      听一遍新歌次日唱出更长更好的版本,见洛德《故事的歌手》);朝戈金
      《口传史诗诗学:冉皮勒〈江格尔〉程式句法研究》(2000)对程式句法的计量。
      断言:①口传文本的重复 n-gram 覆盖率显著高于书面对照——不懂任何
      「程式库」的分析者,光看重复结构就能分辨口传与书面 ②歌手的即兴=
      程式重组:库组合空间远小于自由取词空间,但口传行 100% 可解析为
      程式拼接,自由行几乎从不合法——口头诗人的记忆术:不背词句,备零件库。
  幕二 类型流传的地理衰减
      一个故事类型(情节核 8 母题+装饰壳 10 母题)自起源地向四周流传:
      异文强度随距离指数衰减;情节核高保留,装饰壳随距离本地化替换。
      通说锚:孟姜女故事两千年演变(顾颉刚 1924);《看见她》异文地图
      (董作宾,四十余首异文,通说);梁祝「读书处」多地并存的风物锚定。
      断言:①异文密度随地理距离分桶严格单调下降 ②各距离桶情节核保留率
      均处高位且几乎不随距离变,装饰壳保留率严格单调下坠——核/壳分离:
      故事走千里,骨头不变衣服常换。
  幕三 异文谱系的重构与采录者效应
      同一故事 12 份异文按真谱系(根→两大支→四小支→叶)生成:共享核继承
      +分支创新+叶创新+抄录噪声;按特征相似度做 UPGMA 聚类重构。再注入
      「采录者效应」:3 名采录者各收 4 份,每人给文本盖上自己的文体偏好
      (20 个风格特征)——谱系信号被伪造;剔除采录者特征后恢复。
      通说锚:芬兰历史-地理学派(克罗恩)的原型重构;三套集成按省编卷、
      同省异文常出同一批采录者之手的制度性来源。
      断言:①干净数据:兄弟对相似度显著高于跨大支对,前 6 次合并全为
      真兄弟 ②污染数据:跨大支同采录者对的相似度反超兄弟异采录者对,
      前 6 次合并不再按谱系抱团;剔除采录者特征后信号恢复
      ——手稿距离≠传承距离。

跑法: python3 -u experiments/formula_type_variation.py
"""

import math
import random
import statistics as stats

SEED = 20260909  # 建族日,固定种子全程可复现


# ==================== 幕一:程式密度与口头性 ====================

V = 120          # 风格化「音节」词表规模
N_LINES = 220    # 一场表演的行数
NGRAM = 4        # 程式探测窗:4-gram
SLOTS = (("开头", 10), ("中段", 10), ("结尾", 8))


def build_library(rng):
    """程式库:三槽位(开头/中段/结尾),每槽 4-5 音节的定型短语。

    帕里定义的风格化:同一槽位的程式可互换地表达同一基本观念
    (如史诗的「祈祷—启程—战斗—庆功」各有一组现成说法)。
    """
    lib = {}
    for name, k in SLOTS:
        lib[name] = [tuple(rng.randrange(V) for _ in range(rng.choice((4, 5))))
                     for _ in range(k)]
    return lib


def oral_performance(rng, lib):
    """口传表演:每行 = 开头程式 + 中段程式 + 结尾程式(零件库现拼)。"""
    return [lib["开头"][rng.randrange(10)] + lib["中段"][rng.randrange(10)]
            + lib["结尾"][rng.randrange(8)] for _ in range(N_LINES)]


def written_text(rng):
    """书面文本:自由取词(Zipf 分布)+ 少量书面套语(成语式的固定 4 字组)。"""
    weights = [1.0 / (i + 1) for i in range(V)]
    z = sum(weights)
    idioms = [tuple(rng.choices(range(V), weights=weights)[0]
                    for _ in range(NGRAM)) for _ in range(6)]
    lines = []
    for _ in range(N_LINES):
        line = [rng.choices(range(V), weights=weights)[0] for _ in range(13)]
        if rng.random() < 0.04:                      # 偶用书面套语
            pos = rng.randrange(10)
            line[pos:pos + NGRAM] = list(rng.choice(idioms))
        lines.append(tuple(line))
    return lines, idioms


def gram_counts(lines):
    counts = {}
    for line in lines:
        for i in range(len(line) - NGRAM + 1):
            g = line[i:i + NGRAM]
            counts[g] = counts.get(g, 0) + 1
    return counts


def repeat_coverage(lines):
    """重复 n-gram 覆盖率:出现在≥2 处的 n-gram 所覆盖的位置占比(盲检指标)。"""
    counts = gram_counts(lines)
    total = sum(counts.values())
    covered = sum(c for c in counts.values() if c >= 2)
    return covered / total


def library_coverage(lines, lib):
    """库覆盖率:n-gram 落入库内程式片段的位置占比(懂行的指标)。"""
    inside = set()
    for fs in lib.values():
        for f in fs:
            for i in range(len(f) - NGRAM + 1):
                inside.add(f[i:i + NGRAM])
    counts = gram_counts(lines)
    total = sum(counts.values())
    hit = sum(c for g, c in counts.items() if g in inside)
    return hit / total


def parse_rate(lines, lib):
    """合法行率:能否精确分解为(开头,中段,结尾)程式拼接(外部检验,暴力对表)。"""
    combos = [a + b + c for a in lib["开头"] for b in lib["中段"]
              for c in lib["结尾"]]
    legal = sum(1 for ln in lines if tuple(ln) in set(combos))
    return legal / len(lines), len(combos)


def jaccard(a, b):
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb)


def act1():
    print("=" * 84)
    print("幕一 程式密度与口头性(口传史诗 vs 书面文本,帕里-洛德风格化)")
    print("=" * 84)
    rng_lib = random.Random(SEED)
    lib = build_library(rng_lib)
    n_f = sum(len(fs) for fs in lib.values())
    print(f"\n程式库:三槽位 {'/'.join(f'{n}×{k}' for n, k in SLOTS)} 共 {n_f} 条零件,"
          f"可拼出 {10 * 10 * 8} 种合法行")
    print("对照:书面文本 13 音节自由取词(Zipf)+4% 行嵌入书面套语——")
    print("      同一歌手连唱两场(种子不同),看「即兴」到底换了什么")

    p1 = oral_performance(random.Random(SEED + 1), lib)
    p2 = oral_performance(random.Random(SEED + 2), lib)
    w, _idioms = written_text(random.Random(SEED + 3))

    cov_o1, cov_o2 = repeat_coverage(p1), repeat_coverage(p2)
    cov_w = repeat_coverage(w)
    lib_o1, lib_w = library_coverage(p1, lib), library_coverage(w, lib)
    print(f"\n重复 {NGRAM}-gram 覆盖率(盲检,不知库):口传第一场 {cov_o1:.1%} /"
          f" 第二场 {cov_o2:.1%};书面 {cov_w:.1%}")
    print(f"库覆盖率(懂行,按零件库解析):口传 {lib_o1:.1%};书面 {lib_w:.1%}")
    # 断言 1:口传的程式(重复短语)覆盖率显著高于书面对照
    assert min(cov_o1, cov_o2) >= 6 * cov_w, f"覆盖率差距不足:{cov_o1:.2f}/{cov_o2:.2f} vs {cov_w:.2f}"
    assert min(cov_o1, cov_o2) >= 0.25, f"口传覆盖率应≥25%:{cov_o1:.2f}/{cov_o2:.2f}"
    assert cov_w <= 0.05, f"书面覆盖率应≤5%:{cov_w:.2f}"
    print(f"\n✓ 幕一断言①通过:盲检覆盖率口传 {cov_o1:.0%}/{cov_o2:.0%} vs 书面 {cov_w:.1%}"
          f"(差 {min(cov_o1, cov_o2) / cov_w:.0f}×)——光看重复结构即可认出口传文本")

    rate_o, n_combos = parse_rate(p1, lib)
    free_lines = written_text(random.Random(SEED + 4))[0]
    rate_w, _ = parse_rate(free_lines, lib)
    free_space = V ** 13
    print(f"\n合法行率:口传 {rate_o:.0%};自由文本 {rate_w:.0%}"
          f"({len(free_lines)} 行对照)")
    print(f"组合空间:程式库 {n_combos} 种行(log10={math.log10(n_combos):.1f})"
          f" vs 自由取词 {V}^{13}≈{free_space:.1e}(log10={math.log10(free_space):.1f})")
    # 断言 2:组合数远小于自由生成,但每次组合合法
    assert rate_o == 1.0, f"口传行应 100% 可解析:{rate_o}"
    assert rate_w == 0.0, f"自由行不应有合法拼接:{rate_w}"
    assert free_space / n_combos >= 1e20, "组合空间差距应≥20 个数量级"
    print(f"\n✓ 幕一断言②通过:零件拼装空间 {n_combos} 行,比自由取词小"
          f" {math.log10(free_space / n_combos):.0f} 个数量级,但口传行 100% 合法、"
          f"自由行 0/{len(free_lines)} 合法")

    ov = jaccard(p1, p2)
    d1 = len(set(p1)) / len(p1)
    print(f"\n两场表演对照:场内行重复率 {1 - d1:.0%};两场行集合的交并比 {ov:.0%}"
          f"(Jaccard)——词句大半不重样,零件库一模一样")
    print("  ——「口头诗人的记忆术:不背词句,备零件库」;即兴 = 程式的重新组合")
    return {"cov_o": cov_o1, "cov_w": cov_w, "rate_o": rate_o,
            "space_log": math.log10(free_space / n_combos), "ov": ov}


# ==================== 幕二:类型流传的地理衰减 ====================

CORE, SHELL = 8, 10          # 情节核母题数 / 装饰壳母题数
RINGS = list(range(100, 1001, 50))   # 距起源地 100-1000(风格化:公里)
SITES_PER_RING = 8


def intensity(d):
    """距起源地 d 处每地点的期望异文数(指数衰减+底噪)。"""
    return 14.0 * math.exp(-d / 420.0) + 0.4


def core_keep(d):
    """情节核母题保留率:高位,缓降(骨头不变)。"""
    return 0.96 - 0.012 * (d / 100)


def shell_keep(d):
    """装饰壳母题保留率:随距离指数下坠(衣服常换)。"""
    return 0.93 * math.exp(-d / 300.0) + 0.05


def act2():
    print("\n" + "=" * 84)
    print("幕二 类型流传的地理衰减(起源地 100-1000 公里,每环 8 个采录点)")
    print("=" * 84)
    print("通说锚:孟姜女两千年演变跨二十余省(顾颉刚汇编);《看见她》一歌")
    print("      而异文四十余首遍布各省;梁祝「读书处」多地并存——故事在")
    print("      流传中「走千里」,也在流传中「换衣裳」")
    rng = random.Random(SEED + 10)
    sites = []                       # (距离, 异文数, 核保留率, 壳保留率)
    for d in RINGS:
        for _ in range(SITES_PER_RING):
            n = max(0, round(rng.gauss(intensity(d), 1.2)))
            if n == 0:
                sites.append((d, 0, float("nan"), float("nan")))
                continue
            ck = sum(rng.random() < core_keep(d) for _ in range(CORE * n)) / (CORE * n)
            sk = sum(rng.random() < shell_keep(d) for _ in range(SHELL * n)) / (SHELL * n)
            sites.append((d, n, ck, sk))

    edges = [100, 280, 460, 640, 820, 1000]
    dens, cores, shells = [], [], []
    print(f"\n按距离分桶({len(sites)} 个采录点):")
    for lo, hi in zip(edges, edges[1:]):
        ss = [s for s in sites if lo <= s[0] <= hi and s[1] > 0]
        dens.append(sum(s[1] for s in ss) / len(ss))
        cores.append(stats.mean(s[2] for s in ss))
        shells.append(stats.mean(s[3] for s in ss))
        print(f"  {lo:4d}-{hi:4d}km:有效点 {len(ss):3d},场均异文 {dens[-1]:5.2f} 份,"
              f"情节核保留 {cores[-1]:.1%},装饰壳保留 {shells[-1]:.1%}")

    # 断言 1:异文密度随地理距离严格单调下降
    assert all(a > b for a, b in zip(dens, dens[1:])), f"异文密度应单调下降:{dens}"
    print(f"\n✓ 幕二断言①通过:场均异文 {dens[0]:.2f}→{dens[-1]:.2f} 份,分桶严格"
          f"单调下降({dens[0] / dens[-1]:.1f}× 衰减)")

    # 断言 2:核保守壳多变(核/壳分离)
    assert min(cores) >= 0.80, f"情节核保留率各桶应≥80%:{cores}"
    assert max(cores) - min(cores) <= 0.12, f"情节核保留率应几乎不随距离变:{cores}"
    assert all(a > b for a, b in zip(shells, shells[1:])), f"装饰壳保留率应单调下坠:{shells}"
    assert shells[0] - shells[-1] >= 0.40, f"装饰壳首末桶降幅应≥40 个点:{shells}"
    drop_ratio = (shells[0] - shells[-1]) / (cores[0] - cores[-1])
    print(f"✓ 幕二断言②通过:情节核各桶保留 {cores[-1]:.0%}-{cores[0]:.0%}"
          f"(极差仅 {max(cores) - min(cores):.0%});装饰壳 {shells[0]:.0%}"
          f"→{shells[-1]:.0%} 严格下坠——壳的衰减是核的 {drop_ratio:.0f} 倍")
    print("  ——「故事走千里,骨头不变衣服常换」:情节核是结构约束,装饰壳是地方胃口")
    return {"dens": dens, "cores": cores, "shells": shells}


# ==================== 幕三:异文谱系的重构与采录者效应 ====================

NF = 60                     # 特征数(风格化:母题在场/缺席+措辞特征)
LEAVES = [f"{b}{i}" for b in ("A1", "A2", "B1", "B2") for i in "abc"]  # 12 份异文
BRANCH = {lf: lf[:2] for lf in LEAVES}     # 四个小支
SUPER = {lf: lf[0] for lf in LEAVES}       # 两大支(A/B)
N_COLLECTORS, STYLE_N = 3, 20              # 采录者数 / 每人风格特征数


def build_stemma(rng):
    """真谱系:根文本 60 特征 → 边上创新逐步覆盖(A/B 各 6,子支各 5,叶各 4+噪声 3)。"""
    root = list(range(NF))                 # 根态:特征 i 取值 i
    edge = {}
    for no, (name, k) in enumerate(
            (("A", 6), ("B", 6), ("A1", 5), ("A2", 5), ("B1", 5), ("B2", 5))):
        edge[name] = [(rng.randrange(NF), 500 + no * 20 + j)   # 每条边独占取值段
                      for j in range(k)]
    texts = {}
    for lf in LEAVES:
        vec = root[:]
        for e in (SUPER[lf], BRANCH[lf]):
            for idx, val in edge[e]:
                vec[idx] = val
        for _ in range(4):                                 # 叶创新
            vec[rng.randrange(NF)] = 200 + rng.randrange(50)
        for _ in range(3):                                 # 抄录噪声
            vec[rng.randrange(NF)] = 260 + rng.randrange(40)
        texts[lf] = vec
    return texts


def similarity(a, b, feats=None):
    fs = range(NF) if feats is None else feats
    hit = n = 0
    for i in fs:
        n += 1
        hit += a[i] == b[i]
    return hit / n


def pairs_by(texts, feats=None):
    """返回(兄弟对相似度, 跨大支对相似度, 堂支对相似度)列表。"""
    sib, cross, cousin = [], [], []
    for i, x in enumerate(LEAVES):
        for y in LEAVES[i + 1:]:
            s = similarity(texts[x], texts[y], feats)
            (sib if BRANCH[x] == BRANCH[y] else
             cross if SUPER[x] != SUPER[y] else cousin).append(s)
    return sib, cross, cousin


def upgma(texts, feats=None):
    """平均连接层次聚类;返回逐次合并记录(用于看「谁先跟谁抱团」)。"""
    cls = {lf: [lf] for lf in LEAVES}
    merges = []
    while len(cls) > 1:
        keys = sorted(cls)
        best = None
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = keys[i], keys[j]
                s = stats.mean(similarity(texts[x], texts[y], feats)
                               for x in cls[a] for y in cls[b])
                if best is None or s > best[0]:
                    best = (s, a, b)
        _, a, b = best
        merged = cls.pop(a) + cls.pop(b)
        merges.append(merged)
        cls[f"M{len(merges)}"] = merged
    return merges


def first_sibling_merges(merges, k=6):
    return sum(1 for m in merges[:k]
               if len({BRANCH[x] for x in m}) == 1)


def act3():
    print("\n" + "=" * 84)
    print("幕三 异文谱系的重构与采录者效应(12 份异文,真谱系 A1/A2/B1/B2 各 3 叶)")
    print("=" * 84)
    rng = random.Random(SEED + 20)
    texts = build_stemma(rng)
    sib, cross, cousin = pairs_by(texts)
    print(f"\n干净数据(共享核继承+分支创新+叶创新+噪声):")
    print(f"  兄弟对(同小支)相似度均值 {stats.mean(sib):.3f};"
          f"堂支对(同大支) {stats.mean(cousin):.3f};跨大支对 {stats.mean(cross):.3f}")
    m0 = upgma(texts)
    k0 = first_sibling_merges(m0)
    print(f"  UPGMA 前 6 次合并:真兄弟(同小支内部)合并 {k0}/6 次")
    # 断言 1:真实谱系信号——兄弟显著高于跨大支,且聚类先按真谱系抱团
    assert stats.mean(sib) - stats.mean(cross) >= 0.15, "兄弟对应显著高于跨大支对"
    assert k0 == 6, f"前 6 次合并应全为真兄弟,实测 {k0}"
    print(f"\n✓ 幕三断言①通过:兄弟 {stats.mean(sib):.2f} vs 跨大支 {stats.mean(cross):.2f}"
          f"(领先 {stats.mean(sib) - stats.mean(cross):.2f}),聚类先按真谱系抱团")

    # 采录者效应:3 名采录者各收 4 份,各盖 20 个风格特征(覆盖原有取值)
    order = LEAVES[:]
    rng.shuffle(order)
    assign = {lf: i for i, lf in enumerate(order)}   # 轮流分给 0/1/2 → 每 4 份一人
    assign = {lf: assign[lf] % N_COLLECTORS for lf in LEAVES}
    style_feats = {c: [rng.randrange(NF) for _ in range(STYLE_N)]
                   for c in range(N_COLLECTORS)}
    dirty = {}
    for lf in LEAVES:
        vec = texts[lf][:]
        c = assign[lf]
        for j, idx in enumerate(style_feats[c]):
            vec[idx] = 400 + c * 50 + j              # 采录者文体偏好盖戳
        dirty[lf] = vec

    sib_d, cross_d, cousin_d = pairs_by(dirty)
    same_col_cross = [similarity(dirty[x], dirty[y]) for x in LEAVES for y in LEAVES
                      if SUPER[x] != SUPER[y] and assign[x] == assign[y]]
    diff_col_sib = [similarity(dirty[x], dirty[y]) for x in LEAVES for y in LEAVES
                    if BRANCH[x] == BRANCH[y] and x < y and assign[x] != assign[y]]
    m1 = upgma(dirty)
    k1 = first_sibling_merges(m1)
    print(f"\n污染数据(采录者盖戳 {STYLE_N} 特征/人,3 人各 4 份):")
    print(f"  跨大支同采录者对相似度均值 {stats.mean(same_col_cross):.3f} 反超"
          f" 兄弟异采录者对 {stats.mean(diff_col_sib):.3f}")
    print(f"  UPGMA 前 6 次合并:真兄弟合并只剩 {k1}/6 次——聚类先按采录者抱团")
    # 断言 2:采录者效应伪造谱系信号(信号反转+聚类抱团对象改变)
    assert stats.mean(same_col_cross) > stats.mean(diff_col_sib), \
        "跨大支同采录者对应反超兄弟异采录者对"
    assert k1 <= 3, f"污染后前 6 次合并应≤3 次真兄弟,实测 {k1}"

    # 修正:知道哪些特征是采录者盖的(元数据),全部剔除后重聚
    drop = sorted({i for c in style_feats for i in style_feats[c]})
    keep = [i for i in range(NF) if i not in drop]
    sib_c, cross_c, cousin_c = pairs_by(dirty, keep)
    m2 = upgma(dirty, keep)
    k2 = first_sibling_merges(m2)
    print(f"\n修正数据(剔除采录者特征 {len(drop)} 个,余 {len(keep)} 个):")
    print(f"  兄弟 {stats.mean(sib_c):.3f} / 堂支 {stats.mean(cousin_c):.3f} /"
          f" 跨大支 {stats.mean(cross_c):.3f},序恢复;前 6 次合并真兄弟 {k2}/6")
    assert k2 == 6, f"修正后前 6 次合并应全为真兄弟,实测 {k2}"
    assert stats.mean(sib_c) > stats.mean(cousin_c) > stats.mean(cross_c), "修正后序应恢复"
    print(f"\n✓ 幕三断言②通过:采录者效应把「同人之手」伪装成「同源之文」")
    print(f"  (跨大支同采录者 {stats.mean(same_col_cross):.2f} > 兄弟异采录者"
          f" {stats.mean(diff_col_sib):.2f}),剔除元数据标记的盖戳特征后"
          f"谱系信号恢复——手稿距离≠传承距离")
    return {"sib": stats.mean(sib), "cross": stats.mean(cross),
            "inv_gap": stats.mean(same_col_cross) - stats.mean(diff_col_sib),
            "k0": k0, "k1": k1, "k2": k2}


def main():
    r1 = act1()
    r2 = act2()
    r3 = act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print(f"  ① 程式密度:盲检 {r1['cov_o']:.0%} vs 书面 {r1['cov_w']:.1%}"
          f"(差 {r1['cov_o'] / r1['cov_w']:.0f}×),口传行合法率 {r1['rate_o']:.0%}"
          f" 而组合空间小 {r1['space_log']:.0f} 个数量级——不背词句,备零件库")
    print(f"  ② 地理衰减:场均异文 {r2['dens'][0]:.2f}→{r2['dens'][-1]:.2f} 单调下降;"
          f"情节核保留 {r2['cores'][-1]:.0%}-{r2['cores'][0]:.0%} 几乎不变,"
          f"装饰壳 {r2['shells'][0]:.0%}→{r2['shells'][-1]:.0%} 下坠——核/壳分离")
    print(f"  ③ 谱系重构:兄弟 {r3['sib']:.2f} vs 跨大支 {r3['cross']:.2f} 可聚类"
          f"({r3['k0']}/6→{r3['k1']}/6→{r3['k2']}/6);采录者效应反超量 "
          f"{r3['inv_gap']:+.2f}——手稿距离≠传承距离")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
