# -*- coding: utf-8 -*-
"""文化动力学三律:品味区隔的涌现 / 简单传染 vs 复杂传染 / 巴斯扩散拐点。

00-体系结构.md(反直觉三发现)、03-可构造与结构.md(位置转写引擎与扩散引擎的
严格可构造性)、04-文化社会学转代码.md(走廊 1/2/3)的配套实验。
纯标准库(math/random/statistics),无第三方依赖。

三律:
  律一 品味区隔的涌现(布迪厄《区分》的最小计算模型):
      二维文化空间(横轴=大众-小众,纵轴=俗-雅),三个资本位置不同的群体
      各在自己的中心生成品味点(组内同方差各向同性高斯,σ=0.5,每组 80 人)。
      区隔度 = 组间均方 / 组内均方(2D 合并的 F 比)。资本极化参数 d 把
      三个群体中心撑开(等边三角,半径 d;d=0 时三心合一)。
      断言:区隔度随 d 单调上升(d=0 时 ≈1 无区隔);组内发散度从头到尾
      没变——品味差异不是个人癖好的统计,是群体位置的投影。
  律二 简单传染 vs 复杂传染(Centola 复杂传染的最小对照):
      两网同源于 100 节点规则环格(度 8):
        随机规则网络 = 全重连 p=1.0(度保持,局部聚类被抹平)
        重连聚类网络 = 低重连 p=0.1(度保持,聚类保留≈环格的 70%+)
      种子同一批(连续块 0..4,5%);规则:简单传染 1 个感染邻居即采纳,
      复杂传染需 3 个感染邻居。
      断言:简单传染两网终染率无差(都近 100%);复杂传染在聚类网络
      终染率显著高于随机规则网络——谣言一次接触就传,规范要多次见证
      才信,而"见证"需要圈子:网络结构只对复杂传染重要。
  律三 巴斯扩散拐点(Bass 1969 扩散模型):
      采纳者 F 的每步新增 dF = dt·(1−F)·(p + q·F)(p 创新/外生,q 模仿/
      内生)。峰值采纳率发生在 F* = 1/2 − p/(2q)(连续解析解)。
      断言:p=0.03、q=0.5 时 F*=0.47——峰值增长出现在市场渗透近半
      **之前**;p 增大使峰值前移且发生在更低渗透率上;q=0(纯创新无
      模仿)时无 S 曲线(峰值在第 0 步)——新文化产品的成败在早期
      采纳结构里就已押注。

跑法: python3 -u experiments/culture_dynamics.py
"""

import math
import random
import statistics

# ==================== 律一:品味区隔的涌现 ====================

SIGMA = 0.5      # 组内品味发散度(三组相同,从头到尾不变)
N_PER = 80       # 每组人数
GROUPS = 3       # 三个资本位置不同的群体
ANGLES = (90.0, 210.0, 330.0)   # 群体中心在文化空间中的方位(等边三角)
POLARIZATIONS = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5)   # 资本极化参数 d


def segregation_ratio(rng, d):
    """给定极化 d,生成三组品味点,返回区隔度(2D 合并 F 比)与各组均值。"""
    groups = []
    for ang in ANGLES:
        cx = d * math.cos(math.radians(ang))
        cy = d * math.sin(math.radians(ang))
        groups.append([(rng.gauss(cx, SIGMA), rng.gauss(cy, SIGMA))
                       for _ in range(N_PER)])
    means = [(sum(x for x, _ in g) / len(g), sum(y for _, y in g) / len(g))
             for g in groups]
    grand = (sum(mx for mx, _ in means) / GROUPS,
             sum(my for _, my in means) / GROUPS)
    ss_within = sum((x - mx) ** 2 + (y - my) ** 2
                    for g, (mx, my) in zip(groups, means) for x, y in g)
    ss_between = sum(N_PER * ((mx - grand[0]) ** 2 + (my - grand[1]) ** 2)
                     for mx, my in means)
    n = GROUPS * N_PER
    ms_within = ss_within / (n - GROUPS)
    ms_between = ss_between / (GROUPS - 1)
    return ms_between / ms_within, means


def act1():
    print("=" * 84)
    print("律一 品味区隔的涌现(三组资本位置不同,组内同方差高斯 σ=0.5,各 80 人)")
    print("=" * 84)
    print("\n文化空间:横轴=大众-小众,纵轴=俗-雅;三组中心构成等边三角,")
    print("极化参数 d 撑开三角半径;区隔度 = 组间均方 / 组内均方(2D 合并 F 比)\n")
    rng = random.Random(840371)
    print(f"{'极化 d':>7} {'区隔度':>10}  读数")
    ratios = {}
    for d in POLARIZATIONS:
        ratio, means = segregation_ratio(rng, d)
        ratios[d] = ratio
        if d == 0.0:
            note = "三心合一:文化空间只有一片云,无组间结构"
        else:
            note = "三团品味云按资本位置分开"
        print(f"{d:>7.1f} {ratio:>10.1f}  {note}")
    print("\n读数:")
    print("  · 组内发散度 σ=0.50 从头到尾没有变——变的是群体中心的间距;")
    print("    区隔度随极化单调上升:品味差异不是个人癖好的统计,")
    print("    是群体位置在文化空间上的投影(《区分》的最小计算模型)")
    print("  · 区隔度≈(d₂/d₁)² 标度:d 翻倍,区隔度约四倍——投影按平方级放大")

    # 断言 1:d=0 无区隔;区隔度随极化单调上升;d² 标度
    assert ratios[0.0] < 1.5, f"d=0 应无区隔(≈1),实测 {ratios[0.0]:.2f}"
    seq = [ratios[d] for d in POLARIZATIONS[1:]]
    assert all(a < b for a, b in zip(seq, seq[1:])), \
        f"区隔度应随极化单调上升,实测 {['%.1f' % r for r in seq]}"
    assert ratios[0.5] >= 45.0, f"d=0.5 区隔度应已显著,实测 {ratios[0.5]:.1f}"
    assert ratios[2.5] / ratios[0.5] >= 15.0, "区隔度应近 d² 标度(≈25 倍)"
    print(f"\n✓ 律一断言通过:d=0 区隔度 {ratios[0.0]:.2f}(≈1);"
          f"d=0.5→2.5 区隔度 {ratios[0.5]:.0f}→{ratios[2.5]:.0f} 单调上升"
          f"(约 {ratios[2.5] / ratios[0.5]:.0f} 倍,近 d² 标度)")


# ==================== 律二:简单传染 vs 复杂传染 ====================

N_NET = 100   # 节点数
K_DEG = 8     # 度(环格每侧 4 个邻居)
SEEDS = tuple(range(5))   # 种子:连续块 0..4(5%),两网同一批


def ring_lattice(n, k):
    """规则环格:节点 i 连接 i±1..i±(k/2)。"""
    adj = [set() for _ in range(n)]
    half = k // 2
    for i in range(n):
        for j in range(1, half + 1):
            b = (i + j) % n
            adj[i].add(b)
            adj[b].add(i)
    return adj


def rewire(base, p, rng):
    """WS 式重连:每条边以概率 p 把一端改接到随机新节点(去重/去自环)。

    边数与平均度精确保持(度保持):重连目标避开当前邻居与环格邻居,
    保证每条枚举边恰好落成一条新边;p 越大,局部聚类被抹得越平。
    """
    adj = [set(s) for s in base]
    n = len(adj)
    half = K_DEG // 2
    edges = [(i, (i + j) % n) for i in range(n) for j in range(1, half + 1)]
    for i, j in edges:
        if rng.random() < p:
            forbidden = adj[i] | base[i] | {i}   # 已连的 + 环格邻居 + 自己
            m = rng.choice([x for x in range(n) if x not in forbidden])
            adj[i].discard(j)      # 摘掉环格边 (i,j)
            adj[j].discard(i)
            adj[i].add(m)          # 改接为 (i,m),双向记账
            adj[m].add(i)
    return adj


def clustering_coefficient(adj):
    """平均局部聚类系数:邻居之间也互为邻居的比例(圈子的密度)。"""
    coeffs = []
    for i in range(len(adj)):
        nbrs = list(adj[i])
        k = len(nbrs)
        if k < 2:
            continue
        links = sum(1 for a in nbrs for b in nbrs if a < b and b in adj[a])
        coeffs.append(2 * links / (k * (k - 1)))
    return statistics.mean(coeffs)


def spread(adj, seeds, need):
    """传染:每步同步更新,未感染者感染邻居数 ≥ need 即采纳;返回终染率。"""
    infected = set(seeds)
    while True:
        new = [i for i in range(len(adj)) if i not in infected
               and sum(1 for nb in adj[i] if nb in infected) >= need]
        if not new:
            return len(infected) / len(adj)
        infected.update(new)


def act2():
    print("\n" + "=" * 84)
    print("律二 简单传染 vs 复杂传染(两网同源于 100 节点规则环格·度 8)")
    print("=" * 84)
    base = ring_lattice(N_NET, K_DEG)
    rng_c = random.Random(840372)
    rng_r = random.Random(840373)
    clustered = rewire(base, 0.1, rng_c)   # 重连聚类网络:低重连,聚类保留
    regular = rewire(base, 1.0, rng_r)     # 随机规则网络:全重连,聚类抹平

    c_cluster = clustering_coefficient(clustered)
    c_regular = clustering_coefficient(regular)
    deg_cluster = sum(len(s) for s in clustered) / N_NET
    deg_regular = sum(len(s) for s in regular) / N_NET
    print(f"\n{'网络':　<6} {'平均度':>6} {'聚类系数':>8}  读数")
    print(f"{'重连聚类网络(p=0.1)':　<6} {deg_cluster:>6.1f} {c_cluster:>8.3f}"
          "  环格的圈子里 70% 以上的邻居互相认识")
    print(f"{'随机规则网络(p=1.0)':　<6} {deg_regular:>6.1f} {c_regular:>8.3f}"
          "  同样的度,圈子被打散——邻居彼此几乎不认识")
    print(f"\n种子同一批:节点 0-4(连续块,{len(SEEDS)}%)")

    results = {}
    for rule, need in (("简单传染(1 个感染邻居即采纳)", 1),
                       ("复杂传染(需 3 个感染邻居)", 3)):
        fr = spread(regular, SEEDS, need)
        fc = spread(clustered, SEEDS, need)
        results[need] = (fr, fc)
        print(f"\n{rule}")
        print(f"    随机规则网络终染率 {fr:>6.1%}    重连聚类网络终染率 {fc:>6.1%}")
    fr_simple, fc_simple = results[1]
    fr_complex, fc_complex = results[3]
    print("\n读数:")
    print("  · 简单传染(谣言式):一次接触就传——两网都近 100%,结构无关;")
    print("  · 复杂传染(规范式):要 3 个邻居都感染才信——随机网络里种子周围")
    print("    没有三个互相认识的见证人,传染冻死在 5%;聚类网络里波前每一步")
    print("    都有 4 个本地邻居冗余作保(宽桥),一路烧穿全图;")
    print("  · 「见证」需要圈子:网络结构只对复杂传染重要")

    # 断言 2:简单传染两网无差;复杂传染聚类网络显著更高
    assert abs(deg_cluster - K_DEG) < 1e-9 and abs(deg_regular - K_DEG) < 1e-9, \
        "重连应保持平均度(度保持)"
    assert c_cluster > 2.5 * c_regular, \
        f"聚类网络应显著更聚类,实测 {c_cluster:.3f} vs {c_regular:.3f}"
    assert fc_simple >= 0.99 and fr_simple >= 0.99, \
        "简单传染两网都应近 100%"
    assert abs(fc_simple - fr_simple) <= 0.01, \
        "简单传染两网终染率应无差"
    assert fc_complex >= 0.95, f"复杂传染在聚类网络应烧穿,实测 {fc_complex:.1%}"
    assert fr_complex <= 0.10, f"复杂传染在随机规则网络应冻死,实测 {fr_complex:.1%}"
    assert fc_complex - fr_complex >= 0.85, "两网复杂传染差距应显著"
    print(f"\n✓ 律二断言通过:简单传染 {fr_simple:.0%} vs {fc_simple:.0%}(无差);"
          f"复杂传染 {fc_complex:.0%} vs {fr_complex:.0%}"
          f"(差 {fc_complex - fr_complex:.0%})——结构只对复杂传染重要")


# ==================== 律三:巴斯扩散拐点 ====================

DT = 0.1   # 时间步长(连续模型的离散化)


def bass_curve(p, q, dt=DT, steps=4000):
    """巴斯扩散:F_{t+1} = F_t + dt·(1−F)(p+qF);返回轨迹(含 F₀=0)。"""
    traj = [0.0]
    F = 0.0
    for _ in range(steps):
        dF = dt * (1 - F) * (p + q * F)
        F += dF
        traj.append(F)
        if F >= 1 - 1e-9:
            break
    return traj


def peak_of(traj):
    """返回(峰值步索引, 峰值步起点渗透率 F_peak, 峰值增量)。"""
    incs = [(traj[t + 1] - traj[t]) for t in range(len(traj) - 1)]
    t_peak = max(range(len(incs)), key=lambda t: incs[t])
    return t_peak, traj[t_peak], incs[t_peak]


def act3():
    print("\n" + "=" * 84)
    print("律三 巴斯扩散拐点(dF = dt·(1−F)(p+qF);峰值采纳率何时出现)")
    print("=" * 84)
    p0, q0 = 0.03, 0.5
    Fstar = 0.5 - p0 / (2 * q0)
    traj = bass_curve(p0, q0)
    t_peak, F_peak, inc_peak = peak_of(traj)
    print(f"\n基准参数 p={p0}(创新), q={q0}(模仿):")
    print(f"  解析拐点 F* = 1/2 − p/(2q) = {Fstar:.4f}(连续模型)")
    print(f"  模拟峰值:第 {t_peak} 步(t={t_peak * DT:.1f}),"
          f"该步起点渗透率 F={F_peak:.4f},单步采纳 {inc_peak:.4f}")
    print(f"  终点渗透率 {traj[-1]:.6f}(S 曲线饱和)")

    print(f"\n{'p':>5} {'q':>4} {'F*=1/2−p/2q':>12} {'峰值t':>6} {'峰值处F':>8}  读数")
    peaks = []
    for p in (0.02, 0.03, 0.05, 0.10, 0.20):
        fs = 0.5 - p / (2 * q0)
        tr = bass_curve(p, q0)
        tp, fp, ip = peak_of(tr)
        peaks.append((p, tp, fp))
        print(f"{p:>5.2f} {q0:>4.1f} {fs:>12.3f} {tp * DT:>6.1f} {fp:>8.3f}"
              "  p 越大,峰值越早且渗透率越低")
    print("\n对照:q=0(纯创新无模仿,p=0.03)")
    traj_q0 = bass_curve(0.03, 0.0)
    tp0, fp0, ip0 = peak_of(traj_q0)
    print(f"  峰值在第 {tp0} 步(开局即巅峰),其后单调衰减——无 S 曲线,"
          f"终点 {traj_q0[-1]:.4f}")
    print("\n读数:")
    print("  · 峰值增长发生在渗透率 0.47(近半之前)——直觉以为「大多数人")
    print("    接受后增长见顶」,巴斯说见顶在近半之前,下半场永远在减速;")
    print("  · p(创新/外生推动)增大 → 峰值前移且落在更低渗透率上:")
    print("    增长的窗口被外生力量提前预支;")
    print("  · q=0 时没有模仿引擎,只剩指数衰减的创新流——S 曲线是模仿的产物;")
    print("  · 新文化产品的成败在早期采纳结构里就已押注(拐点之前定成败)")

    # 断言 3:拐点位置、p 的前移效应、q=0 无 S 曲线
    assert abs(Fstar - 0.47) < 1e-12, "F* 应为 0.47"
    tol = DT * (1 - Fstar) * (p0 + q0 * Fstar) + 1e-9   # 一个欧拉步的容差
    assert abs(F_peak - Fstar) <= tol, \
        f"峰值处 F 应贴近 F*(差不超过一步 {tol:.4f}),实测 {F_peak:.4f} vs {Fstar:.4f}"
    assert traj[-1] >= 0.999, "巴斯 S 曲线应饱和到近 100%"
    tps = [tp for _, tp, _ in peaks]
    fps = [fp for _, _, fp in peaks]
    assert all(a > b for a, b in zip(tps, tps[1:])), \
        f"p 增大应使峰值前移,实测 {[t * DT for t in tps]}"
    assert all(a > b for a, b in zip(fps, fps[1:])), \
        f"p 增大应使峰值落在更低渗透率,实测 {['%.3f' % f for f in fps]}"
    assert tp0 == 0, "q=0 时峰值应在第 0 步(无 S 曲线)"
    print(f"\n✓ 律三断言通过:p=0.03,q=0.5 → F*={Fstar:.2f},模拟峰值处 "
          f"F={F_peak:.3f}(贴解析解);p 0.02→0.20 峰值时间 "
          f"{tps[0] * DT:.1f}→{tps[-1] * DT:.1f} 单调前移;q=0 无 S 曲线")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① 区隔度随资本极化单调上升(d=0 时≈1,组内发散度不变):")
    print("     品味差异是群体位置的投影,不是个人癖好的统计(《区分》最小模型)")
    print("  ② 简单传染两网无差(都近 100%),复杂传染聚类≫随机(差 ≥85%):")
    print("     谣言一次接触就传,规范要多次见证才信——见证需要圈子(Centola)")
    print("  ③ 巴斯拐点 F*=1/2−p/(2q)=0.47 在渗透近半之前,p 增大使峰值前移,")
    print("     q=0 无 S 曲线:新文化产品的成败在早期采纳结构里就已押注(Bass)")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
