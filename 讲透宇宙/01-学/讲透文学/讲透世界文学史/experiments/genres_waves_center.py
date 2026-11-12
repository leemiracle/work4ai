# -*- coding: utf-8 -*-
"""体裁接力-思潮传播-经典层积三律模拟:世界文学史家族实验(GB/T 75047)。

00-体系结构.md(反直觉三发现)、03-可构造与结构.md(可构造谱系左端)、
04-世界文学史转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260909(建族日)可复现。

与兄弟家族实验的分工(不同题,不重复):
  - 比较文学家族 worldlit_travel.py 管当代翻译流网络(共时截面+观念漂移);
  - 中国近代文学家族管译介时滞(中国单点的接收端);
  - 本实验管**长时段编年动力学**——体裁接力/思潮波/经典层积,以百年为刻度单位。

风格化参数声明:体裁参数/网络时距/重估权重均为按文学史通说给定的风格化取值
(锚序不锚值),断言的是序与过程方向(错列/单调/层积),不是数值本身。

三幕:
  幕一 体裁的生命周期与轮替:6 个体裁(史诗/悲剧/骑士传奇/长篇小说/现代诗/
      电影叙事,通说风格化序列)各按双 logistic 兴衰曲线共存于同一条编年轴。
      断言: 1) 体裁峰值错列(相邻峰值间隔>2 刻度);相邻体裁活跃期(份额>0.30)
               重叠段非空(长度>1 刻度);新体裁萌芽(份额>0.05)落在旧体裁
               鼎盛期(峰值)之前
            2) "每时代的主导体裁"序列成立(主导块顺序=体裁顺序,块长>3 刻度),
               交接点在旧体裁峰值之后、新体裁峰值之前(=旧衰退线与新崛起线的
               交点)——文学史的编年骨架是体裁接力,不是齐头并进
               (对照模型:六体裁齐头并起,交接数=0)。
  幕二 思潮传播的波动力学:思潮从起源中心沿文学圈网络(4 条路线×5 环)扩散,
      每跳时距~U(6,10) 刻度,每跳本土化改造一次(原型偏离当量逐跳累积,
      只增不减——每次接收都在改写)。三波(浪漫主义/现代主义/魔幻现实主义,
      风格化)独立复跑。
      断言: 1) 到达时间随网络距离(环数)严格单调增(各波各环均值逐环增大;
               汇总 Pearson r(到达,距离)>0.95)
            2) 本土化强度(原型偏离指数)随距离单调增(各环均值逐环增大,
               汇总 Spearman>0.90);到达越迟偏离越大(Pearson r>0.80)——
               思潮的世界旅行:越远越迟,越迟越变。
  幕三 经典的层积与重估:60 部作品×12 代重估,每代按自己的价值权重
      (其中一代为价值观反转代)给作品打分,取前 20 入经典集。
      断言: 1) 经典集合的长期成员(在典率>=70%)是重估波动小的"核心层"
               (经典集进出跳变<搅动层的一半;核心层与搅动层之外存在中间带)
            2) 任何单一代名单预测末代名单都不足(平均重叠<0.72,最大重叠
               <0.85;显著高于随机 1/3 但远非全预测),但核心层在末代的
               生存率比首代名单成员的生存率高>=15 个百分点;反转代也翻不掉
               核心层(核心在典率>=0.70)而外围名单大换血(重叠<0.50)——
               经典是层积岩不是排行榜:越往下越稳,越往上越换。

跑法: python -X utf8 experiments/genres_waves_center.py
"""

import math
import random
import statistics

SEED = 20260909  # 建族日作种子,可复现


def sig(x):
    return 1.0 / (1.0 + math.exp(-x))


# ==================== 幕一:体裁的生命周期与轮替 ====================

# 体裁: (名, 上升中心a, 上升率ra, 下降中心b, 下降率rb, 通说注)
# 时间轴 t∈[0,100] 为抽象编年刻度(锚序不锚值):0≈文字之初,100≈当代
GENRES = [
    ("史诗",     2.0, 0.90, 15.0, 0.70, "青铜时代口头史诗:吉尔伽美什/荷马/吠陀(通说)"),
    ("悲剧",     8.0, 0.80, 25.0, 0.60, "古典雅典悲喜剧及其后世古典主义剧场"),
    ("骑士传奇", 17.0, 0.70, 38.0, 0.60, "中世纪罗曼司:亚瑟王圈/特里斯丹,与东亚物语并世"),
    ("长篇小说", 30.0, 0.55, 70.0, 0.50, "印刷资本主义与小说兴起:塞万提斯-巴尔扎克-托尔斯泰"),
    ("现代诗",   50.0, 0.80, 86.0, 0.80, "象征主义以降的现代主义诗"),
    ("电影叙事", 69.0, 1.00, 100.0, 0.80, "20 世纪镜头叙事:影像加入文学体裁序列"),
]


def share(g, t):
    """双 logistic 体裁份额:上升 sigmoid × 下降 sigmoid。"""
    _, a, ra, b, rb, _ = g
    return sig(ra * (t - a)) * sig(rb * (b - t))


GRID = [i * 0.25 for i in range(0, 401)]  # 0..100,步长 0.25


def curve(g):
    return [share(g, t) for t in GRID]


def act1():
    print("=" * 88)
    print("幕一 体裁的生命周期与轮替:六体裁双 logistic 兴衰(编年骨架是体裁接力)")
    print("=" * 88)
    curves = [curve(g) for g in GENRES]
    names = [g[0] for g in GENRES]

    # 每体裁:峰值时刻/萌芽(份额>0.05)/活跃窗(份额>0.30)
    peaks, onsets, wins = [], [], []
    print(f"\n{'体裁':<6}{'峰值':>6}{'萌芽':>7}{'活跃窗(>0.30)':>16}   通说注")
    for g, c in zip(GENRES, curves):
        pk = max(range(len(GRID)), key=lambda i: c[i])
        peaks.append(GRID[pk])
        on = next(GRID[i] for i in range(len(GRID)) if c[i] > 0.05)
        onsets.append(on)
        w = [GRID[i] for i in range(len(GRID)) if c[i] > 0.30]
        wins.append((w[0], w[-1]))
        print(f"{g[0]:<6}{GRID[pk]:>6.2f}{on:>7.2f}{wins[-1][0]:>9.1f}-{wins[-1][1]:<6.1f}   {g[5]}")

    # 断言 1a:峰值错列
    gaps = [peaks[i + 1] - peaks[i] for i in range(len(GENRES) - 1)]
    print(f"\n峰值序列: " + " < ".join(f"{n}{p:.1f}" for n, p in zip(names, peaks)))
    print(f"相邻峰值间隔: {['%.1f' % gp for gp in gaps]}")
    assert all(gp > 2.0 for gp in gaps), "相邻体裁峰值应错列(间隔>2 刻度)"

    # 断言 1b:相邻体裁活跃期重叠非空 + 新体裁在旧体裁鼎盛期萌芽
    print("\n相邻体裁关系(重叠段/萌芽对鼎盛):")
    for i in range(len(GENRES) - 1):
        ov = [t for t, c0, c1 in zip(GRID, curves[i], curves[i + 1]) if c0 > 0.30 and c1 > 0.30]
        print(f"  {names[i]:<5}×{names[i + 1]:<5}: 重叠段 [{ov[0]:.1f},{ov[-1]:.1f}] 长 {len(ov) * 0.25:.1f};"
              f" {names[i + 1]}萌芽 {onsets[i + 1]:.1f} < {names[i]}峰值 {peaks[i]:.1f}")
        assert len(ov) * 0.25 > 1.0, f"{names[i]}与{names[i + 1]}活跃期应重叠(>1 刻度)"
        assert onsets[i + 1] < peaks[i], f"{names[i + 1]}应在{names[i]}鼎盛期萌芽"

    # 断言 2:主导体裁序列与交接点
    dom = [max(range(len(GENRES)), key=lambda k: curves[k][i]) for i in range(len(GRID))]
    blocks = []
    for i, d in enumerate(dom):
        if not blocks or blocks[-1][0] != d:
            blocks.append([d, GRID[i], GRID[i]])
        else:
            blocks[-1][2] = GRID[i]
    print("\n每时代的主导体裁(份额最大者)的分块:")
    for d, s0, s1 in blocks:
        print(f"  [{s0:>5.2f},{s1:>5.2f}]  主导:{names[d]}  (块长 {s1 - s0:.2f})")
    assert [b[0] for b in blocks] == list(range(len(GENRES))), "主导块顺序应为体裁顺序"
    assert all(b[2] - b[1] > 3.0 for b in blocks), "每个主导块应长于 3 刻度"

    handovers = []
    print("\n主导交接点(旧衰退线×新崛起线交点):")
    for i in range(len(GENRES) - 1):
        cross = next(GRID[j] for j in range(len(GRID))
                     if curves[i + 1][j] > curves[i][j])
        assert all((curves[i + 1][j] > curves[i][j]) == (GRID[j] >= cross - 1e-9)
                   for j in range(len(GRID))), f"{names[i]}→{names[i+1]}应只有一次交接"
        so, sn = share(GENRES[i], cross), share(GENRES[i + 1], cross)
        print(f"  {names[i]:<5}→{names[i + 1]:<5}: 交接点 t*={cross:.2f}"
              f" (旧峰值 {peaks[i]:.1f} < t* < 新峰值 {peaks[i + 1]:.1f}; 交点份额 {so:.2f}={sn:.2f})")
        assert cross > peaks[i], "交接应在旧体裁峰值之后(旧在衰退)"
        assert cross < peaks[i + 1], "交接应在新体裁峰值之前(新在崛起)"
        handovers.append(cross)
    n_relay = len(handovers)

    # 对照模型:六体裁齐头并起(同升同降)——没有接力
    CF = [(n, 40.0, 0.7, 100.0, 0.7, "") for n in names]
    cf_curves = [curve(g) for g in CF]
    cf_dom = [max(range(len(CF)), key=lambda k: cf_curves[k][i]) for i in range(len(GRID))]
    n_cf = len(set(cf_dom)) - 1
    print(f"\n对照(齐头并进模型:六体裁同升同降): 主导体裁不变,交接数={n_cf}")
    assert n_cf == 0, "齐头并进模型应无交接"
    assert n_relay == len(GENRES) - 1, "接力模型应有 n-1 次交接"
    print(f"  接力模型交接数={n_relay} vs 齐头并进交接数={n_cf}——编年骨架是体裁接力,")
    print("  不是齐头并进:每时代有自己的主导体裁,交接=旧衰退线与新崛起线的交点。")
    print("\nOK 幕一断言通过:峰值错列+活跃期重叠+新体萌芽于旧体鼎盛期;主导序列成立,")
    print("   交接点夹在旧峰之后新峰之前;齐头并进对照交接数为 0。")


# ==================== 幕二:思潮传播的波动力学 ====================

WAVES = ("浪漫主义波", "现代主义波", "魔幻现实主义波")  # 风格化三次思潮
ROUTES, RINGS = 4, 5      # 4 条路线 × 5 环(网络距离 1..5)
HOP_DELAY = (6.0, 10.0)   # 每跳时距(刻度,风格化"年")
DRIFT = (0.06, 0.18)      # 每跳本土化改造当量(偏离指数只增不减)


def act2():
    print("\n" + "=" * 88)
    print("幕二 思潮传播的波动力学:起源中心→文学圈网络(越远越迟,越迟越变)")
    print("=" * 88)
    all_arr, all_dev, all_dist = [], [], []
    for w, wave in enumerate(WAVES):
        rng = random.Random(SEED + 100 * w)
        byring = {d: [] for d in range(1, RINGS + 1)}
        for _r in range(ROUTES):                 # 每条路线从起源中心出发
            t_acc, dev = 0.0, 0.0
            for d in range(1, RINGS + 1):
                t_acc += rng.uniform(*HOP_DELAY)  # 距离延迟
                dev = math.sqrt(dev ** 2 + rng.uniform(*DRIFT) ** 2)  # 本土化改造累积
                byring[d].append((t_acc, dev))
                all_arr.append(t_acc)
                all_dev.append(dev)
                all_dist.append(d)
        print(f"\n{wave}(路线×环,均值):")
        print(f"  {'环(距离)':<8}{'到达时间':>10}{'原型偏离指数':>12}")
        for d in range(1, RINGS + 1):
            ma = statistics.mean(x[0] for x in byring[d])
            md = statistics.mean(x[1] for x in byring[d])
            print(f"  d={d:<5}{ma:>10.2f}{md:>12.3f}")
        # 断言 1&2(逐波):环均值单调
        means_a = [statistics.mean(x[0] for x in byring[d]) for d in range(1, RINGS + 1)]
        means_d = [statistics.mean(x[1] for x in byring[d]) for d in range(1, RINGS + 1)]
        assert all(means_a[i] < means_a[i + 1] for i in range(RINGS - 1)), \
            f"{wave}:到达时间应随距离逐环增大"
        assert all(means_d[i] < means_d[i + 1] for i in range(RINGS - 1)), \
            f"{wave}:本土化偏离应随距离逐环增大"

    pear_ad = statistics.correlation(all_arr, all_dist)
    pear_dd = statistics.correlation(all_dev, all_dist)
    pear_a_dev = statistics.correlation(all_arr, all_dev)

    def rank(xs):
        order_ = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0] * len(xs)
        for pos, i in enumerate(order_):
            r[i] = pos
        return r

    spear_dd = statistics.correlation(rank(all_dev), rank(all_dist))
    print(f"\n汇总(3 波×{ROUTES} 路线×{RINGS} 环={len(all_arr)} 站):")
    print(f"  Pearson r(到达,网络距离)   = {pear_ad:.3f}")
    print(f"  Spearman ρ(偏离,网络距离)  = {spear_dd:.3f}  (Pearson {pear_dd:.3f})")
    print(f"  Pearson r(到达,偏离指数)   = {pear_a_dev:.3f}")
    assert pear_ad > 0.95, "到达时间应与网络距离强正相关"
    assert spear_dd > 0.90, "偏离指数应与网络距离强秩相关"
    assert pear_a_dev > 0.80, "到达越迟,偏离应越大(越迟越变)"

    t5 = statistics.mean(all_arr[i] for i in range(len(all_arr)) if all_dist[i] == 5)
    d5 = statistics.mean(all_dev[i] for i in range(len(all_dev)) if all_dist[i] == 5)
    print(f"\n读数: 思潮从起源中心出发,第 5 环平均 t={t5:.1f} 才到达(距离延迟),")
    print(f"  而当地版本已偏离原型 {d5:.3f}(本土化改造逐跳累积)——思潮的世界旅行:")
    print("  越远越迟(网络距离换算成时间差),越迟越变(时间差换算成改造量)。")
    print("  分工注记:单点接收端的译介时滞归中国近代文学家族;当代翻译流网络归")
    print("  比较文学家族;本幕管百年尺度的全球波。")
    print("\nOK 幕二断言通过:到达随距离单调增(r>0.95);偏离随距离单调增(ρ>0.90);")
    print("   到达-偏离强相关(越迟越变)。")


# ==================== 幕三:经典的层积与重估 ====================

N_WORKS, N_CANON, N_ERAS = 60, 20, 12
N_COREC, DIMS_V = 10, 5            # 核心层候选 10 部(高稳定禀赋,基岩压过时代偏好)
BASE_W, ALIGN_W = 2.4, 0.9         # 作品稳定禀赋项 / 时代alignment项
REVERSE_ERA = 6                    # 第 7 代(0 基):价值观反转代(取第 3 代权重的负)


def act3():
    print("\n" + "=" * 88)
    print("幕三 经典的层积与重估:60 部作品×12 代重估(经典是层积岩不是排行榜)")
    print("=" * 88)
    rng = random.Random(SEED + 300)
    stable, profs = [], []
    for i in range(N_WORKS):
        s = rng.uniform(0.92, 1.05) if i < N_COREC else rng.uniform(0.10, 0.46)
        stable.append(s)
        v = [rng.gauss(0.0, 1.0) for _ in range(DIMS_V)]
        nrm = math.sqrt(sum(x * x for x in v))
        profs.append([x / nrm for x in v])
    weights = {}
    for t in range(N_ERAS):
        w = [rng.gauss(0.0, 1.0) for _ in range(DIMS_V)]
        nrm = math.sqrt(sum(x * x for x in w))
        weights[t] = [x / nrm for x in w]
    weights[REVERSE_ERA] = [-x for x in weights[2]]  # 第 7 代=第 3 代价值观反转

    canon, ranks = {}, {}
    for t in range(N_ERAS):
        scores = [BASE_W * stable[i] + ALIGN_W * sum(weights[t][k] * profs[i][k]
                                                     for k in range(DIMS_V))
                  + rng.uniform(-0.04, 0.04) for i in range(N_WORKS)]
        order = sorted(range(N_WORKS), key=lambda i: -scores[i])
        canon[t] = set(order[:N_CANON])
        rmap = {i: r + 1 for r, i in enumerate(order)}
        ranks[t] = rmap

    frac = [sum(1 for t in range(N_ERAS) if i in canon[t]) / N_ERAS for i in range(N_WORKS)]
    core = [i for i in range(N_WORKS) if frac[i] >= 0.70]
    churn = [i for i in range(N_WORKS) if 0.0 < frac[i] < 0.30]   # 进过又出=搅动层
    mid = [i for i in range(N_WORKS) if 0.30 <= frac[i] < 0.70]
    never = [i for i in range(N_WORKS) if frac[i] == 0.0]
    print(f"\n层积剖面(12 代在典率): 核心层(>=70%) {len(core)} 部 | 中间带(30-70%) {len(mid)} 部 |"
          f" 搅动层(进过又出,<30%) {len(churn)} 部 | 圈外(从未入典) {len(never)} 部")
    for label, grp in (("核心层示例", core[:3]), ("搅动层示例", churn[:3])):
        for i in grp:
            bar = "".join("■" if i in canon[t] else "·" for t in range(N_ERAS))
            print(f"  [{label}] 作品#{i:<3d} 禀赋 {stable[i]:.2f}  {bar}")

    # 断言 1:核心层=重估波动小(经典集进出跳变<搅动层一半)
    def flips(i):
        return sum(1 for t in range(1, N_ERAS)
                   if (i in canon[t - 1]) != (i in canon[t]))

    vol = {i: flips(i) for i in range(N_WORKS)}
    v_core, v_churn = (statistics.mean(vol[i] for i in core),
                       statistics.mean(vol[i] for i in churn))
    print(f"\n重估波动(12 代经典集进出跳变次数均值): 核心层 {v_core:.2f} vs 搅动层 {v_churn:.2f}")
    assert v_core < 0.5 * v_churn, "核心层进出跳变应小于搅动层一半"
    assert len(never) > 0 and len(churn) > 0, "应有圈外作品与搅动层(层积岩全剖面)"
    assert len(mid) > 0, "应存在中间带(层积岩有过渡层)"

    # 断言 2:单代名单不能预测末代名单;核心层生存率显著高于总体
    ov = [len(canon[t] & canon[N_ERAS - 1]) / N_CANON for t in range(N_ERAS - 1)]
    chance = N_CANON / N_WORKS
    core_surv = sum(1 for i in core if i in canon[N_ERAS - 1]) / len(core)
    overall_surv = len(canon[0] & canon[N_ERAS - 1]) / N_CANON
    print(f"\n各代名单与末代名单的重叠率: " + " ".join(f"{o:.2f}" for o in ov))
    print(f"  平均 {statistics.mean(ov):.3f}, 最大 {max(ov):.2f}(随机基线 {chance:.2f})")
    print(f"  核心层在末代生存率 {core_surv:.2f} vs 首代名单成员在末代生存率 {overall_surv:.2f}")
    assert statistics.mean(ov) < 0.72, "单代名单平均预测力应不足(<0.72)"
    assert max(ov) < 0.85, "任何单代名单都不能接近全预测(<0.85)"
    assert statistics.mean(ov) > chance + 0.08, "但应显著高于随机(核心层供锚)"
    assert core_surv > overall_surv + 0.15, "核心层生存率应高于总体 15 个百分点以上"

    # 断言 3:反转代翻不掉核心层,外围大换血
    core_in_rev = sum(1 for i in core if i in canon[REVERSE_ERA]) / len(core)
    per6 = canon[REVERSE_ERA - 1] - set(core)
    per7 = canon[REVERSE_ERA] - set(core)
    per_ov = len(per6 & per7) / min(len(per6), len(per7))
    print(f"\n重估反转代(第 {REVERSE_ERA + 1} 代,价值观取第 3 代的负):")
    print(f"  核心层在典率 {core_in_rev:.2f} vs 反转前后外围名单重叠 {per_ov:.2f}")
    assert core_in_rev >= 0.70, "反转代也翻不掉核心层"
    assert per_ov < 0.50, "反转代外围名单应大换血"
    print("  价值观整个翻面,核心层岿然,外围名单重洗——重估冲击翻动的是上层,")
    print("  不是基岩。")
    print("\nOK 幕三断言通过:长期成员=低波动核心层(进出跳变减半以上);单代预测")
    print("   不足而核心生存率高出总体 15pp+;反转代核心不倒、外围换血。")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 88)
    print("总断言收口:")
    print("  1) 体裁接力:六体裁峰值错列、活跃期重叠、新体萌芽于旧体鼎盛期;")
    print("     主导体裁序列成立,交接=旧衰退线×新崛起线交点(对照齐头并进=0 交接)——")
    print("     文学史的编年骨架是体裁接力,不是齐头并进")
    print("  2) 思潮波:到达时间随网络距离单调增(r>0.95),本土化偏离随距离单调增")
    print("     (ρ>0.90)且越迟越变(r>0.80)——思潮的世界旅行:越远越迟,越迟越变")
    print("  3) 经典层积:长期成员=重估波动小的核心层;单代名单不能预测百年后名单")
    print("     而核心层生存率显著高于总体;反转代翻不掉核心层——经典是层积岩,")
    print("     不是排行榜:越往下越稳,越往上越换")
    print("OK 全部自验证通过")


if __name__ == "__main__":
    main()
