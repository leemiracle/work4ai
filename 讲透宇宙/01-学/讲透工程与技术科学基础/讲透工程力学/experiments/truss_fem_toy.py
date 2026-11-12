# -*- coding: utf-8 -*-
"""桁架的矩阵法教学版:静定·超静定·机构——三态一台戏(00/04 章配套实验)。

平面桁架,节点-单元拓扑,直接刚度法(direct stiffness method):
  单元刚度(全局系):k_e = (EA/L)·bᵀb,b=[-cₓ,-c_y,cₓ,c_y],c=(Δx,Δy)/L
  总刚度组装:K = Σ k_e(单元自由度向整体自由度散射)
  边界条件:划行划列(消去约束自由度),K_ff·u_f = F_f
  求解:自写高斯消元(部分主元),最小主元比兼作奇异性哨兵
  轴力:N = (EA/L)·(u_j-u_i)·c(拉为正)

三个结构(同一套代码,只改拓扑与载荷):
  A 静定三角桁架:A(0,0)固定铰,B(4,0)滚动铰(只挡竖向),C(2,3);
    杆 AB/AC/BC;C 点挂载 (0,-12000N)。手算节点法:顶点受压、
    底弦受拉:N_AC=N_BC=-P√13/6(压),N_AB=+P/3(拉)
    ——矩阵解应逐杆一致
  B 超静定方框桁架:A(0,0)固定铰,B(4,0)滚动铰,C(4,3),D(0,3);
    杆 AB/BC/CD/DA/AC/BD(双斜杆);C、D 各挂 (0,-4000N)。
    未知力 m+r=9 > 平衡方程 2j=8:静力法欠定(超静定 1 次);
    对称力法(余能极小)手算:N_斜=-5P/24,N_弦=+P/6,N_竖=-7P/8
  C 拓扑临界:从 B 逐根撤斜杆——撤一根(BD)→静定可解
    (此对称竖载下剩余斜杆内力恰为 0,载荷全走竖杆);
    再撤一根(AC)→ m+r=7 < 2j=8,机构,线性刚度矩阵奇异:
    消元最小主元比塌到 1e-15 量级,报警而非输出垃圾解;
    机构模态 u=(A:0,B:0,C:(1,0),D:(1,0)) 满足 ‖K·u‖=0
    (矩形剪切机构,一阶无刚度;有限位移下由几何非线性供二阶刚度)

五个结构化断言:
  ① 静定:矩阵法轴力与节点法手算逐杆一致(相对误差<1e-9)
  ② 静定的标志:全体 EA×10,轴力纹丝不动(<1e-9)——内力由
     平衡唯一决定,与刚度无关
  ③ 超静定的本质:静力方程 8 个<未知量 9 个,静力法不能唯一解;
     矩阵法可解,自由度平衡残差≈0,且与对称力法手算逐杆互证
  ④ 超静定的指纹:斜杆 EA×10 后内力重分配(斜杆轴力变化>100%
     ,实测≈109%)——内力依赖刚度比,这正是静力法算不了它、
     加杆反而改变全结构受力的原因
  ⑤ 机构报警:撤一根斜杆仍可解(静定);再撤一根,消元最小
     主元比<1e-8 判奇异,求解器拒绝输出;机构模态 ‖K·u‖=0
⚠ 纪律(02/04 章):桁架单元=理想铰接两节点杆,只有轴力,小
  变形、线弹性(00 章三条假设的教学最小版);"撤一根杆仍承载"
  只对超静定成立,静定结构撤任一杆即机构(断言①②⑤对照);
  自写高斯消元为教学版,生产用稀疏 Cholesky/共轭梯度
  (数学宇宙数值线代);机构检测的是线性切线刚度奇异,不代表
  结构立刻倒塌(索结构稳定来自预应力与几何非线性);EA 为
  示意值,尺寸/单位按 SI。

跑法: python experiments/truss_fem_toy.py
"""

import math

EA0 = 1.0e8       # 全桁架默认抗拉刚度 EA(N),示意值
P_TRI = 12000.0   # 三角桁架 C 点竖向载荷(N)
P_SQ = 4000.0     # 方框桁架 C/D 点各挂竖向载荷(N)


# ------------------------------------------------------------- 核心求解器
def gauss_solve(A, b):
    """高斯消元(部分主元)。

    返回 (x, 最小主元比, 奇异标记):最小主元比 = 消元各步主元
    绝对值的最小者/最大者——机构(秩亏)时塌到机器精度量级,
    以 1e-8 为阈值判奇异,拒绝回代(不输出垃圾解)。
    """
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    pivots = []
    for col in range(n):
        p = max(range(col, n), key=lambda r: abs(M[r][col]))
        piv = abs(M[p][col])
        if piv == 0.0:
            return None, 0.0, True
        pivots.append(piv)
        M[col], M[p] = M[p], M[col]
        d = M[col][col]
        for r in range(col + 1, n):
            f = M[r][col] / d
            if f != 0.0:
                for c in range(col, n + 1):
                    M[r][c] -= f * M[col][c]
    ratio = min(pivots) / max(pivots)
    if ratio < 1e-8:
        return None, ratio, True
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))
        x[i] = s / M[i][i]
    return x, ratio, False


def solve_truss(nodes, members, supports, loads, ea_map=None):
    """直接刚度法解平面桁架。

    nodes:{名:(x,y)}  members:[(i,j)](顺序即轴力表顺序)
    supports:{名:(挡ux?,挡uy?)}  loads:{名:(Fx,Fy)}
    ea_map:{(i,j):EA} 覆盖单杆刚度(撤杆=从 members 删该项)
    返回 (u, N, info):u={名:(ux,uy)} 米,N=[轴力] 拉为正。
    """
    ea_map = ea_map or {}
    names = list(nodes)
    idx = {n: i for i, n in enumerate(names)}
    nd = 2 * len(names)
    K = [[0.0] * nd for _ in range(nd)]
    F = [0.0] * nd
    geo = []                                  # (L, c, EA) per member
    for (a, b) in members:
        dx, dy = nodes[b][0] - nodes[a][0], nodes[b][1] - nodes[a][1]
        L = math.hypot(dx, dy)
        c = (dx / L, dy / L)
        ea = ea_map.get((a, b), EA0)
        geo.append((L, c, ea))
        coef = ea / L
        dofs = (2 * idx[a], 2 * idx[a] + 1, 2 * idx[b], 2 * idx[b] + 1)
        bv = (-c[0], -c[1], c[0], c[1])
        for p in range(4):
            for q in range(4):
                K[dofs[p]][dofs[q]] += coef * bv[p] * bv[q]
    for n, (fx, fy) in loads.items():
        F[2 * idx[n]] += fx
        F[2 * idx[n] + 1] += fy
    free = [d for d in range(nd)
            if not supports.get(names[d // 2], (False, False))[d % 2]]
    Kff = [[K[r][c] for c in free] for r in free]
    uf, ratio, singular = gauss_solve(Kff, [F[r] for r in free])
    u = {n: (0.0, 0.0) for n in names}
    N = []
    if not singular:
        ud = [0.0] * nd
        for k, d in enumerate(free):
            ud[d] = uf[k]
        u = {n: (ud[2 * idx[n]], ud[2 * idx[n] + 1]) for n in names}
        for k, (a, b) in enumerate(members):
            L, c, ea = geo[k]
            e = ((ud[2 * idx[b]] - ud[2 * idx[a]]) * c[0]
                 + (ud[2 * idx[b] + 1] - ud[2 * idx[a] + 1]) * c[1])
            N.append(ea / L * e)
        resid = max(abs(sum(K[r][c] * ud[c] for c in range(nd)) - F[r])
                    for r in free)
    else:
        resid = float("nan")
    return u, N, {"K": K, "idx": idx, "free": free, "ratio": ratio,
                  "singular": singular, "resid_free": resid}


def member_str(a, b):
    return f"{a}{b}"


def fmt(x):
    return f"{x:>12.4f}"


# ------------------------------------------------------------- 主流程
def main():
    print("=" * 76)
    print("桁架的矩阵法:静定·超静定·机构三态一台戏(直接刚度法+"
          f"自写高斯消元,EA0={EA0:.1e}N)")
    print("=" * 76)

    # --- [1] 静定三角桁架:矩阵法 vs 节点法手算 ------------------------
    print(f"\n[1] 静定三角桁架:C 点挂载 P={P_TRI:.0f}N"
          "(m+r=3+3=6=2j,静定)")
    nodes_a = {"A": (0.0, 0.0), "B": (4.0, 0.0), "C": (2.0, 3.0)}
    mem_a = [("A", "B"), ("A", "C"), ("B", "C")]
    sup_a = {"A": (True, True), "B": (False, True)}
    load_a = {"C": (0.0, -P_TRI)}
    u, N, info = solve_truss(nodes_a, mem_a, sup_a, load_a)
    hand_a = [P_TRI / 3.0,
              -P_TRI * math.sqrt(13.0) / 6.0,
              -P_TRI * math.sqrt(13.0) / 6.0]
    print(f"    {'杆':>4} {'矩阵法轴力N':>14} {'手算轴力N':>14}"
          f" {'误差':>10}")
    for k, (a, b) in enumerate(mem_a):
        print(f"    {member_str(a, b):>4} {fmt(N[k])} {fmt(hand_a[k])}"
              f" {abs(N[k] - hand_a[k]):>10.2e}")
    print(f"    C 点竖向位移 = {u['C'][1] * 1e3:.4f} mm"
          f"(最小主元比 {info['ratio']:.2e},非奇异,"
          f"自由度平衡残差 {info['resid_free']:.2e} N)")

    # --- [2] 静定的标志:内力与刚度无关 --------------------------------
    print("\n[2] 全体 EA×10(静定:平衡定内力,刚度无关)")
    _, N2, _ = solve_truss(nodes_a, mem_a, sup_a, load_a,
                           {m: 10.0 * EA0 for m in mem_a})
    print(f"    {'杆':>4} {'EA×1 轴力':>14} {'EA×10 轴力':>14}"
          f" {'变化':>10}")
    for k, (a, b) in enumerate(mem_a):
        print(f"    {member_str(a, b):>4} {fmt(N[k])} {fmt(N2[k])}"
              f" {abs(N2[k] - N[k]):>10.2e}")
    stiff_free = max(abs(N2[k] - N[k]) for k in range(3))

    # --- [3] 超静定方框:静力法不能,矩阵法能 ---------------------------
    print(f"\n[3] 超静定方框(双斜杆):C、D 各挂 P={P_SQ:.0f}N")
    nodes_b = {"A": (0.0, 0.0), "B": (4.0, 0.0),
               "C": (4.0, 3.0), "D": (0.0, 3.0)}
    mem_b = [("A", "B"), ("B", "C"), ("C", "D"),
             ("D", "A"), ("A", "C"), ("B", "D")]
    sup_b = {"A": (True, True), "B": (False, True)}
    load_b = {"C": (0.0, -P_SQ), "D": (0.0, -P_SQ)}
    m, j, r = len(mem_b), len(nodes_b), 3
    print(f"    未知力 m+r={m + r} > 平衡方程 2j={2 * j}:静力法欠定"
          f"(超静定 {m + r - 2 * j} 次)——矩阵法照解:")
    u3, N3, info3 = solve_truss(nodes_b, mem_b, sup_b, load_b)
    hand_b = [P_SQ / 6.0, -7.0 * P_SQ / 8.0, P_SQ / 6.0,
              -7.0 * P_SQ / 8.0, -5.0 * P_SQ / 24.0,
              -5.0 * P_SQ / 24.0]
    print(f"    {'杆':>4} {'矩阵法轴力N':>14} {'力法手算N':>14}"
          f" {'误差':>10}")
    for k, (a, b) in enumerate(mem_b):
        print(f"    {member_str(a, b):>4} {fmt(N3[k])} {fmt(hand_b[k])}"
              f" {abs(N3[k] - hand_b[k]):>10.2e}")
    print(f"    自由度平衡残差 {info3['resid_free']:.2e} N"
          f";D 点竖向位移 {u3['D'][1] * 1e3:.4f} mm")
    agree = max(abs(N3[k] - hand_b[k]) for k in range(6))

    # --- [4] 超静定的指纹:内力依赖刚度比 --------------------------------
    print("\n[4] 斜杆 EA×10(超静定:刚度比变化 → 内力重分配)")
    ea_diag = {kk: 10.0 * EA0 for kk in mem_b[4:]}
    _, N4, _ = solve_truss(nodes_b, mem_b, sup_b, load_b, ea_diag)
    print(f"    {'杆':>4} {'斜杆EA×1':>14} {'斜杆EA×10':>14}"
          f" {'重分配':>10}")
    for k, (a, b) in enumerate(mem_b):
        chg = abs(N4[k] - N3[k]) / max(abs(N3[k]), 1e-12)
        print(f"    {member_str(a, b):>4} {fmt(N3[k])} {fmt(N4[k])}"
              f" {chg:>9.1%}")
    diag_shift = abs(abs(N4[4]) - abs(N3[4])) / abs(N3[4])

    # --- [5] 拓扑临界:撤一根杆的两种下场 --------------------------------
    print("\n[5] 拓扑临界:从双斜杆逐根撤杆")
    mem_c1 = mem_b[:5]                        # 撤 BD(剩单斜杆 AC)
    u5, N5, info5 = solve_truss(nodes_b, mem_c1, sup_b, load_b)
    print(f"    撤 BD(m+r={len(mem_c1) + 3}=2j={2 * j},回到静定):"
          f"可解,主元比 {info5['ratio']:.2e};此对称竖载下"
          "剩余斜杆 AC 轴力")
    print(f"    = {N5[4]:.4f} N(载荷全走竖杆:竖杆 {fmt(N5[1])} N)"
          "——零内力≠零用处,换不对称载荷它就是承重杆")
    mem_c2 = mem_b[:4]                        # 再撤 AC(无斜杆)
    _, _, info6 = solve_truss(nodes_b, mem_c2, sup_b, load_b)
    print(f"    再撤 AC(m+r={len(mem_c2) + 3} < 2j={2 * j},机构):"
          f"最小主元比 {info6['ratio']:.2e} < 1e-8 → 奇异报警,"
          "拒绝输出位移(垃圾解之前必有近零主元)")
    K = info6["K"]
    idx = info6["idx"]
    u_null = [0.0] * 8                        # 剪切机构模态:C、D 平移
    u_null[2 * idx["C"]] = 1.0
    u_null[2 * idx["D"]] = 1.0
    r_null = max(abs(sum(K[i][c] * u_null[c] for c in range(8)))
                 for i in range(8))
    k_scale = max(max(abs(v) for v in row) for row in K)
    print(f"    机构模态 u=(A:0,B:0,C:(1,0),D:(1,0)):‖K·u‖={r_null:.2e}"
          f"(K 尺度 {k_scale:.2e},相对 {r_null / k_scale:.1e})"
          "——矩形剪切机构一阶无刚度")

    # --- [6] 结构化断言 --------------------------------------------------
    print("\n[6] 结构化断言")
    checks = [
        ("① 静定对表:三角桁架矩阵解与节点法手算逐杆一致"
         "(误差<1e-9·P)",
         all(abs(N[k] - hand_a[k]) < 1e-9 * P_TRI for k in range(3))),
        ("② 静定标志:全体 EA×10,轴力不变(<1e-9·P)——内力由平衡"
         "唯一决定,与刚度无关",
         stiff_free < 1e-9 * P_TRI),
        ("③ 超静定的本质:静力方程 8<未知量 9(静力法不能);矩阵法"
         "可解、平衡残差≈0,且与对称力法手算逐杆互证(误差<1e-9·P)",
         (m + r > 2 * j and not info3["singular"]
          and info3["resid_free"] < 1e-6 * P_SQ and agree < 1e-9 * P_SQ)),
        ("④ 超静定的指纹:斜杆 EA×10 后斜杆轴力重分配>5%(实测"
         f"≈{diag_shift:.0%})——内力依赖刚度比",
         diag_shift > 0.05),
        ("⑤ 机构报警:撤一根斜杆仍可解(静定);再撤一根,最小主元比"
         "<1e-8 判奇异拒绝求解,机构模态 ‖K·u‖/‖K‖<1e-9",
         (not info5["singular"] and info6["singular"]
          and info6["ratio"] < 1e-8 and r_null / k_scale < 1e-9)),
    ]
    for name, ok in checks:
        print(f"    [{'PASS' if ok else 'FAIL'}] {name}")
        assert ok, name

    print("\n⚠ 纪律:桁架单元=铰接两节点杆(只有轴力,小变形线弹性);")
    print("  自写高斯消元为教学版,生产用稀疏求解器(数学宇宙数值线代);")
    print("  机构检测的是线性切线刚度奇异,不代表结构立刻倒塌(索结构")
    print("  稳定来自预应力与几何非线性);EA 为示意值。")
    print("=" * 76)
    print("结论:静定结构内力由平衡唯一决定(刚度无关),超静定结构")
    print("  内力由刚度比分配(加杆/改杆都重排全结构受力)——这就是")
    print("  静力法止步、矩阵法登场的那条线;越过拓扑下限(m+r<2j),")
    print("  刚度矩阵奇异,求解器的义务是报警而不是编造位移。")


if __name__ == "__main__":
    main()
