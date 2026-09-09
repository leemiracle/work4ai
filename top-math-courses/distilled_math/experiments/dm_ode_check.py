#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_ode_check.py — 蒸馏卡 DM-ODE-01（微分方程与动力系统）的 L1 机器断言
对应卡：../DM-ODE-01-微分方程与动力系统.md §4（编号 O1-O13 一一对应）
断言计数：13 组（若干组含子断言）
运行方式：python3 dm_ode_check.py   （依赖 numpy）
铁律：浮点断言带容差；数值积分容差放宽到 1e-3 量级并逐条注明。
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

print("== DM-ODE-01 微分方程与动力系统 · L1 断言 ==")

# ---------- O1 Peano 非唯一性：dx/dt = sqrt(|x|), x(0)=0 有 x≡0 与 x=t^2/4 两解 ----------
ts = np.linspace(1e-6, 5.0, 200)
x_sol = ts**2 / 4.0
resid = np.abs(ts / 2.0 - np.sqrt(x_sol))          # x'(t)=t/2 vs sqrt(x)=t/2 (t>=0)
check("O1 dx/dt=√|x| 的 t²/4 解残差 <1e-12（连同 x≡0 构成非唯一；Lipschitz 失败处 x=0）",
      resid.max() < 1e-12)

# ---------- O2 有限逃逸时间：dx/dt = x², x(0)=1 → x=1/(1-t)，t→1 爆炸 ----------
t2 = np.linspace(0.0, 0.99, 100)
x2 = 1.0 / (1.0 - t2)
resid2 = np.abs(x2**2 - 1.0 / (1.0 - t2)**2)       # x'(t) = 1/(1-t)² = x²
check("O2 x'=x² 闭式解 x=1/(1−t) 残差 <1e-9；x(0.999)=1000 单调爆炸（最大存在区间 <∞）",
      resid2.max() < 1e-9 and abs(1.0/(1-0.999) - 1000.0) < 1e-9)

# ---------- O3 线性系统稳定性由特征值实部决定（阻尼振子） ----------
A = np.array([[0.0, 1.0], [-4.0, -0.4]])
ev = np.linalg.eigvals(A)
def rk4(f, x0, T, h):
    n = int(round(T / h)); x = np.array(x0, float); tr = [x.copy()]
    for _ in range(n):
        k1 = f(x); k2 = f(x + 0.5*h*k1); k3 = f(x + 0.5*h*k2); k4 = f(x + h*k3)
        x = x + (h/6.0)*(k1 + 2*k2 + 2*k3 + k4); tr.append(x.copy())
    return np.array(tr)
tr = rk4(lambda x: A @ x, (1.0, 0.0), 20.0, 0.01)
ratio3 = np.linalg.norm(tr[-1]) / np.linalg.norm(tr[0])
check("O3 阻尼振子：eig 实部全 <0，且 ‖x(20)‖/‖x(0)‖ < 0.1（包络 e^{−0.2·20}≈0.018）",
      ev.real.max() < 0 and ratio3 < 0.1)

# ---------- O4 Lyapunov 函数单调性（阻尼单摆，能量直觉） ----------
def pend(x):
    return np.array([x[1], -0.2*x[1] - np.sin(x[0])])
tr4 = rk4(pend, (2.0, 0.0), 20.0, 0.01)
V = 0.5*tr4[:,1]**2 + (1.0 - np.cos(tr4[:,0]))
dV = np.diff(V)
check("O4 阻尼单摆 V=½ẋ²+1−cos x：全程 V̇=−0.2ẋ²≤0（数值增量 ≤1e-6），V(20)<0.5·V(0)",
      dV.max() <= 1e-6 and V[-1] < 0.5*V[0])

# ---------- O5 saddle-node 分岔：x' = μ − x² ----------
def scalar(mu):
    return lambda x: np.array([mu - x[0]**2])
t5 = rk4(scalar(1.0), (0.5,), 10.0, 0.01)[-1, 0]
t5b = rk4(scalar(-1.0), (0.0,), 1.55, 0.001)       # 无平衡点，解向 −tan(t) 逃逸
check("O5 μ=+1：x→稳定平衡 +1（|x(10)−1|<1e-6）；μ=−1：无平衡点，|x(1.55)|>30 有限逃逸",
      abs(t5 - 1.0) < 1e-6 and abs(t5b[-1, 0]) > 30)

# ---------- O6 超临界 pitchfork：x' = μx − x³ ----------
a1 = rk4(scalar2 := (lambda x: np.array([x[0] - x[0]**3])), (0.1,), 15.0, 0.01)[-1, 0]
a2 = rk4(scalar2, (-0.1,), 15.0, 0.01)[-1, 0]
a3 = rk4(scalar2, (2.5,), 15.0, 0.01)[-1, 0]
a4 = rk4(scalar2, (0.001,), 0.1, 0.001)[-1, 0]     # 0 不稳定：小扰动放大
a5 = rk4((lambda x: np.array([-0.5*x[0] - x[0]**3])), (0.1,), 30.0, 0.01)[-1, 0]
check("O6 μ=1：±0.1→±1、2.5→1（吸到稳定支）；x(0.001) 在 t=0.1 已放大 >1.05e-3（0 处失稳）；μ=−0.5：x→0",
      abs(a1-1) < 1e-6 and abs(a2+1) < 1e-6 and abs(a3-1) < 1e-6
      and a4 > 1.05*0.001 and abs(a5) < 1e-6)

# ---------- O7 Lorenz 系统：有界混沌 + 初值敏感 + 确定性可复现 ----------
def lorenz(x, s=10.0, r=28.0, b=8.0/3.0):
    return np.array([s*(x[1]-x[0]), x[0]*(r-x[2])-x[1], x[0]*x[1]-b*x[2]])
def lorenz_run(x0):
    return rk4(lorenz, x0, 40.0, 0.005)
p = lorenz_run((1.0, 1.0, 1.0))
q = lorenz_run((1.0 + 1e-6, 1.0, 1.0))
p2 = lorenz_run((1.0, 1.0, 1.0))
sep = np.linalg.norm(p[-1] - q[-1])
check("O7 Lorenz(σ=10,ρ=28,β=8/3)：两轨全程 |坐标|<60（有界吸引子）；1e-6 扰动在 T=40 放大到 >1（瞬态收缩后指数分离）；重跑逐位相同",
      np.abs(p).max() < 60 and np.abs(q).max() < 60 and sep > 1.0 and np.array_equal(p, p2))

# ---------- O8 最大 Lyapunov 指数（Benettin 重正化）≈ 0.9 ----------
def benettin(T=200.0, tau=0.5, d0=1e-8):
    h = 0.005; steps = int(tau/h)
    x = np.array([1.0, 1.0, 1.0]); v = np.array([1.0, 0.0, 0.0]); v = v/np.linalg.norm(v)*d0
    acc = 0.0
    for _ in range(int(round(T/tau))):
        for _ in range(steps):
            k1 = lorenz(x); k2 = lorenz(x+0.5*h*k1); k3 = lorenz(x+0.5*h*k2); k4 = lorenz(x+h*k3)
            x = x + (h/6)*(k1+2*k2+2*k3+k4)
            k1 = lorenz(v+x)-lorenz(x); k2 = lorenz(v+x+0.5*h*k1)-lorenz(x+0.5*h*k1)
            k3 = lorenz(v+x+0.5*h*k2)-lorenz(x+0.5*h*k2); k4 = lorenz(v+x+h*k3)-lorenz(x+h*k3)
            v = v + (h/6)*(k1+2*k2+2*k3+k4)
        d = np.linalg.norm(v); acc += np.log(d/d0); v = v/d*d0
    return acc/T
lam = benettin()
check(f"O8 Benettin 重正化：λ̂ = {lam:.3f} ∈ (0.5, 1.3)（文献值 ≈0.90，容差放宽）",
      0.5 < lam < 1.3)

# ---------- O9 Hopf 分岔范式（极坐标 r'=r(μ−r²), θ'=1 的笛卡尔形式） ----------
def hopf(x, mu=1.0):
    r2 = x[0]**2 + x[1]**2
    return np.array([-x[1] + x[0]*(mu - r2), x[0] + x[1]*(mu - r2)])
r_in = np.linalg.norm(rk4(hopf, (0.3, 0.0), 30.0, 0.01)[-1])
r_out = np.linalg.norm(rk4(hopf, (2.5, 0.0), 30.0, 0.01)[-1])
check("O9 Hopf 超临界 μ=1：环内 r₀=0.3 与环外 r₀=2.5 都收敛到极限环 r=1（±0.01）",
      abs(r_in-1) < 0.01 and abs(r_out-1) < 0.01)

# ---------- O10 显式 Euler 能量漂移 vs 辛 Euler 能量有界（谐振子） ----------
h, N = 0.05, 2000
q, p = 1.0, 0.0; E0 = 0.5*(q*q + p*p)
qe, pe = q, p
for _ in range(N):                       # 显式 Euler：E 增长 (1+h²)^N
    qe, pe = qe + h*pe, pe - h*qe
E_eul = 0.5*(qe*qe + pe*pe)
qs, ps = q, p; dev = 0.0
for _ in range(N):                       # 辛 Euler（先动量后位置）：修正能量振荡有界
    ps = ps - h*qs; qs = qs + h*ps
    dev = max(dev, abs(0.5*(qs*qs + ps*ps) - E0))
check(f"O10 显式 Euler：E/E₀={E_eul/E0:.0f}（>2，指数漂移）；辛 Euler：|E−E₀|/E₀ 最大偏差 {dev/E0:.3f} <8%",
      E_eul/E0 > 2.0 and dev/E0 < 0.08)

# ---------- O11 热方程极值原理（显式格式） ----------
n = 64; dx = 1.0/(n-1); dt = dx*dx/4
u = np.zeros((n, n)); u[1:-1, 1:-1] = rng.uniform(0, 1, (n-2, n-2))  # 边界恒 0
M0, m0 = u[1:-1,1:-1].max(), u[1:-1,1:-1].min()
for _ in range(400):
    u[1:-1,1:-1] = u[1:-1,1:-1] + dt*( (np.roll(u,1,0)+np.roll(u,-1,0)+np.roll(u,1,1)+np.roll(u,-1,1))[1:-1,1:-1]/dx**2 - 4*u[1:-1,1:-1]/dx**2 )
M1 = u[1:-1,1:-1].max()
check("O11 热方程 400 步后：内部 max ≤ 初值 max+1e-10，且严格下降 >1e-3（极值在边界/初值达到）",
      M1 <= M0 + 1e-10 and M0 - M1 > 1e-3)

# ---------- O12 波方程 leapfrog：CFL≤1 能量有界，CFL>1 不稳定 ----------
J = 200; dx = 1.0/J
def wave_run(cfl, steps, mode='gauss'):
    dt = cfl*dx
    xs = np.arange(J)*dx
    u0 = np.exp(-((xs-0.5)**2)/0.01) if mode == 'gauss' else ((-1.0)**np.arange(J))
    u1 = u0.copy()                                  # u̇(0)=0 → u^{±1}=u^0
    E = []
    for k in range(steps):
        u2 = np.roll(u1,1) + np.roll(u1,-1) - u0
        u0, u1 = u1, u2
        if k % 20 == 0:
            v = (u1 - u0)/dt                        # 速度（半步）
            gx = (np.roll(u1,-1) - u1)/dx           # 梯度
            E.append(0.5*np.sum(v**2) + 0.5*np.sum(gx**2))
    return np.array(E)
E_ok = wave_run(0.95, 4000)
E_bad = wave_run(1.06, 300, mode='pi')              # π 模激发最不稳定模
check(f"O12 周期波方程：CFL=0.95 光滑初值能量带 |E−E₀|/E₀ max={(abs(E_ok-E_ok[0])/E_ok[0]).max():.3f}<12%（有界无漂移）；CFL=1.06 π 模能量放大 {E_bad[-1]/E_bad[0]:.0f}×>100",
      abs(E_ok - E_ok[0]).max()/E_ok[0] < 0.12 and E_bad[-1]/E_bad[0] > 100)

# ---------- O13 倒向热方程病态：单傅里叶模放大因子 e^{+k²t} ----------
k, t = 10.0, 0.1
amp_back, amp_fwd = np.exp(k*k*t), np.exp(-k*k*t)
check(f"O13 模式 k=10：正向热方程 t=0.1 衰减 {amp_fwd:.1e}(<1e-3)；倒向放大 {amp_back:.0f}(>1e3)——倒向不适定",
      amp_fwd < 1e-3 and amp_back > 1e3)

print(f"\n== 结果：{PASS}/{TOTAL} 通过 ==")
import sys
sys.exit(0 if PASS == TOTAL else 1)
