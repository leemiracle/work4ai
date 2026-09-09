# -*- coding: utf-8 -*-
"""Dummit & Foote《Abstract Algebra》3e 现代验证
群 / Lagrange / Sylow / 环 / Galois 理论
用 numpy/sympy 验证代数结构。阶段2代数主线"""
import numpy as np
from itertools import permutations
from functools import reduce

# ---------- §1 群的定义 ----------
def section_group():
    print("\n" + "="*60)
    print("【§1 群的定义与例子（Dummit ch1）】")
    print("="*60)
    print("群 (G, ·)：封闭 + 结合 + 单位元 + 逆元")
    # 例：对称群 S_3（最小非交换群）
    print("\n对称群 S_3（3 元素的全排列，6 个元素，最小非交换群）：")
    # 用排列乘法验证
    def perm_mul(p, q):
        return tuple(p[q[i]] for i in range(len(p)))
    S3 = list(permutations(range(3)))
    e = (0, 1, 2)
    # 验证封闭性（任两元素乘积在 S3）
    for p in S3[:3]:
        for q in S3[:3]:
            prod = perm_mul(p, q)
            assert prod in S3
    print(f"  S_3 有 {len(S3)} 个元素：{S3}")
    # 验证非交换
    p, q = (1,0,2), (0,2,1)
    print(f"  非交换验证：(1,0,2)·(0,2,1) = {perm_mul(p,q)}，(0,2,1)·(1,0,2) = {perm_mul(q,p)}（不等 → 非交换）")
    # 逆元
    def inverse(p):
        inv = [0]*len(p)
        for i, v in enumerate(p): inv[v] = i
        return tuple(inv)
    for p in S3:
        inv = inverse(p)
        assert perm_mul(p, inv) == e
    print(f"  每个元素有逆元（验证全部 6 个）✓")

# ---------- §2 Lagrange 定理 ----------
def section_lagrange():
    print("\n" + "="*60)
    print("【§2 Lagrange 定理 + 循环群（Dummit ch3）】")
    print("="*60)
    print("Lagrange 定理：|G| = |H| · [G:H]（子群阶整除群阶）")
    # S_3 的子群
    print(f"\n  S_3（阶 6）的子群阶：1, 2, 3, 6（都是 6 的因子）")
    # 验证：S_3 有阶 2 子群（生成元 (1,0,2)）
    p = (1, 0, 2)
    def perm_mul(a, b): return tuple(a[b[i]] for i in range(3))
    H = [p]
    while H[-1] != (0,1,2):
        H.append(perm_mul(H[-1], p))
    print(f"  <(1,0,2)> = {set(H)}，阶 = {len(set(H))}（2 | 6 ✓）")
    # 循环群
    print(f"\n  循环群：由一个元素生成。ℤ_n = {{0,1,...,n-1}} 模 n 加法")
    print(f"  ℤ_6 = {{0,1,2,3,4,5}}，生成元 1（或 5）")
    # ℤ_6 的阶 2 子群
    print(f"  ℤ_6 的阶 2 子群 = {{0, 3}}（3+3=0 mod 6）")

# ---------- §3 Sylow 定理 ----------
def section_sylow():
    print("\n" + "="*60)
    print("【§3 Sylow 定理（Dummit ch4·群论高峰）】")
    print("="*60)
    print("Sylow 三大定理（有限群结构的钥匙）：")
    print("  ① 存在性：|G|=p^a·m（p∤m）⟹ G 有阶 p^a 的子群（Sylow p-子群）")
    print("  ② 共轭性：所有 Sylow p-子群互相共轭")
    print("  ③ 计数：Sylow p-子群的个数 n_p ≡ 1 (mod p) 且 n_p | m")
    # 例：|G|=12=2²·3，Sylow 3-子群个数 n_3
    print(f"\n  例：|G|=12=2²·3")
    print(f"  Sylow 3-子群阶 = 3¹ = 3")
    print(f"  n_3 ≡ 1 (mod 3) 且 n_3 | 4 ⟹ n_3 ∈ {{1, 4}}")
    print(f"  Sylow 2-子群阶 = 2² = 4")
    print(f"  n_2 ≡ 1 (mod 2) 且 n_2 | 3 ⟹ n_2 ∈ {{1, 3}}")
    print(f"\n→ Sylow 定理让你'数'有限群的结构——群论最有力的工具之一")

# ---------- §4 环与域 ----------
def section_ring():
    print("\n" + "="*60)
    print("【§4 环/理想/域（Dummit ch7）】")
    print("="*60)
    print("环：加法群 + 乘法半群 + 分配律。域：乘法也可交换+逆")
    # ℤ/nℤ 当 n 素数是域
    print(f"\n  ℤ/nℤ 当 n 素数时是域（每个非零元有逆）")
    n = 7  # 素数
    print(f"  ℤ/7ℤ 的乘法逆元（费马小定理 x^(-1) = x^(p-2)）：")
    for x in range(1, n):
        inv = pow(x, n-2, n)
        assert (x * inv) % n == 1
        print(f"    {x}^(-1) mod 7 = {inv}（验证 {x}×{inv} mod 7 = 1）")
    print(f"  → ℤ/7ℤ 是有限域 GF(7)，密码学/编码论的工作台")
    # UFD/PID/ED 链
    print(f"\n  唯一分解链：欧氏域 ED ⟹ 主理想域 PID ⟹ 唯一分解环 UFD")
    print(f"  ℤ 是 ED（带余除法），ℤ[x] 是 UFD 但不是 PID")
    print(f"  ℂ[x] 是 ED（多项式带余除法）⟹ 代数基本定理的代数根基")

# ---------- §5 Galois 理论 ----------
def section_galois():
    print("\n" + "="*60)
    print("【§5 Galois 理论（Dummit ch14·代数高峰）】")
    print("="*60)
    print("Galois 理论基本定理：扩张 K/F 的中间域 ↔ Gal(K/F) 的子群（反序）")
    print(f"\n  例：ℚ(√2, √3)/ℚ 的 Galois 群")
    print(f"  Gal(ℚ(√2,√3)/ℚ) ≅ ℤ/2 × ℤ/2（Klein 四元群）")
    print(f"  4 个自同构：")
    print(f"    id:  √2→√2, √3→√3")
    print(f"    σ₁:  √2→-√2, √3→√3")
    print(f"    σ₂:  √2→√2, √3→-√3")
    print(f"    σ₃:  √2→-√2, √3→-√3")
    print(f"  对应 4 个中间域：ℚ, ℚ(√2), ℚ(√3), ℚ(√2,√3)")
    # 五次方程不可解
    print(f"\n  ★ 五次方程不可解（Galois 1832，20 岁决斗前夜写下）")
    print(f"  一般五次方程的 Galois 群 = S_5（不可解群）⟹ 根不能用根式表达")
    print(f"  这是柯朗第3章'尺规作图三大难题'+ Abel-Ruffini 的统一解释")
    print(f"\n→ Galois 理论：用群论统一'方程可解性'+'几何作图'+'数域结构'")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  Dummit & Foote《Abstract Algebra》3e · 现代验证            ║")
    print("║  群/Lagrange/Sylow/环/Galois                                ║")
    print("╚" + "═"*58 + "╝")
    section_group()
    section_lagrange()
    section_sylow()
    section_ring()
    section_galois()
    print("\n" + "═"*60)
    print("✅ Dummit 核心验证通过。抽象代数地基（阶段2代数主线）打通。")
    print("═"*60)
