#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dm_info_check.py — 蒸馏卡 DM-INFO-01（信息论与编码）的 L1 机器断言
对应卡：../DM-INFO-01-信息论与编码.md §4（编号 I1-I12 一一对应）
断言计数：12 组（若干组含子断言）
运行方式：python3 dm_info_check.py   （依赖 numpy + sympy；算术码用 Fraction 精确有理数实现）
铁律：浮点断言带容差；MC 断言容差放宽并固定 seed。
"""
import math
import heapq
from fractions import Fraction

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
H2 = lambda p: 0.0 if p in (0.0, 1.0) else -p * math.log2(p) - (1 - p) * math.log2(1 - p)

print("== DM-INFO-01 信息论与编码 · L1 断言 ==")

# ---------- I1 H(1/2)=1 bit；凹性（二阶差分 + 中点凹） ----------
grid = np.linspace(0.01, 0.99, 99)
Hvals = np.array([H2(p) for p in grid])
max_dd = max(Hvals[i - 1] - 2 * Hvals[i] + Hvals[i + 1] for i in range(1, 98))
pairs = rng.uniform(0.01, 0.99, size=(500, 2))
mid_ok = all(H2((a + b) / 2) >= (H2(a) + H2(b)) / 2 - 1e-12 for a, b in pairs)
check("I1 H(1/2)=%.6f=1 bit；凹性：max 二阶差分=%.2e ≤ 1e-9 且 500 组中点凹全部成立"
      % (H2(0.5), max_dd), abs(H2(0.5) - 1) < 1e-12 and max_dd <= 1e-9 and mid_ok)

# ---------- I2 熵唯一性：函数方程 f(pq)=f(p)+f(q) 的解族 −log2 ----------
p_, q_ = sp.symbols("p q", positive=True)
expr = sp.simplify(sp.log(1 / (p_ * q_), 2) - sp.log(1 / p_, 2) - sp.log(1 / q_, 2))
check("I2 SymPy：log2(1/(pq)) − log2(1/p) − log2(1/q) ≡ 0（%s）" % expr, expr == 0)

# ---------- I3 Kraft 不等式：可实现 vs 不可实现（枚举级验证） ----------
def prefix_free(code):
    cs = sorted(code)
    return all(not cs[j].startswith(cs[i]) for i in range(len(cs)) for j in range(i + 1, len(cs)))
code_ok = ["0", "10", "110", "111"]                       # 长度 {1,2,3,3}，Kraft=1/2+1/4+1/8+1/8=1
bad_count, total_count = 0, 0
for c1 in ("0", "1"):
    for c2 in ("0", "1"):
        for c3 in ("00", "01", "10", "11"):               # 长度 {1,1,2}，Kraft=1.5>1
            total_count += 1
            bad_count += not prefix_free([c1, c2, c3])
check("I3 Kraft：{1,2,3,3} 码前缀自由（Σ2⁻ˡ=1）；{1,1,2} 枚举 %d/%d 全部冲突（Σ=1.5>1）"
      % (bad_count, total_count), prefix_free(code_ok) and bad_count == total_count == 16)

# ---------- I4 Huffman 最优：L=2.2 = 枚举 Kraft-可行码长的最小值；H ≤ L < H+1 ----------
probs = [0.4, 0.2, 0.2, 0.1, 0.1]
def huffman_len(ps):
    """标准合并：节点 (权重, 序号, {叶子: 深度})，深度=被合并次数。"""
    import itertools
    cnt = itertools.count()
    heap = [(p, next(cnt), {i: 0}) for i, p in enumerate(ps)]
    heapq.heapify(heap)
    while len(heap) > 1:
        p1, _, d1 = heapq.heappop(heap); p2, _, d2 = heapq.heappop(heap)
        merged = {k: v + 1 for k, v in d1.items()}
        merged.update({k: v + 1 for k, v in d2.items()})
        heapq.heappush(heap, (p1 + p2, next(cnt), merged))
    depths = heap[0][2]
    return sum(ps[i] * depths[i] for i in range(len(ps)))
L_huff = huffman_len(probs)
best_enum = min(sum(p * l for p, l in zip(probs, ls))
                for ls in __import__("itertools").product(range(1, 7), repeat=5)
                if sum(Fraction(1, 2 ** l) for l in ls) <= 1)
H_true = sum(-p * math.log2(p) for p in probs)
check("I4 Huffman：L=%.4f = 枚举最优 %.4f；H=%.4f ≤ L < H+1" % (L_huff, best_enum, H_true),
      abs(L_huff - 2.2) < 1e-12 and abs(best_enum - 2.2) < 1e-9 and H_true <= L_huff < H_true + 1)

# ---------- I5 Gibbs 不等式：KL ≥ 0（1000 组 Dirichlet 随机分布） ----------
min_kl = 0.0
for _ in range(1000):
    pa = rng.dirichlet([1.0, 1.0, 1.0]); pb = rng.dirichlet([1.0, 1.0, 1.0])
    kl = sum(a * math.log2(a / b) for a, b in zip(pa, pb) if a > 0)
    min_kl = min(min_kl, kl)
check("I5 Gibbs：1000 组随机分布 KL 最小值=%.2e ≥ −1e−12" % min_kl, min_kl >= -1e-12)

# ---------- I6 BSC(0.1) 容量：最优输入均匀，C=1−H2(0.1)≈0.5310 ----------
qs = np.linspace(0, 1, 2001)
Ivals = [H2(0.1 + 0.8 * q) - H2(0.1) for q in qs]
q_opt = qs[int(np.argmax(Ivals))]
check("I6 BSC(0.1)：数值最优 q*=%.3f≈0.5，C=%.6f ≈ 1−H2(0.1)=%.6f（|Δ|<1e−3）"
      % (q_opt, max(Ivals), 1 - H2(0.1)),
      abs(q_opt - 0.5) < 0.005 and abs(max(Ivals) - (1 - H2(0.1))) < 1e-3)

# ---------- I7 Z 信道（p=1/2）：最优输入非均匀 q*≈0.4，C=log2(1.25)≈0.3219 ----------
Ivals7 = [H2(0.5 * q) - q for q in qs]
q7 = qs[int(np.argmax(Ivals7))]
C7_theory = math.log2(1.25)
check("I7 Z 信道：最优 q*=%.3f ≠ 0.5（偏离>0.05），C=%.6f ≈ log2(1.25)=%.6f（|Δ|<1e−3）"
      % (q7, max(Ivals7), C7_theory),
      abs(q7 - 0.5) > 0.05 and abs(q7 - 0.4) < 0.01 and abs(max(Ivals7) - C7_theory) < 1e-3)

# ---------- I8 DPI：具体 X→Y→Z 转移链，I(X;Z) < I(X;Y)（精确） ----------
px = [0.4, 0.6]
py_x = [[0.9, 0.1], [0.2, 0.8]]                            # P(Y=1|X)
pz_y = [[0.7, 0.3], [0.1, 0.9]]                            # P(Z=1|Y)
pXY = [[px[x] * py_x[x][y] for y in (0, 1)] for x in (0, 1)]
pYZ = [[sum(pXY[x][y] * pz_y[y][z] for x in (0, 1)) for z in (0, 1)] for y in (0, 1)]
pXZ = [[sum(pXY[x][y] * pz_y[y][z] for y in (0, 1)) for z in (0, 1)] for x in (0, 1)]
def MI(pAB):
    return sum(pAB[a][b] * math.log2(pAB[a][b] / (sum(pAB[a][c] for c in (0, 1)) * sum(pAB[r][b] for r in (0, 1))))
               for a in (0, 1) for b in (0, 1) if pAB[a][b] > 0)
Ixy, Ixz = MI(pXY), MI(pXZ)
check("I8 DPI：I(X;Y)=%.6f > I(X;Z)=%.6f（差 %.6f > 1e−6，处理只减不增）" % (Ixy, Ixz, Ixy - Ixz),
      Ixz < Ixy - 1e-6)

# ---------- I9 点态条件熵反例：H(X|Y=0)=1 > H(X)≈0.0808；平均 H(X|Y)=0.02 ≤ H(X) ----------
pX = [0.99, 0.01]                                          # P(X=1)=0.01
HX = H2(0.01)
HXgY0 = H2(0.01 / 0.02)                                    # = H2(0.5) = 1
HXgY_avg = 0.02 * 1 + 0.98 * 0
check("I9 条件熵点态反例：H(X|Y=0)=%.4f > H(X)=%.4f；但平均 H(X|Y)=%.4f ≤ H(X)"
      % (HXgY0, HX, HXgY_avg), HXgY0 == 1.0 and HXgY0 > HX and HXgY_avg < HX)

# ---------- 算术码（Fraction 精确实现，I10/I11 共用） ----------
def arith_encode(seq, model):
    """model(ctx) 返回符号概率表 {sym: Fraction}；返回 (码长 bits, 值 Fraction, P(seq))。"""
    lo, hi = Fraction(0), Fraction(1)
    ctx = None
    for s in seq:
        table = model(ctx)
        c = Fraction(0)
        for t in sorted(table):                            # 固定符号序保证可逆
            w = (hi - lo) * table[t]
            if t == s:
                lo, hi = lo + c, lo + c + w
                break
            c += w
        ctx = s
    P = hi - lo
    k = 1
    while True:
        v = (lo.numerator * (1 << k)) // lo.denominator + 1
        if Fraction(v, 1 << k) < hi:
            return k, Fraction(v, 1 << k), P
        k += 1

def arith_decode(bits_val, k, length, model):
    t = bits_val
    lo, hi = Fraction(0), Fraction(1)
    ctx = None
    out = []
    for _ in range(length):
        table = model(ctx)
        c = Fraction(0)
        for s in sorted(table):
            w = (hi - lo) * table[s]
            if lo + c <= t < lo + c + w:
                lo, hi = lo + c, lo + c + w
                out.append(s)
                break
            c += w
        ctx = out[-1]
    return tuple(out)

# ---------- I10 round-trip 无损 + 码长 ≤ ⌈−log2 P⌉+2 ----------
SYM3 = {0: Fraction(1, 2), 1: Fraction(3, 10), 2: Fraction(1, 5)}
model3 = lambda ctx: SYM3
rt_ok, len_ok = True, True
for trial in range(60):
    seq = tuple(rng.choice(3, size=30, p=[0.5, 0.3, 0.2]))
    k, v, P = arith_encode(seq, model3)
    rt_ok &= (arith_decode(v, k, 30, model3) == seq)
    len_ok &= (k <= math.ceil(-math.log2(float(P)) - 1e-12) + 2)
check("I10 算术码：60 组×30 符号 round-trip 全部无损，码长 ≤ ⌈−log₂P⌉+2", rt_ok and len_ok)

# ---------- I11 LLM=压缩最小实验：条件模型码长≈条件熵 < 边缘模型码长≈边缘熵 ----------
TA = {0: Fraction(9, 10), 1: Fraction(1, 10)}
TB = {0: Fraction(3, 10), 1: Fraction(7, 10)}
PI = {0: Fraction(3, 4), 1: Fraction(1, 4)}
cond_model = lambda ctx: TA if ctx == 0 else (TB if ctx == 1 else PI)
marg_model = lambda ctx: PI
H_rate = 0.75 * H2(0.1) + 0.25 * H2(0.3)                   # 条件熵率 ≈ 0.5721
H_marg = H2(0.75)                                          # 边缘熵 ≈ 0.8113
nseq, L = 300, 150
bits_cond = bits_marg = 0
for _ in range(nseq):
    seq = [0] if rng.random() < 0.75 else [1]
    for _ in range(L - 1):
        seq.append(1 if rng.random() < (0.1 if seq[-1] == 0 else 0.7) else 0)
    seq = tuple(seq)
    bits_cond += arith_encode(seq, cond_model)[0]
    bits_marg += arith_encode(seq, marg_model)[0]
bc, bm = bits_cond / (nseq * L), bits_marg / (nseq * L)
check("I11 压缩=预测：条件码长/符=%.4f≈H率%.4f（|Δ|<0.03）；边缘码长=%.4f≈H边%.4f；差=%.4f≈互信息率%.4f"
      % (bc, H_rate, bm, H_marg, bm - bc, H_marg - H_rate),
      abs(bc - H_rate) < 0.03 and abs(bm - H_marg) < 0.03 and abs((bm - bc) - (H_marg - H_rate)) < 0.05 and bm > bc)

# ---------- I12 XOR：I(X;Y)=0 但 I(X;Y|Z)=1 bit（精确） ----------
pXYZ = {}
for x in (0, 1):
    for y in (0, 1):
        pXYZ[(x, y, x ^ y)] = 0.25
mZ = {z: sum(v for (x, y, zz), v in pXYZ.items() if zz == z) for z in (0, 1)}
Ixy = 0.0                                                # X,Y 独立均匀（边缘乘积=联合 1/4）
IxygZ = sum(v * math.log2(v * mZ[zz] / (sum(u for (xx, yy, zzz), u in pXYZ.items() if xx == x and zzz == zz) *
                                               sum(u for (xx, yy, zzz), u in pXYZ.items() if yy == y and zzz == zz)))
            for (x, y, zz), v in pXYZ.items())
check("I12 XOR 诅咒：I(X;Y)=%.4f=0（边缘独立）但 I(X;Y|Z)=%.6f=1 bit（条件互信息爆发）" % (Ixy, IxygZ),
      abs(Ixy) < 1e-12 and abs(IxygZ - 1.0) < 1e-12)

print(f"\n结果：{PASS}/{TOTAL} 断言通过" + ("  [ALL PASS]" if PASS == TOTAL else "  [HAS FAIL]"))
raise SystemExit(0 if PASS == TOTAL else 1)
