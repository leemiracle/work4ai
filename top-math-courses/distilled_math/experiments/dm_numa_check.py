# -*- coding: utf-8 -*-
"""
card_id: DM-NUMA-01（数值分析蒸馏卡）L1 机器验证脚本
断言计数: 14（A1-A14，对应卡内 §4）
运行方式: python3 dm_numa_check.py
依赖: numpy（标准库 math 亦用）
铁律: 浮点断言全部带容差；扰动实验（A2/A3）容差放宽并注明理由。
"""
import math
import numpy as np

PASS = 0
FAIL = 0

def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")

print("== DM-NUMA-01 数值分析断言 ==")

# --- A1 浮点结合律失效（二进制表示层）---
a = (0.1 + 0.2) + 0.3
b = 0.1 + (0.2 + 0.3)
check("A1a 浮点加法不满足结合律: (0.1+0.2)+0.3 != 0.1+(0.2+0.3)", a != b)
check("A1b 差异在双精度舍入量级 |diff|<1e-15（不是 bug 是 IEEE754）", abs(a - b) < 1e-15)

# --- A2 大数吃小数（吸收）---
big = 1e16
check("A2 (1.0+1e16)+1.0 == 1.0+1e16：第二被加的 1 被完全吸收", (1.0 + big) + 1.0 == 1.0 + big)

# --- A3 Wilkinson W20：系数微扰动 -> 根剧变 ---
# W20(x) = prod_{i=1..20}(x-i)，展开系数由 numpy 精确构造（整数，float 可精确表示到 2^53）
from math import comb
# 用整数卷积构造精确系数
coeffs = [1]
for r in range(1, 21):
    # prod(x-i) = sum_{k} e_k(1..r) x^{r-k} 符号交替；直接整数递推
    new = [0] * (len(coeffs) + 1)
    for j, c in enumerate(coeffs):
        new[j] += c          # * x
        new[j + 1] -= r * c  # * (-r)
    coeffs = new
coeffs = np.array(coeffs, dtype=float)  # 最高次在前，整数系数 <=2^53 精确
roots_exact = np.roots(coeffs)
err0 = np.max(np.abs(np.sort(roots_exact.real) - np.arange(1, 21)))
check("A3a 零扰动下 roots 已偏差 >0.01：系数的浮点表示本身即扰动（u~2e-16 放大为根误差 ~6e-2）",
      err0 > 0.01)

# 对 x^19 系数（= -210）扰动 1e-8
c_pert = coeffs.copy()
c_pert[1] += 1e-8
roots_pert = np.roots(c_pert)
# 与真根（整数 1..20）的最近邻距离取最大：根位移
d = np.abs(roots_pert.reshape(-1, 1) - np.arange(1, 21).reshape(1, -1).astype(float))
max_shift = np.max(np.min(d, axis=1))
has_complex = np.max(np.abs(roots_pert.imag)) > 1e-6
# 容差说明：本断言验证的是数量级现象（相对扰动 5e-11 -> 根位移 O(1)），
# 阈值取得宽松（位移>1，复根出现），跨 numpy 版本稳定。
check("A3b 系数扰动 1e-8 -> 最大根位移 > 1（放大因子 >1e8）", max_shift > 1.0)
check("A3c 扰动后出现复根（实多项式根成对跨出实轴）", has_complex)

# --- A4 矩阵条件数：κ2 >= 1 恒成立（谱范数=σmax/σmin）---
rng = np.random.default_rng(42)
ok = all(np.linalg.cond(rng.standard_normal((5, 5)), 2) >= 1.0 - 1e-12 for _ in range(20))
check("A4 20 个随机 5x5 矩阵 κ2(A)>=1（κ=σmax/σmin>=1 是几何事实）", ok)

# --- A5 Hilbert 矩阵病态 ---
def hilbert(n):
    return 1.0 / (np.arange(1, n + 1)[:, None] + np.arange(n)[None, :])
H10 = hilbert(10)
check("A5 H10 的 κ2 > 1e12（指数级病态）", np.linalg.cond(H10, 2) > 1e12)

# --- A6 残差小 != 误差小（backward vs forward）---
n = 10
A = hilbert(n)
x_true = np.ones(n)
b = A @ x_true
x_hat = np.linalg.solve(A, b)
rel_res = np.linalg.norm(b - A @ x_hat) / np.linalg.norm(b)
rel_err = np.linalg.norm(x_hat - x_true) / np.linalg.norm(x_true)
# 容差：本断言只验证数量级分离（残差比误差小 >=4 个数量级），跨版本稳定
check(f"A6 残差小但误差大: rel_res={rel_res:.2e} < 1e-10 且 rel_err={rel_err:.2e} > 100*rel_res",
      rel_res < 1e-10 and rel_err > 100 * rel_res)

# --- A7 Runge 现象：等距 vs Chebyshev ---
def lagrange_eval(nodes, vals, x):
    x = np.asarray(x, dtype=float)
    out = np.zeros_like(x)
    for j, xj in enumerate(nodes):
        w = np.ones_like(x)
        for k, xk in enumerate(nodes):
            if k != j:
                w *= (x - xk) / (xj - xk)
        out += vals[j] * w
    return out

runge = lambda t: 1.0 / (1.0 + 25.0 * t ** 2)
n_nodes = 16  # 15 次插值
xe = np.linspace(-1, 1, n_nodes)
xc = np.cos((2 * np.arange(n_nodes) + 1) * np.pi / (2 * n_nodes))  # Chebyshev-Gauss
t = np.linspace(0.90, 0.99, 20)  # 端部是重灾区
err_eq = np.max(np.abs(lagrange_eval(xe, runge(xe), t) - runge(t)))
err_ch = np.max(np.abs(lagrange_eval(xc, runge(xc), t) - runge(t)))
check(f"A7a 等距 15 次插值在 x∈[0.90,0.99] 最大误差 err_eq={err_eq:.2f} > 1（发散）", err_eq > 1.0)
check(f"A7b Chebyshev 节同区误差 err_ch={err_ch:.2e} < 1e-2（收敛）", err_ch < 1e-2)

# --- A8 Newton 法二阶收敛（sqrt(2)）---
xs = [1.0]
for _ in range(5):
    xs.append(0.5 * (xs[-1] + 2.0 / xs[-1]))
sq2 = math.sqrt(2)
e = [abs(x - sq2) for x in xs]
# 用中段比值（末段误差已到机器精度会饱和）
ratio = e[4] / e[3] ** 2
check(f"A8 e_(k+1)/e_k^2 -> 1/(2√2)≈0.3536（实测 {ratio:.5f}，二阶收敛）",
      abs(ratio - 1 / (2 * sq2)) < 1e-3)

# --- A9 Newton 法 arctan：远初值发散（收敛域有限）---
def newton_arctan(x0, iters=20):
    x = x0
    for _ in range(iters):
        x = x - (1 + x * x) * math.atan(x)
        if not math.isfinite(x):  # 溢出后 inf-inf=nan，提前终止
            break
    return x
check("A9a arctan Newton 初值 x0=2 发散（|x|>1e3 或溢出为 inf/nan）",
      abs(newton_arctan(2.0)) > 1e3 or not math.isfinite(newton_arctan(2.0)))
check("A9b 同法初值 x0=1 收敛到 0（|x|<1e-8）", abs(newton_arctan(1.0)) < 1e-8)

# --- A10 Euler 显式格式稳定域：y'=-100y ---
lam = -100.0
def euler(h, steps, y0=1.0):
    y = y0
    for _ in range(steps):
        y *= (1.0 + h * lam)
    return y
y_bad = euler(0.05, 300)   # |1-5|=4>1 不稳定
y_good = euler(0.019, 800) # |1-1.9|=0.9<1 稳定
check(f"A10a h=0.05 超出绝对稳定域: |y|={abs(y_bad):.2e} > 1e50（爆掉）", abs(y_bad) > 1e50 or math.isinf(y_bad))
check(f"A10b h=0.019 在稳定域内: |y|={abs(y_good):.2e} < 1e-3（正确衰减）", abs(y_good) < 1e-3)

# --- A11 Simpson 四阶：h 减半误差降 ~16 倍 ---
def simpson(f, a, b, m):  # m 个子区间（偶数）
    h = (b - a) / m
    s = f(a) + f(b) + 4 * sum(f(a + (2 * i - 1) * h) for i in range(1, m // 2 + 1)) \
        + 2 * sum(f(a + 2 * i * h) for i in range(1, m // 2))
    return s * h / 3
I_true = math.e - 1.0
e8 = abs(simpson(math.exp, 0, 1, 8) - I_true)
e16 = abs(simpson(math.exp, 0, 1, 16) - I_true)
ratio = e8 / e16
check(f"A11 h 减半 Simpson 误差比 e8/e16={ratio:.2f} ∈ (12,20)（理论 ~16=2^4）", 12 < ratio < 20)

# --- A12 中心差分 U 形误差曲线：步长过小被浮点噪声淹没 ---
f, x0 = math.sin, 1.0
d_true = math.cos(1.0)
def fwd(h):
    return (f(x0 + h) - f(x0)) / h
err_tiny = abs(fwd(1e-16) - d_true)   # x0+1e-16==x0，导数算出 0
err_best = abs(fwd(1e-8) - d_true)    # 接近最优步长 √u≈1.5e-8
err_big = abs(fwd(1e-2) - d_true)
check(f"A12a h=1e-16 时 x0+h==x0：前向差分=0，误差 {err_tiny:.3f}≈|cos1|（灾难）",
      err_tiny > 0.5 and (x0 + 1e-16) == x0)
check(f"A12b 误差曲线 U 形: err(1e-8)={err_best:.2e} 同时 < err(1e-16) 和 < err(1e-2)={err_big:.2e}",
      err_best < err_tiny and err_best < err_big)

# --- A13 Kahan 补偿求和 ---
def kahan_sum(arr):
    s, c = 0.0, 0.0
    for v in arr:
        y = v - c
        t = s + y
        c = (t - s) - y
        s = t
    return s
naive = 0.0
for v in [0.1] * 10:
    naive += v
check(f"A13a 朴素累加 10 个 0.1 得 {naive!r} != 1.0", naive != 1.0)
check(f"A13b Kahan 补偿后 == 1.0（得到最近浮点）", kahan_sum([0.1] * 10) == 1.0)

# --- A14 Krylov/CG：对称正定系统上 CG n 步内收敛（有限终止性）---
def conjugate_gradient(A, b, x0=None, tol=1e-12, maxit=None):
    n = len(b)
    x = np.zeros(n) if x0 is None else x0.copy()
    r = b - A @ x
    p = r.copy()
    if maxit is None:
        maxit = n
    for k in range(maxit):
        Ap = A @ p
        alpha = r @ r / (p @ Ap)
        x += alpha * p
        r_new = r - alpha * Ap
        if np.linalg.norm(r_new) < tol:
            return x, k + 1
        beta = (r_new @ r_new) / (r @ r)
        p = r_new + beta * p
        r = r_new
    return x, maxit
M = hilbert(6) + 6 * np.eye(6)  # SPD
rhs = M @ np.arange(1.0, 7.0)
x_cg, iters = conjugate_gradient(M, rhs)
check(f"A14 CG 在 6x6 SPD 系统上 {iters} 步内收敛到 1e-12（<=n=6，有限终止性）",
      iters <= 6 and np.linalg.norm(M @ x_cg - rhs) < 1e-10)

print(f"\n结果: {PASS} PASS / {FAIL} FAIL（共 {PASS+FAIL} 断言）")
exit(0 if FAIL == 0 else 1)
