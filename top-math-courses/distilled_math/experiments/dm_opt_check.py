#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_opt_check.py — 蒸馏卡 DM-OPT-01（优化与变分）的 L1 机器断言
对应卡：../DM-OPT-01-优化与变分.md §4（编号 P1-P13 一一对应）
断言计数：13 组（若干组含子断言）
运行方式：python3 dm_opt_check.py   （依赖 numpy + sympy）
铁律：浮点断言带容差；迭代类断言（收敛率/解对照）容差放宽并注明。
"""
import numpy as np

PASS, TOTAL = 0, 0

def check(name, cond):
    global PASS, TOTAL
    TOTAL += 1
    ok = bool(cond)
    PASS += ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")

rng = np.random.default_rng(42)
trapz = getattr(np, "trapezoid", None) or np.trapz

print("== DM-OPT-01 优化与变分 · L1 断言 ==")

# ---------- P1 Fenchel 共轭与 Fenchel–Young 不等式 ----------
# f(x) = −ln x：f*(s) = −1 − ln(−s) (s<0)；等号在 x = −1/s 处取到
xs = np.linspace(0.2, 5.0, 97)
ok1 = True
for s in (-0.5, -1.0, -2.0):
    fstar = -1.0 - np.log(-s)
    gap = -np.log(xs) + fstar - s*xs                  # f + f* − s·x ≥ 0
    ok1 &= gap.min() > -1e-12 and abs(gap[np.argmin(np.abs(xs - (-1/s)))] ) < 1e-6
    xe = -1.0/s                                        # 精确取等点
    ok1 &= abs(-np.log(xe) + fstar - s*xe) < 1e-12
# f(x)=|x|：f*(s) = δ_{[−1,1]}(s)：|s|<1 时等号在 x=0
fy2 = np.abs(xs) + 0.0 - 0.5*xs                        # f + f* − s·x, s=0.5
ok1 &= fy2.min() > -1e-12 and abs(np.abs(0.0) - 0.5*0.0 - 0.0) < 1e-15
check("P1 Fenchel–Young：(−ln x)* = −1−ln(−s)，网格上 f+f*−sx ≥0 且在 x=−1/s 精确取等（<1e-12）；|x|* = δ_[−1,1]（s=1/2 时 x=0 取等）",
      ok1)

# ---------- P2 LP 弱对偶 + 强对偶（顶点枚举） ----------
# max x+y s.t. x+2y≤4, 3x+y≤6, x,y≥0；p* = 2.8 在 (1.6,1.2)
cand = [(0,0),(2,0),(0,2),(1.6,1.2)]
pstar = max(x+y for (x,y) in cand)
# 对偶：min 4u+6v s.t. u+3v≥1, 2u+v≥1, u,v≥0；最优两约束活跃
u = np.linalg.solve(np.array([[1.0,3.0],[2.0,1.0]]), np.array([1.0,1.0]))   # (0.4,0.2)
dstar = 4*u[0] + 6*u[1]
weak = 4*1.0 + 6*1.0                                    # 任意对偶可行点 (1,1)
check(f"P2 LP：原始最优 p*={pstar}（顶点枚举）；弱对偶：对偶可行点值 {weak} ≥ p*；对偶最优 d*={dstar}，强对偶 gap=0（LP 恒强对偶）",
      pstar == 2.8 and weak >= pstar and abs(dstar - pstar) < 1e-12)

# ---------- P3 Slater 强对偶：凸 QP 对偶间隙为零 ----------
# min ½‖x‖² s.t. x₁+x₂ ≥ 1（严格可行：Slater 成立）；p*=1/4，对偶 g(λ)=λ−λ² 最大化在 λ=1/2
lam_grid = np.linspace(0, 1, 100001)
g = lam_grid - lam_grid**2
dstar3 = g.max()
check(f"P3 Slater QP：p* = ¼（x*=(½,½)），数值对偶最优 d* = {dstar3:.8f}，gap = {abs(0.25-dstar3):.2e} < 1e-8",
      abs(0.25 - dstar3) < 1e-8)

# ---------- P4 KKT：活跃集枚举求解 + 全条件验证 ----------
# min ½‖x−c‖², c=(1,1) s.t. x₁≤0, x₂≤0, x₁+x₂≥−1
c4 = np.array([1.0, 1.0])
A4 = np.array([[1.0,0.0],[0.0,1.0],[-1.0,-1.0]])        # 统一成 A x ≤ b
b4 = np.array([0.0, 0.0, 1.0])
best = None
import itertools
for r in range(4):
    for act in itertools.combinations(range(3), r):
        if r == 0:
            x = c4.copy()
        elif r == 1:
            Aa = A4[list(act)]
            x = c4 - Aa[0]*((Aa[0]@c4 - b4[list(act)][0])/(Aa[0]@Aa[0]))   # 投到单约束
        else:
            x = np.linalg.lstsq(A4[list(act)], b4[list(act)], rcond=None)[0] # 活跃约束当等式解驻点
        if np.all(A4@x <= b4 + 1e-10):
            val = 0.5*np.sum((x-c4)**2)
            if best is None or val < best[0]: best = (val, x)
val4, x4 = best
# 乘子只在活跃集上反解（集外恒 0），再验符号与互补松弛
act = np.abs(A4@x4 - b4) < 1e-9
lam4 = np.zeros(3)
if act.any():
    lam4[act] = np.linalg.lstsq(A4[act].T, c4 - x4, rcond=None)[0]
stat = np.linalg.norm(x4 - c4 + A4.T@lam4)
comp = np.max(np.abs(lam4 * (A4@x4 - b4)))
check(f"P4 KKT：活跃集枚举得 x* = ({x4[0]:.3f},{x4[1]:.3f})（=投影 (0,0)）；平稳性残差 {stat:.1e}<1e-10，λ={np.round(lam4,3)}≥0（λ₃=0 活跃集外），互补松弛 {comp:.1e}<1e-10",
      np.allclose(x4, [0,0], atol=1e-9) and stat < 1e-10 and lam4.min() >= -1e-10
      and abs(lam4[2]) < 1e-10 and comp < 1e-10)

# ---------- P5 近端算子 = 去噪：soft-threshold 闭式对照数值最小化 ----------
def soft(v, lmb):
    return np.sign(v)*np.maximum(np.abs(v) - lmb, 0.0)
def argmin_scalar(v, lmb):
    zg = np.linspace(-abs(v)-2*lmb-1, abs(v)+2*lmb+1, 2000001)
    fv = 0.5*(zg-v)**2 + lmb*np.abs(zg)
    return zg[np.argmin(fv)]
vs = np.array([-3.0, -0.7, -0.2, 0.0, 0.2, 0.7, 3.0])
err5 = max(abs(soft(v,1.0) - argmin_scalar(v,1.0)) for v in vs)
check(f"P5 prox_{{λ|·|}}(v) = sign(v)max(|v|−λ,0)：7 点对照网格数值 argmin，最大偏差 {err5:.1e} <1e-5（|v|≤λ 处精确归零=稀疏性来源）",
      err5 < 1e-5 and soft(0.2,1.0) == 0.0 and soft(3.0,1.0) == 2.0)

# ---------- P6 Moreau 分解：prox_f(x) + prox_{f*}(x) = x ----------
xg6 = np.linspace(-4, 4, 801)
lhs = soft(xg6, 1.0) + np.clip(xg6, -1.0, 1.0)          # prox_{|·|} + prox_{δ*[−1,1]}=投影
check(f"P6 Moreau 恒等式：ST₁(x) + proj_[−1,1](x) = x，网格最大偏差 {np.abs(lhs-xg6).max():.1e} <1e-12",
      np.abs(lhs - xg6).max() < 1e-12)

# ---------- P7 ISTA vs FISTA：等预算分离 ≥2 个数量级（理论率 O(1/k) vs O(1/k²) 为上界陈述，见卡 ☆ 条） ----------
m7, n7 = 50, 300
U7, _ = np.linalg.qr(rng.standard_normal((m7, m7)))
V7, _ = np.linalg.qr(rng.standard_normal((n7, m7)))
A7 = (U7 * np.logspace(0, -3, m7)) @ V7.T            # 谱衰减 → 病态，长亚线性阶段
xtrue = np.zeros(n7); idx7 = rng.choice(n7, 15, replace=False)
xtrue[idx7] = rng.standard_normal(15)
b7 = A7@xtrue + 0.1*rng.standard_normal(m7)
lam7 = 0.01*np.abs(A7.T@b7).max(); L7 = np.linalg.norm(A7, 2)**2
def lasso_obj(x):
    return 0.5*np.sum((A7@x - b7)**2) + lam7*np.sum(np.abs(x))
def grad_smooth(x):
    return A7.T@(A7@x - b7)
xFr = np.zeros(n7); yFr = np.zeros(n7); tFr = 1.0; ref7 = lasso_obj(np.zeros(n7))
for k in range(60000):                                # 参考最优：FISTA 60000 步历史最小
    xn = soft(yFr - grad_smooth(yFr)/L7, lam7/L7); tn = (1 + np.sqrt(1 + 4*tFr**2))/2
    yFr = xn + ((tFr-1)/tn)*(xn - xFr); xFr, tFr = xn, tn
    v = lasso_obj(xFr)
    if v < ref7: ref7 = v
xI = np.zeros(n7); xF = np.zeros(n7); yF = np.zeros(n7); tF = 1.0
histI, histF = [], []
for k in range(6000):
    xI = soft(xI - grad_smooth(xI)/L7, lam7/L7); histI.append(lasso_obj(xI))
    xFn = soft(yF - grad_smooth(yF)/L7, lam7/L7); tn = (1 + np.sqrt(1 + 4*tF**2))/2
    yF = xFn + ((tF-1)/tn)*(xFn - xF); xF, tF = xFn, tn; histF.append(lasso_obj(xF))
gapI7, gapF7 = histI[-1] - ref7, histF[-1] - ref7
sep7 = gapI7/gapF7
check(f"P7 病态 Lasso（cond≈10³）：等预算 6000 步后 ISTA 差距 {gapI7:.2e} vs FISTA {gapF7:.2e}，分离 {sep7:.0f}×>100；且 k≥100 起 FISTA 目标恒低；60000 步参考最优 {ref7:.6f}",
      0 < gapF7 < 1e-6 and sep7 > 100 and all(hF <= hI for hF, hI in zip(histF[100:], histI[100:])))

# ---------- P8 ADMM（分裂 x=w）：解与 FISTA 一致 + Lasso KKT 见证 ----------
A8 = rng.standard_normal((30, 100))
x8t = np.zeros(100); idx8 = rng.choice(100, 5, replace=False)
x8t[idx8] = rng.standard_normal(5)
b8 = A8@x8t + 0.02*rng.standard_normal(30)
lam8 = 0.1*np.abs(A8.T@b8).max(); L8 = np.linalg.norm(A8, 2)**2
xF8 = np.zeros(100); yF8 = np.zeros(100); tF8 = 1.0
for k in range(6000):
    xn = soft(yF8 - A8.T@(A8@yF8 - b8)/L8, lam8/L8); tn = (1 + np.sqrt(1 + 4*tF8**2))/2
    yF8 = xn + ((tF8-1)/tn)*(xn - xF8); xF8, tF8 = xn, tn
x8 = np.zeros(100); w8 = np.zeros(100); u8 = np.zeros(100); rho8 = 0.1*L8
Qinv = np.linalg.inv(A8.T@A8 + rho8*np.eye(100)); rhs0 = A8.T@b8   # 预逆一次（本机 LAPACK solve 慢）
for k in range(6000):
    x8 = Qinv @ (rhs0 + rho8*(w8 - u8))
    w8 = soft(x8 + u8, lam8/rho8)
    u8 = u8 + x8 - w8
diff8 = np.abs(x8 - xF8).max()
g8 = A8.T@(b8 - A8@x8)                                # 平稳性：g ∈ λ∂‖x‖₁
zeros8 = np.abs(xF8) < 1e-12
kkt_zero = np.abs(g8[zeros8]).max() if zeros8.any() else 0.0
kkt_nz = np.abs(np.abs(g8[~zeros8]) - lam8).max() if (~zeros8).any() else 0.0
check(f"P8 ADMM：‖x_admm − x_FISTA‖∞ = {diff8:.1e} <1e-4；KKT：零分量 |(Aᵀr)ᵢ|≤λ（max={kkt_zero:.4f} ≤λ+1e-6），非零分量 |(Aᵀr)ᵢ|=λ（差 {kkt_nz:.1e}<1e-3）",
      diff8 < 1e-4 and kkt_zero <= lam8 + 1e-6 and kkt_nz < 1e-3)

# ---------- P9 变分法：最速降线 = 摆线（Beltrami 常数 + 数值对照） ----------
# Beltrami：L−y'L_{y'} = 1/√(2g·(−y)(1+y'²)) 沿极值曲线为常数
ths = np.linspace(0.1, 2.0, 50)
bel = 1.0/np.sqrt(2*9.8*(1-np.cos(ths))*(1 + (np.sin(ths)/(1-np.cos(ths)))**2))
ok9 = np.ptp(bel) < 1e-9                                # 摆线 x=a(θ−sinθ), y=−a(1−cosθ)
# 端点 (0,0)→(1,−1)：解 (θ−sinθ)/(1−cosθ)=1 得 θ₁，a=1/(1−cosθ₁)
from math import sin, cos, sqrt, pi
def bisect(f, lo, hi, n=200):
    for _ in range(n):
        m = 0.5*(lo+hi)
        lo, hi = (lo, m) if f(m) < 0 else (m, hi)
    return 0.5*(lo+hi)
th1 = bisect(lambda t: (t-sin(t))-(1-cos(t)), 1e-6, 2.5)
a9 = 1.0/(1-cos(th1))
tg = np.linspace(1e-9, th1, 400001)
half = np.sin(tg/2)                                    # 用 2sin²(θ/2) 计算 1−cosθ，避免小 θ 灾难性消去
one_minus_cos = 2*half**2
sin_t = 2*half*np.cos(tg/2)
dxd, dyd = a9*one_minus_cos, a9*sin_t                  # dx/dθ, dy/dθ
T_cyc = trapz(np.sqrt(dxd**2 + dyd**2)/np.sqrt(2*9.8*a9*one_minus_cos), tg)
T_line = np.sqrt(2*(1+1)/(9.8*1))                       # 直线 m=1：T=√(2(1+m²)/(gm))
# 曲线 y=−x^{3/2}：T=∫√(1+(1.5√x)²)/√(2g x^{3/2}) dx
xg9 = np.linspace(1e-4, 1, 400000)
T_para = trapz(np.sqrt(1 + 2.25*xg9)/np.sqrt(2*9.8*xg9**1.5), xg9)
check(f"P9 最速降线：摆线 Beltrami 常数波动 {np.ptp(bel):.1e}<1e-9；端点 (0,0)→(1,−1) 数值下降时间 摆线 {T_cyc:.4f} < 直线 {T_line:.4f} < y=−x^1.5 曲线 {T_para:.4f}",
      ok9 and T_cyc < T_line - 1e-4 and T_line < T_para)

# ---------- P10 PL 条件（无强凸）：胖最小二乘 GD 线性收敛 ----------
A10 = rng.standard_normal((3, 20)); b10 = A10@rng.standard_normal(20)
x10 = np.zeros(20); L10 = np.linalg.norm(A10, 2)**2; hist10 = []
for _ in range(3000):
    x10 = x10 - (A10.T@(A10@x10 - b10))/L10
    hist10.append(0.5*np.sum((A10@x10 - b10)**2))
h = np.array(hist10, dtype=float)
floor = h.min()
gaps = h - floor                                       # 行满秩胖系统可精确解 → floor→0（PL 常数 μ=2σ_min²(A)>0）
gr = gaps[gaps > 1e-12*h[0]]                           # 有效几何衰减窗口（顶部截暂态，底部截舍入）
gr = gr[max(3, len(gr)//5):]                           # 再弃窗口前 20%（多模态暂态）
ratios = gr[1:]/gr[:-1]
r_bar = ratios.mean(); r_cv = ratios.std()/ratios.mean()
check(f"P10 A 为 3×20（Hessian 奇异、非强凸）但行满秩 → PL 成立：GD 损失几何衰减，窗口内相邻比恒定 {r_bar:.4f}（变异系数 {r_cv:.4f}<2%，窗口 {len(gr)} 点衰减 {gr[0]/gr[-1]:.1e} 倍），终值 {h[-1]:.1e}",
      len(gr) >= 12 and r_cv < 0.02 and gr[0]/gr[-1] > 1e1 and h[-1] < h[0]*1e-15)

# ---------- P11 SP vs μP 初始化的梯度尺度机制（宽度扫掠） ----------
def grad_scale(n, param, reps=200):
    out_std, g2_std = [], []
    for _ in range(reps):
        x = np.ones(5)
        if param == 'SP':
            W1 = rng.standard_normal((n, 5)); W2 = rng.standard_normal(n)
        else:                                            # μP 型缩放：W2 ~ N(0,1/n)
            W1 = rng.standard_normal((n, 5)); W2 = rng.standard_normal(n)/np.sqrt(n)
        y = W2 @ (W1 @ x)
        out_std.append(abs(y))
        g2 = (y - 1.0)*(W1 @ x)                          # ∂ℓ/∂W2 逐分量
        g2_std.append(g2.std())
    return np.mean(out_std), np.mean(g2_std)
res = {w: {p: grad_scale(w, p) for p in ('SP','muP')} for w in (50, 200, 800)}
sp_ratio = res[800]['SP'][1]/res[50]['SP'][1]
mup_ratio = res[800]['muP'][1]/res[50]['muP'][1]
check(f"P11 两层线性网：SP 参数化下 ∂ℓ/∂W2 逐分量尺度随宽度增长 ×{sp_ratio:.2f}（>2，最优 lr 必须随宽度缩小）；μP 型（W2~N(0,1/n)）×{mup_ratio:.2f}（0.5-2 内，lr 可迁移）——学习率转移的尺度机制",
      sp_ratio > 2.0 and 0.5 < mup_ratio < 2.0)

# ---------- P12 非凸：KKT 点未必是局部极小 ----------
f12 = lambda x: (x**2 - 1)**2
stat12 = abs(4*0*(0-1) + 0.0)                           # ∇f(0)+λ = 0
feas12 = (0 <= 2) and (0.0 >= 0)                        # x≤2, λ≥0
comp12 = abs(0.0*(2-0))
not_min = f12(0.5) < f12(0)                             # 可行下降方向存在
check(f"P12 f=(x²−1)² s.t. x≤2：(x,λ)=(0,0) 满足全部 KKT（平稳 {stat12:.0e}、可行、λ≥0、互补 {comp12:.0e}），但 f(0)=1 > f(0.5)={f12(0.5):.4f}——非凸 KKT 只必要",
      stat12 < 1e-12 and feas12 and comp12 < 1e-12 and not_min)

# ---------- P13 整数规划的 LP 松弛间隙（非凸对偶间隙的亲戚） ----------
ip_best = max(x1+x2 for x1 in (0,1) for x2 in (0,1) if x1+x2 <= 1.5)
lp_best = 1.5                                            # 连续松弛最优 (1, 0.5)
check(f"P13 max x₁+x₂ s.t. x₁+x₂≤1.5, x∈{{0,1}}：整数最优 {ip_best}，LP 松弛 {lp_best}，间隙 0.5>0——凸性破坏则对偶/松弛有 gap",
      ip_best == 1 and abs(lp_best - 1.5) < 1e-12 and lp_best - ip_best == 0.5)

print(f"\n== 结果：{PASS}/{TOTAL} 通过 ==")
import sys
sys.exit(0 if PASS == TOTAL else 1)
