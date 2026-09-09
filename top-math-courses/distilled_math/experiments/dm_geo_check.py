#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_geo_check.py — 蒸馏卡 DM-GEO-01（几何与拓扑）的 L1 机器断言
对应卡：../DM-GEO-01-几何与拓扑.md §4（编号 G1-G14 一一对应，G1 拆 G1/G1b 两组）
断言计数：15 组（若干组含子断言）
运行方式：python3 dm_geo_check.py   （依赖 numpy + sympy）
铁律：浮点断言带容差；符号断言 simplify 后判等；网格积分容差放宽到 1e-3 量级并注明。
"""
import numpy as np
import sympy as sp

trapz = getattr(np, "trapezoid", None) or np.trapz

PASS, TOTAL = 0, 0

def check(name, cond):
    global PASS, TOTAL
    TOTAL += 1
    ok = bool(cond)
    PASS += ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")

print("== DM-GEO-01 几何与拓扑 · L1 断言 ==")

# ---------- G1 球面 Gauss 曲率 K=1/R²（第一/第二基本形式符号计算） ----------
th, ph = sp.symbols('th ph', positive=True)
def gauss_curvature(X, nrm):
    X1 = [sp.diff(X[i], th) for i in range(3)]
    X2 = [sp.diff(X[i], ph) for i in range(3)]
    dot = lambda a, b: sum(a[i]*b[i] for i in range(3))
    E, F, G = dot(X1, X1), dot(X1, X2), dot(X2, X2)
    X11 = [sp.diff(X[i], th, 2) for i in range(3)]
    X12 = [sp.diff(sp.diff(X[i], th), ph) for i in range(3)]
    X22 = [sp.diff(X[i], ph, 2) for i in range(3)]
    L, M, N = dot(X11, nrm), dot(X12, nrm), dot(X22, nrm)
    return sp.simplify((L*N - M**2) / (E*G - F**2))
Xs = sp.Matrix([sp.sin(th)*sp.cos(ph), sp.sin(th)*sp.sin(ph), sp.cos(th)])
Ks = gauss_curvature(list(Xs), list(Xs))            # 单位球法向 = 位置向量
check(f"G1 球面符号曲率 simplify → {Ks} = 1；R=2.5 数值 K≈0.16=1/R²",
      sp.simplify(Ks - 1) == 0)

def K_numeric_sphere(R):
    f = sp.lambdify((th, ph), sp.Matrix([R*sp.sin(th)*sp.cos(ph), R*sp.sin(th)*sp.sin(ph), R*sp.cos(th)]))
    return f
# 数值 R=2.5：直接用公式 EG-F² 与 LN-M² 的 lambdify 版本
Xv = sp.Matrix([sp.Symbol('R')*sp.sin(th)*sp.cos(ph), sp.Symbol('R')*sp.sin(th)*sp.sin(ph), sp.Symbol('R')*sp.cos(th)])
Rsym = sp.Symbol('R', positive=True)
K_R = gauss_curvature([Rsym*sp.sin(th)*sp.cos(ph), Rsym*sp.sin(th)*sp.sin(ph), Rsym*sp.cos(th)],
                      [sp.sin(th)*sp.cos(ph), sp.sin(th)*sp.sin(ph), sp.cos(th)])
K_num = float(sp.N(K_R.subs(Rsym, sp.Rational(5,2))))
check("G1b R=2.5 数值 K = 0.16 = 1/6.25（±1e-12）", abs(K_num - 0.16) < 1e-12)

# ---------- G2 柱面/平面 K=0（绝妙定理的等距见证：可展曲面） ----------
z = sp.symbols('z')
u, v = sp.symbols('u v', real=True)
def gauss_curvature_uv(X, nrm, s1, s2):
    X1 = [sp.diff(X[i], s1) for i in range(3)]
    X2 = [sp.diff(X[i], s2) for i in range(3)]
    dot = lambda a, b: sum(a[i]*b[i] for i in range(3))
    E, F, G = dot(X1, X1), dot(X1, X2), dot(X2, X2)
    X11 = [sp.diff(X[i], s1, 2) for i in range(3)]
    X12 = [sp.diff(sp.diff(X[i], s1), s2) for i in range(3)]
    X22 = [sp.diff(X[i], s2, 2) for i in range(3)]
    L, M, N = dot(X11, nrm), dot(X12, nrm), dot(X22, nrm)
    return sp.simplify((L*N - M**2) / (E*G - F**2))
Xc = [sp.cos(th), sp.sin(th), z]
nc = [sp.cos(th), sp.sin(th), 0]
Kc = gauss_curvature_uv(Xc, nc, th, z)
Xp = [u, v, 0]
Kp = gauss_curvature_uv(Xp, [0, 0, 1], u, v)
check(f"G2 柱面 K = {Kc} = 0（平面 K = {Kp} = 0）——柱面与平面等距、曲率相同（K 内在）",
      sp.simplify(Kc) == 0 and sp.simplify(Kp) == 0)

# ---------- G3 球面三角形（八分圆）：内角和 3π/2，Girard 面积 = 内角和 − π = π/2 ----------
def sphere_angle(A, B, C):
    tB = B - A*np.dot(A, B); tB /= np.linalg.norm(tB)
    tC = C - A*np.dot(A, C); tC /= np.linalg.norm(tC)
    return np.arccos(np.clip(np.dot(tB, tC), -1, 1))
e1, e2, e3 = np.eye(3)
ang_sum = sum([sphere_angle(e1, e2, e3), sphere_angle(e2, e3, e1), sphere_angle(e3, e1, e2)])
area3 = ang_sum - np.pi
check("G3 球面八分圆三角形：内角和 = 3π/2（每角 π/2）；Girard 面积 = π/2 = 4π/8（±1e-12）",
      abs(ang_sum - 1.5*np.pi) < 1e-12 and abs(area3 - np.pi/2) < 1e-12)

# ---------- G4 双曲半平面：Christoffel 符号 + 竖直测地线 + 竖直距离 ----------
xs_, ys_ = sp.symbols('x y', positive=True)
g = sp.diag(ys_**-2, ys_**-2); ginv = g.inv()
Gam = {}
for k in range(2):
    for i in range(2):
        for j in range(2):
            Gam[(k, i, j)] = sp.simplify(sp.Rational(1,2)*sum(ginv[k, l]*(sp.diff(g[j, l], (xs_, ys_)[i])
                             + sp.diff(g[i, l], (xs_, ys_)[j]) - sp.diff(g[i, j], (xs_, ys_)[l])) for l in range(2)))
ok4 = (sp.simplify(Gam[(0, 0, 1)] + 1/ys_) == 0 and sp.simplify(Gam[(0, 1, 0)] + 1/ys_) == 0
       and sp.simplify(Gam[(1, 0, 0)] - 1/ys_) == 0 and sp.simplify(Gam[(1, 1, 1)] + 1/ys_) == 0)
ts = np.linspace(0.1, 2.0, 50)                       # 曲线 x(t)=0, y(t)=e^t
resid = [abs(np.exp(t) + (-1.0/np.exp(t))*np.exp(2*t)) for t in ts]   # y''+Γ^y_{yy} y'²
dist4 = trapz(1.0/np.linspace(1, np.e, 200001), np.linspace(1, np.e, 200001))
check("G4 Poincaré 半平面：Γ^x_{xy}=Γ^y_{yy}=−1/y、Γ^y_{xx}=+1/y（符号验证）；竖直线 x=0,y=e^t 测地 ODE 残差 <1e-12；∫₁^e dy/y = 1（±1e-6）",
      ok4 and max(resid) < 1e-12 and abs(dist4 - 1.0) < 1e-6)

# ---------- G5 双曲三角形 Gauss–Bonnet：Σ内角 − 面积(∫y⁻²) = π ----------
def geodesic_arc(P, Q, n=4000):
    x1, y1 = P; x2, y2 = Q
    c = ((x1*x1 + y1*y1) - (x2*x2 + y2*y2)) / (2*(x1 - x2))
    r = np.hypot(x1 - c, y1)
    a1, a2 = np.arctan2(y1, x1 - c), np.arctan2(y2, x2 - c)
    d = a2 - a1
    while d > np.pi: d -= 2*np.pi
    while d < -np.pi: d += 2*np.pi
    th_ = a1 + d*np.linspace(0, 1, n)
    return np.column_stack([c + r*np.cos(th_), r*np.sin(th_)])
A5, B5, C5 = (-1.0, 1.0), (1.0, 1.0), (0.0, 3.0)
arcs = [geodesic_arc(A5, B5), geodesic_arc(B5, C5), geodesic_arc(C5, A5)]
pts = np.vstack(arcs)
keep = np.linalg.norm(np.roll(pts, -1, axis=0) - pts, axis=1) > 1e-12   # 去弧接头重复点
pts = pts[keep]
shoe = np.sum(pts[:,0]*np.roll(pts[:,1],-1) - np.roll(pts[:,0],-1)*pts[:,1])
if shoe < 0:                                        # 统一为 CCW
    pts = pts[::-1]
angles = []
for V_ in (A5, B5, C5):
    idx = int(np.argmin(np.sum((pts - np.array(V_))**2, axis=1)))
    tin = pts[idx] - pts[idx - 1]; tin /= np.linalg.norm(tin)
    tout = pts[(idx + 1) % len(pts)] - pts[idx]; tout /= np.linalg.norm(tout)
    turn = np.arctan2(tin[0]*tout[1] - tin[1]*tout[0], np.dot(tin, tout))
    if turn < 0: turn += 2*np.pi
    angles.append(np.pi - turn)
dy = np.roll(pts[:,1], -1) - pts[:,1]
area5 = np.sum(pts[:,0] / pts[:,1]**2 * dy)          # Green: ∮ x/y² dy = ∬ y⁻² dA（CCW）
check(f"G5 双曲三角形：Σ内角={sum(angles):.4f}，面积={area5:.4f}，GB 检验 |Σ角+面积−π|<2e-3（K=−1：内角和 <π，亏损=面积）",
      abs(sum(angles) + area5 - np.pi) < 2e-3 and sum(angles) < np.pi)

# ---------- G6 球面大圆=测地线（协变加速度=0），小圆≠ ----------
rng = np.random.default_rng(7)
Qm, _ = np.linalg.qr(rng.standard_normal((3, 3)))
u6, v6 = Qm[:, 0], Qm[:, 1]
t6 = np.linspace(0, 2*np.pi, 100)
xg = np.outer(u6, np.cos(t6)) + np.outer(v6, np.sin(t6))
xdd = -xg                                          # ẍ = −x（向心）
cov_acc = np.linalg.norm(xdd - (xdd * xg).sum(0) * xg, axis=0)   # 投影到切平面
th0 = np.pi/3
xs6 = np.array([np.sin(th0)*np.cos(t6), np.sin(th0)*np.sin(t6), np.cos(th0)*np.ones_like(t6)]).T
xdd6 = np.array([-np.sin(th0)*np.cos(t6), -np.sin(th0)*np.sin(t6), np.zeros_like(t6)]).T
cov6 = xdd6 - (xdd6 * xs6).sum(1, keepdims=True) * xs6
xd6 = np.outer(-u6, np.sin(t6)) + np.outer(v6, np.cos(t6))   # 大圆速度 ẋ
check("G6 大圆：|ẋ|=1 且协变加速度 <1e-12（测地线）；纬线圆 θ₀=π/3：协变加速度范数 ≈sin²θ₀cosθ₀>0.3（非测地）",
      abs(np.linalg.norm(xd6, axis=0) - 1).max() < 1e-12
      and cov_acc.max() < 1e-12 and np.linalg.norm(cov6, axis=1).min() > 0.3)

# ---------- G7 Euler 示性数：球面网格 χ=2，环面网格 χ=0（咖啡杯=甜甜圈） ----------
def icosphere(subdiv=1):
    t = (1 + 5**0.5)/2
    V = [(-1,t,0),(1,t,0),(-1,-t,0),(1,-t,0),(0,-1,t),(0,1,t),(0,-1,-t),(0,1,-t),
         (t,0,-1),(t,0,1),(-t,0,-1),(-t,0,1)]
    V = [np.array(v)/np.linalg.norm(v) for v in V]
    F = [(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),
         (7,1,8),(3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
    for _ in range(subdiv):
        cache, newF = {}, []
        def mid(a, b):
            key = (min(a,b), max(a,b))
            if key not in cache:
                m = V[a] + V[b]; m = m/np.linalg.norm(m)
                V.append(m); cache[key] = len(V) - 1
            return cache[key]
        for (a, b, c) in F:
            ab, bc, ca = mid(a,b), mid(b,c), mid(c,a)
            newF += [(a,ab,ca),(b,bc,ab),(c,ca,bc),(ab,bc,ca)]
        F = newF
    return np.array(V), F
V7, F7 = icosphere(1)
E7 = len({e for f in F7 for e in [(min(f[0],f[1]),max(f[0],f[1])),(min(f[1],f[2]),max(f[1],f[2])),(min(f[0],f[2]),max(f[0],f[2]))]})
chi7 = len(V7) - E7 + len(F7)
m8 = 8; verts = [(i, j) for i in range(m8) for j in range(m8)]
edges = set(); F8 = []
for i in range(m8):
    for j in range(m8):
        a, b, c, d = i*m8+j, ((i+1)%m8)*m8+j, ((i+1)%m8)*m8+((j+1)%m8), i*m8+((j+1)%m8)
        F8 += [(a, b, d), (b, c, d)]
for f in F8:
    for k in range(3):
        edges.add((min(f[k], f[(k+1)%3]), max(f[k], f[(k+1)%3])))
chi8 = len(verts) - len(edges) + len(F8)
check(f"G7 球面网格 V−E+F = {len(V7)}−{E7}+{len(F7)} = {chi7}；环面网格 χ = {len(verts)}−{len(edges)}+{len(F8)} = {chi8}",
      chi7 == 2 and chi8 == 0)

# ---------- G8 离散 Gauss 曲率（角盈余）：球面总曲率 → 4π，K̄ ≈ 1 ----------
V8, F8b = icosphere(2)
angsum = {i: 0.0 for i in range(len(V8))}
for (a, b, c) in F8b:
    for (p, q, r) in ((a,b,c), (b,c,a), (c,a,b)):
        e1v = V8[q] - V8[p]; e2v = V8[r] - V8[p]
        angsum[p] += np.arccos(np.dot(e1v, e2v)/(np.linalg.norm(e1v)*np.linalg.norm(e2v)))
defect = sum(2*np.pi - angsum[i] for i in range(len(V8)))
Kbar = defect / (4*np.pi)                          # 单位球总面积 4π
check(f"G8 角盈余：Σ(2π−Σθ) = {defect:.4f} ≈ 4π（误差<2%）；平均曲率 K̄ = {Kbar:.4f} ≈ 1（±5%）",
      abs(defect - 4*np.pi) < 0.02*4*np.pi and abs(Kbar - 1) < 0.05)

# ---------- G9 环绕数：π₁(S¹)=ℤ 的数值见证 ----------
def winding(th_fn, n=4000):
    t = np.linspace(0, 1, n, endpoint=False)
    zk = np.exp(1j*th_fn(t))
    dz = np.conj(zk)*np.roll(zk, -1)
    return np.sum(np.arctan2(dz.imag, dz.real))/(2*np.pi)
w1, w2, w0 = winding(lambda t: 2*np.pi*t), winding(lambda t: 4*np.pi*t), winding(lambda t: 0*t)
check(f"G9 环绕数：绕一圈={w1:.6f}，两圈={w2:.6f}，常值回路={abs(w0):.1e}（±1e-6）",
      abs(w1-1) < 1e-6 and abs(w2-2) < 1e-6 and abs(w0) < 1e-6)

# ---------- G10 Fisher 信息度规（Bernoulli）：KL 二阶展开系数 = ½I(θ) ----------
th10 = 0.3
def kl_bern(a, b):
    return a*np.log(a/b) + (1-a)*np.log((1-a)/(1-b))
coeffs = [kl_bern(th10 + d, th10)/d**2 for d in (3e-6, 6e-6, 1.2e-5)]
target = 1.0/(2*th10*(1-th10))
check(f"G10 Bernoulli Fisher：KL(θ+d‖θ)/d² = {coeffs[-1]:.8f} → 1/(2θ(1−θ)) = {target:.8f}（相对误差<1e-4，d 取小避开三阶项）",
      all(abs(c - target)/target < 1e-4 for c in coeffs))

# ---------- G11 高斯 Fisher：(μ,σ) 参数化 I=diag(1/σ², 2/σ²)；(μ,σ²) 参数化 I=diag(1/σ², 1/(2σ⁴)) ----------
def kl_gauss_same_sigma(mu0, mu1, s):
    return (mu0-mu1)**2/(2*s**2)
def kl_gauss_var(v0, v1):                           # μ=0，方差参数 v=σ²
    return 0.5*np.log(v1/v0) + 0.5*v0/v1 - 0.5
s11 = 2.0; v11 = 4.0
c_mu = [kl_gauss_same_sigma(0, d, s11)/d**2 for d in (1e-4, 2e-4)]
c_sg = [kl_gauss_var(v11, v11+d)/d**2 for d in (4e-5, 8e-5)]
check(f"G11 高斯 Fisher：μ 向 KL/d² = {c_mu[-1]:.8f} → 1/(2σ²)；σ(标准差) 向 → 1/(2σ²)·½I=1/σ²；方差 v=σ² 向 KL/d² = {c_sg[-1]:.8f} → 1/(4v²)=½I_vv（相对误差<1e-4；参数化改变 Fisher 是经典陷阱）",
      all(abs(c - 0.5/s11**2)/(0.5/s11**2) < 1e-4 for c in c_mu)
      and all(abs(c - 0.25/v11**2)/(0.25/v11**2) < 1e-4 for c in c_sg))

# ---------- G12 Rao 距离自洽：线积分 ∫√I dθ = 闭式 2 arccos(√θ₁θ₂+√(1−θ₁)(1−θ₂)) ----------
th1, th2 = 0.2, 0.85
grid = np.linspace(th1, th2, 200001)
line_int = trapz(1.0/np.sqrt(grid*(1-grid)), grid)
closed = 2*np.arccos(np.sqrt(th1*th2) + np.sqrt((1-th1)*(1-th2)))
check(f"G12 Bernoulli Rao 距离：线积分 = {line_int:.8f}，闭式 = {closed:.8f}（差<1e-6）——统计流形上 Fisher 度规的测地距离",
      abs(line_int - closed) < 1e-6)

# ---------- G13 KL 不对称（信息几何：发散≠距离） ----------
kl_ab = kl_bern(0.2, 0.5); kl_ba = kl_bern(0.5, 0.2)
check(f"G13 KL(0.2‖0.5) = {kl_ab:.4f} ≠ KL(0.5‖0.2) = {kl_ba:.4f}（不对称，非距离函数；θ↔1−θ 时 Bernoulli KL 对称是巧合）",
      abs(kl_ab - kl_ba) > 0.01)

# ---------- G14 双曲圆周长 2π sinh r > 2π r（指数增长=树状容量） ----------
r14 = 1.5
phi = np.linspace(0, 2*np.pi, 40001)
ys = np.cosh(r14) + np.sinh(r14)*np.sin(phi)
circ = trapz(np.sinh(r14)/ys, phi)
check(f"G14 双曲圆（Poincaré 半平面，r=1.5）：周长 = {circ:.6f} ≈ 2π sinh r = {2*np.pi*np.sinh(r14):.6f}（差<1e-6），且 > 2πr = {2*np.pi*r14:.4f}",
      abs(circ - 2*np.pi*np.sinh(r14)) < 1e-6 and circ > 2*np.pi*r14)

print(f"\n== 结果：{PASS}/{TOTAL} 通过 ==")
import sys
sys.exit(0 if PASS == TOTAL else 1)
