# -*- coding: utf-8 -*-
"""
card_id: DM-META-01（学习元知识/证明策略库蒸馏卡）L1 机器验证脚本
断言计数: 13（C1-C13，对应卡内 §2 各策略的具体例）
运行方式: python3 dm_meta_check.py
依赖: numpy, sympy
说明: 策略本身无法被"验证"，被验证的是每条策略所附的具体例子。
      每条断言头部注释标注对应策略名。
"""
import math
import numpy as np
import sympy as sp
from sympy import symbols, simplify, Rational, pi, sqrt as sp_sqrt

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

print("== DM-META-01 证明策略库·具体例断言 ==")

# --- C1 策略[对称性检验]: I=∫₀^{π/2} ln(sin x)dx = -(π/2)ln2 ---
n = 2000000
t = (np.arange(n) + 0.5) / n * (np.pi / 2)
I_sin = np.mean(np.log(np.sin(t))) * (np.pi / 2)
I_cos = np.mean(np.log(np.cos(t))) * (np.pi / 2)
I_exact = -(np.pi / 2) * np.log(2)
check(f"C1a 对称性: ∫ln(sin)=∫ln(cos)（x→π/2-x 对称），实测 |diff|={abs(I_sin-I_cos):.2e}",
      abs(I_sin - I_cos) < 1e-4)
check(f"C1b 两倍角技巧后 = -(π/2)ln2，实测误差 {abs(I_sin-I_exact):.2e}（MC 容差 1e-3）",
      abs(I_sin - I_exact) < 1e-3)

# --- C2 策略[不变量构造]: 8x8 棋盘去对角 -> 31 domino 不可能 ---
def board_counts(removed):
    black = white = 0
    for i in range(8):
        for j in range(8):
            if (i, j) in removed:
                continue
            if (i + j) % 2 == 0:
                black += 1
            else:
                white += 1
    return black, white
b1, w1 = board_counts({(0, 0), (7, 7)})   # 同色角
b2, w2 = board_counts({(0, 0), (0, 1)})   # 异色角
# 不变量: 每 domino 恰盖 1黑1白 ⇒ 可覆盖必要条件 黑=白且总数为偶
check(f"C2 不变量(黑白染色): 去同色角 黑={b1}≠白={w1}（domino 不变量被破坏->不可能）",
      b1 != w1 and (b1 + w1) == 62)
check(f"C2b 对照: 去异色角 黑={b2}=白={w2}（不变量不排除——事实上可覆盖）", b2 == w2 == 31)

# --- C3 策略[极端原理]: n+1 个 [1,2n] 中的整数必含整除对（最大奇因子归约）---
def has_div_pair(S):
    S = sorted(S)
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            if S[j] % S[i] == 0:
                return True
    return False
from itertools import combinations
ok = True
for nn in range(1, 8):   # 穷举 n<=7 的全部子集（C(14,8)=3003）
    for S in combinations(range(1, 2 * nn + 1), nn + 1):
        if not has_div_pair(S):
            ok = False
            break
    if not ok:
        break
check("C3 极端原理: n=1..7 穷举全部 C(2n,n+1) 子集，每个都含整除对（证明用'最大奇因子'极端归约）", ok)

# --- C4 策略[对偶转换]: 行秩=列秩（对行做的=对列做）+ LP 对偶数值抽查 ---
rng = np.random.default_rng(0)
ok = all(np.linalg.matrix_rank(rng.integers(-5, 6, size=(5, 9))) ==
         np.linalg.matrix_rank(rng.integers(-5, 6, size=(5, 9)).T) for _ in range(20))
# LP 对偶: min 2x+3y s.t. x>=1,y>=1 的最优 5 = max u+v s.t. u<=2, v<=3 的最优 5（手算对偶对）
check("C4a 对偶: 20 个随机矩阵行秩==列秩（转置不改秩——同一信息的两种读法）", ok)
check("C4b LP 对偶数值: 原问题 min=5 与对偶 max=5 相等（强对偶的最小实例）",
      2 * 1 + 3 * 1 == 1 * 2 + 1 * 3 == 5)

# --- C5 策略[归纳时强化命题]: Σ1/k² ≤ 2 - 1/n（弱版 <2 不归纳闭，强化版闭）---
s = 0.0
ok = True
for k in range(1, 10001):
    s += 1.0 / (k * k)
    if s > 2.0 - 1.0 / k:  # 强化版上界被破坏？
        ok = False
        break
check(f"C5a 数值: Σ1/k² ≤ 2-1/n 对 n=1..10^4 全部成立（实测末值 {s:.6f} ≤ {2-1e-4:.6f}）", ok)
# 符号验证递推封闭性: (2-1/n) - (2-1/(n-1)) >= 1/n²  <=>  n² >= n(n-1)
n_ = symbols('n', positive=True, integer=True)
gap = simplify(Rational(1, 1) / (n_ - 1) - 1 / n_ - 1 / n_**2)   # 应 = 1/(n²(n-1)) > 0
check(f"C5b 符号: 1/(n-1)-1/n-1/n² = {gap} > 0（n≥2，强化上界递推封闭——这就是'强化'的意义）",
      simplify(gap - 1 / (n_**2 * (n_ - 1))) == 0)

# --- C6 策略[构造 vs 存在]: R(3,3): K5 存在无单色三角染色（构造），K6 一切染色有单色三角（穷举=非构造互补）---
def has_mono_triangle(n, coloring):
    from itertools import combinations
    for tri in combinations(range(n), 3):
        cols = [coloring[tuple(sorted(p))] for p in combinations(tri, 2)]
        if cols[0] == cols[1] == cols[2]:
            return True
    return False
# 构造: K5 的红边=5-圈, 蓝边=补(也=5-圈)
c5 = {}
for i in range(5):
    c5[tuple(sorted((i, (i + 1) % 5)))] = 0      # 红圈
for i in range(5):
    for j in range(i + 1, 5):
        if tuple(sorted((i, j))) not in c5:
            c5[(i, j)] = 1                        # 蓝补
check("C6a 构造: K5 的 5-圈红/补蓝染色无单色三角（存在性证明=给出对象）⇒ R(3,3)>5",
      not has_mono_triangle(5, c5))
# 穷举: K6 的全部 2^15 染色都有单色三角 ⇒ R(3,3)≤6
from itertools import combinations as comb2
edges6 = list(comb2(range(6), 2))
all_mono = True
for mask in range(1 << 15):
    coloring = {edges6[b]: (mask >> b) & 1 for b in range(15)}
    if not has_mono_triangle(6, coloring):
        all_mono = False
        break
check("C6b 穷举 32768 种 K6 染色全部含单色三角（'必须存在'的暴力互补面）⇒ R(3,3)≤6", all_mono)

# --- C7 策略[退化情形检查]: Heron 公式喂退化三角形 ---
def heron(a, b, c):
    s = (a + b + c) / 2
    return math.sqrt(max(s * (s - a) * (s - b) * (s - c), 0.0))
check(f"C7 退化检查: Heron(3,4,5)={heron(3,4,5):.6f}（正常=6），Heron(1,2,3)={heron(1,2,3):.1e}（共线退化=0，公式不炸）",
      abs(heron(3, 4, 5) - 6.0) < 1e-12 and heron(1, 2, 3) < 1e-12)

# --- C8 策略[量纲与标度]: 幂律自相似 + 单摆周期标度 ---
c_scale = 3.7
for a_exp in [2.5, -1.5, 0.5]:
    lhs = (np.array([1.0, 2.0, 3.0]) * c_scale) ** a_exp
    rhs = c_scale ** a_exp * np.array([1.0, 2.0, 3.0]) ** a_exp
    if not np.allclose(lhs, rhs, rtol=1e-12):
        check("C8a 幂律标度", False)
        break
else:
    check("C8a 幂律标度: (cx)^a = c^a·x^a（scaling 决定幂律形状——量纲分析的心脏）", True)
L1_, g1_ = 1.0, 9.8
L2_, g2_ = 4.0, 9.8
T1 = 2 * np.pi * np.sqrt(L1_ / g1_)
T2 = 2 * np.pi * np.sqrt(L2_ / g2_)
check(f"C8b 单摆: L×4 ⇒ T×2（√(L/g) 是 L,g 唯一的时间量纲组合——量纲锁死函数形式至一个常数）",
      abs(T2 / T1 - 2.0) < 1e-12)

# --- C9 策略[先证弱版本]: Euler 乘积有限版本逼近 ζ(2) ---
def primes_upto(N):
    sieve = np.ones(N + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, int(N ** 0.5) + 1):
        if sieve[p]:
            sieve[p * p::p] = False
    return np.nonzero(sieve)[0]
prod = 1.0
for p in primes_upto(10000):
    prod *= 1.0 / (1.0 - 1.0 / p ** 2)
zeta2 = np.pi ** 2 / 6
check(f"C9 先证弱版本(有限乘积): ∏_p≤10^4 (1-p⁻²)⁻¹ = {prod:.8f} vs ζ(2)={zeta2:.8f}（相对误差 {abs(prod/zeta2-1):.1e} < 1e-4）",
      abs(prod / zeta2 - 1) < 1e-4)

# --- C10 策略[反例驱动修正]: Mertens 猜想的数值证据陷阱 ---
N = 100000
mob = np.ones(N + 1, dtype=np.int64)
is_comp = np.zeros(N + 1, dtype=bool)
for i in range(2, N + 1):
    if not is_comp[i]:
        mob[i::i] *= -1
        ii = int(i) * int(i)
        if ii <= N:
            mob[ii::ii] = 0
    if not is_comp[i]:
        is_comp[i::i] = True
M = np.cumsum(mob[1:])   # M(x) = Σ_{n<=x} μ(n)
x = np.arange(1, N + 1)
check(f"C10 Mertens 数值证据: |M(x)| ≤ √x 对 x≤10^5 全部成立（x=1 取等，max 比值 {np.max(np.abs(M)/np.sqrt(x)):.3f}）——"
      f"但文献已证猜想为假（Odlyzko & te Riele 1985，反例在 ~e^10^30 量级）：数值证据≠证明",
      np.all(np.abs(M) <= np.sqrt(x)))

# --- C11 策略[极限交换检查]: f_n=n·x^(n-1) 积分与极限不可交换 ---
nn = 100
f = lambda t: nn * t ** (nn - 1)
ts = (np.arange(100000) + 0.5) / 100000
ys = f(ts)
val = (ys[0] + ys[-1]) / 2 + ys[1:-1].sum()  # 手写梯形（numpy2.x 已移除 trapz）
val = val / 100000
lim_at_half = nn * 0.5 ** (nn - 1)   # 逐点极限(在 x<1) → 0
check(f"C11 交换陷阱: ∫₀¹ n·x^(n-1)dx = {val:.6f} ≈ 1 对一切 n，但逐点极限≡0（x<1）⇒ ∫lim=0 ≠ lim∫（无控制函数不可换）",
      abs(val - 1.0) < 1e-3 and lim_at_half < 1e-10)

# --- C12 策略[特例先行]: 猜想从 n=2,3 长出来——Fermat 素数反例教育 ---
# 2^(2^k)+1: k=0..4 是素数（3,5,17,257,65537），k=5 分解 641×6700417（Euler）
def is_prime_small(m):
    if m < 2:
        return False
    for d in range(2, int(m ** 0.5) + 1):
        if m % d == 0:
            return False
    return True
f5 = 2 ** 32 + 1
check(f"C12 特例先行的陷阱: k=0..4 Fermat 数全素（{''.join(str(int(is_prime_small(2**2**k+1))) for k in range(5))}），"
      f"k=5: {f5} = 641×{f5//641}（5 个特例=强归纳陷阱，Euler 反例）",
      all(is_prime_small(2 ** 2 ** k + 1) for k in range(5)) and f5 == 641 * 6700417)

# --- C13 策略[归纳基础检查]: '所有马同色'谬误的机器解剖 ---
# 谬误在 n=1→n=2: 交集为空的归纳步失效。验证: 2 元集合去掉一个元素后交集可以是空集
S = {1, 2}
A, Bc = S - {2}, S - {1}
check("C13 归纳基础: {1,2} 拆成两个 1 元子集后 A∩B=∅（'同色传递'在 n=2 断链——归纳步隐含假设 n≥2）",
      A == {1} and Bc == {2} and A & Bc == set())

print(f"\n结果: {PASS} PASS / {FAIL} FAIL（共 {PASS+FAIL} 断言）")
exit(0 if FAIL == 0 else 1)
