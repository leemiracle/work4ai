# -*- coding: utf-8 -*-
"""
dm_alg_check.py — 蒸馏卡 DM-ALG-01《抽象代数》§4 机器验证
对应卡片: distilled_math/DM-ALG-01-抽象代数.md
断言计数: 14（ALG-01 ~ ALG-14）
运行方式: python3 dm_alg_check.py
依赖: sympy（仅 ALG-09/14 用到）；群论部分手写小类，零依赖。
置信含义: 全过 → 卡内对应断言可标 ★（= 有限实例机器抽查通过，非定理证明，见 METHODOLOGY §六）
"""
import itertools
from sympy import Poly, symbols

x = symbols('x')
PASS = []

def check(name, cond):
    assert cond, f"FAIL: {name}"
    PASS.append(name)
    print(f"  [PASS] {name}")

# ============ 置换小类（S3 具体计算，0-indexed） ============
class Perm:
    """p.t[i] = i 被映到的位置。self * other = 先作用 other 再作用 self。"""
    def __init__(self, t): self.t = tuple(t)
    def __mul__(self, o): return Perm(tuple(self.t[o.t[i]] for i in range(len(self.t))))
    def inverse(self):
        r = [0] * len(self.t)
        for i in range(len(self.t)): r[self.t[i]] = i
        return Perm(r)
    def order(self):
        y, n = self, 1
        while y.t != tuple(range(len(self.t))):
            y = y * self; n += 1
        return n
    def __eq__(self, o): return isinstance(o, Perm) and self.t == o.t
    def __hash__(self): return hash(self.t)
    def __repr__(self):
        names = "012"
        return "(" + ")(".join(names[i] for i in self.t) + ")"

S3 = [Perm(p) for p in itertools.permutations(range(3))]
e   = Perm((0, 1, 2))          # 恒等
s12 = Perm((1, 0, 2))          # 对换 (12)
r   = Perm((1, 2, 0))          # 轮换 (012)：3 循环
r2  = r * r                    # (021)

print("== ALG-01/02: S3 基本事实 ==")
check("ALG-01 |S3|=6 且元素互异", len(set(S3)) == 6)
check("ALG-02 S3 非交换: (12)(012) != (012)(12)", (s12 * r) != (r * s12))
print(f"    (12)*(012) = {s12 * r},  (012)*(12) = {r * s12}")

print("== ALG-03/04/05/06: 子群·共轭·正规性 ==")
# 穷举 2^6=64 个子集，找封闭子群
subgroups = []
for k in range(7):
    for comb in itertools.combinations(S3, k):
        H = set(comb)
        if e in H and all(a * b in H for a in H for b in H):
            subgroups.append(H)
subgroup_orders = sorted(len(H) for H in subgroups)
check("ALG-03 Lagrange 实例: S3 恰有 6 个子群, 阶 {1,2,2,2,3,6} 全整除 6",
      len(subgroups) == 6 and subgroup_orders == [1, 2, 2, 2, 3, 6]
      and all(6 % d == 0 for d in subgroup_orders))
# 共轭类
cls = []
seen = set()
for g in S3:
    if g in seen: continue
    c = {h * g * h.inverse() for h in S3}
    cls.append(c); seen |= c
check("ALG-04 类方程实例: 共轭类大小 1+2+3 = 6", sorted(len(c) for c in cls) == [1, 2, 3])
conj = r * s12 * r.inverse()
H12 = {e, s12}
check("ALG-05 (012)(12)(012)^-1 = (23) ∉ <(12)> → <(12)> 不正规",
      conj == Perm((0, 2, 1)) and conj not in H12)
print(f"    共轭结果 = {conj}（即对换 (23)）")
A3 = {e, r, r2}
check("ALG-06 A3 = {e,(012),(021)} 正规: ∀g gA3g^-1 = A3",
      all({h * a * h.inverse() for a in A3} == A3 for h in S3))

print("== ALG-07/08: Z/6 零因子 vs Z/5 域 ==")
check("ALG-07 Z/6 有零因子: 2*3 ≡ 0 (mod 6), 2,3 ≠ 0", (2 * 3) % 6 == 0 and 2 % 6 != 0 and 3 % 6 != 0)
inv5 = {a: b for a in range(1, 5) for b in range(1, 5) if (a * b) % 5 == 1}
check("ALG-08 Z/5 是域: 1..4 每个元素有乘法逆元", len(inv5) == 4)

print("== ALG-09~13: GF(8) = GF(2)[x]/(x^3+x+1) 具体构造 ==")
# 元素用 3 位整数表示: a2*x^2 + a1*x + a0 ↔ 位模式 a2a1a0
MODPOLY = 0b1011  # x^3 + x + 1

def gf_mul(a, b):
    """GF(8) 乘法（carry-less + 模 x^3+x+1 归约, 因 x^3 ≡ x+1）"""
    res = 0
    while b:
        if b & 1: res ^= a
        b >>= 1
        a <<= 1
        if a & 0b1000: a ^= MODPOLY
    return res & 0b111

check("ALG-09 x^3+x+1 在 GF(2)[x] 不可约（三次无根即不可约）",
      Poly(x**3 + x + 1, x, modulus=2).is_irreducible is True)
gen = 0b010  # 元素 x
pows, cur = [], 1
for _ in range(7):
    pows.append(cur); cur = gf_mul(cur, gen)
check("ALG-10 x 的阶为 7 且幂遍历全部非零元 → GF(8)* ≅ C7 循环群",
      cur == 1 and pows[1:] != [1] * 6 and set(pows) == set(range(1, 8)))
check("ALG-11 GF(8) 无零因子: 非零×非零 ≠ 0（8×8 全表）",
      all(gf_mul(a, b) != 0 for a in range(1, 8) for b in range(1, 8)))
# 幂表: pows[k] = x^k
powtab = {a: k for k, a in enumerate(pows)}  # 离散对数（以 x 为底）
def gf_pow(a, n):
    r = 1
    for _ in range(n): r = gf_mul(r, a)
    return r
check("ALG-12 有限域 Fermat: a^8 = a 对全体 8 元素成立",
      all(gf_pow(a, 8) == a for a in range(8)))
check("ALG-13 Frobenius (a+b)^2 = a^2 + b^2（加法=XOR，特征 2）",
      all(gf_mul(a ^ b, a ^ b) == gf_mul(a, a) ^ gf_mul(b, b)
          for a in range(8) for b in range(8)))

print("== ALG-14: GF(8) ≇ Z/8（同阶不同构） ==")
check("ALG-14 Z/8 有零因子 2*4≡0 而 GF(8) 无 → 8 元域不是 Z/8",
      (2 * 4) % 8 == 0 and all(gf_mul(a, b) != 0 for a in range(1, 8) for b in range(1, 8)))

print(f"\n全部通过: {len(PASS)}/14 条断言")
print("（★ 含义 = 实例级机器抽查通过；定理级确证归 L3 Lean，见 METHODOLOGY §六）")
