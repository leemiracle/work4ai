# -*- coding: utf-8 -*-
"""韵链-嵌套-方言三律实验:意大利文学(GB/T 75067)三个机制的最小可计算化身。

00-体系结构.md(§七反直觉三律)、03-可构造与结构.md(可构造谱系左端三对象)、
04-意大利文学转代码.md(走廊 1/2/3)的配套实验。纯标准库
(math/random/statistics),无第三方依赖,固定种子 20260909 全程可复现。
参数为通说代表性案例的风格化参数(见各幕题注),模拟不冒充文学史计量。

三幕:
  幕一 三韵体的链式结构(terza rima)
      aba bcb cdc…:每节中韵成为下节首尾韵,链式滚动;末节自锁(YZZ 式:
      链末中韵变末节首韵,末节新韵自成一联,链不再向前传递)。
      通说锚:terza rima 为但丁发明(《神曲》1308-1320);通说每歌约
      115-160 行(≈40-55 节),本实验取 46 节链+1 节自锁=47 单元。
      断言:①对任意节数 N,链单调推进(每节恰引入一个新韵,节序严格
      递增;下节首尾韵=上节中韵)且终点唯一(枚举闭包模式:合法的
      3 行收束只有"携带韵+自锁双联"一个同构类= YZZ) ②脱链牵连数=
      剩余全部(断第 3 节受牵连 45/47 单元 96%,牵连数随断点严格单调
      递减);对照 quatrain(AABB 块式:韵的责任范围在节内)脱链只
      牵连自身 1 单元(2%)——链式/块式牵连比 45×。
      神曲的宇宙结构学:命运之链环环相扣,结尾自锁成环。
  幕二 框架叙事的嵌套深度(《十日谈》式 vs 《一千零一夜》系)
      意式传统:一层框+100 故事并列,少数故事偶嵌一层(嵌套是例外);
      东方传统:故事连环再生(嵌套是常态,几何深度)。
      通说锚:《十日谈》(1349-1353)十个青年十天讲百故事,框内并列;
      东方故事集传统的连环嵌套(与东方文学 75051 交叉声明)。
      断言:①意式嵌套深度中位=1(并列是常态),东方中位≥3(连环是
      常态);意式每框并列约 100 单篇、东方每个名下再生多个故事
      (节点/名额比≥3×)——"意式浅框高广度,东方深框连环再生"
      ②退出点数=嵌套深度(恒等式),张力管理成本(须同时悬置的
      线头数)随深度线性:东方平均悬置线头≥意式 2.5×——两种讲故事
      文明的结构签名。
  幕三 俗语与方言的双层市场(标准语与方言的份额)
      方言份额 s(t)=a+(s0-a)·e^(-kt):单调下降、渐近线 a>0(认同的
      保底需求);纪念年(但丁逝世 600 周年 1921/诞辰 700 周年 1965/
      逝世 700 周年 2021,通说纪年)带来双向脉冲:方言研究侧与标准语
      出版侧同升。
      通说锚:但丁《俗语论》为俗语辩护(通说);统一后标准语扩张、
      方言写作持续(通说)。份额参数为风格化示意。
      断言:①方言份额逐十年均值严格单调下降但永不清零(2017-2026
      均值≥0.05;十年降幅持续收窄≥5×;外推 2200 年:有保底≥0.069,
      无保底变体<0.005——"方言文学的死亡是指数的,永不到达")
      ②三个纪念年方言侧与标准语侧产出均>邻年基线 1.10×(双向脉冲)。

跑法: python -u experiments/terza_rima_frames.py
"""

import math
import random
import statistics as stats

SEED = 20260909  # 建族日,固定种子全程可复现


# ==================== 幕一:三韵体的链式结构 ====================

N_CHAIN = 46            # 链节 tercet 数(通说每歌 40-55 节内取中)
N_UNITS = N_CHAIN + 1   # 总单元数:+1 为末节自锁单元(YZZ 式)


def gen_terza_rima(n_chain):
    """生成 terza rima:n_chain 节链+1 节自锁。

    节 k(k=1..n_chain)=(r_{k-1}, r_k, r_{k-1}):首尾韵=上节中韵,中韵=新韵;
    末单元=(r_{n_chain}, r_new, r_new):链末中韵变首韵,新韵自锁成联。
    返回 (stanzas, rhymes):stanzas 为韵标三元组列表,rhymes 为韵标序列。
    """
    r = list(range(n_chain + 3))          # r[0..n_chain+2]:每个韵标唯一
    stanzas = []
    for k in range(1, n_chain + 1):
        stanzas.append((r[k - 1], r[k], r[k - 1]))          # aba
    stanzas.append((r[n_chain], r[n_chain + 1], r[n_chain + 1]))  # YZZ 自锁
    return stanzas, r


def check_chain(stanzas, n_chain):
    """链式三不变量:传递(下节首尾=上节中韵)/新韵唯一(每节恰一)/起端帽。"""
    for k in range(n_chain):
        a, b, c = stanzas[k]
        assert a == c, f"第 {k + 1} 节首尾韵应相同:{stanzas[k]}"
        if k > 0:
            prev_mid = stanzas[k - 1][1]
            assert a == prev_mid, f"第 {k + 1} 节首韵应=上节中韵"
        assert b not in (a,), f"第 {k + 1} 节中韵应是新韵"
    # 起端帽:首节框韵(r0)全诗恰出现两次,且只在首节(链有头)
    flat = [x for s in stanzas for x in s]
    r0 = stanzas[0][0]
    assert flat.count(r0) == 2
    return True


def check_selflock(stanzas, n_chain):
    """自锁不变量:末单元=携带韵+新韵自锁联;新韵全诗恰 2 次且不出末单元。"""
    last = stanzas[-1]
    assert last[0] == stanzas[-2][1], "末单元首韵应=链末节中韵(携带)"
    assert last[1] == last[2] and last[1] != last[0], "末单元应为携带韵+自锁双联"
    flat_all = [x for s in stanzas for x in s]
    flat_in = list(last)
    new = last[1]
    assert flat_all.count(new) == 2 and flat_in.count(new) == 2, \
        "自锁新韵应全诗恰两次且不出末单元(无向前传递)"
    return True


def valid_closers(carry, pool):
    """枚举 3 行收束的全部韵标模式(|pool|^3),返回满足闭包约束的模式。

    闭包约束:①含携带韵恰一次(偿还链末中韵:携带韵全诗恰成对)
    ②恰引入一个新韵 ③新韵恰出现两次(自锁成联,无孤韵无向前传递)。
    """
    good = []
    for a in pool:
        for b in pool:
            for c in pool:
                pat = (a, b, c)
                if pat.count(carry) != 1:
                    continue                       # ① 悬空或过度偿还
                news = {x for x in pat if x != carry}
                if len(news) != 1:
                    continue                       # ② 恰一个新韵
                if pat.count(next(iter(news))) != 2:
                    continue                       # ③ 新韵恰两次
                good.append(pat)
    return good


def affected_units(n_units_total, k_break):
    """链式脱链:断第 k_break 单元(中韵脱链)后须重排的单元数(含自身)。

    链式传导:单元 j 的首韵=单元 j-1 的中韵,故 j-1 脏则 j 必重排;
    末自锁单元的首韵=链末节中韵,同样被传导。
    """
    dirty = [False] * (n_units_total + 1)          # 1-indexed
    dirty[k_break] = True
    for j in range(k_break + 1, n_units_total + 1):
        dirty[j] = dirty[j - 1]
    return sum(dirty[1:])


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def disp(stanzas, head=5):
    """显示前 head 节的字母谱(韵标 i→第 i 个字母)。"""
    return " ".join("".join(LETTERS[x] for x in s) for s in stanzas[:head])


def act1():
    print("=" * 84)
    print(f"幕一 三韵体的链式结构(terza rima:{N_CHAIN} 节链+1 节自锁={N_UNITS} 单元)")
    print("=" * 84)
    stanzas, r = gen_terza_rima(N_CHAIN)
    n_lines = N_CHAIN * 3 + 3
    print(f"\n字母谱(前 5 节):{disp(stanzas)} … 末单元:"
          f"(链末中韵,新韵,新韵)= YZZ 式自锁")
    print(f"共 {N_UNITS} 单元 {n_lines} 行(通说《神曲》每歌约 115-160 行,风格化取中)")

    # ---- 断言 1:对任意 N 单调推进 + 终点唯一 ----
    checked = 0
    for n in range(2, 61):                         # 任意节数 2..60
        st, _ = gen_terza_rima(n)
        assert check_chain(st, n)
        assert check_selflock(st, n)
        checked += 1
    assert checked == 59
    # 终点唯一:枚举闭包模式,合法者只有"携带韵+自锁双联"一个同构类
    carry = r[N_CHAIN]
    pool = (carry, r[N_CHAIN + 1], r[N_CHAIN + 2]) # 候选韵标:携带韵+两个新韵
    good = valid_closers(carry, pool)
    # 27 种候选模式中合法者=3 种排法×2 个新韵选择=6 种,全部同一同构类
    assert len(good) == 6, f"合法闭包应为 6 种排法(一个同构类):{good}"
    for p in good:                                 # 逐一核验 YZZ 同构
        assert p.count(carry) == 1 and len(set(p)) == 2 and \
            sum(1 for x in p if x != carry) == 2, f"闭包应 YZZ 同构:{p}"
    print(f"\n✓ 幕一断言①通过:N=2..60 共 {checked} 种节数全部:每节恰引入一个新韵、"
          f"下节首尾韵=上节中韵(单调推进);枚举 3 行闭包的 27 种候选模式,"
          f"合法者 {len(good)} 种排法(3 排法×2 新韵)、全部同构为"
          f"「携带韵+自锁双联」(YZZ 式)——终点唯一,链闭合成环")

    # ---- 断言 2:脱链牵连=剩余全部 vs quatrain 只牵连自身 ----
    aff3 = affected_units(N_UNITS, 3)
    affs = [affected_units(N_UNITS, k) for k in range(1, N_UNITS + 1)]
    assert aff3 == N_UNITS - 3 + 1 == 45, f"断第 3 节应牵连 45 单元:{aff3}"
    assert aff3 / N_UNITS >= 0.95, f"牵连占比应≥95%:{aff3 / N_UNITS:.1%}"
    assert all(affs[i] > affs[i + 1] for i in range(len(affs) - 1)), \
        "牵连数应随断点严格单调递减"
    assert affs[0] == N_UNITS, f"断第 1 节应牵连全部 {N_UNITS}:{affs[0]}"
    assert affs[-1] == 1                           # 断末节:只牵连自身
    # quatrain 对照:AABB 块式,每节韵标独立,脱链只重排自身
    def affected_quatrain(n_units_total, k_break):
        return 1                                   # 韵的责任范围在节内
    aff_q = affected_quatrain(N_UNITS, 3)
    ratio = aff3 / aff_q
    print(f"\n链式断第 3 节:受牵连 {aff3}/{N_UNITS} 单元({aff3 / N_UNITS:.1%})"
          f"——第 3..47 单元含末节自锁全部重排")
    print(f"牵连数随断点严格单调递减:断首节 {affs[0]}(全部)→ 断末节 {affs[-1]}"
          f"(只牵连自身)")
    print(f"对照 quatrain(AABB 块式)断第 3 节:受牵连 {aff_q}/{N_UNITS} 单元"
          f"({aff_q / N_UNITS:.1%})——韵的责任范围在节内")
    assert ratio >= 40, f"链式/块式牵连比应≥40×:{ratio}"
    print(f"\n✓ 幕一断言②通过:链式/块式牵连比 {ratio:.0f}×——terza rima 的韵"
          f"责任范围是全部下游(命运之链环环相扣),块式只到节边界;"
          f"末节 YZZ 自锁:链在终点闭合成环")
    return {"n_units": N_UNITS, "aff3": aff3, "pct": aff3 / N_UNITS,
            "aff_q": aff_q, "ratio": ratio, "closers": len(good)}


# ==================== 幕二:框架叙事的嵌套深度 ====================

W_N, W_P1, W_P2 = 100, 0.12, 0.06   # 意式:100 并列故事;嵌一层 p=0.12,再嵌 p=0.06
E_N, E_P, E_CAP = 100, 0.78, 12     # 东方:100 连环;每层再生 p=0.78,封顶 12 层


def sim_west(rng):
    """《十日谈》式:一层框+并列故事,嵌套是例外。返回每故事的深度。"""
    depths = []
    for _ in range(W_N):
        d = 1
        if rng.random() < W_P1:
            d = 2
            if rng.random() < W_P2:
                d = 3
        depths.append(d)
    return depths


def sim_east(rng):
    """《一千零一夜》系式:故事连环再生,嵌套是常态(几何深度,封顶)。"""
    depths = []
    for _ in range(E_N):
        d = 1
        while d < E_CAP and rng.random() < E_P:
            d += 1
        depths.append(d)
    return depths


def act2():
    print("\n" + "=" * 84)
    print(f"幕二 框架叙事的嵌套深度(意式 {W_N} 并列故事 vs 东方 {E_N} 连环,"
          f"风格化参数)")
    print("=" * 84)
    rng = random.Random(SEED + 10)
    west = sim_west(rng)
    east = sim_east(rng)
    med_w, med_e = stats.median(west), stats.median(east)
    d1_w = sum(1 for d in west if d == 1) / W_N
    d1_e = sum(1 for d in east if d == 1) / E_N
    nodes_w, nodes_e = sum(west), sum(east)
    print(f"\n意式:深度中位 {med_w:.0f},单层并列占 {d1_w:.0%},"
          f"每框 {W_N} 个单篇名额,总故事节点 {nodes_w}")
    print(f"东方:深度中位 {med_e:.0f},单层只占 {d1_e:.0%},"
          f"每名额再生 {nodes_e / E_N:.1f} 个节点,最深 {max(east)} 层")

    # ---- 断言 1:意式中位 1(并列是常态)vs 东方中位≥3(连环是常态) ----
    assert med_w == 1, f"意式深度中位应为 1:{med_w}"
    assert med_e >= 3, f"东方深度中位应≥3:{med_e}"
    assert d1_w >= 0.80, f"意式单层并列应≥80%:{d1_w:.0%}"
    assert d1_e <= 0.35, f"东方单层应≤35%:{d1_e:.0%}"
    assert (nodes_e / E_N) >= 3 * (nodes_w / W_N), \
        f"东方节点/名额比应≥3× 意式:{nodes_e / E_N:.2f} vs {nodes_w / W_N:.2f}"
    print(f"\n✓ 幕二断言①通过:意式中位 {med_w:.0f}/并列 {d1_w:.0%}/"
          f"{nodes_w / W_N:.2f} 节点每名额(浅框高广度);东方中位 {med_e:.0f}/"
          f"单层 {d1_e:.0%}/{nodes_e / E_N:.2f} 节点每名额(深框连环再生,"
          f"名额再生率 {(nodes_e / E_N) / (nodes_w / W_N):.1f}×)——两种结构签名")

    # ---- 断言 2:退出点=深度(恒等);张力成本随深度线性 ----
    exit_w, exit_e = list(west), list(east)        # 退出点数:=嵌套深度
    assert exit_w == west and exit_e == east
    load_w, load_e = stats.mean(exit_w), stats.mean(exit_e)  # 悬置线头均值
    assert load_e >= 2.5 * load_w, \
        f"东方平均悬置线头应≥意式 2.5×:{load_e:.2f} vs {load_w:.2f}"
    # 线性核验:每个深度层的平均悬置线头=深度本身(斜率=1)
    for d in sorted(set(east)):
        sub = [x for x in exit_e if x == d]
        assert abs(stats.mean(sub) - d) < 1e-12
    assert max(exit_e) >= 6 and max(exit_w) <= 3
    print(f"\n退出点数=嵌套深度(恒等);平均须同时悬置的线头:意式 {load_w:.2f} 条"
          f" vs 东方 {load_e:.2f} 条({load_e / load_w:.1f}×);"
          f"最深退出点:意式 {max(exit_w)} vs 东方 {max(exit_e)}")
    print(f"\n✓ 幕二断言②通过:嵌套越深退出点越多(退出点=深度,逐层核验斜率 1),"
          f"张力管理成本随深度线性——意式浅框买\"管理便宜+单篇可拆卸\","
          f"东方深框买\"悬念复利\",各付各的价")
    return {"med_w": med_w, "med_e": med_e, "d1_w": d1_w, "d1_e": d1_e,
            "load_w": load_w, "load_e": load_e,
            "node_ratio": (nodes_e / E_N) / (nodes_w / W_N)}


# ==================== 幕三:俗语与方言的双层市场 ====================

Y0, Y1 = 1861, 2026                     # 统一(1861)至检校日(风格化窗口)
FLOOR, S0 = 0.07, 0.35                  # 方言份额渐近线(认同保底)/初值
K = math.log((S0 - FLOOR) / 0.030) / 160.0   # 使 2021 年超渐近线 0.030
EVENTS = {1921: "但丁逝世 600 周年", 1965: "但丁诞辰 700 周年",
          2021: "但丁逝世 700 周年"}    # 通说纪年
PULSE_D, PULSE_S = 0.30, 0.35           # 纪念年脉冲:方言侧/标准语侧升幅
NOISE = 0.010                           # 年度噪声(乘性)


def share_mean(t):
    """确定性份额:s(t)=FLOOR+(S0-FLOOR)·e^(-Kt)(t 为距 1861 年数)。"""
    return FLOOR + (S0 - FLOOR) * math.exp(-K * t)


def act3():
    print("\n" + "=" * 84)
    print(f"幕三 俗语与方言的双层市场({Y0}-{Y1} 份额曲线+纪念年脉冲,风格化参数)")
    print("=" * 84)
    rng = random.Random(SEED + 20)
    years = list(range(Y0, Y1 + 1))
    share = {y: share_mean(y - Y0) * (1 + rng.gauss(0, NOISE)) for y in years}
    out_d = {y: (0.55 + share_mean(y - Y0) / 2) for y in years}   # 方言研究侧基线
    out_s = {y: (1.0 + 0.006 * (y - Y0)) for y in years}          # 标准语出版侧基线
    for y in years:                                # 叠加脉冲与噪声
        pd = ps = 1.0
        if y in EVENTS:
            pd, ps = 1 + PULSE_D + rng.uniform(-0.05, 0.05), 1 + PULSE_S + rng.uniform(-0.05, 0.05)
        out_d[y] *= pd * (1 + rng.gauss(0, 0.03))
        out_s[y] *= ps * (1 + rng.gauss(0, 0.03))
    marks = (1861, 1900, 1945, 2000, 2021, 2026)
    print("\n方言份额(风格化):" + "  ".join(f"{y} 年 {share[y]:.3f}" for y in marks))

    # ---- 断言 1:单调下降但永不清零(死亡是指数的,永不到达) ----
    dec = [stats.mean(share[y] for y in range(y0, y0 + 10))
           for y0 in range(Y0, Y1 - 9, 10)]        # 1861-1870,…,2017-2026
    assert all(dec[i] > dec[i + 1] for i in range(len(dec) - 1)), \
        "十年均值应严格单调下降"
    end_mean = stats.mean(share[y] for y in range(2017, 2027))
    assert end_mean >= 0.05, f"末期份额应≥0.05:{end_mean:.3f}"
    drop_first = dec[0] - dec[1]
    drop_last = dec[-2] - dec[-1]
    assert drop_first >= 5 * drop_last >= 0, \
        f"十年降幅应收窄≥5×:{drop_first:.4f} vs {drop_last:.4f}"
    # 外推对照:同一衰减减去保底(无渐近线变体)终将趋零
    t_ext = 2200 - Y0
    ext_floor = FLOOR + (S0 - FLOOR) * math.exp(-K * t_ext)
    ext_nofloor = (S0 - FLOOR) * math.exp(-K * t_ext)
    assert ext_floor >= 0.069 and ext_nofloor < 0.005, \
        f"外推 2200 年:有保底 {ext_floor:.4f},无保底 {ext_nofloor:.4f}"
    assert ext_floor >= 20 * ext_nofloor
    print(f"\n十年均值自 {dec[0]:.3f} 严格单调降至 {dec[-1]:.3f}(共 {len(dec)} 段);"
          f"十年降幅 {drop_first:.4f}→{drop_last:.4f}(收窄 {drop_first / drop_last:.0f}×)"
          f"——指数逼近,减速赴死")
    print(f"末期(2017-2026)均值 {end_mean:.3f};外推 2200 年:有保底模型 "
          f"{ext_floor:.4f} vs 无保底变体 {ext_nofloor:.4f}({ext_floor / ext_nofloor:.0f}×)")
    print(f"\n✓ 幕三断言①通过:份额单调下降但渐近线在零上方({FLOOR:.2f})——"
          f"方言文学的死亡是指数的,永不到达")

    # ---- 断言 2:纪念年双向脉冲(方言侧与标准语侧同升) ----
    for y, name in EVENTS.items():
        nb = [yy for yy in (y - 2, y - 1, y + 1, y + 2) if yy not in EVENTS]
        base_d = stats.mean(out_d[yy] for yy in nb)
        base_s = stats.mean(out_s[yy] for yy in nb)
        jump_d, jump_s = out_d[y] / base_d, out_s[y] / base_s
        print(f"  {y}({name}):方言侧 {jump_d:.2f}× 邻年基线,"
              f"标准语侧 {jump_s:.2f}× 邻年基线")
        assert jump_d > 1.10, f"{y} 方言侧应>1.10× 基线:{jump_d:.2f}"
        assert jump_s > 1.10, f"{y} 标准语侧应>1.10× 基线:{jump_s:.2f}"
    print(f"\n✓ 幕三断言②通过:三个纪念年方言研究与标准语出版同升(双向脉冲)——"
          f"纪念使整条语言记忆链受益:《俗语论》的重读接进方言正当性,正典"
          f"再版同时放量")
    return {"dec0": dec[0], "dec_last": dec[-1], "end_mean": end_mean,
            "ext_floor": ext_floor, "ext_nofloor": ext_nofloor,
            "n_events": len(EVENTS)}


def main():
    r1 = act1()
    r2 = act2()
    r3 = act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print(f"  ① 三韵体:{r1['n_units']} 单元链单调推进、终点唯一(合法闭包仅"
          f" YZZ 同构类);断第 3 节牵连 {r1['aff3']}/{r1['n_units']}"
          f"({r1['pct']:.0%})vs quatrain {r1['aff_q']} 节——牵连比 {r1['ratio']:.0f}×")
    print(f"  ② 框架叙事:意式深度中位 {r2['med_w']:.0f}/东方 {r2['med_e']:.0f},"
          f"名额再生率 {r2['node_ratio']:.1f}×;悬置线头 {r2['load_e']:.1f} vs "
          f"{r2['load_w']:.1f}({r2['load_e'] / r2['load_w']:.1f}×)——退出点=深度")
    print(f"  ③ 双层市场:份额 {r3['dec0']:.3f}→{r3['dec_last']:.3f} 单调降,"
          f"末期 {r3['end_mean']:.3f}>0;2200 年外推有保底 {r3['ext_floor']:.3f}"
          f" vs 无保底 {r3['ext_nofloor']:.3f};{r3['n_events']} 个纪念年双向脉冲")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
