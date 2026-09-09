# -*- coding: utf-8 -*-
"""体裁距离-规范长短程-跨体棘轮三律模拟:中国各体文学家族实验(GB/T 75034)。

00-体系结构.md(反直觉三发现)、03-可构造与结构.md(可构造谱系左端)、
04-中国各体文学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖;固定种子 20260907 可复现。

风格化参数声明:四体的特征向量是按文学史通说给定的风格化取值(锚序不锚值),
断言的是距离的序(谁远谁近)与过程的方向(收敛/单调/不可逆),不是数值本身。

三幕:
  幕一 体裁距离矩阵:四体各按 8 维形式特征给定风格化坐标,距离=加权欧氏
      (形式约束维加权加倍——体裁距离首先是形式约束的距离)。
      断言: 1) d(诗,散) 为全矩阵最大对(形式谱系两端)
            2) 戏剧到其余三体的最近邻距离仅次于诗歌居第二——戏剧没有近邻,
               独立性由舞台性一维独撑:去掉舞台性维,戏剧各距离坍缩最狠,
               d(小,戏) 甚至跌到 d(散,小) 之下
            3) 杂交作品=两体坐标的凸组合+小噪声:最近两顶点恰为双亲,
               距离配比近似线段内分比——杂交落在两体连线上。
  幕二 形式规范的长短程:16 个亚文体各带规范强度 n;文群演化=继承+突变+
      规范门(严体门窄,宽体门宽)。
      断言: 1) 规范强度与演化后形式变异率强负相关(Pearson<-0.93,
               Spearman<-0.93):严体保守,宽体多变
            2) 最严体(近体)与最宽体(现代散文)的变异率差>4 倍
            3) 规范崩解(近体 t=40 释放规范):变异率 15 代内跳升>5 倍,
               出旧门限的新变体从 0 升到>60%——规范崩解期后爆发新变体。
  幕三 跨体旅行的代价:近体诗特征的作品沿 诗-词-曲 迁移(句式化过程),
      再试图拟古回近体。形式约束维装棘轮:松则一步到位,紧则恢复乏力。
      断言: 1) 去程每步向目标体深度收敛(残距<45%)
            2) 回程收敛显著残缺(残距>60%)——松紧不对称
            3) 离原体距离沿去程单调增;回程之后仍比第一站(词)更远离原体,
               句式整齐度回不到 0.55——破体是单行道。

跑法: python -X utf8 experiments/genre_distance_drift.py
"""

import math
import random
import statistics

SEED = 20260907  # 检索校准日作种子,可复现

# ==================== 公共:八维形式特征空间 ====================

DIMS = ("韵律性", "句式整齐度", "程式度", "抒情度", "叙事度", "篇幅结构度", "口语度", "舞台性")
# 体裁距离=形式约束的距离:约束维(韵律/整齐/程式/舞台)加权加倍,容量维(叙事/篇幅)减半
WEIGHTS = (2.0, 1.5, 1.2, 1.0, 0.6, 0.6, 0.8, 1.5)

# 四体风格化坐标(通说口径:诗=最强形式约束;散=最少约束;小居自由侧;
# 戏居中间带并被舞台性一维抬起)
POETRY = (0.95, 0.95, 0.85, 0.90, 0.30, 0.10, 0.15, 0.15)   # 诗(以近体为典型)
DRAMA  = (0.60, 0.50, 0.85, 0.40, 0.85, 0.65, 0.75, 1.00)   # 戏(杂剧传奇为典型)
NOVEL  = (0.25, 0.45, 0.65, 0.30, 0.95, 0.85, 0.60, 0.05)   # 小(章回到现代)
PROSE  = (0.05, 0.15, 0.15, 0.65, 0.50, 0.45, 0.55, 0.10)   # 散(古文到现代)
CENTROIDS = (("诗", POETRY), ("戏", DRAMA), ("小", NOVEL), ("散", PROSE))


def wdist(a, b, skip_stage=False):
    """加权欧氏距离;skip_stage=True 时消融舞台性维(幕一的归因实验)。"""
    s = 0.0
    for k in range(len(DIMS)):
        if skip_stage and k == 7:
            continue
        s += WEIGHTS[k] * (a[k] - b[k]) ** 2
    return math.sqrt(s)


def fmt_vec(v):
    return "(" + ", ".join(f"{x:.2f}" for x in v) + ")"


# ==================== 幕一:体裁距离矩阵 ====================

def act1():
    print("=" * 88)
    print("幕一 体裁距离矩阵:四体的八维形式坐标与体-体距离(体裁不是标签是空间坐标)")
    print("=" * 88)
    print("\n特征维(权重): " + "; ".join(f"{DIMS[k]}×{WEIGHTS[k]:g}" for k in range(8)))
    for name, v in CENTROIDS:
        print(f"  {name}: {fmt_vec(v)}")

    names = [n for n, _ in CENTROIDS]
    vecs = dict(CENTROIDS)
    pairs = [("诗", "散"), ("诗", "小"), ("诗", "戏"), ("散", "戏"), ("小", "戏"), ("散", "小")]
    print("\n体-体距离(全矩阵 6 对):")
    D = {}
    for a, b in pairs:
        D[(a, b)] = wdist(vecs[a], vecs[b])
        print(f"  d({a},{b}) = {D[(a, b)]:.3f}")

    # 断言 1: 诗-散为最大对
    max_pair = max(D, key=D.get)
    assert max_pair == ("诗", "散"), f"最大对应为(诗,散),实测 {max_pair}={D[max_pair]:.3f}"
    assert D[("诗", "散")] > 1.05 * D[("诗", "小")], "诗-散应明显大于诗-小(两端极距需有边距)"
    print(f"\n读数 1: d(诗,散)={D[('诗', '散')]:.3f} 为全矩阵最大——最强形式约束(齐言格律)"
          f"对最少形式约束(形散),形式谱系的两端。")

    # 断言 2: 戏剧无近邻(最近邻距离第二,仅次于诗);舞台性一维独撑
    nn = {n: min(wdist(vecs[n], vecs[m]) for m in names if m != n) for n in names}
    order = sorted(names, key=lambda n: -nn[n])
    print(f"\n各体到其余三体的最近邻距离: " + ", ".join(f"{n}:{nn[n]:.3f}" for n in order))
    assert order[0] == "诗" and order[1] == "戏", f"最近邻距离序应为 诗>戏>散/小,实测 {order}"
    assert nn["戏"] > 1.3 * nn["散"], "戏剧的最近邻距离应显著大于散文的(戏剧没有近邻)"

    D_noS = {p: wdist(vecs[p[0]], vecs[p[1]], skip_stage=True) for p in pairs}
    print("\n消融实验:去掉舞台性维后的距离(括号内为降幅)")
    for p in pairs:
        drop = 1 - D_noS[p] / D[p]
        mark = "  <- 戏剧对" if "戏" in p else ""
        print(f"  d({p[0]},{p[1]}): {D[p]:.3f} -> {D_noS[p]:.3f}  (降 {drop:.0%}){mark}")
    drama_drops = [1 - D_noS[p] / D[p] for p in pairs if "戏" in p]
    other_drops = [1 - D_noS[p] / D[p] for p in pairs if "戏" not in p]
    assert min(drama_drops) > max(other_drops), "戏剧各对的降幅应全部超过非戏剧对"
    assert D_noS[("小", "戏")] < D_noS[("散", "小")], "去舞台性后 小-戏 应落到 散-小 之下"
    print("  去掉舞台性,戏剧的三对距离坍缩最狠;d(小,戏) 甚至跌到 d(散,小) 之下——")
    print("  戏剧的独立坐标由舞台性一维独撑,舞台性归零则戏剧混入散文-小说连续体。")

    # 断言 3: 杂交作品落在两体连线上
    print("\n杂交作品定位(凸组合+种子噪声,每型 200 件):")
    rng = random.Random(SEED)
    hybrids = [
        ("散文诗(诗×散,通说:鲁迅《野草》型)", "诗", "散", 0.65),
        ("章回韵散间(诗×小,通说:'有诗为证'型)", "诗", "小", 0.30),
        ("散文化小说(小×散,通说:汪曾祺型)", "小", "散", 0.55),
        ("诗剧(诗×戏,通说:剧场诗化独白型)", "诗", "戏", 0.35),
    ]
    for label, pa, pb, alpha in hybrids:
        va, vb = vecs[pa], vecs[pb]
        resids, fracs, top2 = [], [], 0
        for _ in range(200):
            w = tuple(alpha * va[k] + (1 - alpha) * vb[k] + rng.uniform(-0.04, 0.04)
                      for k in range(8))
            d_a, d_b = wdist(w, va), wdist(w, vb)
            fracs.append(d_a / (d_a + d_b))
            # 到双亲连线段的残差(投影回到线段)
            t = sum(WEIGHTS[k] * (w[k] - va[k]) * (vb[k] - va[k]) for k in range(8))
            t /= sum(WEIGHTS[k] * (vb[k] - va[k]) ** 2 for k in range(8))
            t = min(1.0, max(0.0, t))
            proj = tuple(va[k] + t * (vb[k] - va[k]) for k in range(8))
            resids.append(wdist(w, proj))
            # 断言 3a: 最近顶点必是双亲之一(每件都成立)
            ranked = sorted(names, key=lambda n: wdist(w, vecs[n]))
            assert ranked[0] in (pa, pb), f"{label} 最近顶点应为双亲,实测 {ranked}"
            if ranked[:2] in ([pa, pb], [pb, pa]):
                top2 += 1
        frac_med = statistics.median(fracs)
        resid_med = statistics.median(resids)
        print(f"  {label}: 内分比中位 d(w,{pa})/(和)={frac_med:.3f}(纯线段={1 - alpha:.2f});"
              f" 离双亲连线残差中位={resid_med:.3f}; 双亲包揽前二 {top2 / 200:.0%}")
        assert abs(frac_med - (1 - alpha)) < 0.12, f"{label} 内分比应近线段值"
        assert resid_med < 0.12, f"{label} 残差应贴着双亲连线"
    print("  每件杂交的最近顶点都是双亲之一,残差贴着双亲连线,配比近似内分比——")
    print("  体裁空间可以给跨体作品报坐标。附带读数:第二近邻常被第三体抢走(小说/戏剧")
    print("  都住在离双亲连线不远的中带)——体裁空间有'中部',杂交作品天然面向多个邻居。")
    print("\nOK 幕一断言通过:诗-散最大对;戏剧无近邻(舞台性独撑,消融即坍缩);杂交贴线。")


# ==================== 幕二:形式规范的长短程 ====================

# 16 亚文体: (名, 规范强度 n, 通说注)
SUBFORMS = [
    ("近体诗", 0.95, "格律定型后千年守恒"),
    ("词(依谱)", 0.80, "依声填词,谱存律在"),
    ("杂剧", 0.80, "一本四折一楔子,体制规整"),
    ("骈文", 0.90, "四六对仗用典"),
    ("传奇", 0.60, "篇幅铺展,数十出"),
    ("古体诗", 0.45, "历代自由拟作"),
    ("古文", 0.45, "单行散句,义法宽"),
    ("章回", 0.60, "回目说书程式"),
    ("话本", 0.50, "入话诗赞程式"),
    ("曲(衬字)", 0.55, "衬字增句,句式自由"),
    ("花部乱弹", 0.35, "板式自由,格律让位"),
    ("笔记", 0.30, "随笔记之,无定体"),
    ("小品", 0.30, "闲适随笔,不拘格套"),
    ("话剧", 0.25, "白话对话,无曲律"),
    ("现代小说", 0.20, "无定式"),
    ("现代散文", 0.15, "形散神聚,最少约束"),
]

W_POP, T_GENS, RUNS = 240, 80, 3
INERTIA, MUT_SD = 0.85, 0.30


def gate_of(n):
    """规范门宽:严体门窄,宽体门宽(突变尺度保证最宽的门仍是约束)。"""
    return 0.05 + 0.50 * (1.0 - n)


def evolve(rng, n, gens, collapse_at=None, collapse_n=0.10):
    """文群演化:继承+突变+规范门(出门者淘汰,幸存者复制回补)。"""
    xs = [rng.gauss(0.0, 0.05) for _ in range(W_POP)]
    hist = []
    for t in range(gens):
        cur_n = collapse_n if (collapse_at is not None and t >= collapse_at) else n
        g = gate_of(cur_n)
        xs = [INERTIA * x + rng.gauss(0.0, MUT_SD) for x in xs]
        surv = [x for x in xs if abs(x) <= g]
        while len(surv) < W_POP:
            surv.append(surv[rng.randrange(len(surv))])
        xs = surv
        hist.append((statistics.pstdev(xs), g))
    return hist


def act2():
    print("\n" + "=" * 88)
    print("幕二 形式规范的长短程:规范强度 vs 演化变异率(严体保守,宽体多变)")
    print("=" * 88)
    rng = random.Random(SEED)
    results = []
    print(f"\n{'亚文体':<8}{'规范强度':>6}{'门宽':>7}{'终代变异率(std)':>14}   通说注")
    for name, n, note in SUBFORMS:
        std_f = statistics.mean(evolve(rng, n, T_GENS)[-1][0] for _ in range(RUNS))
        results.append((name, n, std_f, note))
        print(f"{name:<8}{n:>6.2f}{gate_of(n):>7.3f}{std_f:>14.3f}   {note}")

    ns = [r[1] for r in results]
    ss = [r[2] for r in results]
    pearson = statistics.correlation(ns, ss)

    def rank(xs):
        order_ = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0] * len(xs)
        for pos, i in enumerate(order_):
            r[i] = pos
        return r

    spearman = statistics.correlation(rank(ns), rank(ss))
    strict = min(results, key=lambda r: r[2])
    loose = max(results, key=lambda r: r[2])
    print(f"\n读数: 规范强度 vs 变异率 Pearson r = {pearson:.3f}, Spearman = {spearman:.3f}")
    print(f"  最严 {strict[0]}(n={strict[1]:.2f}) 变异率 {strict[2]:.3f};"
          f" 最宽 {loose[0]}(n={loose[1]:.2f}) 变异率 {loose[2]:.3f},"
          f" 相差 {loose[2] / strict[2]:.1f} 倍")
    assert pearson < -0.93, f"应强负相关,实测 {pearson:.3f}"
    assert spearman < -0.93, f"秩应近于完全倒置,实测 {spearman:.3f}"
    assert loose[2] > 4.0 * strict[2], "宽体变异率应超严体 4 倍"
    assert strict[0] == "近体诗" and loose[0] == "现代散文", "两端应为近体与现代散文"
    print("  体裁身份证的松紧决定演化速度:门越窄,偏差被逐代筛掉,形式千年守恒;")
    print("  门越宽,偏差逐代累积,形式百态丛生。")

    # 规范崩解实验:近体在 t=40 释放规范
    print("\n规范崩解实验:近体诗(n=0.95)跑到 t=40 规范释放(n->0.10,文体解放的最小模型)")
    rng2 = random.Random(SEED + 1)
    hist = evolve(rng2, 0.95, T_GENS, collapse_at=40)
    pre = hist[39]
    post = hist[54]
    old_gate = gate_of(0.95)
    # 出旧门限的变体占比(崩解前直接为 0:门限就是生存线)
    rng3 = random.Random(SEED + 2)
    xs = [rng3.gauss(0.0, 0.05) for _ in range(W_POP)]
    for t in range(55):
        cur_n = 0.10 if t >= 40 else 0.95
        g = gate_of(cur_n)
        xs = [INERTIA * x + rng3.gauss(0.0, MUT_SD) for x in xs]
        surv = [x for x in xs if abs(x) <= g]
        while len(surv) < W_POP:
            surv.append(surv[rng3.randrange(len(surv))])
        xs = surv
    beyond = sum(1 for x in xs if abs(x) > old_gate) / W_POP
    print(f"  崩解前(t=39): 变异率 {pre[0]:.3f}(门宽 {pre[1]:.3f}),出旧门限变体 0%")
    print(f"  崩解后 15 代(t=54): 变异率 {post[0]:.3f}(门宽 {post[1]:.3f}),"
          f"出旧门限变体 {beyond:.0%}")
    assert post[0] > 5.0 * pre[0], f"崩解后变异率应跳升>5倍,实测 {pre[0]:.3f}->{post[0]:.3f}"
    assert beyond > 0.6, f"出旧门限变体应>60%,实测 {beyond:.0%}"
    print("  门一开,被压了千年的偏差十五代内喷出:新形式变体占文群六成以上——")
    print("  规范崩解期(文体解放)后爆发新变体,严体的保守是门在撑,不是创造力在枯。")
    print("\nOK 幕二断言通过:强负相关+秩近倒置;两端差>4倍;崩解后跳升>5倍且变体>60%。")


# ==================== 幕三:跨体旅行的代价(诗-词-曲-拟古回诗) ====================

CONSTRAINT_DIMS = (0, 1, 2)      # 韵律/整齐/程式:形式约束维,装棘轮
BETA_CONTENT, GAMMA_RETIGHTEN, NOISE = 0.65, 0.15, 0.02

# 诗系内部谱系的规范向量(风格化):近体(齐言极严)->词(依谱长短句)->曲(衬字更自由)
JINTI = POETRY
CI    = (0.85, 0.45, 0.80, 0.90, 0.35, 0.08, 0.40, 0.20)   # 词:依声填词,破齐言
QU    = (0.70, 0.30, 0.75, 0.60, 0.55, 0.15, 0.75, 0.45)   # 曲:曲牌+衬字,口语大兴


def migrate(rng, w, target):
    """跨体迁移一步:约束维松则一步到位/紧则恢复乏力;内容维部分收敛。"""
    new = []
    for k in range(8):
        eps = rng.uniform(-NOISE, NOISE)
        if k in CONSTRAINT_DIMS:
            if target[k] < w[k]:                      # 目标更自由:解放一步到位
                v = target[k]
            else:                                     # 目标更严:恢复乏力(棘轮)
                v = w[k] + GAMMA_RETIGHTEN * (target[k] - w[k])
        else:
            v = w[k] + BETA_CONTENT * (target[k] - w[k])
        new.append(min(1.0, max(0.0, v + eps)))
    return tuple(new)


def act3():
    print("\n" + "=" * 88)
    print("幕三 跨体旅行的代价:诗-词-曲-拟古回近体(破体是单行道)")
    print("=" * 88)
    print("\n诗系内部规范向量(韵律,整齐,程式,抒情,叙事,篇幅,口语,舞台):")
    for nm, v in (("近体", JINTI), ("词", CI), ("曲", QU)):
        print(f"  {nm}: {fmt_vec(v)}")
    rng = random.Random(SEED)
    w = tuple(x + rng.uniform(-NOISE, NOISE) for x in JINTI)   # 起程:一部规矩的近体
    origin = JINTI
    legs = [("词", CI), ("曲", QU), ("拟古回近体", JINTI)]
    print(f"\n起程作品(近体): {fmt_vec(w)}  d(w,近体)={wdist(w, origin):.3f}")
    dist_home = []
    for name, target in legs:
        before = wdist(w, target)
        w = migrate(rng, w, target)
        after = wdist(w, target)
        dh = wdist(w, origin)
        dist_home.append(dh)
        conv = after / before
        print(f"\n迁往 {name:<6} 收敛率(残距/原距)={conv:.2f}  d(w,近体)={dh:.3f}")
        print(f"  落点: {fmt_vec(w)}")
        if name != "拟古回近体":
            assert conv < 0.45, f"去程应深度收敛(<45%),实测 {conv:.2f}"
        else:
            assert conv > 0.60, f"回程应收敛残缺(>60%),实测 {conv:.2f}"

    print("\n读数:")
    print(f"  去程离原体单调增: d(词站,近体)={dist_home[0]:.3f} < d(曲站,近体)={dist_home[1]:.3f}")
    assert dist_home[0] < dist_home[1], "去程离原体距离应单调增"
    print(f"  回程之后 d(终态,近体)={dist_home[2]:.3f},仍大于第一站 {dist_home[0]:.3f}——"
          f"想回家,却回不到只走到词时的近")
    assert dist_home[2] > dist_home[0], "回程后应仍比第一站离原体远(不可逆)"
    g_final = w[1]
    print(f"  句式整齐度: 起 0.95 -> 终 {g_final:.2f}(近体需 0.95):"
          f"句式一旦解放,回不去严格齐言")
    assert g_final < 0.55, f"整齐度应回不到 0.55,实测 {g_final:.2f}"
    rng_c = random.Random(SEED + 3)
    control = tuple(x + rng_c.uniform(-NOISE, NOISE) for x in JINTI)  # 从未出门的对照组
    dc = wdist(control, origin)
    print(f"  对照组(从未出门的近体作者) d={dc:.3f}; 旅行者回程后 {dist_home[2]:.3f},"
          f" 是对照的 {dist_home[2] / dc:.1f} 倍")
    assert dist_home[2] > 5.0 * dc, "旅行者应远比从未出门者偏离原体"
    print("\nOK 幕三断言通过:去程深收敛/回程残缺;离原体单调增且回不去;整齐度棘轮锁死。")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 88)
    print("总断言收口:")
    print("  1) 体裁距离矩阵:诗-散为最大对(形式谱系两端);戏剧无近邻,独立性由")
    print("     舞台性一维独撑(消融即坍缩);杂交作品贴双亲连线落位——体裁不是")
    print("     标签,是八维形式空间里的坐标")
    print("  2) 规范的长短程:规范强度与演化变异率强负相关(严体保守,宽体多变);")
    print("     规范崩解后 15 代变异率跳升>5 倍、出旧门限变体>60%——体裁身份证")
    print("     的松紧决定演化速度")
    print("  3) 跨体棘轮:每次迁移向目标体收敛;离原体距离单调增且回程收敛残缺;")
    print("     句式整齐度一旦解放回不去——文体演化的棘轮:破体是单行道")
    print("OK 全部自验证通过")


if __name__ == "__main__":
    main()
