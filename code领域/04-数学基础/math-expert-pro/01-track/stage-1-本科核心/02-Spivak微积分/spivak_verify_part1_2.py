# -*- coding: utf-8 -*-
"""Spivak《Calculus》Part I-II 现代验证（实数公理 + 极限 + 连续 + 三硬定理）
阶段1灵魂。纯 Python 无依赖"""
import math

# ---------- Part I 实数公理 P1-P13 ----------
def part1_real_axioms():
    print("\n" + "="*60)
    print("【Part I 实数的公理 P1-P13（Spivak 第1章）】")
    print("="*60)
    # Spivak 用 13 条公理刻画实数：域公理(P1-P9) + 序公理(P10-P12) + 完备性(P13)
    print("Spivak 把实数 ℝ 建立在 13 条公理上：")
    print("  P1-P9  域公理（加乘运算 + 结合/交换/分配 + 单位/逆元）→ ℝ 是域")
    print("  P10-P12 序公理（三分性/传递/与加乘相容）→ ℝ 是有序域")
    print("  P13   最小上界公理（完备性）→ ℝ '没有洞'")
    # 数值验证域公理（对若干实数）
    import random
    random.seed(7)
    for _ in range(3):
        a, b, c = random.uniform(-5,5), random.uniform(-5,5), random.uniform(-5,5)
        # P1 加法结合律 (a+b)+c == a+(b+c)
        assert abs((a+b)+c - (a+(b+c))) < 1e-12
        # P5 加法逆元 a+(-a)=0
        assert abs(a + (-a)) < 1e-12
        # P7 乘法结合律
        assert abs((a*b)*c - (a*(b*c))) < 1e-12
        # P8 分配律 a*(b+c)=a*b+a*c
        assert abs(a*(b+c) - (a*b+a*c)) < 1e-12
    print(f"\n数值验证域公理（随机实数）：(a+b)+c=a+(b+c)、a+(-a)=0、a(b+c)=ab+ac 全成立 ✓")
    # 关键：P13 完备性——ℚ 没有，ℝ 才有
    print(f"\nP13 最小上界公理（完备性，最关键）：")
    print(f"  集合 S = {{x ∈ ℚ : x² < 2}}（所有平方小于 2 的有理数）")
    print(f"  在 ℚ 中 S 没有最小上界（√2 不是有理数）→ ℚ '有洞'")
    print(f"  在 ℝ 中 S 的最小上界 = √2 = {math.sqrt(2):.10f} → ℝ '没有洞'")
    print(f"\n→ P13 是 ℝ 区别于 ℚ 的本质：完备性。没有它，极限/连续/微积分都建不起来。")
    print(f"→ Spivak 的教学革命：第 1 章就给你 13 条公理当'宪法'，全书所有定理都从它们推出。")

# ---------- Part II 极限：ε-δ ----------
def part2_limit():
    print("\n" + "="*60)
    print("【Part II 极限：ε-δ 严格定义（Spivak 第5章）】")
    print("="*60)
    # ε-δ 定义：∀ε>0 ∃δ>0 使 0<|x-a|<δ ⟹ |f(x)-L|<ε
    print("ε-δ 定义（Spivak 第5章核心）：lim(x→a) f(x) = L")
    print("  ∀ε>0, ∃δ>0, 使 0<|x-a|<δ ⟹ |f(x)-L|<ε")
    # 例：lim(x→2) x² = 4，求 δ(ε)
    print("\n例：lim(x→2) x² = 4，给定 ε 求 δ：")
    print("  |x²-4| = |x-2|·|x+2|。若 |x-2|<δ，且限制 δ≤1，则 |x+2|<5，故 |x²-4|<5δ")
    print("  要 |x²-4|<ε，取 δ = min(1, ε/5)")
    for eps in [1, 0.1, 0.01, 0.001]:
        delta = min(1, eps/5)
        # 验证边界：x = 2+delta 时 |f(x)-4| 应 ≤ eps
        x_test = 2 + delta
        actual_err = abs(x_test**2 - 4)
        print(f"    ε={eps}: δ=min(1,ε/5)={delta:.6f}, x=2+δ={x_test:.6f}, |x²-4|={actual_err:.6f} ≤ ε={eps} ✓")
    # 极限的代数性质
    print("\n极限定理（Spivak 第5章）：若 lim f, lim g 存在，则")
    print("  lim(f±g) = lim f ± lim g；lim(f·g) = lim f · lim g；lim(f/g) = lim f / lim g（分母非0）")
    print("→ 这些'显然'的性质，在 Spivak 里每条都要从 ε-δ 严格证明（不靠直觉）")

# ---------- Part II 连续 ----------
def part2_continuity():
    print("\n" + "="*60)
    print("【Part II 连续：定义 + 一致连续（Spivak 第6章）】")
    print("="*60)
    # 连续：lim(x→a) f(x) = f(a)
    print("连续定义：f 在 a 连续 ⟺ lim(x→a) f(x) = f(a)")
    print("  即 ∀ε>0 ∃δ>0, |x-a|<δ ⟹ |f(x)-f(a)|<ε")
    # 数值验证 f(x)=x² 在 a=2 连续
    a = 2
    for eps in [0.1, 0.01, 0.001]:
        delta = min(1, eps/5)  # 同极限
        x_test = a + delta
        assert abs(x_test**2 - a**2) <= eps + 1e-9
    print(f"  f(x)=x² 在 a=2 连续：δ=min(1,ε/5) 守住任意 ε ✓")
    # 一致连续：δ 只依赖 ε，不依赖点 a
    print(f"\n一致连续（更强）：δ 只依赖 ε，不依赖点 a")
    print(f"  f(x)=x² 在 [0,2] 一致连续（有界闭区间上连续⟹一致连续，Cantor 定理）")
    print(f"  f(x)=x² 在 ℝ 上连续，但**不一致连续**（x 越大，同样的 δ 误差越大）")
    for a in [1, 10, 100, 1000]:
        delta = 0.001
        err = abs((a+delta)**2 - a**2)
        print(f"    δ=0.001 时：a={a:>5}, |f(a+δ)-f(a)|={err:.4f}（随 a 增大而增大）")
    print("→ '连续'是逐点的，'一致连续'是整体的——Spivak 让你区分这两者")

# ---------- Part II 三个硬定理（Spivak 第7章） ----------
def part2_hard_theorems():
    print("\n" + "="*60)
    print("【Part II 三个硬定理（Spivak 第7章·依赖 P13 完备性）】")
    print("="*60)
    print("Spivak 故意把这三个'显然'的定理推迟到第7章，因为它们需要 P13 完备性：")
    print()
    # 定理1：介值定理
    print("① 介值定理：f 在 [a,b] 连续，f(a)<0<f(b)，则 ∃c∈(a,b) 使 f(c)=0")
    # 数值：f(x)=x²-2 在 [1,2]，f(1)=-1, f(2)=2，根=√2
    def f(x): return x**2 - 2
    lo, hi = 1.0, 2.0
    for _ in range(60):  # 二分法找根
        mid = (lo+hi)/2
        if f(mid) < 0: lo = mid
        else: hi = mid
    print(f"   例：f(x)=x²-2 在 [1,2]，f(1)={f(1)}, f(2)={f(2)}")
    print(f"   二分法 60 次找根：c = {(lo+hi)/2:.12f} ≈ √2 = {math.sqrt(2):.12f} ✓")
    # 定理2：极值定理
    print()
    print("② 极值定理：f 在闭区间 [a,b] 连续 ⟹ f 取得最大值和最小值")
    # 数值：f(x)=-(x-3)²+5 在 [0,6] 的最大值在 x=3
    xs = [i*0.001 for i in range(6001)]
    f_max = max(-(x-3)**2+5 for x in xs)
    x_at_max = xs[(([-(x-3)**2+5 for x in xs]).index(f_max))]
    print(f"   例：f(x)=-(x-3)²+5 在 [0,6]，数值最大值 = {f_max:.4f}（精确 5，在 x=3）")
    # 定理3：中值定理
    print()
    print("③ 中值定理：f 在 [a,b] 连续且在 (a,b) 可导，则 ∃c∈(a,b) 使 f'(c)=(f(b)-f(a))/(b-a)")
    # f(x)=x² 在 [1,3]：f'(c)=2c=(9-1)/(3-1)=4，c=2
    print(f"   例：f(x)=x² 在 [1,3]，(f(3)-f(1))/(3-1)={(9-1)/(3-1)}，f'(c)=2c=4 ⟹ c=2 ∈(1,3) ✓")
    print()
    print("→ 这三个定理'看起来显然'，但**没有 P13 完备性它们就崩**：")
    print("  在 ℚ 上 f(x)=x²-2 在 [1,2] 连续、f(1)<0<f(2)，但**没有有理根**——介值定理失效！")
    print("  这就是为什么 Spivak 要先建 P13——'没有洞'才能保证这些定理。")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  Spivak《Calculus》Part I-II · 现代验证                    ║")
    print("║  实数公理 P1-P13 + 极限 ε-δ + 连续 + 三硬定理              ║")
    print("╚" + "═"*58 + "╝")
    part1_real_axioms()
    part2_limit()
    part2_continuity()
    part2_hard_theorems()
    print("\n" + "═"*60)
    print("✅ Part I-II 验证通过。Spivak 地基（公理+极限+连续+硬定理）打通。")
    print("═"*60)
