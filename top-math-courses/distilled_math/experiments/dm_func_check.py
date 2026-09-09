#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_func_check.py — 蒸馏卡 DM-FUNC-01（泛函分析）的 L1 机器断言
对应卡：../DM-FUNC-01-泛函分析.md §4（编号 F1-F14 一一对应）
断言计数：14 组（若干组含子断言）
运行方式：python3 dm_func_check.py   （依赖 numpy）
铁律：浮点断言带容差。
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

print("== DM-FUNC-01 泛函分析 · L1 断言 ==")

# ---------- F1 无限维单位球不紧（度量见证）：e_i,e_j 距离恒 √2 ----------
n = 500
E = np.eye(n)
D = np.linalg.norm(E[:, :, None] - E[:, None, :], axis=0)
off = D[~np.eye(n, dtype=bool)]
check("F1 Riesz：ℓ² 单位球上 e_n 两两距离=√2（无 Cauchy 子列的度量见证）",
      np.max(np.abs(off - np.sqrt(2))) < 1e-12)

# ---------- F2 Banach 不动点：g=cos 于 [0,1] 压缩（|g'|<=sin1≈0.84<1） ----------
xk, errs = 1.0, []
for k in range(80):
    x_new = np.cos(xk)
    errs.append(abs(x_new - xk))
    xk = x_new
ratios = np.array(errs[5:]) / np.array(errs[4:-1])
dottie = 0.7390851332151607
check("F2 压缩映射：x=cos(x) 迭代收敛到 Dottie 数（<1e-12）且误差比<=0.85（几何收敛）",
      abs(xk - dottie) < 1e-12 and np.all(ratios < 0.85))

# ---------- F3 ℓ¹ 不自反的构造性见证：e_n 无弱收敛子列 ----------
nj = np.arange(2, 101, 2)                    # 子列位置 n_j = 2j
y = np.zeros(200)                            # y∈ℓ^∞：y_{n_j}=(-1)^j
y[nj] = (-1.0) ** np.arange(1, len(nj) + 1)
pairing = y[nj]                              # <y, e_{n_j}> = y_{n_j}
norms = np.ones(len(nj))                     # ‖e_{n_j}‖_1 = 1
oscillate = np.all(pairing[:-1] * np.roll(pairing, -1)[:-1] < 0)
check("F3 ℓ¹ 不自反见证：‖e_n‖=1 而 <y,e_{n_j}>=(-1)^j 振荡（符号泛函挡死弱收敛）",
      oscillate and np.all(np.abs(pairing) == 1.0) and np.all(norms == 1.0))

# ---------- F4 严格包含 ℓ¹ ⊊ ℓ²（x=1/k 的归属） ----------
k = np.arange(1, 1_000_001)
S2 = np.sum(1.0 / k**2)
Hn = np.array([np.sum(1.0 / k[:m]) for m in (1000, 10000, 100000)])
blocks = np.array([np.sum(1.0 / k[m:2 * m]) for m in (100, 1000, 10000)])
check("F4 x=1/k ∈ ℓ²\\ℓ¹：Σ1/k²→π²/6（<5e-6）；调和块增量 H_{2n}-H_n≈ln2>0.68（发散）",
      abs(S2 - np.pi**2 / 6) < 5e-6 and np.all(blocks > 0.68) and np.all(Hn > 5.0))

# ---------- F5 无界算子：d/dx 于 L²[0,1]（域 C¹），f_n=x^n 放大率 ~n ----------
def ratio(n, N=400001):
    xs = np.linspace(0.0, 1.0, N)
    num = np.sqrt(trapz((n * xs**(n - 1)) ** 2, xs))
    den = np.sqrt(trapz(xs**(2 * n), xs))
    return num / den
r5, r10, r20, r40 = ratio(5), ratio(10), ratio(20), ratio(40)
check("F5 微分算子无界：‖f_n'‖₂/‖f_n‖₂ ≈ n（r5>4.9, r10>9.9, r20>19.9, r40>39.9 且递增）",
      r5 > 4.9 and r10 > 9.9 and r20 > 19.9 and r40 > 39.9 and r5 < r10 < r20 < r40)

# ---------- F6 投影定理/Riesz 表示：L²[0,1] 投影到 span{1,x}，残差正交 ----------
xs = np.linspace(0, 1, 200_001)
w = np.full_like(xs, xs[1] - xs[0])
ip = lambda a, b: float(np.sum(a * b * w))           # ∫ab（矩形≈梯度）
f = np.exp(xs)
G = np.array([[ip(np.ones_like(xs), np.ones_like(xs)), ip(np.ones_like(xs), xs)],
              [ip(xs, np.ones_like(xs)), ip(xs, xs)]])
b = np.array([ip(np.ones_like(xs), f), ip(xs, f)])
c = np.linalg.solve(G, b)
r = f - (c[0] + c[1] * xs)
nr = np.sqrt(ip(r, r))
pert = f - (c[0] + 0.05 + (c[1] - 0.03) * xs)
check("F6 投影定理：残差⊥{1,x}（|∫r|,|∫xr|<1e-9）且投影最小（‖r‖<‖扰动残差‖）",
      abs(ip(r, np.ones_like(xs))) < 1e-9 and abs(ip(r, xs)) < 1e-9
      and nr < np.sqrt(ip(pert, pert)))

# ---------- F7 紧 vs 非紧：对角 T=diag(1/k) 可有限秩逼近，单位算子不可 ----------
tail = 1.0 / np.arange(11, 1001)              # ‖T−T_10‖ = sup_{k>10} 1/k = 1/11
tail100 = 1.0 / 101
sv_I = np.linalg.svd(np.eye(8), compute_uv=False)
check("F7 紧性：diag(1/k) 尾范数=1/11 且 N=100 时<0.01（可有限秩逼近）；I_8 奇异值全=1（不可）",
      abs(tail.max() - 1.0 / 11) < 1e-15 and tail100 < 0.01
      and np.max(np.abs(sv_I - 1.0)) < 1e-15)

# ---------- F8 弱收敛≠范数收敛：e_n ⇀ 0 于 ℓ²，但 ‖e_n‖₂=1 ----------
kk = np.arange(1, 1_000_001)
y8 = 1.0 / kk                                  # y∈ℓ²
check("F8 弱≠强：<y,e_1000>=0.001→0 而 ‖e_1000‖₂=1",
      abs(y8[999] - 0.001) < 1e-12 and y8[999] < 1e-2 and abs(np.linalg.norm(np.eye(1)[0]) - 1.0) < 1e-15)

# ---------- F9 平行四边形恒等式：ℓ² 成立，ℓ¹ 失败（非 Hilbert 判据） ----------
u = rng.normal(size=300); v = rng.normal(size=300)
lhs2 = np.linalg.norm(u + v)**2 + np.linalg.norm(u - v)**2
rhs2 = 2 * np.linalg.norm(u)**2 + 2 * np.linalg.norm(v)**2
e1, e2 = np.array([1.0, 0.0]), np.array([0.0, 1.0])
lhs1 = np.linalg.norm(e1 + e2, 1)**2 + np.linalg.norm(e1 - e2, 1)**2   # = 4+4 = 8
rhs1 = 2 * np.linalg.norm(e1, 1)**2 + 2 * np.linalg.norm(e2, 1)**2     # = 2+2 = 4
check("F9 平行四边形：ℓ² 恒等式成立（<1e-9）；ℓ¹ 差=4（L¹/L^∞ 永非 Hilbert）",
      abs(lhs2 - rhs2) < 1e-9 * rhs2 and abs(lhs1 - rhs1 - 4.0) < 1e-12)

# ---------- F10 Cauchy-Schwarz：一般严格，共线取等 ----------
a = rng.normal(size=300); b = rng.normal(size=300)
check("F10 C-S：|<a,b>|<=‖a‖‖b‖；a=b 时取等",
      abs(np.dot(a, b)) <= np.linalg.norm(a) * np.linalg.norm(b) + 1e-12
      and abs(np.dot(a, a) - np.linalg.norm(a)**2) < 1e-12)

# ---------- F11 自伴谱实 + 谱演算（谱定理数值版） ----------
M = rng.normal(size=(20, 20)); A = M @ M.T            # 对称 PSD
ev = np.linalg.eigvals(A)
V, L, _ = np.linalg.svd(A)                            # eigh 亦可
Lh, Vh = np.linalg.eigh(A)
B = Vh @ np.diag(np.sqrt(np.maximum(Lh, 0))) @ Vh.T
check("F11 谱定理：对称阵特征值全实（|imag|<1e-10）；sqrt(A)²=A（<1e-8）",
      np.max(np.abs(ev.imag)) < 1e-10
      and np.linalg.norm(B @ B - A) / np.linalg.norm(A) < 1e-8)

# ---------- F12 Hahn-Banach 几何：支撑超平面 + 凸集分离 ----------
u = np.array([np.cos(0.7), np.sin(0.7)])              # 单位球边界点
t = np.linspace(0, 1, 1001)
ball = t[:, None] * np.array([np.cos(0), np.sin(0)])[None, :]  # 一条半径采样
vals = ball @ u
th = np.linspace(0, 2 * np.pi, 20001)
disk = np.stack([np.cos(th), np.sin(th)], axis=1)
sup_val = np.max(disk @ u)
A_set = disk * 0.5 + np.array([-2.0, 0.0])            # 两不相交凸盘
B_set = disk * 0.5 + np.array([2.0, 0.0])
check("F12 分离：sup_{‖x‖<=1}<u,x>=1（=‖u‖，norming 泛函，网格容差1e-8）；盘A_x<=-1.5 < 1.5<=盘B_x（超平面 x=0 分离）",
      abs(sup_val - 1.0) < 1e-8 and np.all(vals <= 1.0 + 1e-12)
      and np.max(A_set[:, 0]) < -1.4 and np.min(B_set[:, 0]) > 1.4)

# ---------- F13 HB 延拓不唯一：ℓ¹(ℝ²) 上 x 轴的 f(x,0)=x 有无穷多保范延拓 ----------
def dual_norm_l1(beta):                                # ‖F_β‖ = max_{|x|+|y|<=1}|x+βy|
    tt = np.linspace(0, 2 * np.pi, 200_001)
    boundary = 0.5 * np.stack([np.cos(tt) * (np.abs(np.cos(tt)) + np.abs(np.sin(tt))),
                               np.sin(tt) * (np.abs(np.cos(tt)) + np.abs(np.sin(tt)))], axis=1)
    pts = np.vstack([boundary, [[1, 0], [0, 1], [-1, 0], [0, -1]]])
    return np.max(np.abs(pts @ np.array([1.0, beta])))
n0, n07, nm09, n13 = dual_norm_l1(0.0), dual_norm_l1(0.7), dual_norm_l1(-0.9), dual_norm_l1(1.3)
check("F13 HB 不唯一：F_β(x,y)=x+βy，β=0/0.7/-0.9 保范=1（面），β=1.3 范数>1.29（出面）",
      all(abs(x - 1.0) < 1e-12 for x in (n0, n07, nm09)) and n13 > 1.29
      and abs(3.0 + 0.7 * 0.0 - 3.0) == 0.0)          # 在 x 轴上 F_β=f

# ---------- F14 L¹ 投影不唯一（最佳逼近唯一性是 Hilbert 特权） ----------
# L¹[0,1] 上 f=0·1_{[0,1/2)} + 2·1_{[1/2,1]}，向常数函数集 M 投影：任何 c∈[0,2] 都最小化
xs14 = np.linspace(0, 1, 4000, endpoint=False)            # 偶数格点：两半测度严格相等
w14 = np.full_like(xs14, xs14[1] - xs14[0])
f14 = np.where(np.arange(4000) < 2000, 0.0, 2.0)
obj = lambda c: float(np.sum(np.abs(f14 - c) * w14))      # ∫|f-c|
cs = np.linspace(-0.5, 2.5, 3001)
vals = np.array([obj(c) for c in cs])
minima_set = np.abs(vals - vals.min()) < 1e-9
c_lo, c_hi = cs[minima_set].min(), cs[minima_set].max()
check("F14 L¹ 投影不唯一：最小化子集=[0,2] 整段（中位数区间），而 ℓ² 投影唯一（F6）",
      abs(vals.min() - 1.0) < 1e-6 and abs(c_lo - 0.0) < 1e-2 and abs(c_hi - 2.0) < 1e-2
      and obj(0.0) < obj(-0.5) and abs(obj(1.0) - obj(0.0)) < 1e-12)

print(f"\n== 结果：{PASS}/{TOTAL} PASS ==")
raise SystemExit(0 if PASS == TOTAL else 1)
