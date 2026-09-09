# -*- coding: utf-8 -*-
"""网络与涌现:数理社会学三个经典机制的最小实现。

00-体系结构.md(反直觉三律)、03-可构造与结构.md(模型规格卡/参数扫描卡/
稳健性卡的样板)、04-数理社会学转代码.md(走廊 1/2)的配套实验。
纯标准库(random),无第三方依赖;固定随机种子,逐幕 assert。

与同波社会学理论家族的 Granovetter 阈值级联实验(threshold_cascade.py)
零重叠:那边管「阈值分布形状压倒均值」,这边管网络结构与空间/生长
机制的涌现——模型族谱的正式理论侧。

三律:
  幕一 Schelling 隔离的微观-宏观断裂(20×20 网格,两类各 30%、空 40%,
      规则=相邻同类占比<t 则迁往随机空位,任务底版 8×8 放大以平滑统计):
      断言 t=0.3(温和偏好)终态平均同类邻居占比>0.7(初始随机约 0.5)
      ——温和偏好滚成接近完全的隔离;对照 t=0.7:初始大面积不满意(约八成)、
      迁移人次约八倍,而偏好+0.4 只买到隔离+约 0.23(严重次线性)——
      从偏好读不出隔离,从隔离也读不回偏好(如实标注:本参数域两档均收敛,
      「高阈值震荡不收敛」见于空位更少或群体不对称的参数域)——
      隔离不是偏好的镜像,是动力学的产物。
  幕二 WS 小世界交叉带(n=1000、k=10 环格,rewiring 概率 p 自 1e-4 到 1
      对数扫描):断言存在 p∈[0.01,0.1] 使平均路径长度 L(p)/L(0)<0.5 而
      聚类系数 C(p)/C(0)>0.5——少数捷径买走大部分距离,朋友团的圈子
      几乎不破。
  幕三 BA 优先连接的枢纽性(n=2000、m=2 生长网络):断言累积度分布
      P(K≥k) 在 log-log 上线性拟合 R²>0.98(幂律尾);同边数 ER 随机
      网络的最大度远小于 BA(打印对比)——同样的连线数,生长机制决定
      有没有枢纽;社会网络的「大人物」是机制产物不是统计偶然。

跑法: python3 -u experiments/networks_and_emergence.py
"""

import math
import random

SIDE = 20        # 幕一网格边长(400 格)
FRAC = 0.30      # 两类各占 30%,其余 40% 空位
RUNS = 10        # 每档阈值重复游程
SEED_BASE = 20260907  # 固定种子(游程/扫描档逐格加号,可复现)


# ==================== 幕一:Schelling 隔离 ====================

def neighbors(r, c, side):
    """摩尔邻域:周围 8 格(边界自动裁剪)。"""
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < side and 0 <= cc < side:
                yield rr, cc


def make_grid(rng):
    """随机初始格局:1/2 两类各 30%,0 为空位。"""
    cells = ([1] * int(SIDE * SIDE * FRAC)
             + [2] * int(SIDE * SIDE * FRAC))
    cells += [0] * (SIDE * SIDE - len(cells))
    rng.shuffle(cells)
    return [cells[r * SIDE:(r + 1) * SIDE] for r in range(SIDE)]


def same_frac(grid, r, c):
    """相邻同类占比(分母=相邻占用格数);无占用邻居返回 None(视为满足)。"""
    occ = same = 0
    for rr, cc in neighbors(r, c, SIDE):
        v = grid[rr][cc]
        if v:
            occ += 1
            if v == grid[r][c]:
                same += 1
    return same / occ if occ else None


def mean_same(grid):
    """全体居民的相邻同类占比均值(隔离度指标)。"""
    vals = [same_frac(grid, r, c)
            for r in range(SIDE) for c in range(SIDE) if grid[r][c]]
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals)


def unsatisfied(grid, t):
    """不满意者清单:相邻同类占比 < t。"""
    out = []
    for r in range(SIDE):
        for c in range(SIDE):
            if grid[r][c]:
                f = same_frac(grid, r, c)
                if f is not None and f < t:
                    out.append((r, c))
    return out


def run_schelling(rng, t, max_rounds=300):
    """一轮 Schelling 动力学:不满意者按随机序迁往随机空位。"""
    grid = make_grid(rng)
    init_same = mean_same(grid)
    init_unsat = len(unsatisfied(grid, t)) / (2 * int(SIDE * SIDE * FRAC))
    empties = [(r, c) for r in range(SIDE)
               for c in range(SIDE) if not grid[r][c]]
    moves = 0
    converged = False
    rounds = 0
    for rounds in range(1, max_rounds + 1):
        uns = unsatisfied(grid, t)
        if not uns:
            converged = True
            break
        rng.shuffle(uns)
        for (r, c) in uns:
            f = same_frac(grid, r, c)      # 轮内重查:邻居变了,先救活的不搬
            if f is not None and f >= t:
                continue
            i = rng.randrange(len(empties))
            dr_, dc_ = empties.pop(i)
            grid[dr_][dc_] = grid[r][c]
            grid[r][c] = 0
            empties.append((r, c))
            moves += 1
    return init_same, init_unsat, mean_same(grid), rounds, converged, moves


def act1():
    print("=" * 84)
    print("幕一 Schelling 隔离:温和偏好滚成完全隔离"
          f"({SIDE}×{SIDE} 网格,两类各 30%、空 40%,{RUNS} 游程/档)")
    print("=" * 84)
    out = {}
    for t in (0.3, 0.7):
        stats = [run_schelling(random.Random(SEED_BASE + int(t * 100) * RUNS + k), t)
                 for k in range(RUNS)]
        init_same = sum(s[0] for s in stats) / RUNS
        init_unsat = sum(s[1] for s in stats) / RUNS
        fin_same = sum(s[2] for s in stats) / RUNS
        conv = sum(1 for s in stats if s[3] and s[4])
        rounds = sum(s[3] for s in stats) / RUNS
        moves = sum(s[5] for s in stats) / RUNS
        out[t] = dict(init_same=init_same, init_unsat=init_unsat,
                      fin_same=fin_same, conv=conv, rounds=rounds, moves=moves)
        print(f"\n阈值 t={t:.1f}  {'(温和偏好:只想至少三成邻居同类)' if t < 0.5 else '(强偏好:要求至少七成邻居同类)'}")
        print(f"    初始隔离度(平均同类邻居占比):{init_same:.4f}(随机混合的理论值 0.5)")
        print(f"    初始不满意居民占比:{init_unsat:.1%}")
        print(f"    终态隔离度:{fin_same:.4f}")
        print(f"    收敛游程:{conv}/{RUNS}(平均轮数 {rounds:.0f},上限 300)")
        print(f"    平均迁移人次:{moves:.0f}")
    g03, g07 = out[0.3], out[0.7]
    print("\n读数:")
    print(f"  · t=0.3:居民只想「同类邻居至少三成」——比随机混合(0.5)还低的要求,")
    print(f"    终态隔离度却升到 {g03['fin_same']:.2f}(是偏好需求的 "
          f"{g03['fin_same'] / 0.3:.1f} 倍):温和偏好被动力学滚成接近完全的隔离")
    print(f"  · t=0.7:初始 {g07['init_unsat']:.0%} 居民不满意(大面积),迁移人次 "
          f"{g07['moves']:.0f} 是 t=0.3 档({g03['moves']:.0f})的 "
          f"{g07['moves'] / g03['moves']:.1f} 倍,剧烈搅动")
    print(f"  · 镜像检验:偏好从 0.3 提到 0.7(+0.4),隔离度只从 {g03['fin_same']:.2f}"
          f" 到 {g07['fin_same']:.2f}(+{g07['fin_same'] - g03['fin_same']:.2f}),")
    print("    代价却是迁移×8——偏好-隔离的映射严重次线性:隔离的大头在温和档就被")
    print("    动力学付清,强偏好只买到边际增量")
    print(f"  · 如实标注:本参数域(30/30/40、随机迁入)两档均收敛({g03['conv']}/{RUNS}、"
          f"{g07['conv']}/{RUNS}),「高阈值震荡不收敛/隔离反降」见于空位更少或")
    print("    群体不对称的参数域,这里不出现——结论以实测为准")
    print("  · 隔离不是偏好的镜像(从偏好读不出隔离水平,从隔离也读不回偏好强度),")
    print("    是局部迁移规则的动力学产物——微观动机与宏观格局之间隔着一整台机器")

    # 断言 1:微观-宏观断裂
    assert 0.44 < g03["init_same"] < 0.56, "初始随机格局的隔离度应约 0.5"
    assert g03["fin_same"] > 0.7, f"t=0.3 终态隔离度应>0.7,实测 {g03['fin_same']:.4f}"
    assert g03["fin_same"] - g03["init_same"] > 0.2, "温和偏好应显著放大隔离"
    assert g07["init_unsat"] > 0.6, f"t=0.7 初始不满意占比应大面积,实测 {g07['init_unsat']:.2f}"
    assert g07["moves"] > 3 * g03["moves"], (
        f"t=0.7 的迁移应数倍于 t=0.3,实测 {g07['moves']:.0f} vs {g03['moves']:.0f}")
    assert (g07["fin_same"] - g03["fin_same"]) < 0.7 - 0.3, (
        "隔离度增幅应远小于偏好增幅(次线性):实测 "
        f"{g07['fin_same'] - g03['fin_same']:.4f} vs +0.4")
    assert g03["conv"] == RUNS, "t=0.3 档应稳定收敛"
    print(f"\n✓ 幕一断言通过:t=0.3 终态隔离度 {g03['fin_same']:.2f}>0.7(初始 "
          f"{g03['init_same']:.2f},偏好需求仅 0.3);偏好+0.4 只买到隔离+"
          f"{g07['fin_same'] - g03['fin_same']:.2f},迁移却×"
          f"{g07['moves'] / g03['moves']:.1f}——隔离是动力学的产物,不是偏好的镜像")
    return out


# ==================== 幕二:WS 小世界交叉带 ====================

def ws_graph(n, k, p, rng):
    """Watts-Strogatz:环格起(每点连最近 k/2×2 个),每条顺时针边以概率 p 重连。"""
    half = k // 2
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(1, half + 1):
            t = (i + j) % n
            adj[i].add(t)
            adj[t].add(i)
    if p <= 0:
        return adj
    for i in range(n):
        for j in range(1, half + 1):
            if rng.random() < p:
                old = (i + j) % n
                if old not in adj[i]:        # 该边已被本方向重连(保险)
                    continue
                adj[i].discard(old)
                adj[old].discard(i)
                while True:                  # 新端点:非自连、非重边
                    t2 = rng.randrange(n)
                    if t2 != i and t2 not in adj[i]:
                        break
                adj[i].add(t2)
                adj[t2].add(i)
    return adj


def avg_path_length(adj, sources):
    """采样源的 BFS 平均最短路(无向连通图)。"""
    total = pairs = 0
    for s in sources:
        dist = {s: 0}
        frontier = [s]
        d = 0
        while frontier:
            d += 1
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    if v not in dist:
                        dist[v] = d
                        nxt.append(v)
            frontier = nxt
        total += sum(dist.values())
        pairs += len(dist) - 1
    return total / pairs


def clustering(adj):
    """平均局部聚类系数:C_i=邻居对中互连比例。"""
    cs = []
    for nbrs in adj:
        d = len(nbrs)
        if d < 2:
            cs.append(0.0)
            continue
        nl = list(nbrs)
        links = 0
        for a in range(len(nl)):
            for b in range(a + 1, len(nl)):
                if nl[b] in adj[nl[a]]:
                    links += 1
        cs.append(2 * links / (d * (d - 1)))
    return sum(cs) / len(cs)


def act2():
    print("\n" + "=" * 84)
    print("幕二 WS 小世界交叉带(n=1000、k=10 环格,rewiring 概率 p 对数扫描)")
    print("=" * 84)
    n, k = 1000, 10
    sources = list(range(0, n, 4))           # 250 个采样源(确定性)
    rng0 = random.Random(SEED_BASE + 1)
    ring = ws_graph(n, k, 0.0, rng0)
    L0 = avg_path_length(ring, sources)
    C0 = clustering(ring)
    print(f"\n参照(p=0 规则环格):L(0)={L0:.2f},C(0)={C0:.4f}")
    ps = [1e-4, 1e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 5e-1, 1.0]
    rows = []
    print(f"\n{'p':>8} {'L(p)':>7} {'L/L0':>6} {'C(p)':>7} {'C/C0':>6}")
    for idx, p in enumerate(ps):
        adj = ws_graph(n, k, p, random.Random(SEED_BASE + 100 + idx))
        L = avg_path_length(adj, sources)
        C = clustering(adj)
        rows.append((p, L, C))
        print(f"{p:>8.0e} {L:>7.2f} {L / L0:>6.3f} {C:>7.4f} {C / C0:>6.3f}")
    cross = [(p, L, C) for (p, L, C) in rows
             if 0.01 <= p <= 0.1 and L / L0 < 0.5 and C / C0 > 0.5]
    p_star, L_star, C_star = cross[0]
    print("\n读数:")
    print(f"  · p={p_star:g} 一档:L/L0={L_star / L0:.3f}(距离砍掉一大半),"
          f"C/C0={C_star / C0:.3f}(朋友团的圈子几乎不破)")
    print("  · 重连边只有 n×k/2×p=" + f"{int(n * k / 2 * p_star)} 条"
          f"(占 {p_star:.0%})——少数长程捷径买走了大部分全局距离")
    print("  · 两指标走的是两条时间尺度:L 对 p 极敏感(捷径是全局资产),")
    print("    C 对 p 缓慢衰减(圈子是局部资产)——交叉带=小世界")

    # 断言 2:交叉带存在
    assert L0 > 20, f"规则环格平均路径应很长,实测 {L0:.2f}"
    assert C0 > 0.4, f"规则环格聚类应高,实测 {C0:.4f}"
    assert cross, "应存在 p∈[0.01,0.1] 使 L 比减半而 C 保持过半"
    assert any(L / L0 < 0.5 for (p, L, C) in rows if p >= 0.1), "大 p 下 L 应进一步走低"
    assert rows[0][2] / C0 > 0.95, "p=1e-4 时 C 应几乎不动"
    print(f"\n✓ 幕二断言通过:p={p_star:g} 处 L/L0={L_star / L0:.3f}<0.5 且 "
          f"C/C0={C_star / C0:.3f}>0.5——少数捷径买走大部分距离,圈子几乎不破")
    return L0, C0, rows


# ==================== 幕三:BA 优先连接的枢纽性 ====================

def ba_degrees(n, m, rng):
    """Barabási-Albert:自 m+1 点完全图起逐点加入,每点 m 条偏好连接边。
    端点池(stubs)按度数重复出现=优先连接权重;返回度序列与边数。"""
    m0 = m + 1
    deg = [0] * n
    stubs = []
    edges = 0
    for i in range(m0):
        for j in range(i + 1, m0):
            deg[i] += 1
            deg[j] += 1
            stubs.extend((i, j))
            edges += 1
    for v in range(m0, n):
        chosen = set()
        while len(chosen) < m:
            u = stubs[rng.randrange(len(stubs))]
            chosen.add(u)
        for u in chosen:
            deg[v] += 1
            deg[u] += 1
            stubs.extend((v, u))
            edges += 1
    return deg, edges


def er_degrees_same_edges(n, target_edges, rng):
    """G(n,M) 随机图:与 BA 完全同边数,做零模型对照。"""
    adj = [set() for _ in range(n)]
    placed = 0
    while placed < target_edges:
        i = rng.randrange(n)
        j = rng.randrange(n)
        if i != j and j not in adj[i]:
            adj[i].add(j)
            adj[j].add(i)
            placed += 1
    return [len(a) for a in adj]


def fit_loglog_cum(deg, n, min_count=15, k_lo=3):
    """累积度分布 P(K≥k) 的 log-log 最小二乘拟合(计数≥min_count 的段)。"""
    counts = {}
    for d in deg:
        counts[d] = counts.get(d, 0) + 1
    kmax = max(counts)
    cum = {}
    run = 0
    for k in range(kmax, 0, -1):
        run += counts.get(k, 0)
        cum[k] = run
    ks = [k for k in range(k_lo, kmax + 1) if cum[k] >= min_count]
    xs = [math.log(k) for k in ks]
    ys = [math.log(cum[k] / n) for k in ks]
    nn = len(xs)
    mx = sum(xs) / nn
    my = sum(ys) / nn
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot
    return slope, r2, ks[0], ks[-1]


def act3():
    print("\n" + "=" * 84)
    print("幕三 BA 优先连接的枢纽性(n=2000、m=2)vs 同边数 ER 零模型")
    print("=" * 84)
    n, m = 2000, 2
    deg_ba, E = ba_degrees(n, m, random.Random(SEED_BASE + 200))
    deg_er = er_degrees_same_edges(n, E, random.Random(SEED_BASE + 201))
    mean_ba = sum(deg_ba) / n
    mean_er = sum(deg_er) / n
    slope, r2, k_lo, k_hi = fit_loglog_cum(deg_ba, n)
    print(f"\nBA 生长网络:n={n},m={m},边数 {E},平均度 {mean_ba:.3f}")
    print(f"  累积度分布 P(K≥k) 的 log-log 拟合(段 k∈[{k_lo},{k_hi}],"
          f"计数≥15):斜率 {slope:.3f},R²={r2:.5f}")
    print(f"  (BA 理论:度分布幂律 γ=3 → 累积分布斜率约 −(γ−1)=−2)")
    print(f"\nER 随机网络(同 {E} 条边):平均度 {mean_er:.3f},"
          f"最大度 {max(deg_er)}")
    print(f"BA 最大度 {max(deg_ba)} = ER 的 {max(deg_ba) / max(deg_er):.1f} 倍")
    hub_tail = sum(1 for d in deg_ba if d >= 30) / n
    er_tail = sum(1 for d in deg_er if d >= 30) / n
    print(f"高度尾 P(K≥30):BA {hub_tail:.2%} vs ER {er_tail:.2%}"
          f"(ER 全体挤在均值附近,几乎没有枢纽)")
    print("\n读数:")
    print("  · 两个网络边数完全相同(平均度都≈4):差别只在「怎么长」——")
    print("    ER 把边均匀撒,度分布近似泊松,尾部指数式死掉;BA 新点")
    print("    按度数比例连旧点,尾部幂律式活着,少数枢纽吃掉大量连线")
    print("  · 社会含义:关系网络里的「大人物」不是统计偶然的离群点,")
    print("    是「富者愈富」生长机制的结构必然——换机制,同样的连线数,")
    print("    枢纽消失(ER 对照组就是反事实世界)")

    # 断言 3:枢纽性
    assert abs(mean_ba - mean_er) < 0.05, "两网平均度应几乎相同"
    assert r2 > 0.98, f"BA 累积度分布 log-log 线性拟合 R² 应>0.98,实测 {r2:.5f}"
    assert -2.6 < slope < -1.5, f"累积分布斜率应近 −2(γ≈3),实测 {slope:.3f}"
    assert max(deg_ba) > 3 * max(deg_er), (
        f"BA 最大度应远大于 ER,实测 {max(deg_ba)} vs {max(deg_er)}")
    assert hub_tail > 10 * max(er_tail, 1 / n), "BA 高度尾应比 ER 厚重"
    print(f"\n✓ 幕三断言通过:R²={r2:.5f}>0.98(斜率 {slope:.2f},γ≈3);"
          f"最大度 BA {max(deg_ba)} vs ER {max(deg_er)}"
          f"({max(deg_ba) / max(deg_er):.1f} 倍)——生长机制决定有没有枢纽")


def main():
    act1()
    act2()
    act3()
    print("\n" + "=" * 84)
    print("总断言收口:")
    print("  ① Schelling 微观-宏观断裂:t=0.3 的温和偏好(初始隔离度≈0.5)")
    print("     终态滚成 >0.7 的隔离;t=0.7 大面积不满意、迁移×8,偏好+0.4 只买到")
    print("     隔离+0.23(次线性,如实标注本域两档均收敛)——隔离不是偏好的镜像,")
    print("     是动力学的产物")
    print("  ② WS 小世界交叉带:p≈0.01-0.1 一档,极少捷径使 L/L0<0.5 而 C/C0>0.5")
    print("     ——少数捷径买走大部分距离,朋友团的圈子几乎不破")
    print("  ③ BA 枢纽性:同边数下累积度分布 log-log 线性 R²>0.98(幂律尾),")
    print("     ER 零模型最大度远小——大人物是机制产物,不是统计偶然")
    print("✓ 全部自验证通过")


if __name__ == "__main__":
    main()
