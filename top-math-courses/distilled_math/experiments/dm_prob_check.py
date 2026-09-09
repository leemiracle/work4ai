#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_prob_check.py — 蒸馏卡 DM-PROB-01（概率与随机过程）的 L1 机器断言
对应卡：../DM-PROB-01-概率与随机过程.md §4（编号 P1-P12 一一对应）
断言计数：12 组（若干组含子断言）
运行方式：python3 dm_prob_check.py   （依赖 numpy；蒙特卡洛 seed 固定）
铁律：浮点断言带容差；蒙特卡洛断言容差放宽（≥1e-2）并固定 seed。
"""
import math
import numpy as np

PASS, TOTAL = 0, 0

def check(name, cond):
    global PASS, TOTAL
    TOTAL += 1
    ok = bool(cond)
    PASS += ok
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")

rng = np.random.default_rng(42)

def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def ks_vs_normal(samples, mu, sd):
    """单样本 Kolmogorov 距离（vs N(mu, sd^2) 的经验上确界近似）。"""
    z = np.sort((np.asarray(samples) - mu) / sd)
    n = len(z)
    cdf = np.array([norm_cdf(v) for v in z])
    emp_hi = np.arange(1, n + 1) / n
    emp_lo = np.arange(0, n) / n
    return max(np.max(np.abs(emp_hi - cdf)), np.max(np.abs(emp_lo - cdf)))

print("== DM-PROB-01 概率与随机过程 · L1 断言 ==")

# ---------- P1 对称 gambler's ruin：P(先到 N) = i/N（MC，seed 固定）----------
N, i0, trials = 10, 3, 50000
steps = rng.choice([-1, 1], size=(trials, 200))     # 200 步足够到达（E[T]=21，P(T>200)<1e-6）
pos = np.full(trials, i0)
won = np.zeros(trials, dtype=bool)
active = np.ones(trials, dtype=bool)
for k in range(200):
    pos[active] += steps[active, k]
    won[active & (pos == N)] = True
    active[pos == 0] = False
    active[won] = False
    if not active.any():
        break
mc1 = won.mean()
check("P1 对称 gambler's ruin：MC P(先到 N)=%.4f ≈ i/N=0.3（|Δ|<0.01）" % mc1,
      abs(mc1 - i0 / N) < 0.01)

# ---------- P2 对称期望时长 E[T] = i(N-i) = 21（MC，容差 2.0）----------
pos = np.full(trials, i0); T = np.zeros(trials)
active = np.ones(trials, dtype=bool)
for k in range(200):
    pos[active] += steps[active, k]
    T[active] += 1
    active[(pos == 0) | (pos == N)] = False
    if not active.any():
        break
check("P2 对称期望时长：MC E[T]=%.2f ≈ i(N-i)=21（|Δ|<2.0）" % T.mean(),
      abs(T.mean() - i0 * (N - i0)) < 2.0)

# ---------- P3 非对称公式 (1-r^i)/(1-r^N), r=q/p（MC vs 解析）----------
p, q = 0.45, 0.55
r = q / p
exact3 = (1 - r**i0) / (1 - r**N)
steps3 = (rng.random((trials, 400)) < p).astype(int) * 2 - 1
pos = np.full(trials, i0); won = np.zeros(trials, dtype=bool); active = np.ones(trials, dtype=bool)
for k in range(400):
    pos[active] += steps3[active, k]
    won[active & (pos == N)] = True
    active[(pos == 0) | won] = False
    if not active.any():
        break
mc3 = won.mean()
check("P3 非对称 p=0.45：MC P=%.4f ≈ 解析 (1-r^i)/(1-r^N)=%.4f（|Δ|<0.01）" % (mc3, exact3),
      abs(mc3 - exact3) < 0.01)

# ---------- P4 CLT：uniform(0,1) 30-样本均值标准化 → N(0,1) ----------
means = rng.uniform(0, 1, size=(10000, 30)).mean(axis=1)
z = (means - 0.5) / math.sqrt(1.0 / 12.0 / 30.0)
ks4 = ks_vs_normal(z, 0.0, 1.0)
check("P4 CLT：KS=%.4f < 0.05，|mean|=%.4f<0.05，|std-1|=%.4f<0.05" % (ks4, z.mean(), abs(z.std() - 1)),
      ks4 < 0.05 and abs(z.mean()) < 0.05 and abs(z.std() - 1) < 0.05)

# ---------- P5 两两独立 XOR 分布：三对独立、联合违反（精确枚举）----------
# X,Y iid Bern(1/2)，Z=X⊕Y：(x,y) 四点等概 1/4
pts = [(0, 0), (0, 1), (1, 0), (1, 1)]
prob = {}
for x, y in pts:
    prob[(x, y, x ^ y)] = 0.25
marg = lambda idx, v: sum(p_ for k, p_ in prob.items() if k[idx] == v)
pair_ok = all(
    abs(sum(p_ for k, p_ in prob.items() if k[a] == va and k[b] == vb) - marg(a, va) * marg(b, vb)) < 1e-12
    for (a, b) in [(0, 1), (0, 2), (1, 2)] for va in (0, 1) for vb in (0, 1)
)
joint_ok = abs(prob.get((1, 1, 1), 0.0) - 0.125) > 1e-12   # P(X=Y=Z=1)=0 ≠ 1/8
check("P5 XOR：全部 12 个两对边缘独立 + P(1,1,1)=0≠1/8（联合不独立）", pair_ok and joint_ok)

# ---------- P6 Cauchy 反例：5-样本均值与单样本同分布（CLT 失效）----------
g5 = rng.standard_cauchy(size=(10000, 5)).mean(axis=1)
g5 = g5[np.abs(g5) < 50]                     # 截尾显示用（Cauchy 重尾，截尾不改 CDF 主段对比）
cdf_cauchy = lambda x: 0.5 + np.arctan(x) / np.pi
zs = np.sort(g5); n6 = len(zs)
c6 = cdf_cauchy(zs)
ks6 = max(np.max(np.abs(np.arange(1, n6 + 1) / n6 - c6)), np.max(np.abs(np.arange(0, n6) / n6 - c6)))
check("P6 Cauchy 稳定性：5-均值 vs Cauchy CDF 的 KS=%.4f < 0.05（均值不集中→SLLN/CLT 双失效）" % ks6,
      ks6 < 0.05)

# ---------- P7 高斯壳：n=2000，半径相对波动 O(1/√n)；均值小球质量≈0 ----------
n7, m7 = 2000, 1000
g = rng.standard_normal((m7, n7))
rad = np.linalg.norm(g, axis=1) / math.sqrt(n7)
frac_in = np.mean((rad > 0.95) & (rad < 1.05))
check("P7a 高斯壳：%.1f%% 样本 ‖g‖/√n ∈ [0.95,1.05]（≥98%%）" % (100 * frac_in), frac_in >= 0.98)
sd_theory = 1.0 / math.sqrt(2.0 * n7)
check("P7b 壳厚：SD=%.4f ≈ 1/√(2n)=%.4f（|Δ|<0.005）" % (rad.std(), sd_theory),
      abs(rad.std() - sd_theory) < 0.005)
small = np.mean(np.linalg.norm(rng.standard_normal((200, n7)), axis=1) <= 0.1 * math.sqrt(n7))
check("P7c 均值小球质量：P(‖g‖≤0.1√n)=%.4f ≈ 0（e^{-O(n)}，直觉陷阱见证）" % small, small < 0.001)

# ---------- P8 反射原理：E[max S_k]/√n → √(2/π)≈0.7979 ----------
n8, t8 = 2000, 10000
rw = np.cumsum(rng.choice([-1, 1], size=(t8, n8)), axis=1)
mx = rw.max(axis=1) / math.sqrt(n8)
check("P8 反射原理：MC E[max/√n]=%.4f ≈ √(2/π)=0.7979（|Δ|<0.02）" % mx.mean(),
      abs(mx.mean() - math.sqrt(2 / math.pi)) < 0.02)

# ---------- P9 Optional stopping 活演示：E[M_{T∧n}]=0 但 M_T=1 ----------
n9, t9 = 10000, 20000
hits = np.zeros(t9, dtype=bool); end = np.zeros(t9)
pos = np.zeros(t9); active = np.ones(t9, dtype=bool)
for k in range(n9):
    pos[active] += np.where(rng.integers(0, 2, size=active.sum()) == 1, 1, -1)
    newly = active & (pos == 1)
    hits[newly] = True
    active[newly] = False
    if not active.any():
        break
end[hits] = 1.0                                 # M_T = 1（命中者）
end[~hits] = pos[~hits]                          # 未命中者 M_{T∧n} = S_n
m_tn = end.mean()                                # OST（T∧n 有界）⟹ E[M_{T∧n}]=E[M₀]=0；但 M_T≡1（UI 失败）
check("P9 OST：MC E[M_{T∧n}]=%.4f ≈ 0（T∧n 有界→定理有效）；而 P(T≤n)=%.4f→M_T≡1≠0=E[M₀]（UI 失败）"
      % (m_tn, hits.mean()),
      abs(m_tn) < 0.2 and hits.mean() > 0.98)

# ---------- P10 临界 Galton–Watson：灭绝 a.s. 但 E[Z_n]≡1 ----------
t10, gens = 5000, 50
Z = np.full(t10, 1, dtype=np.int64)
for _ in range(gens):
    Z = 2 * rng.binomial(Z, 0.5)             # 后代 0/2 各半（临界，σ²=1），且 Z_n 保持鞅
ext = np.mean(Z == 0)
check("P10 临界 GW：灭绝率=%.3f > 0.90（理论≈2/(σ²n)=0.96）且 E[Z_50]=%.3f ≈ 1（|Δ|<0.3）" % (ext, Z.mean()),
      ext > 0.90 and abs(Z.mean() - 1.0) < 0.3)

# ---------- P11 tower property：具体联合分布 E[E[X|Y]]=E[X]（精确）----------
P11 = {(0, 0): 0.1, (0, 1): 0.2, (0, 2): 0.1, (1, 0): 0.2, (1, 1): 0.1, (1, 2): 0.3}
EX = sum(x * pr for (x, y), pr in P11.items())
EXgY = sum(PY * EXy
           for y, PY in [(y, sum(pr for (x, yy), pr in P11.items() if yy == y)) for y in (0, 1, 2)]
           for EXy in [sum(x * pr for (x, yy), pr in P11.items() if yy == y) / PY])
check("P11 tower：E[E[X|Y]]=%.6f = E[X]=%.6f（精确）" % (EXgY, EX), abs(EXgY - EX) < 1e-12)

# ---------- P12 周期链振荡 vs 懒惰链收敛（矩阵幂）----------
Pp = np.array([[0.0, 1.0], [1.0, 0.0]])
d0 = np.array([1.0, 0.0])
even = np.linalg.matrix_power(Pp, 100) @ d0
odd = np.linalg.matrix_power(Pp, 101) @ d0
Pl = np.array([[0.5, 0.5], [0.5, 0.5]])
lazy = np.linalg.matrix_power(Pl, 50) @ d0
check("P12 周期陷阱：2-循环链 P^100δ₀=%.0f / P^101δ₀=%.0f（振荡不收敛）；懒惰版 P^50δ₀≈[0.5,0.5]"
      % (even[0], odd[0]),
      abs(even[0] - 1) < 1e-9 and abs(odd[1] - 1) < 1e-9 and np.allclose(lazy, [0.5, 0.5], atol=1e-9))

print(f"\n结果：{PASS}/{TOTAL} 断言通过" + ("  [ALL PASS]" if PASS == TOTAL else "  [HAS FAIL]"))
raise SystemExit(0 if PASS == TOTAL else 1)
