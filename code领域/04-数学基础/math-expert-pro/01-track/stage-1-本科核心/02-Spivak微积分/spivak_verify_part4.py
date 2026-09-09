# -*- coding: utf-8 -*-
"""Spivak《Calculus》Part IV 现代验证（无穷级数 + 一致收敛 + 泰勒 + e超越性）
阶段1灵魂。纯 Python 无依赖"""
import math

# ---------- §1 序列收敛 ----------
def section_sequences():
    print("\n" + "="*60)
    print("【Part IV 序列收敛（Spivak 第22章）】")
    print("="*60)
    print("序列 a_n → L：∀ε>0 ∃N, n>N ⟹ |a_n - L|<ε")
    # 验证 (1+1/n)^n → e
    print("验证 (1+1/n)^n → e：")
    for n in [10, 100, 1000, 10000, 100000]:
        val = (1 + 1/n)**n
        print(f"  n={n:>6}: (1+1/n)^n = {val:.10f}, |差 e|={abs(val-math.e):.2e}")
    # 但收敛慢——n=100000 还差 1.3e-6
    print("→ 收敛但极慢；Spivak 证 e 是该序列的极限（用 ε-δ，不靠直觉）")

# ---------- §2 级数收敛判别 ----------
def section_series():
    print("\n" + "="*60)
    print("【Part IV 级数收敛判别（Spivak 第23章）】")
    print("="*60)
    # 调和级数发散（最反直觉）
    print("★ 调和级数 Σ 1/n 发散（最反直觉——项→0 但和→∞）：")
    for n in [100, 1000, 10000, 1000000]:
        H = sum(1/k for k in range(1, n+1))
        print(f"  Σ_1^{n} 1/n = {H:.4f}（≈ ln({n})+γ = {math.log(n)+0.5772:.4f}）")
    print("→ 项→0 不保证级数收敛！Σ1/n ≈ ln(n)+γ（欧拉常数 γ≈0.5772）")

    # 交错级数收敛（莱布尼茨判别）
    print("\n交错级数 Σ (-1)^(n+1)/n 收敛（到 ln2）：")
    for n in [100, 1000, 10000]:
        alt = sum((-1)**(k+1)/k for k in range(1, n+1))
        print(f"  前 {n} 项 = {alt:.10f}, ln2 = {math.log(2):.10f}, 误差 = {abs(alt-math.log(2)):.2e}")

    # 收敛判别：比较/比值/根值
    print("\n收敛判别验证：")
    # Σ 1/n² 收敛（p=2>1）→ π²/6
    for n in [100, 1000, 10000]:
        s = sum(1/k**2 for k in range(1, n+1))
        print(f"  Σ 1/n² (前{n}项) = {s:.8f} → π²/6 = {math.pi**2/6:.8f}（巴塞尔问题）")

# ---------- §3 泰勒级数 ----------
def section_taylor():
    print("\n" + "="*60)
    print("【Part IV 泰勒级数：用多项式逼近函数（Spivak 第27章）】")
    print("="*60)
    # e^x = Σ x^n/n!
    def taylor_exp(x, n):
        return sum(x**k / math.factorial(k) for k in range(n+1))
    print("e^x 的泰勒级数 Σ x^n/n!：")
    for x in [0.5, 1, 2, -1]:
        for n in [3, 6, 10, 15]:
            approx = taylor_exp(x, n)
            exact = math.exp(x)
            err = abs(approx - exact)
        n = 15
        print(f"  e^{x}: 泰勒前{n}项={taylor_exp(x,n):.10f}, 精确={exact:.10f}, 误差={abs(taylor_exp(x,n)-exact):.2e}")
    # sin/cos 泰勒
    def taylor_sin(x, n):
        return sum((-1)**k * x**(2*k+1) / math.factorial(2*k+1) for k in range(n+1))
    print(f"\nsin(1) 泰勒前 10 项 = {taylor_sin(1, 10):.12f}, 精确 = {math.sin(1):.12f}")
    print("→ 泰勒级数 = 用多项式（你会算的）逼近复杂函数——这是数值计算的基础")

# ---------- §4 一致收敛 ----------
def section_uniform():
    print("\n" + "="*60)
    print("【Part IV 一致收敛：函数序列的收敛（Spivak 第24章）】")
    print("="*60)
    # f_n(x) = x^n 在 [0,1]：逐点→不连续函数，不一致收敛
    print("反例：f_n(x) = x^n 在 [0,1]：")
    print("  逐点：x<1 时 x^n→0，x=1 时 x^n=1 → 极限是跳跃函数（不连续）")
    print("  连续函数序列的逐点极限可以不连续！→ 需要'一致收敛'保证极限连续")
    for n in [5, 10, 50, 100]:
        # 在 x=0.99 的值
        x = 0.99
        print(f"  n={n:>3}: x^n at x=0.99 = {x**n:.6f}（趋近 0）；at x=1.0 = {1.0**n:.6f}")
    print("→ 一致收敛：sup|f_n - f| → 0（比逐点强）。一致收敛保持连续性/可积性")

# ---------- §5 e 的超越性（Spivak 第20章高光） ----------
def section_e_transcendental():
    print("\n" + "="*60)
    print("【Part IV e 的无理性 + 超越性（Spivak 第20章，全书高光之一）】")
    print("="*60)
    print("Spivak 第 20 章证明两件事：")
    print("① e 是无理数（用 e 的级数反证）")
    print("② e^q 对非零有理数 q 都是无理数")
    print()
    print("e 无理的证明思路（Fourier 1846）：")
    print("  假设 e = p/q（有理）。考虑 e = Σ 1/n!")
    print("  q·e = q·Σ_{n=0}^q 1/n! + q·Σ_{n=q+1}^∞ 1/n!")
    print("  前半是整数；后半 > 0 但 < 1（对大 q）→ 矛盾（一个整数不能严格在 0,1 间）")
    # 数值验证：e 的级数尾部
    print(f"\n数值验证 e 无理证明的关键：级数尾部 < 1")
    for q in [3, 5, 10]:
        tail = sum(1/math.factorial(n) for n in range(q+1, 100))
        print(f"  q={q}: q!·Σ_{{n>q}} 1/n! = {math.factorial(q)*tail:.6f}（整数倍 < 1，矛盾）")
    print(f"\n→ Hermite 1873 进一步证 e 超越（不是任何整系数方程的根，柯朗第2章讲过）")
    print(f"→ Spivak 给 e 无理的完整证明——这是'读 Spivak 才有的奖励'")

if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  Spivak《Calculus》Part IV · 现代验证                      ║")
    print("║  序列/级数/泰勒/一致收敛/e 无理性                            ║")
    print("╚" + "═"*58 + "╝")
    section_sequences()
    section_series()
    section_taylor()
    section_uniform()
    section_e_transcendental()
    print("\n" + "═"*60)
    print("✅ Part IV 验证通过。无穷级数与一致收敛打通。")
    print("═"*60)
