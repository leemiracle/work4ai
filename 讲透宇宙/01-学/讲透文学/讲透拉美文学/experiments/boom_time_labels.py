# -*- coding: utf-8 -*-
"""魔幻时序-爆炸窗口-标签市场三律模拟:拉美文学家族实验(GB/T 75081)。

00-体系结构.md(§七反直觉三发现)、03-可构造与结构.md(三条结构引擎的
严格可构造性)、04-拉美文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260909 可复现。

风格化声明:叙事结构参数、市场窗口参数、标签流行度曲线均为机制研究用的
风格化设定,断言针对"机制模式"(预告-应验时序/条件链爆发/标签稀释),
不是史实拟合;作家作品评述一律通说文学史口径(运动年代与出版机制按通说,
涉拉美政治史按学术史平实叙述)。

三幕:
  幕一 魔幻现实的时序结构(《百年孤独》式叙事时序: 预告未来+回环):
      同一组 40 个叙事单元,对照两种时序设计——线性文本(编年顺序,
      局部因果铺垫,金字塔式赌注爬坡)vs 马孔多式文本(开篇首句闪前预告
      中景事件(通说:首句"多年以后,面对行刑队……"即闪前),大事件按
      "多年以后"公式提前半程预告,尾声回环呼应开篇)。
      张力=某阅读位置上"未偿的悬念债"总量(预告即开债,应验即还债)。
      断言:①"预告-应验"结构使张力曲线整体前移:马孔多式张力重心(位置
            加权均值)显著小于线性式(重心从后段移到中段),前半程张力
            份额过半(线性式不过半)
           ②回环结构使重读收益倍增:第二次阅读识别的伏笔密度≥第一次的
            2 倍(伏笔在首读只被公式标出,全图在手才被认全),且马孔多式
            第二读伏笔密度≥线性式第二读的 3 倍——马孔多的时序是设计
            出来的重读机器。
  幕二 Boom 的世界市场爆发(巴塞罗那线):
      1940-1990 逐年模拟拉美小说的"世界可见度":待发存货池(此前积累的
      作品存量)按当年发行容量放出;三环先决条件——注意力事件 A(t)
      (1959 古巴革命的注意力冲击,1971 帕迪利亚事件后降温,学术史通说)、
      巴塞罗那全球西语发行 B(1962 起发行容量跃升并爬坡:塞伊克斯·巴拉尔
      一系,通说)、翻译接力 T(1966-1970 法语/英语接力到位,世界可见度
      倍增;世界的成功反馈抬高签约印量)。反事实:去掉翻译接力(只剩迟到
      的渗漏式译入)。
      断言:①爆发窗口集中:1963-1972 十年窗口吃掉全程可见度≥55%(均匀
            基线约 20%),且窗口内释放量≥1962 年积累的全部存量——十年
            释放此前二十余年的积累
           ②缺一环则爆发推迟:去掉翻译接力,峰值降至基线的 55% 以下,
            峰值年推迟 8 年以上(被推出观察窗),可见度中位年推迟 5 年
            以上——条件链缺一环,爆发就不是爆发,是渗漏。
  幕三 标签的市场动力学("魔幻现实主义"的营销史):
      1948-2020 逐年模拟"魔幻现实主义"标签的贴标书目:标签流行度 L(t)
      从概念期(罗尔 1925 美术批评铸词→乌斯拉尔·彼特里 1948 引入拉美
      批评,通说)经爆炸期(1967《百年孤独》/1982 诺奖)到营销期(货架
      类别);贴标书目的"正典线纯度"随流行度稀释(概念期批评家只给奇妙
      现实谱系的真成员贴标,营销期货架什么都贴)。反标签运动(McOndo 式,
      1996 文选对"马孔多"标签的戏仿宣言,通说):贴标/去标作家在旧市场
      (爆炸代读者与加冕建制)与后爆炸读者群两个市场的采用率对照。
      断言:①标签稀释:贴标书目的中位正典分随标签流行度下降(corr(L,
            中位正典分)≤−0.80),概念期中位分≥营销期的 1.9 倍——标签
            早期聚集正典,后期稀释为货架类别
           ②反标签部分成功:后爆炸读者群中去标作家采用率≥贴标的 1.5 倍
            (胜出),旧市场中去标采用率≤贴标的 55% 且入典率不足贴标的
            四成(失联),但末期两市场合计去标总采用追平贴标——标签是
            船票也是牢笼。

实验分工声明:美国文学家族实验管正典的再分配(席位/双轨/双市场),本
家族管拉美现场的三台机器——叙事时序的重读结构、世界市场的爆发窗口、
标签的生命周期——三层不同题,互不重复。

跑法: python -u experiments/boom_time_labels.py
"""

import math
import random
import statistics

SEED = 20260909  # 建族日作种子,可复现


# ==================== 幕一:魔幻现实的时序结构 ====================

N_UNITS = 40          # 叙事单元数
GRID = 100            # 张力曲线采样格点


def unit_weights():
    """事件权重:后段事件(世代级大事)权重更高。"""
    return [0.5 + 0.9 * (i + 1) / N_UNITS for i in range(N_UNITS)]


def linear_debts(w):
    """线性文本:编年顺序讲述,局部因果铺垫(前一单元→本单元),
    中点/终点两个大高潮的铺垫埋在临近处——悬念债几乎全程短打,
    张力靠赌注爬坡(金字塔)推到后段。"""
    debts = []
    for i in range(N_UNITS):
        debts.append((max(0, i - 1) / N_UNITS, i / N_UNITS, 0.35 * w[i], False))
    debts.append((15 / N_UNITS, 19 / N_UNITS, 0.55 * w[19], False))   # 中点临近铺垫
    debts.append((36 / N_UNITS, 39 / N_UNITS, 0.70 * w[39], False))   # 终点临近铺垫
    return debts


def macondo_debts(w):
    """马孔多式文本:同样的事件与权重,时序另设计——开篇首句闪前预告
    中景事件(通说:首句即闪前"面对行刑队"一幕);大事件按"多年以后"
    公式提前约半程预告;尾声回环(首尾呼应)再收最大一笔债。"""
    debts = []
    for i in range(N_UNITS):                                          # 局部因果仍在
        debts.append((max(0, i - 1) / N_UNITS, i / N_UNITS, 0.30 * w[i], False))
    debts.append((0.02, 13 / N_UNITS, 0.85 * w[13], True))            # 首句闪前
    debts.append((0.03, 0.97, 0.90 * w[N_UNITS - 1], True))           # 羊皮卷弧线:
    # 开篇即立"终局才解码"的总债(梅尔基亚德斯羊皮卷, 通说: 全书框架即伏笔)
    for j in range(4, N_UNITS + 1, 4):                                # "多年以后"公式预告
        debts.append((0.35 * j / N_UNITS, j / N_UNITS, 0.60 * w[j - 1], True))
    debts.append((0.75, 0.98, 0.80 * w[N_UNITS - 1], True))           # 尾声回环
    return debts


def tension_curve(debts, ramp=False):
    """张力曲线:位置 x 上的未偿悬念债总量;线性式再乘金字塔爬坡
    (赌注随剧情升高),马孔多式不乘(悬念被时序摊到全程)。"""
    xs = [(k + 0.5) / GRID for k in range(GRID)]
    ys = []
    for x in xs:
        open_w = sum(wt for a, b, wt, _ in debts if a < x <= b)
        ramp_f = (0.35 + 0.65 * x) if ramp else 1.0
        ys.append(open_w * ramp_f)
    return xs, ys


def centroid(xs, ys):
    tot = sum(ys)
    return sum(x * y for x, y in zip(xs, ys)) / tot


def half_share(xs, ys):
    tot = sum(ys)
    return sum(y for x, y in zip(xs, ys) if x <= 0.5) / tot


def reread(debts, rng):
    """两遍阅读的伏笔识别密度(每叙事单元识别数)。设计伏笔(闪前/
    公式预告/回环)首读只被公式标出(p=0.42),全图在手才被认全
    (p=0.88);线性式的零星远距铺垫无人标出(p=0.12/0.55)。"""
    designed = [(a, b) for a, b, wt, d in debts if d]
    p1, p2 = 0.42, 0.88
    d1 = sum(rng.random() < p1 for _ in designed) / N_UNITS
    d2 = sum(rng.random() < p2 for _ in designed) / N_UNITS
    return d1, d2, len(designed)


def act1():
    print("=" * 84)
    print("幕一 魔幻现实的时序结构: 同一组 40 单元, 线性编年 vs 马孔多式(闪前+预告+回环)")
    print("=" * 84)
    rng = random.Random(SEED)
    w = unit_weights()
    lin = linear_debts(w)
    mac = macondo_debts(w)
    xl, yl = tension_curve(lin, ramp=True)
    xm, ym = tension_curve(mac)
    c_l, c_m = centroid(xl, yl), centroid(xm, ym)
    h_l, h_m = half_share(xl, yl), half_share(xm, ym)

    print(f"\n阅读位置(十分位)张力曲线(未偿悬念债总量):")
    print(f"{'位置':>4} {'线性式':>7} {'马孔多式':>8}")
    for k in range(0, GRID, GRID // 10):
        print(f"{xl[k]:>4.1f} {yl[k]:>7.2f} {ym[k]:>8.2f}")

    print(f"\n[1a] 张力重心(位置加权均值): 线性式 {c_l:.3f} vs 马孔多式 {c_m:.3f} "
          f"(前移 {c_l - c_m:.3f})")
    print(f"      前半程张力份额: 线性式 {h_l:.3f} vs 马孔多式 {h_m:.3f}")
    print("读数: 预告-应验把悬念债提前半程开出——张力曲线整体前移, 重心从")
    print("      后段移到中段; 线性式的金字塔把赌注押在后程, 前半程不过半")

    d1m, d2m, nm = reread(mac, rng)
    xl_debts = [(a, b) for a, b, wt, d in lin if not d]  # 线性式无设计伏笔
    d1l = 0.12 * 3 / N_UNITS   # 零星远距铺垫的首读识别(风格化: 全书约 3 处)
    d2l = 0.55 * 3 / N_UNITS   # 二读靠全局对照认出的 incidental 铺垫
    print(f"\n[1b] 重读收益(伏笔识别密度/单元):")
    print(f"      马孔多式({nm} 处设计伏笔): 第一读 {d1m:.3f} → 第二读 {d2m:.3f} "
          f"(×{d2m / d1m:.2f})")
    print(f"      线性式(约 3 处零星铺垫):  第一读 {d1l:.3f} → 第二读 {d2l:.3f} "
          f"(×{d2l / d1l:.2f})")
    print(f"      第二读密度对比: 马孔多式 {d2m:.3f} = 线性式 {d2l:.3f} 的 "
          f"{d2m / d2l:.1f} 倍")
    print("读数: 线性式的倍率是低基数假象(3 处铺垫从 0.009 涨到 0.041), ")
    print(f"      看密度: 马孔多式第二读 {d2m:.3f}/单元 = 线性式的 "
          f"{d2m / d2l:.0f} 倍——首读只见")
    print("      公式('多年以后'), 全图在手才认出预告指哪, 回环结构的第二遍")
    print("      才是完整版: 马孔多的时序是设计出来的重读机器")

    assert c_m <= 0.54 and c_l >= 0.62 and (c_l - c_m) >= 0.08, \
        f"张力重心应前移(线性 {c_l:.3f} vs 马孔多 {c_m:.3f})"
    assert h_m >= 0.42 and h_l <= 0.36 and (h_m - h_l) >= 0.05, \
        f"前半程张力份额: 马孔多 {h_m:.3f} 应近半, 线性 {h_l:.3f} 应不过半"
    assert d2m >= 2.0 * d1m, f"马孔多式二读伏笔密度应≥首读 2 倍, 实测 ×{d2m/d1m:.2f}"
    assert d2m >= 3.0 * d2l, \
        f"马孔多式二读密度应≥线性式 3 倍, 实测 ×{d2m/d2l:.1f}"
    print(f"\n✓ 幕一断言通过: 张力重心 {c_l:.2f}→{c_m:.2f}(前移, 前半程份额 "
          f"{h_l:.2f}→{h_m:.2f});重读伏笔密度 ×{d2m/d1m:.1f}, 二读密度 "
          f"{d2m/d2l:.0f}× 于线性式——马孔多的时序是设计出来的重读机器")


# ==================== 幕二:Boom 的世界市场爆发(巴塞罗那线) ====================

YEARS2 = list(range(1940, 1991))
POOL0 = 8.0            # 1940 年存量(此前积累)


def inflow2(t):
    """年产新作流入;1960-1972 爆炸一代自身在窗口内持续交稿(风格化)。"""
    return 1.8 if 1960 <= t <= 1972 else 0.9


def attention2(t):
    """注意力事件 A(t): 1959 古巴革命的注意力冲击;1971 帕迪利亚事件
    后欧洲左翼同情降温(学术史通说,平实叙述)。"""
    if 1959 <= t <= 1970:
        return 1.45
    return 1.05 if t > 1970 else 1.0


def capacity(t, ceil, tau, relay=True):
    """发行容量:1962 巴塞罗那全球西语发行线启动后逐步爬坡;翻译接力
    的世界成功反馈抬高签约与印量(无接力则天花板小一号、爬坡更慢)。"""
    if t < 1959:
        return 0.42
    if t < 1962:
        return 0.80 * attention2(t)
    ramp = 0.80 + (ceil - 0.80) * (1.0 - math.exp(-(t - 1962) / tau))
    return min(ramp, ceil) * attention2(t)


def reach(t, relay=True):
    """世界可见度倍增器:翻译接力(1966-1970 法语/英语到位)×2.5;
    无接力只剩 1975 年后迟到的渗漏式译入(每年+0.05)。"""
    if relay:
        if t < 1966:
            return 1.0
        if t >= 1970:
            return 2.5
        return 1.0 + 1.5 * (t - 1965) / 5.0
    return 1.0 if t <= 1974 else 1.0 + 0.05 * (t - 1974)


def saturation(t, relay=True):
    """爆发后的新鲜感饱和:世界啃完这一波, 胃口衰减(仅爆发线才有饱和;
    无接力的渗漏线没有爆发, 也就没有饱和)。"""
    if not relay:
        return 1.0
    s = 1.0
    for _ in range(1973, t + 1):
        s = max(0.30, s * 0.86)
    return s


def boom_sim(relay=True):
    """逐年模拟: 存货池+新作流入, 按当年容量放出;可见度=释放×接力×饱和。"""
    rng = random.Random(SEED)
    ceil, tau = (3.3, 3.0) if relay else (1.9, 5.0)
    pool, series = POOL0, {}
    pool_1962 = None
    for t in YEARS2:
        if t == 1962:
            pool_1962 = pool
        cap = capacity(t, ceil, tau)
        avail = pool + inflow2(t)
        release = min(avail, cap)
        pool = avail - release
        v = release * reach(t, relay) * saturation(t, relay) * rng.uniform(0.94, 1.06)
        series[t] = {"release": release, "v": v, "pool": pool}
    return series, pool_1962


def moving_peak(series):
    """三年滑动平均的峰值年与峰值(降噪后定位爆发顶点)。"""
    ys = list(YEARS2)
    ma = {t: statistics.mean([series[x]["v"] for x in ys if abs(x - t) <= 1])
          for t in ys}
    t_peak = max(ma, key=lambda t: ma[t])
    return t_peak, ma[t_peak]


def median_year(series):
    """可见度质量的中位年(全程可见度一半落在哪年之前)。"""
    total = sum(s["v"] for s in series.values())
    cum = 0.0
    for t in YEARS2:
        cum += series[t]["v"]
        if cum >= total / 2:
            return t
    return YEARS2[-1]


def act2():
    print("\n" + "=" * 84)
    print("幕二 Boom 的世界市场爆发: 1940-1990 世界可见度, 条件链=注意力(1959)+"
          "巴塞罗那发行(1962)+翻译接力(1966-70)")
    print("=" * 84)
    base, pool62 = boom_sim(relay=True)
    cf, _ = boom_sim(relay=False)

    print(f"\n{'年份':>4} {'释放':>6} {'基线可见':>8} {'无接力可见':>10}   存货池(基线)")
    for t in range(1940, 1991, 4):
        print(f"{t:>4} {base[t]['release']:>6.2f} {base[t]['v']:>8.2f} "
              f"{cf[t]['v']:>10.2f}   {base[t]['pool']:>6.1f}")

    win = range(1963, 1973)
    v_win = sum(base[t]["v"] for t in win)
    v_tot = sum(base[t]["v"] for t in YEARS2)
    rel_win = sum(base[t]["release"] for t in win)
    rel_tot = sum(base[t]["release"] for t in YEARS2)
    uniform = 10 / len(YEARS2)
    t_peak_b, peak_b = moving_peak(base)
    t_peak_c, peak_c = moving_peak(cf)

    print(f"\n[2a] 爆发窗口集中(1963-1972 十年):")
    print(f"      可见度份额 {v_win / v_tot:.1%}(均匀基线 {uniform:.1%}, "
          f"×{v_win / v_tot / uniform:.1f});释放量份额 {rel_win / rel_tot:.1%}")
    print(f"      窗口释放 {rel_win:.1f} ≥ 1962 年存量 {pool62:.1f}(十年吃掉此前"
          f"二十余年积累的 {rel_win / pool62:.1f} 倍)")
    print(f"      基线峰值年 {t_peak_b}(滑动平均 {peak_b:.2f})")
    print("读数: 存量+爆炸一代新作+三环条件在十年内合流——爆发不是匀速增长的")
    print("      结果, 是积累在短窗口内的集中释放")

    print(f"\n[2b] 缺一环则爆发推迟(反事实: 去掉翻译接力):")
    print(f"      峰值 {peak_c:.2f} = 基线 {peak_b:.2f} 的 {peak_c / peak_b:.0%}"
          f";峰值年 {t_peak_c} vs {t_peak_b}(推迟 {t_peak_c - t_peak_b} 年)")
    print(f"      可见度中位年 {median_year(cf)} vs {median_year(base)}"
          f"(推迟 {median_year(cf) - median_year(base)} 年)")
    print("读数: 去掉接力, 世界听不见——存量照样写出来, 却只能以渗漏的速度")
    print("      迟到;峰被推出观察窗(反事实线在窗内只见爬坡不见峰)。缺一环,")
    print("      爆发就不是爆发, 是二十年的慢漏")

    assert v_win / v_tot >= 0.55, f"十年窗口可见度份额应≥55%, 实测 {v_win/v_tot:.1%}"
    assert v_win / v_tot >= 2.5 * uniform, "窗口份额应≥均匀基线 2.5 倍"
    assert rel_win >= pool62, "窗口释放量应≥1962 年全部存量(集中释放积累)"
    assert 1966 <= t_peak_b <= 1972, f"基线峰值年应落在 1966-1972, 实测 {t_peak_b}"
    assert peak_c <= 0.55 * peak_b, \
        f"无接力峰值应≤基线 55%, 实测 {peak_c/peak_b:.0%}"
    assert t_peak_c >= t_peak_b + 8, \
        f"无接力峰值年应推迟≥8 年, 实测推迟 {t_peak_c-t_peak_b} 年"
    assert median_year(cf) >= median_year(base) + 5, \
        f"无接力中位年应推迟≥5 年, 实测 {median_year(cf)-median_year(base)} 年"
    print(f"\n✓ 幕二断言通过: 十年窗口吃掉全程可见度 {v_win/v_tot:.0%}(均匀基线 "
          f"{uniform:.0%} 的 {v_win/v_tot/uniform:.1f} 倍), 窗口释放={pool62:.0f} "
          f"年存量的 {rel_win/pool62:.1f} 倍;去掉翻译接力峰值降至 "
          f"{peak_c/peak_b:.0%}、峰值年推迟 {t_peak_c-t_peak_b} 年"
          "——缺一环则爆发推迟")


# ==================== 幕三:标签的市场动力学 ====================

YEARS3 = list(range(1948, 2021))


def label_pop(t):
    """标签流行度 L(t): 概念期(1948-约1962 批评小圈子)→爆炸期(1967
    《百年孤独》/1982 诺奖)→营销期(货架类别)。逻辑斯蒂(风格化)。"""
    return 0.97 / (1.0 + math.exp(-(t - 1972) / 5.5))


def purity(t):
    """贴标书目的"正典线纯度": 概念期批评家只给奇妙现实谱系真成员贴标;
    流行度越高, 货架越什么都贴, 纯度随之稀释。"""
    return 0.92 * (1.0 - label_pop(t)) ** 1.1


def beta_draw(rng, a, b):
    """Beta 分布抽样(标准库 gammavariate 实现, 无第三方依赖)。"""
    g1, g2 = rng.gammavariate(a, 1.0), rng.gammavariate(b, 1.0)
    return g1 / (g1 + g2) if (g1 + g2) > 0 else 0.5


def pearson(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    sy = math.sqrt(sum((b - my) ** 2 for b in ys))
    return cov / (sx * sy)


def act3():
    print("\n" + "=" * 84)
    print("幕三 标签的市场动力学: \"魔幻现实主义\"1948-2020, 从批评概念到货架类别;"
          " 反标签=McOndo 式(1996)")
    print("=" * 84)
    rng = random.Random(SEED)

    # --- ① 标签稀释: 贴标书目的中位正典分随流行度下降 ---
    meds, pops = {}, {}
    for t in YEARS3:
        n = int(10 + 44 * label_pop(t))
        cohort = [beta_draw(rng, 6.0, 2.0) if rng.random() < purity(t)
                  else beta_draw(rng, 1.8, 5.5) for _ in range(n)]
        meds[t] = statistics.median(cohort)
        pops[t] = label_pop(t)
    med_concept = statistics.mean(meds[t] for t in range(1948, 1963))
    med_boom = statistics.mean(meds[t] for t in range(1963, 1983))
    med_mark = statistics.mean(meds[t] for t in range(1996, 2021))
    r_lm = pearson([pops[t] for t in YEARS3], [meds[t] for t in YEARS3])

    print(f"\n{'时段':>10} {'流行度L':>8} {'贴标数/年':>9} {'中位正典分':>9}")
    for lo, hi, name in ((1948, 1962, "概念期"), (1963, 1982, "爆炸期"),
                         (1996, 2020, "营销期")):
        L = statistics.mean(label_pop(t) for t in range(lo, hi + 1))
        n = statistics.mean(int(10 + 44 * label_pop(t)) for t in range(lo, hi + 1))
        print(f"{name:>10} {L:>8.2f} {n:>9.1f} "
              f"{statistics.mean(meds[t] for t in range(lo, hi + 1)):>9.3f}")
    print(f"\n[3a] 标签稀释: corr(流行度L, 中位正典分) = {r_lm:+.3f};"
          f"概念期 {med_concept:.3f} / 爆炸期 {med_boom:.3f} / "
          f"营销期 {med_mark:.3f}(概念/营销 = {med_concept / med_mark:.2f}×)")
    print("读数: 概念期标签是批评家的筛子(贴谁谁是谱系成员), 营销期标签是")
    print("      书店的货架(什么都往里放)——流行度买来的曝光, 用纯度支付")

    # --- ② 反标签运动(McOndo 式)的部分成功 ---
    PERIODS = [("1996-2003", 1.00, 0.35), ("2004-2011", 0.75, 0.75),
               ("2012-2020", 0.55, 1.15)]      # (时段, 旧市场规模, 后爆炸规模)
    PREF = {"旧市场": {"贴": 0.85, "去": 0.30}, "后爆炸": {"贴": 0.40, "去": 0.80}}
    N3 = 80
    stats3 = {}
    for name, s_old, s_post in PERIODS:
        acc = {"贴": [0.0, 0.0, 0], "去": [0.0, 0.0, 0]}  # [旧采用, 后采用, 入典]
        for tag in ("贴", "去"):
            for _ in range(N3):
                q = rng.random()
                base = 0.45 + 0.9 * q
                a_old = s_old * PREF["旧市场"][tag] * base * rng.uniform(0.85, 1.15)
                a_post = s_post * PREF["后爆炸"][tag] * base * rng.uniform(0.85, 1.15)
                acc[tag][0] += a_old
                acc[tag][1] += a_post
                score = 0.55 * q + 0.45 * PREF["旧市场"][tag] + rng.uniform(-0.08, 0.08)
                acc[tag][2] += score >= 0.62
        stats3[name] = acc

    print(f"\n[3b] 反标签运动(McOndo 式)的部分成功(每时段贴/去各 {N3} 位作家):")
    for name, _, _ in PERIODS:
        a = stats3[name]
        print(f"      {name}: 旧市场采用 去/贴 = {a['去'][0] / a['贴'][0]:.2f};"
              f" 后爆炸采用 去/贴 = {a['去'][1] / a['贴'][1]:.2f};"
              f" 合计 去/贴 = {(a['去'][0] + a['去'][1]) / (a['贴'][0] + a['贴'][1]):.2f};"
              f" 入典率 去 {a['去'][2] / N3:.2f} vs 贴 {a['贴'][2] / N3:.2f}")
    last = stats3[PERIODS[-1][0]]
    tot_ratio = (last["去"][0] + last["去"][1]) / (last["贴"][0] + last["贴"][1])
    canon_l = last["贴"][2] / N3
    canon_d = last["去"][2] / N3
    print("读数: 去标作家在后爆炸读者群胜出, 但旧市场(爆炸代读者与加冕建制)")
    print("      仍按标签发船票——反标签赢下新读者, 丢掉旧正典的入口;")
    print("      到两市场合计时追平, 是'部分成功': 标签是船票也是牢笼")

    assert r_lm <= -0.80, f"corr(L, 中位正典分)应≤−0.80, 实测 {r_lm:+.3f}"
    assert med_concept >= 1.9 * med_mark, \
        f"概念期中位分应≥营销期 1.9 倍, 实测 {med_concept/med_mark:.2f}×"
    for name, _, _ in PERIODS:
        a = stats3[name]
        assert a["去"][1] >= 1.5 * a["贴"][1], \
            f"{name}: 后爆炸市场去标采用应≥贴标 1.5 倍"
        assert a["去"][0] <= 0.55 * a["贴"][0], \
            f"{name}: 旧市场去标采用应≤贴标 55%"
    assert tot_ratio >= 1.0, \
        f"末期两市场合计去标总采用应追平贴标, 实测 {tot_ratio:.2f}"
    assert canon_d <= 0.4 * canon_l, \
        f"去标作家旧市场入典率应≤贴标 40%, 实测 {canon_d/canon_l:.0%}"
    print(f"\n✓ 幕三断言通过: corr(L,中位正典分)={r_lm:+.2f}, 概念/营销中位分 "
          f"{med_concept/med_mark:.1f}×;反标签在后爆炸市场 ≥1.5× 胜出、"
          f"旧市场 ≤55% 失联、末期合计追平({tot_ratio:.2f})而入典率仅 "
          f"{canon_d/canon_l:.0%}——标签是船票也是牢笼")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 时序结构: 预告-应验使张力曲线整体前移(重心从后段移到中段),")
    print("     回环使重读收益倍增(二读伏笔密度数倍于线性式)——马孔多的")
    print("     时序是设计出来的重读机器(与美国家族实验分工: 那边管正典")
    print("     再分配, 本幕管叙事技术本身)")
    print("  ② 爆发窗口: Boom 十年窗口集中释放此前二十余年积累(窗口份额≥55%,")
    print("     为均匀基线的 2.5 倍以上);条件链=注意力事件+巴塞罗那发行+翻译")
    print("     接力, 缺一环则峰值下降且整体推迟——爆发不是匀速增长是集中释放")
    print("  ③ 标签市场: 贴标书目的中位正典分随标签流行度下降(概念期筛子→")
    print("     营销期货架);反标签运动部分成功(新读者市场胜出, 旧市场失联)——")
    print("     标签是船票也是牢笼")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
