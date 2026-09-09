# -*- coding: utf-8 -*-
"""分化·结构·援助三幕实验:收敛的 Galton 佯谬 / 中心-边缘的结构位置 / 援助干预的一般均衡。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(三张结构卡的可构造端)、
04-发展社会学转代码.md(三条走廊)的配套实验。纯标准库(math/random/statistics),
无第三方依赖。

三幕:
  幕一 收敛的 Galton 佯谬——β 收敛与 σ 发散同时成立:
      100 国对数人均 GDP 演化 60 期,两臂对照。①纯 Gibrat 臂:增长率与水平
      无关(每期共同增速 2%+独立冲击 σ=0.09)——国家间对数标差逐十年单调
      扩大,增长对初始水平的截面回归无信号;②条件收敛臂:每国向自己的
      稳态回归(增长率=λ×(稳态−当前水平),λ=0.06;稳态=半承继初始水平
      +独立漂移)——增长对初始水平的截面回归出现显著为负的 β(穷国快,
      向均值的回归存在),但国家间分布的对数标差仍显著扩大。断言:均值
      回归≠差距缩小——每个国家都在追赶自己的稳态,而世界差距照样拉开
      (Galton 佯谬的发展版:β 收敛与 σ 发散不矛盾,单看增长回归会被
      「回归 toward the mean」骗到)。
  幕二 中心-边缘的结构位置——位置是接入史的函数:
      100 国贸易网络按优先连接生长:新国接入时以正比于 (度+1)×(1+0.25×
      禀赋) 的权重选择 2 个老国连边(禀赋=各国固定的微小质量差)。网络
      建成后 40 轮增长机会沿边流动(每轮抽 30 条边,两端各得一次增长),
      增长机会与中心度正相关。两轮宇宙对照:完全相同的国家禀赋,仅接入
      顺序不同(换随机种子重排)。断言:①终态累积增长与度中心度的
      Spearman 等级相关显著为正(机会沿边走,度即机会);②接入次序与
      终态度等级相关显著为负(先来者成枢纽);③跨宇宙同一国家的度排名
      相关弱、位置大幅洗牌——初始随机的接入顺序差异滚成大的位置分化
      (依附理论的最小机器:结构位置不是努力的函数,是接入史的函数)。
  幕三 援助干预的一般均衡——善意的实物投放可以是本地市场的价格炸弹:
      一个地方粮食市场:需求 P=10−0.1Q,本地供给 P=2+0.1Q,基准均衡
      Q*=40、P*=6、消费者剩余=生产者剩余=80。三臂等额注入预算 M=60
      (按基准价折 10 单位粮食):A 现金转移(需求右移 10);B 实物进口
      援助(按世界价 3 用 60 买 20 单位,供给右移 20;免费发放替代私人
      购买,需求左移 12);C 本地采购援助(需求右移 10,买本地)。断言:
      B 使本地均衡价格下降幅度最大(6→4.4),本地生产者剩余与产量大损
      (80→28.8、40→24);A/C 的总福利增量(ΔCS+ΔPS+受益人所得−预算)
      ≥B(42.5/47.5 vs −6.4)——单位预算送来更多粮食的 B 反而总福利为负;
      C 推高价格(6→6.5)的代价如实标注(food aid 与本地生产争论的
      教学版,通说口径)。

跑法: python -u experiments/divergence_structure_aid.py
"""

import math
import random
import statistics
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower().replace("-", "") != "utf8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ==================== 通用统计工具(纯标准库) ====================

def pearson(xs, ys):
    """Pearson 相关系数。"""
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / math.sqrt(vx * vy)


def ranks(xs):
    """排序取秩(并列取平均秩)。"""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    """Spearman 等级相关 = 秩上的 Pearson。"""
    return pearson(ranks(xs), ranks(ys))


def t_stat(rho, n):
    """相关系数的 t 统计量(原假设:不相关)。"""
    return rho * math.sqrt((n - 2) / max(1e-12, 1.0 - rho * rho))


def ols(xs, ys):
    """一元回归 y = a + b·x;返回 (a, b, t_b)。"""
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    s2 = sum(e * e for e in resid) / (n - 2)
    se = math.sqrt(s2 / sxx)
    return a, b, b / se


# ==================== 幕一:收敛的 Galton 佯谬 ====================

N_C = 100          # 国家数
T_YRS = 60         # 演化期数(年)
G_COMMON = 0.02    # 共同长期增速
GIBRAT_SIG = 0.09  # 纯 Gibrat 臂:独立冲击标准差
CONV_LAM = 0.06    # 条件收敛臂:向稳态的调整速度
CONV_RHO = 0.5     # 稳态对初始水平的承继系数
CONV_U = 0.7       # 稳态的独立漂移标准差
CONV_ETA = 0.02    # 收敛臂的每期噪声


def sigma_series(path):
    """按 10 年一档返回对数人均 GDP 的截面标准差序列(含 t=0 与 t=60)。"""
    return [statistics.pstdev(path[t]) for t in range(0, T_YRS + 1, 10)]


def act1():
    print("=" * 84)
    print("幕一 收敛的 Galton 佯谬:β 收敛与 σ 发散同时成立(均值回归≠差距缩小)")
    print("=" * 84)
    print(f"\n{N_C} 国对数人均 GDP,期初 N(8.0, 0.5²);演化 {T_YRS} 期,每 10 年一档看截面。")

    # —— 臂一:纯 Gibrat(增长率与水平无关)——
    rng = random.Random(8406411)
    y0 = [8.0 + 0.5 * rng.gauss(0.0, 1.0) for _ in range(N_C)]
    y = list(y0)
    traj = [list(y)]
    for _ in range(T_YRS):
        y = [v + G_COMMON + GIBRAT_SIG * rng.gauss(0.0, 1.0) for v in y]
        traj.append(list(y))
    g_gib = [yt - y00 for yt, y00 in zip(y, y0)]
    a1, b1, t1 = ols(y0, g_gib)
    sig_g = sigma_series(traj)

    # —— 臂二:条件收敛(每国向自己的稳态回归)——
    rng = random.Random(8406412)
    y0c = [8.0 + 0.5 * rng.gauss(0.0, 1.0) for _ in range(N_C)]
    theta = [8.0 + CONV_RHO * (v - 8.0) + CONV_U * rng.gauss(0.0, 1.0) for v in y0c]
    y = list(y0c)
    traj_c = [list(y)]
    for _ in range(T_YRS):
        y = [v + CONV_LAM * (th - v) + CONV_ETA * rng.gauss(0.0, 1.0)
             for v, th in zip(y, theta)]
        traj_c.append(list(y))
    g_conv = [yt - y00 for yt, y00 in zip(y, y0c)]
    a2, b2, t2 = ols(y0c, g_conv)
    sig_c = sigma_series(traj_c)

    # 穷国(初始最低 20 国)vs 富国(初始最高 20 国)的平均累计增长
    order0 = sorted(range(N_C), key=lambda i: y0c[i])
    poor = statistics.mean(g_conv[i] for i in order0[:20])
    rich = statistics.mean(g_conv[i] for i in order0[-20:])

    print(f"\n  {'臂':<14}{'β̂(增长对初始水平)':>20}{'t 值':>8}"
          f"{'σ(0)':>8}{'σ(60)':>9}{'σ 扩大':>8}")
    rows = (("纯 Gibrat", b1, t1, sig_g), ("条件收敛", b2, t2, sig_c))
    for name, b, t, sg in rows:
        print(f"  {name:<14}{b:>20.3f}{t:>8.2f}{sg[0]:>8.3f}{sg[-1]:>9.3f}"
              f"{sg[-1] / sg[0] - 1:>7.0%}")
    print(f"\n  纯 Gibrat 臂 σ 轨迹(每 10 年): "
          + " → ".join(f"{v:.3f}" for v in sig_g))
    print(f"  条件收敛臂 σ 轨迹(每 10 年): "
          + " → ".join(f"{v:.3f}" for v in sig_c))
    print(f"\n  条件收敛臂:初始最穷 20 国平均累计增长 {poor:+.3f}"
          f" vs 最富 20 国 {rich:+.3f}(穷国确实快)")

    # 断言 1a:纯 Gibrat 臂对数标差逐档单调扩大
    assert all(a < b for a, b in zip(sig_g, sig_g[1:])), \
        f"纯 Gibrat 臂 σ 应单调扩大:{[round(v, 3) for v in sig_g]}"
    # 断言 1b:纯 Gibrat 臂增长对初始水平回归无信号(β 不显著)
    assert abs(t1) < 2.0, f"纯 Gibrat 臂 β 不应显著(实测 t={t1:.2f})"
    # 断言 1c:条件收敛臂 β 显著为负(回归上出现「收敛」)
    assert b2 < 0 and t2 < -2.0, \
        f"条件收敛臂 β 应显著为负(实测 β={b2:.3f}, t={t2:.2f})"
    # 断言 1d:条件收敛臂穷国快于富国(向均值的回归存在)
    assert poor > rich + 0.1, f"穷国应快于富国({poor:.3f} vs {rich:.3f})"
    # 断言 1e:条件收敛臂的 σ 仍显著扩大(β 收敛与 σ 发散同时成立)
    assert sig_c[-1] > 1.25 * sig_c[0], \
        f"条件收敛臂 σ 应显著扩大({sig_c[0]:.3f}→{sig_c[-1]:.3f})"

    print("\n读数:")
    print("  · 纯 Gibrat 臂:增长率与水平无关,冲击逐年累加,对数标差 "
          f"{sig_g[0]:.2f}→{sig_g[-1]:.2f} 逐档单调扩大——差距是随机游走")
    print("    攒出来的;增长回归 β 不显著,没人追赶任何人")
    print(f"  · 条件收敛臂:每国向自己的稳态回归(λ={CONV_LAM}),60 年后"
          f"回归给出 β̂={b2:.3f}(t={t2:.2f},显著为负)")
    print(f"    ——只看这张回归表,你会宣布「世界在收敛」:穷国平均快 "
          f"{poor - rich:.2f} 个对数点")
    print(f"  · 但 σ 从 {sig_c[0]:.2f} 扩大到 {sig_c[-1]:.2f}"
          f"(+{sig_c[-1] / sig_c[0] - 1:.0%}):稳态本身是分散的"
          f"(承继 {CONV_RHO:.0%}+漂移 σ={CONV_U}),各国在追赶各自的")
    print("    稳态,而稳态之间的距离就是世界差距——β 收敛与 σ 发散")
    print("    同时成立:均值回归≠差距缩小(Galton 佯谬的发展版)")
    print(f"  · 头十年 σ 略有回缩({sig_c[0]:.3f}→{sig_c[1]:.3f})再拉开——"
          "这正是「收敛证据」最诱人的窗口期")
    print(f"\n✓ 幕一断言通过:Gibrat 臂 σ 单调扩大({sig_g[0]:.3f}→{sig_g[-1]:.3f});"
          f"收敛臂 β={b2:.3f}(t={t2:.2f})显著为负而 σ 仍扩大"
          f"({sig_c[0]:.3f}→{sig_c[-1]:.3f})")
    return rows


# ==================== 幕二:中心-边缘的结构位置 ====================

N_NET = 100        # 国家数
M0 = 4             # 初始核心(全连)
M_EDGES = 2        # 每个新国接入时连的边数
FIT_D = 0.25       # 禀赋进入连接权重的系数(微小质量差)
G_ROUNDS = 40      # 增长时间(轮)
G_PICKS = 30       # 每轮被抽中的边数(增长机会沿边流动)


def build_network(seed, fitness):
    """优先连接生长的贸易网络。返回(度表, 边表, 接入次序表)。"""
    rng = random.Random(seed)
    order = list(range(N_NET))
    rng.shuffle(order)                      # 接入顺序(本实验唯一的「初始差异」)
    deg = [0] * N_NET
    edges = []
    for i in range(M0):                     # 初始核心:全连
        for j in range(i + 1, M0):
            a, b = order[i], order[j]
            edges.append((a, b))
            deg[a] += 1
            deg[b] += 1
    for r in range(M0, N_NET):
        new = order[r]
        targets = []
        for _ in range(M_EDGES):
            pool = [c for c in range(N_NET) if deg[c] > 0 and c != new]
            weights = [(deg[c] + 1.0) * max(0.05, 1.0 + FIT_D * fitness[c])
                       for c in pool]
            x = rng.random() * sum(weights)
            acc = 0.0
            for c, w in zip(pool, weights):
                acc += w
                if x <= acc:
                    targets.append(c)
                    break
            else:
                targets.append(pool[-1])
        for t in targets:
            edges.append((new, t))
            deg[new] += 1
            deg[t] += 1
    return deg, edges, order


def grow_along_edges(edges, seed):
    """增长机会沿边流动:每轮抽 30 条边,两端各得一次增长。返回累积增长表。"""
    rng = random.Random(seed)
    growth = [0.0] * N_NET
    for _ in range(G_ROUNDS):
        for _ in range(G_PICKS):
            a, b = edges[rng.randrange(len(edges))]
            growth[a] += rng.uniform(0.01, 0.03)
            growth[b] += rng.uniform(0.01, 0.03)
    return growth


def act2():
    print("\n" + "=" * 84)
    print("幕二 中心-边缘的结构位置:位置不是努力的函数,是接入史的函数")
    print("=" * 84)
    rng = random.Random(8406420)
    fitness = [rng.gauss(0.0, 1.0) for _ in range(N_NET)]   # 各国固定的微小禀赋差

    deg1, edges1, order1 = build_network(8406421, fitness)
    deg2, edges2, order2 = build_network(8406422, fitness)  # 同禀赋,不同接入顺序
    grow1 = grow_along_edges(edges1, 8406423)
    grow2 = grow_along_edges(edges2, 8406424)
    # 接入次序表:entry_rank[cid] = 国家 cid 的接入名次(0 = 最早)
    rank1 = [0] * N_NET
    rank2 = [0] * N_NET
    for r, cid in enumerate(order1):
        rank1[cid] = r
    for r, cid in enumerate(order2):
        rank2[cid] = r

    # ①累积增长 vs 度中心度(两个宇宙各自)
    rho_g1 = spearman(grow1, deg1)
    rho_g2 = spearman(grow2, deg2)
    # ②接入次序 vs 终态度(先来者成枢纽)
    rho_e1 = spearman(rank1, deg1)
    rho_e2 = spearman(rank2, deg2)
    # ③跨宇宙:同一国家的度排名相关(位置洗牌程度)
    rho_x = spearman(deg1, deg2)
    rk1, rk2 = ranks(deg1), ranks(deg2)
    swing = [abs(a - b) for a, b in zip(rk1, rk2)]
    top1 = set(sorted(range(N_NET), key=lambda i: -deg1[i])[:10])
    bot2 = set(sorted(range(N_NET), key=lambda i: deg2[i])[:50])
    crash = len(top1 & bot2)   # 宇宙一的前 10 枢纽在宇宙二掉进后半区
    # 集中度与接入队列效应
    tot_deg = sum(deg1)
    top10_share = sum(sorted(deg1, reverse=True)[:10]) / tot_deg
    early = statistics.mean(deg1[i] for i in order1[:20])
    late = statistics.mean(deg1[i] for i in order1[-20:])
    early2 = statistics.mean(deg2[i] for i in order2[:20])
    late2 = statistics.mean(deg2[i] for i in order2[-20:])

    print(f"\n  {N_NET} 国按优先连接接入(新国连 2 个老国,权重∝(度+1)×(1±{FIT_D}×禀赋));")
    print(f"  网络建成后 {G_ROUNDS} 轮增长:每轮抽 {G_PICKS} 条边,两端各得一次增长")
    print(f"  (增长机会沿边流动)。两个宇宙:国家禀赋完全相同,仅接入顺序不同。")
    print(f"\n  宇宙一:累计增长×度中心度 Spearman ρ={rho_g1:.3f}(t={t_stat(rho_g1, N_NET):.1f})"
          f" | 接入序×度 ρ={rho_e1:.3f}")
    print(f"  宇宙二:累计增长×度中心度 Spearman ρ={rho_g2:.3f}(t={t_stat(rho_g2, N_NET):.1f})"
          f" | 接入序×度 ρ={rho_e2:.3f}")
    print(f"  跨宇宙:同一国家的度排名相关 ρ={rho_x:.3f};平均排名摆动 "
          f"{statistics.mean(swing):.1f} 位,最大 {max(swing):.0f} 位")
    print(f"  宇宙一的前 10 枢纽里 {crash} 个在宇宙二掉进度排名后半区")
    print(f"  集中度:前 10 国吃下 {top10_share:.0%} 的总贸易度;"
          f"最早 20 国平均度 {early:.1f} vs 最晚 20 国 {late:.1f}"
          f"(宇宙二 {early2:.1f} vs {late2:.1f})")

    # 断言 2a:终态累积增长与中心度显著正相关(机会沿边走)
    assert rho_g1 > 0.8 and t_stat(rho_g1, N_NET) > 3.0 and \
        rho_g2 > 0.8 and t_stat(rho_g2, N_NET) > 3.0, \
        f"增长×中心度应显著为正({rho_g1:.3f}/{rho_g2:.3f})"
    # 断言 2b:接入次序与终态度显著负相关(先来者成枢纽)
    assert rho_e1 < -0.5 and rho_e2 < -0.5, \
        f"接入序×度应显著为负({rho_e1:.3f}/{rho_e2:.3f})"
    # 断言 2c:跨宇宙位置洗牌——同一国家、同一禀赋,位置大变
    assert abs(rho_x) < 0.5, f"跨宇宙度排名相关应弱(实测 {rho_x:.3f})"
    assert max(swing) > 40 and crash >= 3, \
        f"应出现大幅位置洗牌(最大摆动 {max(swing):.0f}, 坠落枢纽 {crash} 个)"
    # 断言 2d:优先连接制造中心-边缘等级(先来者与晚来者的位置差)
    assert top10_share > 0.22 and early > 1.8 * late, \
        f"应出现枢纽集中({top10_share:.2%})与队列效应({early:.1f} vs {late:.1f})"

    print("\n读数:")
    print(f"  · 增长机会与网络中心度等级相关 ρ≈{rho_g1:.2f}/{rho_g2:.2f}"
          "(t>10)——机会沿边流动,")
    print("    度数就是机会的入口:中心-边缘结构直接换算成增长分配")
    print(f"  · 优先连接+队列效应:最早 20 国平均度≈{early:.1f},最晚 20 国"
          f"≈{late:.1f};前 10 枢纽")
    print(f"    吃下 {top10_share:.0%} 的总度——中心-边缘不是努力排序,是接入史排序")
    print(f"  · 两轮宇宙只换了接入顺序(禀赋分毫未动):跨宇宙度排名相关仅 "
          f"{rho_x:.2f},平均")
    print(f"    摆动 {statistics.mean(swing):.0f} 位,宇宙一的 10 大枢纽有 "
          f"{crash} 个在宇宙二")
    print("    坠入后半区——初始随机的顺序差异被优先连接滚成巨大的位置分化:")
    print("    「同样的国家,早到三十年就是枢纽」——依附理论的最小机器")
    print(f"\n✓ 幕二断言通过:增长×中心度 ρ={rho_g1:.3f}/{rho_g2:.3f} 显著;"
          f"接入序×度 ρ={rho_e1:.3f}/{rho_e2:.3f};跨宇宙 ρ={rho_x:.3f} 弱、"
          f"最大摆动 {max(swing):.0f} 位")
    return rho_g1, rho_x, top10_share


# ==================== 幕三:援助干预的一般均衡 ====================

DEM_A, DEM_B = 10.0, 0.1   # 需求:P = 10 − 0.1·Q
SUP_C, SUP_D = 2.0, 0.1    # 本地供给:P = 2 + 0.1·Q
P_WORLD = 3.0              # 世界价格(进口到岸价)
BUDGET = 60.0              # 三臂等额预算(=基准价 6×10 单位)
UNIT_EQ = BUDGET / 6.0     # 按基准价折算的等值数量=10 单位
DISPLACE = 0.6             # 实物发放对私人购买的替代率


def market(shift_d, imports):
    """求干预后的局部均衡。shift_d=需求水平位移(右正),imports=进口数量。
    返回 dict:Q(总交易量)、P(价格)、Q_local(本地产量)、CS、PS、给受益人的数量。"""
    dem_int = DEM_A + DEM_B * shift_d          # 需求截距(位移后)
    sup_int = SUP_C - SUP_D * imports          # 含进口的供给截距
    q = (dem_int - sup_int) / (DEM_B + SUP_D)
    p = dem_int - DEM_B * q
    q_local = q - imports
    cs = 0.5 * (dem_int - p) * q
    ps = 0.5 * (p - SUP_C) * q_local
    return {"Q": q, "P": p, "Q_local": q_local, "CS": cs, "PS": ps}


def act3():
    print("\n" + "=" * 84)
    print("幕三 援助干预的一般均衡:善意的实物投放可以是本地市场的价格炸弹")
    print("=" * 84)
    base = market(0.0, 0.0)
    # 三臂等额预算 M=60(按基准价折 10 单位)
    armA = market(UNIT_EQ, 0.0)                       # A 现金:需求右移 10
    armB = market(-DISPLACE * (BUDGET / P_WORLD),     # B 实物:需求左移 12(替代)
                  BUDGET / P_WORLD)                   #   供给右移 20(进口)
    armC = market(UNIT_EQ, 0.0)                       # C 本地采购:需求右移 10(买本地)

    welfare = {}
    welfare["A"] = (armA["CS"] - base["CS"]) + (armA["PS"] - base["PS"]) \
        + BUDGET - BUDGET                             # 受益人得现金面值 60,捐赠成本 60
    welfare["B"] = (armB["CS"] - base["CS"]) + (armB["PS"] - base["PS"]) \
        + (BUDGET / P_WORLD) * armB["P"] - BUDGET     # 受益人得 20 单位,按新市价折
    welfare["C"] = (armC["CS"] - base["CS"]) + (armC["PS"] - base["PS"]) \
        + UNIT_EQ * armC["P"] - BUDGET                # 受益人得 10 单位(本地采购所得)

    print(f"\n  地方粮食市场:需求 P={DEM_A:.0f}−{DEM_B}·Q,本地供给 P={SUP_C:.0f}+{SUP_D}·Q;")
    print(f"  基准均衡 Q*={base['Q']:.0f},P*={base['P']:.0f},CS=PS={base['CS']:.0f}。")
    print(f"  三臂等额注入预算 M={BUDGET:.0f}(按基准价折 {UNIT_EQ:.0f} 单位粮食):")
    print(f"  A 现金转移(需求右移 {UNIT_EQ:.0f}) | B 实物进口(世界价 {P_WORLD:.0f} 买 "
          f"{BUDGET / P_WORLD:.0f} 单位,供给右移 {BUDGET / P_WORLD:.0f}、免费发放替代"
          f"私人购买使需求左移 {DISPLACE * BUDGET / P_WORLD:.0f}) | C 本地采购(需求右移 "
          f"{UNIT_EQ:.0f},买本地)")
    print(f"\n  {'干预':<6}{'均衡价 P':>9}{'价格变动':>9}{'本地产量':>8}{'生产者剩余':>10}"
          f"{'受益人所得':>10}{'总福利增量':>10}")
    for name, arm, val in (("A 现金", armA, BUDGET),
                           ("B 实物", armB, (BUDGET / P_WORLD) * armB["P"]),
                           ("C 本购", armC, UNIT_EQ * armC["P"])):
        print(f"  {name:<6}{arm['P']:>9.1f}{arm['P'] - base['P']:>+9.1f}"
              f"{arm['Q_local']:>8.0f}{arm['PS']:>10.1f}{val:>10.0f}"
              f"{welfare[name[0]]:>+10.1f}")

    # 断言 3a:B 的本地价格下降幅度最大(且远超 A/C 的价格上升)
    drop_b = base["P"] - armB["P"]
    rise_ac = max(armA["P"] - base["P"], armC["P"] - base["P"])
    assert armB["P"] < armA["P"] and armB["P"] < armC["P"] and drop_b > 2 * rise_ac, \
        f"B 的价格下跌应最大({drop_b:.2f} vs {rise_ac:.2f})"
    # 断言 3b:B 使本地生产者剩余与产量大受损
    assert armB["PS"] < 0.5 * base["PS"], f"B 应重创生产者剩余({armB['PS']:.1f})"
    assert armB["Q_local"] < 0.75 * base["Q_local"], \
        f"B 应重挫本地产量({armB['Q_local']:.1f})"
    # 断言 3c:A/C 的总福利增量 ≥ B(B 为负)
    assert welfare["A"] > welfare["B"] + 40 and welfare["C"] > welfare["B"] + 40, \
        f"A/C 福利应远高于 B({welfare})"
    assert welfare["B"] < 0, f"B 的总福利增量应为负({welfare['B']:.1f})"
    # 断言 3d:C 的代价如实标注:推高本地价格
    assert armC["P"] > base["P"], "C 应推高本地价格(代价)"
    # 断言 3e:B 送来的粮食更多,总福利反而更差(价格炸弹)
    assert BUDGET / P_WORLD > UNIT_EQ, "B 应送达更多粮食"

    print("\n读数:")
    print(f"  · B 用世界价 {P_WORLD:.0f} 把 {BUDGET:.0f} 元换成 {BUDGET / P_WORLD:.0f} 单位粮食"
          f"(A/C 只折 {UNIT_EQ:.0f} 单位)——单位预算送达量最大")
    print(f"  · 但进口供给右移+发放替代需求左移双向夹击:本地价 {base['P']:.1f}→"
          f"{armB['P']:.1f}(跌 {drop_b:.1f}),本地产量 {base['Q_local']:.0f}→"
          f"{armB['Q_local']:.0f},生产者剩余 {base['PS']:.0f}→{armB['PS']:.1f}"
          f"(蒸发 {1 - armB['PS'] / base['PS']:.0%})")
    print(f"  · 总福利账(ΔCS+ΔPS+受益人所得−预算):B = {welfare['B']:+.1f}"
          f" < A = {welfare['A']:+.1f} < C = {welfare['C']:+.1f}")
    print("    ——送来最多粮食的那只手臂,是唯一让总福利为负的:本地供给曲线")
    print("      被压弯的部分(生产者剩余)超过了便宜粮食的好处(food aid 与")
    print("      本地生产争论的教学版,通说口径)")
    print(f"  · C 的代价如实标注:本地采购把需求抬起来,价格 {base['P']:.1f}→"
          f"{armC['P']:.1f},未被项目覆盖的净买家(其他贫困户)为粮价上涨买单——")
    print("    「买本地」救了生产者,但把成本转给了市场里的另一半")
    print(f"\n✓ 幕三断言通过:B 价格跌幅最大({drop_b:.1f})、生产者剩余蒸发 "
          f"{1 - armB['PS'] / base['PS']:.0%};A/C 福利({welfare['A']:+.1f}/"
          f"{welfare['C']:+.1f})≫B({welfare['B']:+.1f});C 推价代价已标注")
    return welfare


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① Galton 佯谬:条件收敛臂 β 显著为负(回归上「收敛」)而国家间")
    print("     σ 仍扩大——均值回归≠差距缩小;纯 Gibrat 臂则 σ 单调扩大、")
    print("     回归无信号。增长回归单看 β 会被向均值回归骗到")
    print("  ② 结构位置:增长机会与网络中心度 Spearman 显著为正;优先连接")
    print("     +队列效应造出中心-边缘等级;仅换接入顺序,同一批国家的位置")
    print("     大洗牌——位置不是努力的函数,是接入史的函数")
    print("  ③ 干预均衡:等额预算下,实物进口(送粮最多)价格炸弹效应最强,")
    print("     本地生产者剩余大损、总福利为负;现金与本地采购的总福利增量")
    print("     远高于之;本地采购的推价代价如实标注")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
