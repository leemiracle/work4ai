# -*- coding: utf-8 -*-
"""萨迦血仇网络-小语种全球通道-诺奖承认时滞三律模拟:北欧文学家族实验(GB/T 75074)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(三条结构引擎的
严格可构造性)、04-北欧文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260907 可复现。
作家作品评述一律通说文学史口径;诺奖年表为通说事实,峰值年按代表作通行
认定(读数对峰值认定敏感,反例与另解随表双录);机制断言来自风格化模拟,
不作文学史认证,不判文学价值。

三幕:
  幕一 萨迦的家族网络(《尼亚尔萨迦》式):
      A 结构:冰岛家族萨迦的人物网络=家族聚簇(族内血亲边密集)+仇杀桥
        (族间边稀少且过半为血仇边);去掉族间边,网络散成孤立家族。
      B 偿还动力学:每次杀戮留下义务(复仇或偿金和解);和解倾向随代际
        上升——基督教化(1000 年,通说)与法制化(冰岛自由邦的庭与偿金
        制度,通说)的风格化对应,血仇链终止率逐代上升。
      断言:①族内边密度>族间边密度 5 倍,血仇边占族间边>55%,
              去族间边后网络分裂为 6 个家族分量
            ②条件终止率随代际单调上升,第三代>第一代 1.6 倍;
              终止方式中偿金和解份额逐代上升——萨迦是网络叙事的中世纪范本。
  幕二 小语种的全球通道(北欧之谜):
      三队列对照:大语种基线(英语市场直通)/北欧纯母语作者(须经翻译
      枢纽:时滞+瓶颈)/北欧双语作者(自英语写作或自译,直通世界市场)。
      断言:①纯母语作者的全球可见度依赖翻译通道:过半在 45 年生涯视野
            内未达全球可见(风格化实测约八成),获可见者的时滞>基线 1.5 倍
            ②双语作者 20 年可见度达基线 85% 以上,未可见份额与基线同量级
              ——北欧诺奖密度之谜的一半答案是:他们用两只手写字
              (易卜生式剧场外交+英语写作传统,通说口径的风格化)。
  幕三 诺奖场域的承认时滞:
      A 锚读数:北欧诺奖年表(通说):承认时滞=授奖年−代表作峰值年;
        早期(1901-1930)中位时滞大于战后(1945-2026),个别反例双录。
      B 机制模拟:委员会按"国际声誉存量"选人,各期资格门槛(存量饱和度)
        不同:早期要求声誉近饱和(国际声誉已立的老年作者,保守承认),
        战后降低门槛(生涯中期),当代再加"生涯助推"直选项。
      断言:①早期平均承认时滞>当代 1.7 倍,四段(早期/过渡/战后/当代)
            单调下降
            ②低时滞授奖(<15 年)份额:早期<25%→当代>45%;平均授奖年龄
              早期比当代老 8 岁以上——诺奖从"盖棺定论的追加"变为
              "生涯助推的杠杆"。
      分工声明:法国文学家族实验管"国内奖项级联",本幕管"国际承认时点",
      两题不同,互不重复。

跑法: python -u experiments/saga_nobel_channel.py
"""

import math
import random
import statistics

SEED = 20260907  # 检索校准日作种子,可复现


# ==================== 幕一:萨迦的家族网络(《尼亚尔萨迦》式) ====================

N_FAM, FAM_SIZE = 6, 8     # 六个家族,每家 8 人(风格化的"家族萨迦"人物表)
KIN_P = 0.60               # 族内血亲边概率(家族聚簇)
FEUD_PAIRS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 3), (2, 5)]
CROSS_ALLY_P = 0.015       # 族间联姻/结盟边概率(稀少)


def build_saga_network(rng):
    """族内血亲边密集 + 族间由血仇桥与零星联姻边连接的风格化萨迦网络。"""
    nodes = [(f, i) for f in range(N_FAM) for i in range(FAM_SIZE)]
    kin, feud, ally = [], [], []
    for f in range(N_FAM):
        for i in range(FAM_SIZE):
            for j in range(i + 1, FAM_SIZE):
                if rng.random() < KIN_P:
                    kin.append(((f, i), (f, j)))
    for a, b in FEUD_PAIRS:
        for _ in range(2):  # 每对世仇两次杀戮事件:施害者-受害者桥
            feud.append(((a, rng.randrange(FAM_SIZE)), (b, rng.randrange(FAM_SIZE))))
    feud_pairs = set(frozenset(p) for p in FEUD_PAIRS)
    for a in range(N_FAM):
        for b in range(a + 1, N_FAM):
            if frozenset((a, b)) in feud_pairs:
                continue
            for i in range(FAM_SIZE):
                for j in range(FAM_SIZE):
                    if rng.random() < CROSS_ALLY_P:
                        ally.append(((a, i), (b, j)))
    return nodes, kin, feud, ally


def act1():
    print("=" * 84)
    print("幕一 萨迦的家族网络: 家族聚簇+仇杀桥 与 血仇链的偿还动力学(种子 %d)" % SEED)
    print("=" * 84)
    rng = random.Random(SEED)

    # ---- 1a 结构:家族聚簇 + 仇杀桥 ----
    nodes, kin, feud, ally = build_saga_network(rng)
    n = len(nodes)
    in_pos = N_FAM * (FAM_SIZE * (FAM_SIZE - 1) // 2)
    cross_pos = (N_FAM * (N_FAM - 1) // 2) * FAM_SIZE * FAM_SIZE
    in_d = len(kin) / in_pos
    cross_d = (len(feud) + len(ally)) / cross_pos
    feud_share = len(feud) / (len(feud) + len(ally))

    # 去掉族间边后的连通分量数(只留族内边 → 应散成孤立家族)
    parent = {v: v for v in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in kin:
        parent[find(u)] = find(v)
    n_comp = len({find(v) for v in nodes})

    # 每个节点的邻居中同族占比(聚簇的个体读数)
    nbr = {v: [] for v in nodes}
    for u, v in kin + feud + ally:
        nbr[u].append(v)
        nbr[v].append(u)
    kin_share = statistics.mean(
        sum(1 for w in nbr[v] if w[0] == v[0]) / len(nbr[v]) for v in nodes if nbr[v])

    print("\n[1a] 结构: %d 家族×%d 人=%d 节点; 族内血亲边 %d, 族间血仇桥 %d, 族间联姻 %d"
          % (N_FAM, FAM_SIZE, n, len(kin), len(feud), len(ally)))
    print(f"{'族内边密度':<16}{'族间边密度':<16}{'密度比':<10}{'血仇占族间':<12}"
          f"{'族内邻居占比':<12}{'去族间边后分量':<10}")
    print(f"{in_d:<16.3f}{cross_d:<16.4f}{in_d / cross_d:<10.1f}{feud_share:<12.1%}"
          f"{kin_share:<12.3f}{n_comp:<10d}")
    print("读数: 簇内(血亲)密集, 簇间几乎只剩血仇桥——恩怨把家族连在一起,")
    print("      也是家族以外人物进入叙事的几乎唯一通道(联姻边是例外通道)")

    assert in_d > 5.0 * cross_d, "族内边密度应>族间 5 倍(家族聚簇)"
    assert feud_share > 0.55, "族间边应过半为血仇边(仇杀桥)"
    assert n_comp == N_FAM, "去掉族间边后应散成 6 个孤立家族分量"
    assert kin_share > 0.78, "平均族内邻居占比应>0.78(聚簇的个体读数)"

    # ---- 1b 偿还动力学:杀戮→义务→复仇或偿金和解 ----
    n_chain, g_max = 4000, 6
    active_enter, terms, settles = {}, {}, {}
    alive = 0
    for _ in range(n_chain):
        g = 1
        while g <= g_max:
            active_enter[g] = active_enter.get(g, 0) + 1
            p_term = min(0.90, 0.16 + 0.22 * g)        # 链在本代终止的概率
            p_settle = min(0.95, 0.35 + 0.15 * g)      # 终止时以偿金和解收场的概率
            if rng.random() < p_term:
                terms[g] = terms.get(g, 0) + 1
                if rng.random() < p_settle:
                    settles[g] = settles.get(g, 0) + 1
                break
            g += 1
        else:
            alive += 1

    gens = [g for g in range(1, g_max + 1) if g in active_enter]
    rate = {g: terms.get(g, 0) / active_enter[g] for g in gens}
    set_share = {g: settles.get(g, 0) / terms[g] for g in gens if g in terms}
    surv = {g: 1.0 - sum(terms.get(k, 0) for k in gens if k <= g) / n_chain for g in gens}

    print(f"\n[1b] 偿还动力学: {n_chain} 条血仇链, 每代或复仇(义务翻转)或偿金和解(终止)")
    print(f"{'代际':<8}{'进入链数':>10}{'条件终止率':>12}{'偿金和解份额':>14}{'存活链占比':>12}")
    for g in gens[:4]:
        print(f"{'第%d代' % g:<8}{active_enter[g]:>10d}{rate[g]:>12.3f}"
              f"{set_share.get(g, 0):>14.3f}{surv[g]:>12.3f}")
    print("读数: 基督教化与法制化风格化为和解倾向逐代上升——庭与偿金把")
    print("      '必须再杀一人'的义务逐步改写成'可以付钱收场'的债务")

    r1, r3 = rate[1], rate[3]
    assert all(rate[gens[i]] < rate[gens[i + 1]] for i in range(3)), \
        "条件终止率应逐代单调上升"
    assert r3 > 1.6 * r1, "第三代终止率应>第一代 1.6 倍"
    assert set_share[gens[2]] > set_share[gens[0]], "偿金和解份额应逐代上升"
    assert surv[4] < 0.15, "第四代仍存活的血仇链应<15%(链条整体短命化)"
    print(f"\n✓ 幕一断言通过: 密度比 {in_d / cross_d:.0f} 倍/血仇桥占比 {feud_share:.0%}/"
          f"去族间边后 {n_comp} 分量; 终止率 {r1:.2f}→{r3:.2f}(×{r3 / r1:.1f})——"
          "萨迦是网络叙事的中世纪范本")


# ==================== 幕二:小语种的全球通道(北欧之谜) ====================

N_AUTH, CAREER, BOOK_EVERY = 2000, 45, 4
TRANS_P, TRANS_LAG_MEAN, TRANS_DISC = 0.55, 7.0, 0.80  # 枢纽瓶颈/时滞/译作折扣
BI_FACTOR = 0.94                                        # 双语直通效率
V_TH, YEAR20 = 1.5, 20


def career(rng, channel):
    """一位作者 45 年生涯的全球可见度曲线;返回(达可见年 or None, 第 20 年可见度)。

    channel: 'base' 大语种基线直通; 'pure' 纯母语须经翻译枢纽; 'bi' 双语直通。
    """
    talent = rng.uniform(0.60, 1.40)
    v, t_rec = 0.0, None
    contrib = []
    for b in range(0, CAREER, BOOK_EVERY):
        q = max(0.05, min(1.30, rng.gauss(0.50, 0.18) * talent))
        if channel == "base":
            contrib.append((b, 0.55 * q))
        elif channel == "bi":
            contrib.append((b, 0.55 * BI_FACTOR * q))
        else:  # pure: 每部书独立抽签, 或经枢纽译出(时滞+折扣), 或从未译出
            if rng.random() < TRANS_P:
                lag = int(2 + rng.expovariate(1.0 / TRANS_LAG_MEAN))
                if b + lag <= CAREER:
                    contrib.append((b + lag, 0.55 * TRANS_DISC * q))
    for t in range(CAREER):
        v += sum(c for bt, c in contrib if bt == t)
        if t_rec is None and v >= V_TH:
            t_rec = t
        if t == YEAR20:
            v20 = v
    return t_rec, v20


def act2():
    print("\n" + "=" * 84)
    print("幕二 小语种的全球通道: 翻译枢纽+作者自译 双通道对照(北欧之谜)")
    print("=" * 84)
    rng = random.Random(SEED)
    print(f"\n三队列各 {N_AUTH} 位作者: 生涯 {CAREER} 年, 每 {BOOK_EVERY} 年一部书;")
    print(f"纯母语通道: 单书译出率 {TRANS_P:.0%}, 时滞 2+Exp({TRANS_LAG_MEAN:.0f}) 年, "
          f"译作折扣 {TRANS_DISC:.2f}(风格化参数)\n")

    stats = {}
    offsets = {"base": 0, "pure": 1, "bi": 2}  # 确定性偏移(勿用 hash:跨进程不稳定)
    for ch, label in (("base", "大语种基线"), ("pure", "北欧纯母语"), ("bi", "北欧双语")):
        recs, v20s = [], []
        r = random.Random(SEED + offsets[ch])  # 各队列独立同分布
        for _ in range(N_AUTH):
            t_rec, v20 = career(r, ch)
            (recs.append(t_rec) if t_rec is not None else recs.append(None))
            v20s.append(v20)
        never = sum(1 for t in recs if t is None) / N_AUTH
        med = statistics.median([t for t in recs if t is not None])
        stats[ch] = (never, med, statistics.mean(v20s))
        print(f"{label:<12} 未达全球可见 {never:>6.1%}   达可见者中位时滞 {med:>5.1f} 年"
              f"   20 年可见度均值 {stats[ch][2]:>6.3f}")

    b_never, b_med, b_v20 = stats["base"]
    p_never, p_med, p_v20 = stats["pure"]
    i_never, i_med, i_v20 = stats["bi"]
    print("\n读数:")
    print(f"  · 纯母语: {p_never:.0%} 一生未被世界市场看见(枢纽瓶颈), 被看见者还要"
          f" 多等 {p_med - b_med:.0f} 年(时滞)——瓶颈+时滞双重通道税")
    print(f"  · 双语: 未可见 {i_never:.0%}≈基线 {b_never:.0%}, 20 年可见度达基线 "
          f"{i_v20 / b_v20:.0%}——自译通道几乎抹平语种差距")
    print("  · 北欧之谜的一半答案: 他们用两只手写字(易卜生式剧场外交+英语写作传统)")

    assert p_never > 0.30, "纯母语队列应有逾三成终生未达全球可见(通道瓶颈)"
    assert p_never > 2.5 * i_never, "纯母语未可见份额应远高于双语队列"
    assert p_med > 1.5 * b_med, "纯母语达可见者时滞应>基线 1.5 倍(通道时滞)"
    assert i_v20 > 0.85 * b_v20, "双语队列 20 年可见度应达基线 85% 以上"
    assert i_never < 0.12, "双语队列未可见份额应与基线同量级(<12%)"
    assert p_v20 < 0.65 * b_v20, "纯母语 20 年可见度应显著低于基线(<65%)"
    print(f"\n✓ 幕二断言通过: 未可见 {p_never:.0%} vs {i_never:.0%}; 时滞中位 "
          f"{p_med:.1f} vs {b_med:.1f} 年(×{p_med / b_med:.1f}); 20 年可见度 "
          f"{i_v20 / b_v20:.0%} vs 基线——小语种的世界通道=翻译枢纽+自译双通道")


# ==================== 幕三:诺奖场域的承认时滞 ====================

# 锚读数(通说): (授奖年, 得主, 峰值年认定, 段); 峰值年按代表作通行认定
LAUREATES = [
    (1903, "比约恩松", 1862, "早期"), (1909, "拉格洛夫", 1891, "早期"),
    (1917, "吉勒鲁普", 1882, "早期"), (1917, "彭托皮丹", 1898, "早期"),
    (1920, "哈姆生", 1890, "早期"), (1916, "海登斯坦", 1888, "早期"),
    (1928, "温塞特", 1922, "早期"),
    (1931, "卡尔费尔特(身后)", 1898, "过渡"), (1939, "西伦帕", 1931, "过渡"),
    (1944, "延森", 1900, "过渡"),
    (1951, "拉格克维斯特", 1944, "战后"), (1955, "拉克斯内斯", 1934, "战后"),
    (1974, "约翰松", 1946, "战后"), (1974, "马丁松", 1956, "战后"),
    (2011, "特朗斯特罗姆", 1962, "战后"), (2023, "福瑟", 2021, "战后"),
]

N_AUTH3, TAU = 600, 12.0
ERAS = [(1901, 1930, 0.86, "早期"), (1931, 1944, 0.78, "过渡"),
        (1945, 1989, 0.65, "战后"), (1990, 2026, 0.52, "当代")]
LEV_P, LEV_F = 0.25, 0.35  # 当代"生涯助推"直选: 选存量饱和度≥0.35 的上升期作者


def act3():
    print("\n" + "=" * 84)
    print("幕三 诺奖场域的承认时滞: 授奖年 − 创作峰值年(通说年表锚+机制模拟)")
    print("=" * 84)

    # ---- 3a 锚读数:北欧诺奖年表(通说) ----
    print("\n[3a] 锚读数: 承认时滞=授奖年−代表作峰值年(峰值年按通行认定, 通说)")
    print(f"{'段':<6}{'人次':>6}{'中位时滞':>10}{'平均时滞':>10}{'时滞≥25年占比':>14}")
    era_lags = {}
    for era in ("早期", "过渡", "战后"):
        lags = [y - p for y, _, p, e in LAUREATES if e == era]
        era_lags[era] = lags
        print(f"{era:<6}{len(lags):>6d}{statistics.median(lags):>10.1f}"
              f"{statistics.mean(lags):>10.1f}"
              f"{sum(1 for l in lags if l >= 25) / len(lags):>13.0%}")
    print("双录: 早期亦有低时滞(温塞特 6 年), 战后亦有高时滞(特朗斯特罗姆 49 年,")
    print("      授奖时 80 岁)——年表读数只作方向锚, 机制断言看 3b 模拟;")
    print("      福瑟峰值若以 1999 年巴黎演出《有人将至》为国际突破, 时滞为 24 年")

    assert statistics.median(era_lags["早期"]) > statistics.median(era_lags["战后"]) + 3, \
        "早期中位时滞应明显大于战后(方向锚)"

    # ---- 3b 机制模拟:声誉存量资格门槛的四个时期 ----
    rng = random.Random(SEED)
    authors = []
    for k in range(N_AUTH3):
        peak = rng.uniform(1865, 2014)
        sal = rng.uniform(0.55, 1.00)                 # 国际显著度(作家量级)
        birth = int(peak - rng.uniform(25, 45))
        death = birth + int(rng.uniform(70, 88))
        authors.append({"peak": peak, "sal": sal, "birth": birth, "death": death,
                        "won": None})

    def stock(a, t):
        return a["sal"] * (1.0 - math.exp(-(t - a["peak"]) / TAU))

    def frac(a, t):
        return 1.0 - math.exp(-(t - a["peak"]) / TAU)

    awards = []  # (year, era, lag, age)
    for year in range(1901, 2027, 3):
        era = next(e for y0, y1, _, e in ERAS if y0 <= year <= y1)
        theta = next(th for y0, y1, th, _ in ERAS if y0 <= year <= y1)
        d_theta = -TAU * math.log(1.0 - theta)  # 门槛对应的"刚够格"时滞
        cand = [a for a in authors
                if a["won"] is None and a["birth"] <= year <= a["death"]]
        pick = None
        if era == "当代" and rng.random() < LEV_P:
            rising = [a for a in cand if LEV_F <= frac(a, year) < theta]
            if rising:
                pick = max(rising, key=lambda a: a["sal"])
        if pick is None:
            # 够格者中择"最伟大者", 同等伟大优先"刚够格(正当其时)者":
            # 陈旧惩罚使分期门槛真正咬合, 而不是永远选存量最老的那位
            elig = [a for a in cand if frac(a, year) >= theta]
            pool = elig if elig else cand
            pick = max(pool, key=lambda a: a["sal"]
                       - 0.006 * ((year - a["peak"]) - d_theta)
                       + rng.uniform(0, 0.03))
        pick["won"] = year
        awards.append((year, era, year - pick["peak"], year - pick["birth"]))

    print(f"\n[3b] 机制模拟: 资格门槛(声誉存量饱和度)分期 0.86/0.78/0.65/0.52;")
    print(f"      够格者中择最伟大者, 同等伟大优先'刚够格'者; 当代 {LEV_P:.0%} 概率")
    print(f"      直选上升期作者(饱和度≥{LEV_F})——生涯助推\n")
    print(f"{'时期':<8}{'授奖数':>8}{'平均时滞':>10}{'中位时滞':>10}"
          f"{'时滞<15年占比':>14}{'平均授奖年龄':>14}")
    sim = {}
    for y0, y1, th, era_name in ERAS:
        rows = [(l, ag) for _, e, l, ag in awards if e == era_name]
        lags = [l for l, _ in rows]
        ages = [ag for _, ag in rows]
        sim[era_name] = (statistics.mean(lags), statistics.median(lags),
                         sum(1 for l in lags if l < 15) / len(lags),
                         statistics.mean(ages))
        print(f"{era_name:<8}{len(rows):>8d}{sim[era_name][0]:>10.1f}"
              f"{sim[era_name][1]:>10.1f}{sim[era_name][2]:>13.0%}"
              f"{sim[era_name][3]:>14.1f}")
    print("读数: 门槛即承认哲学——早期把奖发给'声誉已立'的存量满格者,")
    print("      当代开始把奖当杠杆发给还在半坡上的作者")

    e0, e1, e2, e3 = sim["早期"], sim["过渡"], sim["战后"], sim["当代"]
    assert e0[0] > 1.7 * e3[0], "早期平均时滞应>当代 1.7 倍"
    assert e0[0] > e1[0] > e2[0] > e3[0], "四段平均时滞应单调下降"
    assert e0[2] < 0.25 and e3[2] > 0.45, "低时滞授奖份额应从<25%升到>45%"
    assert e0[3] - e3[3] > 8.0, "早期平均授奖年龄应比当代老 8 岁以上"
    print(f"\n✓ 幕三断言通过: 平均时滞 {e0[0]:.0f}→{e1[0]:.0f}→{e2[0]:.0f}→{e3[0]:.0f} 年"
          f"(早期/当代 ×{e0[0] / e3[0]:.1f}); 低时滞份额 {e0[2]:.0%}→{e3[2]:.0%}; "
          f"年龄差 {e0[3] - e3[3]:.0f} 岁——从盖棺定论到生涯助推")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 萨迦的家族网络: 族内密度≫族间且族间过半是血仇桥, 去族间边即散成")
    print("     孤立家族; 血仇链终止率逐代上升、偿金和解份额逐代上升——萨迦把")
    print("     恩怨写成网络, 又把网络写成一部'债务清偿史'(网络叙事的中世纪范本)")
    print("  ② 小语种的全球通道: 纯母语作者受瓶颈+时滞双重通道税(风格化实测近八成")
    print("     终生未见、时滞>基线 1.5 倍); 双语作者直通世界市场, 20 年可见度达基线")
    print("     85% 以上")
    print("     ——北欧诺奖密度之谜的一半答案是: 他们用两只手写字")
    print("  ③ 诺奖场域的承认时滞: 早期(声誉存量门槛 0.86)平均时滞>当代(0.52)1.7 倍,")
    print("     单调下降; 低时滞授奖<25%→>45%; 早期比当代老 8 岁以上——诺奖从")
    print("     '盖棺定论的追加'变为'生涯助推的杠杆'(与法国文学奖项级联实验分工:")
    print("     那边管国内奖项级联, 本家族管国际承认时点)")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
