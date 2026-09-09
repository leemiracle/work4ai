#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_cplx_check.py — 蒸馏卡 DM-CPLX-01（复分析）的 L1 机器断言
对应卡：../DM-CPLX-01-复分析.md §4（编号 C1-C12，C5 含 4 个子断言）
断言计数：15
运行方式：python3 dm_cplx_check.py   （依赖 numpy + sympy）
方法：闭围道积分用周期梯形法（被积函数光滑 → 谱精度，容差 1e-9）
"""
import numpy as np
import sympy as sp

PASS, TOTAL = 0, 0

def check(name, cond):
    global PASS, TOTAL
    TOTAL += 1
    ok = bool(cond)
    PASS += ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")

TWO_PI = 2 * np.pi

def circle_integral(F, R=1.0, n_wind=1, N=20000):
    """∮_{|z|=R, 绕 n_wind 圈} F(z) dz，周期梯形（谱精度）"""
    t = np.linspace(0, TWO_PI * n_wind, N, endpoint=False)
    z = R * np.exp(1j * t)
    dz = 1j * z * (TWO_PI * n_wind / N)      # dz = i·R·e^{it}·dt
    return np.sum(F(z) * dz)

print("== DM-CPLX-01 复分析 · L1 断言 ==")

# ---------- C1 绕数：∮_{|z|=1} dz/z = 2πi（绕原点一圈）----------
I1 = circle_integral(lambda z: 1.0 / z)
check("C1 exp 绕原点绕数=1：∮dz/z = 2πi（误差<1e-9）",
      abs(I1 - 2j * np.pi) < 1e-9)

# ---------- C2 奇点在圆内/圆外 ----------
Iout = circle_integral(lambda z: 1.0 / (z - 2.0))          # a=2 在 |z|=1 外
Iin = circle_integral(lambda z: 1.0 / (z - 0.3))           # a=0.3 在圆内
check("C2 Cauchy 定理边界：∮dz/(z-2)=0（外）；∮dz/(z-0.3)=2πi（内）",
      abs(Iout) < 1e-9 and abs(Iin - 2j * np.pi) < 1e-9)

# ---------- C3 绕两圈：exp(it), t∈[0,4π] 绕原点 2 圈 ----------
I2 = circle_integral(lambda z: 1.0 / z, R=1.0, n_wind=2)
check("C3 绕数=2：∮dz/z = 4πi（拓扑计数与路径形状无关）",
      abs(I2 - 4j * np.pi) < 1e-9)

# ---------- C4 留数定理数值：∮ e^z/z^3 dz = 2πi·Res = πi ----------
I4 = circle_integral(lambda z: np.exp(z) / z**3)
check("C4 留数定理：∮e^z/z^3 dz = πi（Res(e^z/z^3,0)=1/2）",
      abs(I4 - 1j * np.pi) < 1e-9)

# ---------- C5 SymPy 留数符号验证（4 子断言） ----------
z = sp.symbols("z")
r1 = sp.residue(1 / z, z, 0)
r2 = sp.residue(sp.exp(z) / z**3, z, 0)
r3 = sp.residue(sp.sin(z) / z**2, z, 0)
r4 = sp.residue(1 / z**2, z, 0)          # 极点但留数为 0
check("C5a Res(1/z,0)=1", sp.simplify(r1 - 1) == 0)
check("C5b Res(e^z/z^3,0)=1/2", sp.simplify(r2 - sp.Rational(1, 2)) == 0)
check("C5c Res(sin(z)/z^2,0)=1", sp.simplify(r3 - 1) == 0)
check("C5d Res(1/z^2,0)=0（有极点≠有留数）", sp.simplify(r4) == 0)

# ---------- C6 Cauchy 积分公式：f(z0) = 1/(2πi)∮f(z)/(z-z0)dz ----------
z0 = 0.3
I6 = circle_integral(lambda w: np.exp(w) / (w - z0)) / (2j * np.pi)
check("C6 Cauchy 积分公式：1/(2πi)∮e^z/(z-0.3)dz = e^0.3（误差<1e-9）",
      abs(I6 - np.exp(z0)) < 1e-9)

# ---------- C7 一步登天（导数公式）：f'(z0) = 1/(2πi)∮f(z)/(z-z0)^2 dz ----------
I7 = circle_integral(lambda w: np.exp(w) / (w - z0) ** 2) / (2j * np.pi)
check("C7 高阶公式（全纯⇒无穷可微）：1/(2πi)∮e^z/(z-0.3)^2dz = e^0.3",
      abs(I7 - np.exp(z0)) < 1e-9)

# ---------- C8 Cauchy-Riemann 方程（符号） ----------
xs, ys = sp.symbols("x y", real=True)
u, v = xs**2 - ys**2, 2 * xs * ys                 # f(z)=z^2
cr1 = sp.simplify(sp.diff(u, xs) - sp.diff(v, ys))
cr2 = sp.simplify(sp.diff(u, ys) + sp.diff(v, xs))
u2, v2 = xs, -ys                                  # f(z)=conj(z) 反例
cr_bad = sp.simplify(sp.diff(u2, xs) - sp.diff(v2, ys))
check("C8 CR 方程：z^2 满足 u_x=v_y, u_y=-v_x；conj(z) 两边差=2（处处不满足）",
      cr1 == 0 and cr2 == 0 and cr_bad == 2)

# ---------- C9 最大模原理（网格见证） ----------
th = np.linspace(0, TWO_PI, 4000)
bnd = np.exp(1j * th)
fb = lambda w: w**2 + 1
bnd_max = np.max(np.abs(fb(bnd)))
r_in = np.linspace(0, 0.99, 200)
th_in = np.linspace(0, TWO_PI, 2000)
Zin = (r_in[:, None] * np.exp(1j * th_in)[None, :]).ravel()
int_max = np.max(np.abs(fb(Zin)))
check("C9 最大模：|z^2+1| 边界最大≈2 > 内部(r<=0.99)最大≈1.98",
      bnd_max > 1.999 and int_max < 1.985)

# ---------- C10 解析延拓越过收敛圆 ----------
S_half = np.sum(0.5 ** np.arange(61))          # |z|<1：级数收敛
div = abs(np.sum((-2.0) ** np.arange(61)))     # |z|>1：级数发散（部分和~2^60/3）
cont_val = 1.0 / (1.0 - (-2.0))                # 延拓到 ℂ\{1} 后在 z=-2 的值 = 1/3
check("C10 延拓：z=0.5 级数=1/(1-z)=2（<1e-14）；z=-2 级数发散而延拓值=1/3",
      abs(S_half - 2.0) < 1e-14 and div > 1e6 and abs(cont_val - 1.0 / 3.0) < 1e-15)

# ---------- C11 natural boundary：lacunary 级数 Σ z^{2^k} 在 dyadic 根处奇异 ----------
z8 = np.exp(2j * np.pi / 8)                    # z8^8=1；z8^{2^k}=1 对 k>=3
terms = [z8 ** ((2 ** k) % 8) for k in range(101)]   # Python int 幂模 8：避免大幂相位漂移
S100 = sum(terms)
S3 = sum(z8 ** ((2 ** k) % 8) for k in range(3))
# 函数方程见证：S_N(z) = z + S_{N-1}(z^2)（|z|<1，高阶项下溢为 0）
zc = 0.9 * np.exp(1j * 1.0)
SN = sum(zc ** (2 ** k) for k in range(101))
SNm1_sq = sum((zc ** 2) ** (2 ** k) for k in range(100))
check("C11 Hadamard 间隙级数：z=e^{2πi/8} 处 |S_100|>95（部分和线性增长=奇异）；"
      "函数方程 S(z)=z+S(z^2) 数值吻合",
      abs(S100) > 95 and abs(S100 - (S3 + 98.0)) < 1e-9
      and abs(SN - (zc + SNm1_sq)) < 1e-12)

# ---------- C12 Möbius/Cayley 变换：实轴 ↔ 单位圆（Riemann 球视角） ----------
T = lambda w: (w - 1j) / (w + 1j)
xr = np.linspace(-50, 50, 2001)
on_circle = np.max(np.abs(np.abs(T(xr)) - 1.0))
check("C12 Cayley 变换保广义圆：|T(x)|=1 对实数 x（<1e-12）；上半平面→圆内 T(2i)=1/3",
      on_circle < 1e-12 and abs(T(2j) - 1.0 / 3.0) < 1e-12 and abs(T(-2j)) > 1)

print(f"\n== 结果：{PASS}/{TOTAL} PASS ==")
raise SystemExit(0 if PASS == TOTAL else 1)
