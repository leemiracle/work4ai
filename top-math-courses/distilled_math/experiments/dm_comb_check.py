#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_comb_check.py — 蒸馏卡 DM-COMB-01（组合与图论）的 L1 机器断言
对应卡：../DM-COMB-01-组合与图论.md §4（编号 C1a-C12 一一对应）
断言计数：13 组（若干组含子断言；C12 复验项目 C1 猜想）
运行方式：python3 dm_comb_check.py   （依赖 numpy；MC/随机图 seed 固定）
铁律：浮点断言带容差；谱计算用 eigvalsh。
"""
import math
import itertools
import numpy as np

PASS, TOTAL = 0, 0

def check(name, cond):
    global PASS, TOTAL
    TOTAL += 1
    ok = bool(cond)
    PASS += ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")

rng = np.random.default_rng(42)

def edges_of(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]

def tri_masks(n):
    """每个三角形的 3-边位掩码。"""
    E = edges_of(n)
    idx = {e: k for k, e in enumerate(E)}
    return [ (1 << idx[(a, b)]) | (1 << idx[(a, c)]) | (1 << idx[(b, c)])
             for a, b, c in itertools.combinations(range(n), 3) ]

def adj_matrix(n, edge_set):
    A = np.zeros((n, n))
    for i, j in edge_set:
        A[i, j] = A[j, i] = 1
    return A

def spectral(A):
    ev = np.linalg.eigvalsh(A)
    return np.sort(ev)

def n_components(A):
    n = len(A); seen = [False] * n; c = 0
    for s in range(n):
        if seen[s]:
            continue
        c += 1; stack = [s]; seen[s] = True
        while stack:
            v = stack.pop()
            for u in range(n):
                if A[v, u] and not seen[u]:
                    seen[u] = True; stack.append(u)
    return c

print("== DM-COMB-01 组合与图论 · L1 断言 ==")

# ---------- C1a R(3,3)=6 上界：穷举 K6 全部 2^15 染色，每种含单色三角形 ----------
tris6 = tri_masks(6); full6 = (1 << 15) - 1
n_mono = 0
for m in range(1 << 15):
    found = any(((m & t) == t) or ((m & t) == 0) for t in tris6)
    n_mono += found
check("C1a R(3,3)≤6：穷举 %d/32768 个 K₆ 染色全部含单色三角形" % n_mono, n_mono == 32768)

# ---------- C1b K5 逃生染色：红 C5 + 蓝补 C5 无单色三角形 ----------
E5 = edges_of(5); idx5 = {e: k for k, e in enumerate(E5)}
c5 = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
red = sum(1 << idx5[(min(e), max(e))] for e in c5)
tris5 = tri_masks(5)
no_mono = all(((red & t) != t) and ((red & t) != 0) for t in tris5)
check("C1b K5 反例：红=C₅、蓝=补集，10 个三角形均非单色（R(3,3)>5）", no_mono)

# ---------- C2 R(2,3)=3：穷举 K3 全部 8 染色均含红边或蓝三角 ----------
cnt3 = 0
for m in range(8):
    has_red_edge = any((m >> k) & 1 for k in range(3))
    all_blue_tri = (m == 0)
    cnt3 += (has_red_edge or all_blue_tri)
check("C2 R(2,3)=3：穷举 %d/8 个 K₃ 染色均含红 K₂ 或蓝 K₃" % cnt3, cnt3 == 8)

# ---------- C3 概率方法第一矩：k=5 时 n=11 可证 / n=12 失效 ----------
for_n11 = math.comb(11, 5) * 2.0 ** (1 - math.comb(5, 2))
for_n12 = math.comb(12, 5) * 2.0 ** (1 - math.comb(5, 2))
check("C3 第一矩：C(11,5)·2⁻⁹=%.4f<1（证 R(5,5)>11）但 C(12,5)·2⁻⁹=%.4f>1（n=12 失效）"
      % (for_n11, for_n12), for_n11 < 1 and for_n12 > 1)

# ---------- C4 构造性见证：随机 G(11,1/2) 以正概率同时无 K5 且无独立 5 ----------
subs5 = [sum(1 << v for v in S) for S in itertools.combinations(range(11), 5)]
def mono_k5_free(am):                                     # am: 每点邻居位掩码列表
    for S in subs5:
        verts = [v for v in range(11) if (S >> v) & 1]
        e = sum(bin(am[v] & S).count("1") for v in verts) // 2
        if e == 10 or e == 0:
            return False
    return True
n_trial, n_hit = 1500, 0
for _ in range(n_trial):
    am = []
    U = rng.integers(0, 1 << 11, size=(11, 11))
    A = (U < (1 << 10)).astype(int); A = np.triu(A, 1)
    for i in range(11):
        m = 0
        for j in range(11):
            if A[min(i, j), max(i, j)]:
                m |= 1 << j
        am.append(m)
    n_hit += mono_k5_free(am)
freq = n_hit / n_trial
check("C4 见证频率：%.4f > 0.06（联合界保证 ≥1−0.902=0.098；存在性→采样可得）" % freq, freq > 0.06)

# ---------- C5 Mantel n=5：7 边必有三角形；K_{2,3} 6 边无三角形 ----------
E5b = edges_of(5)
n7_with_tri = 0
for eidx in itertools.combinations(range(10), 7):
    m = sum(1 << k for k in eidx)
    n7_with_tri += any((m & t) == t for t in tris5)
K23 = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)]
m23 = sum(1 << idx5[(min(e), max(e))] for e in K23)
k23_clean = all((m23 & t) != t for t in tris5)
check("C5 Mantel：%d/120 个 7-边 K₅ 子图含三角形；K_{2,3} 6 边无三角形（floor(n²/4)=6）"
      % n7_with_tri, n7_with_tri == 120 and k23_clean)

# ---------- C6 度序列非唯一：(2,2,2,2,2,2) 的 C6 与 2×C3 双实现 ----------
C6 = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
twoC3 = [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]
A1, A2 = adj_matrix(6, C6), adj_matrix(6, twoC3)
deg_ok = np.allclose(A1.sum(1), 2) and np.allclose(A2.sum(1), 2)
comp_ok = (n_components(A1), n_components(A2)) == (1, 2)
check("C6 度序列：C6 与 2×C₃ 度均全 2；连通分量 1 vs 2（同度序列不同构）", deg_ok and comp_ok)

# ---------- C7 二部⟺谱对称；P2 的 A 无 0 特征值（A≠L 坑） ----------
ev_C4 = spectral(adj_matrix(4, [(0, 1), (1, 2), (2, 3), (3, 0)]))
ev_tri = spectral(adj_matrix(3, [(0, 1), (1, 2), (0, 2)]))
ev_P2 = spectral(np.array([[0.0, 1.0], [1.0, 0.0]]))
L_P2 = np.array([[1.0, -1.0], [-1.0, 1.0]])
ev_L_P2 = spectral(L_P2)
check("C7 谱对称：C₄ λ=[%.0f,%.0f,%.0f,%.0f] 对称=二部；三角形 [%.0f,%.1f,%.1f] 不对称；"
      "P₂ 的 A 谱=[%.0f,%.0f] 无 0，而 L 谱=[%.0f,%.0f] 含一个 0（0 属于 L）"
      % (*ev_C4, *ev_tri, *ev_P2, *ev_L_P2),
      abs(ev_C4[0] + ev_C4[3]) < 1e-9 and abs(ev_tri[0] + ev_tri[-1]) > 1e-9
      and abs(ev_P2[0]) > 1e-9 and abs(ev_L_P2[0]) < 1e-9)

# ---------- C8 共谱对 K_{1,4} vs C4∪K1：A 谱同、L 的 0 重数不同 ----------
star = adj_matrix(5, [(0, 1), (0, 2), (0, 3), (0, 4)])
c4k1 = adj_matrix(5, [(0, 1), (1, 2), (2, 3), (3, 0)])
evA_s, evA_c = spectral(star), spectral(c4k1)
Lam = lambda A: spectral(np.diag(A.sum(1)) - A)
evL_s, evL_c = Lam(star), Lam(c4k1)
zL = lambda ev: int(np.sum(np.abs(ev) < 1e-8))
check("C8 共谱对：A 谱一致 %s=%s；L 的 0 重数 %d vs %d；连通分量 %d vs %d（邻接谱不决定结构）"
      % (np.round(evA_s, 6).tolist(), np.round(evA_c, 6).tolist(), zL(evL_s), zL(evL_c),
         n_components(star), n_components(c4k1)),
      np.allclose(evA_s, evA_c, atol=1e-9) and zL(evL_s) == 1 and zL(evL_c) == 2
      and n_components(star) == 1 and n_components(c4k1) == 2)

# ---------- C9 星 S10：λ1=√(n−1)=3 精确；三角形 |λmin|≠λ1 ----------
S10 = adj_matrix(10, [(0, k) for k in range(1, 10)])
ev_s10 = spectral(S10)
check("C9 星 S₁₀：λ₁=%.10f=√9（|Δ|<1e−8）；三角形 |λ_min|=1<2=λ₁（|λ_min|=λ₁ 仅二部正则）"
      % ev_s10[-1],
      abs(ev_s10[-1] - 3.0) < 1e-8 and abs(ev_s10[0] + 3.0) < 1e-8
      and np.sum(np.abs(ev_s10) < 1e-8) == 8 and abs(ev_tri[0]) + 1e-9 < ev_tri[2])

# ---------- C10 Cheeger 双侧：环（下界松）vs 哑铃（下界紧） ----------
def norm_lap(A):
    d = A.sum(1)
    Dm = np.diag(1.0 / np.sqrt(d))
    return np.eye(len(A)) - Dm @ A @ Dm
# 环 C50（2-正则）：h=2/n；λ1=2sin²(π/n)
A_cyc = adj_matrix(50, [(i, (i + 1) % 50) for i in range(50)])
lam1_cyc = spectral(norm_lap(A_cyc))[1]
h_cyc = 2.0 / 50
ok_cyc = (lam1_cyc / 2 <= h_cyc + 1e-12) and (h_cyc <= math.sqrt(2 * lam1_cyc) + 1e-12)
# 哑铃：两个 K25 + 一条桥（点 24-25）；h = 1/vol(单球)=1/601
A_db = adj_matrix(50, [(i, j) for i, j in itertools.combinations(range(25), 2)]
                  + [(i, j) for i, j in itertools.combinations(range(25, 50), 2)]
                  + [(24, 25)])
lam1_db = spectral(norm_lap(A_db))[1]
h_db = 1.0 / 601.0
ok_db = (lam1_db / 2 <= h_db + 1e-12) and (h_db <= math.sqrt(2 * lam1_db) + 1e-9)
sl_lo_cyc, sl_lo_db = lam1_cyc / (h_cyc ** 2 / 2), lam1_db / (h_db ** 2 / 2)   # 下界 λ₁≥h²/2 的松弛倍数
sl_hi_cyc, sl_hi_db = (2 * h_cyc) / lam1_cyc, (2 * h_db) / lam1_db             # 上界 λ₁≤2h 的松弛倍数
check("C10 Cheeger：环 λ₁=%.5f、哑铃 λ₁=%.2e 均满足 λ₁/2≤h≤√(2λ₁)；紧性两侧分离——下界松弛 环 %.1f vs 哑铃 %.0f，上界松弛 环 %.1f vs 哑铃 %.2f"
      % (lam1_cyc, lam1_db, sl_lo_cyc, sl_lo_db, sl_hi_cyc, sl_hi_db),
      ok_cyc and ok_db and sl_lo_cyc < 20 and sl_lo_db > 100 and sl_hi_db < 1.5 and sl_hi_cyc > 5)

# ---------- C11 Matrix–Tree：K5 生成树数 = 5³ = 125（整数余子式） ----------
A_K5 = adj_matrix(5, edges_of(5))
L_K5 = (np.diag(A_K5.sum(1)) - A_K5).astype(np.int64)
tau = int(round(np.linalg.det(L_K5[:4, :4].astype(float))))
check("C11 Matrix–Tree：det L 的 4×4 余子式 = %d = 5³ = 125（Cayley）" % tau, tau == 125)

# ---------- C12 C1 猜想复验：E=Σ|λᵢ| ≥ n+λ₁−α（Kₙ 取等、星族严格强） ----------
def alpha_bruteforce(A):
    n = len(A)
    best = 0
    for S in range(1 << n):
        ok = True
        verts = [v for v in range(n) if (S >> v) & 1]
        for a, b in itertools.combinations(verts, 2):
            if A[a, b]:
                ok = False; break
        if ok:
            best = max(best, len(verts))
    return best
def energy(A):
    return float(np.abs(spectral(A)).sum())
viol, eq_K, strict_star = 0, True, True
graphs = []
graphs += [("K%d" % n, adj_matrix(n, edges_of(n))) for n in range(2, 10)]
graphs += [("S%d" % n, adj_matrix(n, [(0, k) for k in range(1, n)])) for n in range(3, 13)]
graphs += [("P%d" % n, adj_matrix(n, [(i, i + 1) for i in range(n - 1)])) for n in range(2, 13)]
graphs += [("C%d" % n, adj_matrix(n, [(i, (i + 1) % n) for i in range(n)])) for n in range(3, 13)]
graphs += [("K%d,%d" % (m, m), adj_matrix(2 * m, [(a, b + m) for a in range(m) for b in range(m)]))
           for m in range(2, 7)]
for _ in range(300):
    n = 9
    U = rng.integers(0, 1 << 9, size=(9, 9))
    A = ((U < (1 << 8)).astype(int)); A = np.triu(A, 1)
    graphs.append(("rand9", adj_matrix(n, [(i, j) for i in range(9) for j in range(i + 1, 9) if A[i, j]])))
for name, A in graphs:
    n = len(A)
    lam1 = float(np.abs(spectral(A)).max())
    gap = energy(A) - (n + lam1 - alpha_bruteforce(A))
    viol += (gap < -1e-8)
    if name.startswith("K") and name[1:].isdigit():
        eq_K &= abs(gap) < 1e-8
    if name.startswith("S") and name[1:].isdigit() and int(name[1:]) >= 4:
        strict_star &= gap > 0.5
check("C12 C1 复验：%d 张图（K/星/路/圈/完全二部+300 随机 n≤9）E≥n+λ₁−α 全部成立（viol=%d）；"
      "Kₙ 取等、星族严格强（gap>0.5）" % (len(graphs), viol),
      viol == 0 and eq_K and strict_star)

print(f"\n结果：{PASS}/{TOTAL} 断言通过" + ("  [ALL PASS]" if PASS == TOTAL else "  [HAS FAIL]"))
raise SystemExit(0 if PASS == TOTAL else 1)
