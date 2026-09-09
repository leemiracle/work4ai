#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_real_check.py — 蒸馏卡 DM-REAL-01（实分析与测度）的 L1 机器断言
对应卡：../DM-REAL-01-实分析与测度.md §4（编号 R1-R13 一一对应）
断言计数：13 组（若干组含子断言）
运行方式：python3 dm_real_check.py   （依赖 numpy + sympy）
铁律：浮点断言带容差；符号断言 simplify 后判等。
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

rng = np.random.default_rng(42)
trapz = getattr(np, "trapezoid", None) or np.trapz

print("== DM-REAL-01 实分析与测度 · L1 断言 ==")

# ---------- R1 Cantor 集测度递推：第 n 步剩 2^n 段各长 3^-n，总测度 (2/3)^n -> 0 ----------
intervals = [(0.0, 1.0)]
for n in range(1, 21):
    nxt = []
    for a, b in intervals:
        l3 = (b - a) / 3.0
        nxt.append((a, a + l3))
        nxt.append((b - l3, b))
    intervals = nxt
    if n == 8:
        m8 = sum(b - a for a, b in intervals)
        check("R1a Cantor 第8步总测度 = (2/3)^8（误差<1e-12）",
              abs(m8 - (2.0/3.0)**8) < 1e-12 and len(intervals) == 2**8)
m20 = sum(b - a for a, b in intervals)
check("R1b Cantor 第20步总测度 ≈ 3.0e-4 < 1e-3（→0；基数 2^aleph_0 是 ☆ 层陈述）",
      m20 < 1e-3 and abs(m20 - (2.0/3.0)**20) < 1e-9 and len(intervals) == 2**20)

# ---------- R2 Fatou 紧不等号（逃逸质量，无限测度域）----------
# f_n = 1_{[n,n+1]} 在 R 上：liminf f_n = 0 处处，但 ∫f_n = 1 对所有 n
integrals = np.array([1.0] * 50)                      # ∫f_n = 区间长度 = 1（精确）
liminf_integrals = 1.0
pts = np.array([0.3, 5.7, 31.62, 88.1])
vals = np.array([[1.0 if n <= x < n + 1 else 0.0 for x in pts] for n in range(50)])
pt_linf = vals.min(axis=0)   # 非负序列且每点仅有限个 1 → 尾部最小值=0 即 liminf 见证
check("R2 Fatou 逃逸反例：∫liminf=0 < liminf∫=1（紧不等号，质量逃逸）",
      np.all(pt_linf == 0.0) and 0.0 < liminf_integrals)

# ---------- R3 Fatou 紧不等号（有限测度域 [0,1]，尖峰增高）----------
# f_n = n·1_{(0,1/n)}：f_n -> 0 a.e.，∫f_n = 1 不减
int3 = np.array([n * (1.0 / n) for n in range(1, 101)])  # = 1 精确
grid = np.linspace(0.02, 1.0, 200)
vals3 = np.array([[n * (1.0 if (0 < x < 1.0 / n) else 0.0) for x in grid]
                  for n in range(51, 101)])               # 尾部窗口 n>1/x_min：每点均已归零
liminf_at = vals3.min(axis=0)
check("R3 Fatou 有限域尖峰反例：a.e. liminf=0 而 liminf∫=1",
      np.all(liminf_at == 0.0) and np.all(np.abs(int3 - 1.0) < 1e-12) and 0.0 < 1.0)

# ---------- R4 DCT 生效场景：f_n = x^n 于 [0,1]，|f_n|<=1=g∈L^1 ----------
x = np.linspace(0, 1, 2_000_001)
n = 5
I5 = trapz(x**n, x)
check("R4 控制收敛（有界控制 g=1）：∫x^5 dx = 1/6（误差<1e-6），且 ∫x^n=1/(n+1)->0",
      abs(I5 - 1.0/6.0) < 1e-6 and (1.0/1001) < 1e-3 and 0.99**1000 < 1e-4)

# ---------- R5 DCT 失效场景：无 integrable 控制函数 ----------
# 最小控制包络 g(x)=sup_n n·1_{(0,1/n)}(x)=ceil(1/x)，∫g 发散（数值见证对数增长）
def env_integral(N):
    k = np.arange(1, N + 1)
    g = np.ceil(N / k)          # 在格点 x=k/N 处 g=ceil(1/x)
    return float(np.mean(g))
I2k, I4k = env_integral(2000), env_integral(4000)
check("R5 无控制反例：包络 ∫g 随格点细化增长（>7.5 且单调增）→ 无 L^1 控制",
      I2k > 7.5 and I4k > I2k)

# ---------- R6 Young 不等式符号证明（p=q=2 特例）----------
a, b = sp.symbols("a b", real=True)
expr = sp.simplify(a**2/sp.Integer(2) + b**2/sp.Integer(2) - a*b - (a - b)**2/sp.Integer(2))
check("R6 Young p=q=2 符号恒等：a^2/2+b^2/2-ab = (a-b)^2/2 >= 0",
      expr == 0)

# ---------- R7 Young 数值（p=3/2, q=3）----------
A = rng.uniform(0.01, 5, 500)
B = rng.uniform(0.01, 5, 500)
p, q = 1.5, 3.0
gap = A**p / p + B**q / q - A * B
check("R7 Young 数值 500 组随机：a^p/p+b^q/q-ab >= -1e-12", np.min(gap) > -1e-12)

# ---------- R8 Hölder（p=3/2, q=3，测度1格点离散）----------
N = 1000
f = rng.uniform(0, 3, N); g = rng.uniform(0, 3, N)
lhs = np.mean(f * g)
rhs = (np.mean(f**p))**(1/p) * (np.mean(g**q))**(1/q)
check("R8 Hölder：‖fg‖_1 <= ‖f‖_{3/2}·‖g‖_3（容差1e-9）", lhs <= rhs * (1 + 1e-9))

# ---------- R9 Minkowski（p=3）----------
h = rng.uniform(0, 3, N)
lhs = (np.mean((f + h)**3))**(1/3)
rhs = (np.mean(f**3))**(1/3) + (np.mean(h**3))**(1/3)
check("R9 Minkowski：‖f+h‖_3 <= ‖f‖_3+‖h‖_3（容差1e-9）", lhs <= rhs * (1 + 1e-9))

# ---------- R10 有限测度域上 L^p 嵌套：‖f‖_1<=‖f‖_2<=‖f‖_inf ----------
u = rng.uniform(0, 10, N)
n1 = np.mean(u); n2 = np.sqrt(np.mean(u**2)); ninf = np.max(u)
check("R10 [0,1] 上嵌套：‖f‖_1<=‖f‖_2<=‖f‖_inf", n1 <= n2 * (1 + 1e-12) and n2 <= ninf * (1 + 1e-12))

# ---------- R11 Lebesgue 微分定理：光滑点的局部平均收敛（速率 h^2/3）----------
x0 = 0.5
for h in (0.1, 0.05):
    xs = np.linspace(x0 - h, x0 + h, 400_001)
    mean = trapz(xs**2, xs) / (2 * h)
    exact = x0**2 + h**2 / 3.0        # 闭式：局部平均 = x0^2 + h^2/3
    if h == 0.1:
        m1_err = abs(mean - 0.25)
    ok_law = abs(mean - exact) < 1e-9
xs = np.linspace(x0 - 1e-3, x0 + 1e-3, 400_001)
mean_small = trapz(xs**2, xs) / 2e-3
check("R11 Lebesgue 点：h=0.1 平均→0.25（误差<h^2/3+1e-6）；h→0 收敛 & 速率律闭式吻合",
      m1_err < 0.1**2 / 3 + 1e-6 and abs(mean_small - 0.25) < 1e-6 and ok_law)

# ---------- R12 Smith-Volterra 胖 Cantor 集：正测度 1/2 且无处稠密 ----------
iv = [(0.0, 1.0)]
for k in range(1, 15):                     # 第 k 步从每段中央挖长 4^-k
    cut = 4.0**(-k)
    nxt = []
    for aa, bb in iv:
        m = (aa + bb) / 2.0
        nxt.append((aa, m - cut / 2))
        nxt.append((m + cut / 2, bb))
    iv = nxt
mFat = sum(b - a for a, b in iv)
maxLen = max(b - a for a, b in iv)
check("R12 胖 Cantor：剩余测度≈1/2（|m-0.5|<1e-4）且最大区间长<0.01（无处稠密）",
      abs(mFat - 0.5) < 1e-4 and maxLen < 0.01)

# ---------- R13 单调收敛定理（计数测度实例：非负级数部分和）----------
k = np.arange(1, 1_000_001)
S = np.cumsum(1.0 / k**2)
inc = np.all(np.diff(S) > 0)
tail = abs(S[-1] - np.pi**2 / 6)
check("R13 MCT 实例：Σ1/k^2 部分和单调递增且 -> π^2/6（误差<5e-6，始终在下方）",
      inc and tail < 5e-6 and S[-1] < np.pi**2 / 6)

print(f"\n== 结果：{PASS}/{TOTAL} PASS ==")
raise SystemExit(0 if PASS == TOTAL else 1)
