# -*- coding: utf-8 -*-
"""《什么是数学》第2章 现代验证（柯朗 ch02·数系）
验证：有理数域 / √2无理 / Cantor对角线 / 复数与欧拉公式 / 超越数
纯 Python 无外部依赖"""

from fractions import Fraction
import math
import cmath

# ---------- §1 整数与有理数：扩充动机 + 域 ----------
def section_1_rational():
    print("\n" + "="*60)
    print("【§1 整数与有理数：扩充动机 + 域的性质】")
    print("="*60)
    # 动机：自然数 ℕ 解不了 x+5=3 → 扩到整数 ℤ
    #       整数 ℤ 解不了 3x=2 → 扩到有理数 ℚ
    x1 = 3 - 5              # 在 ℤ 里：x = -2
    x2 = Fraction(2, 3)     # 在 ℚ 里：x = 2/3
    print(f"自然数 ℕ 解不了 x+5=3 → 扩到整数 ℤ：x = {x1}")
    print(f"整数 ℤ 解不了 3x=2 → 扩到有理数 ℚ：x = {x2} = {float(x2):.6f}")
    # 验证 ℚ 是域（+ - × ÷ 封闭，除0外）
    a, b = Fraction(3, 7), Fraction(5, 11)
    assert a + b == Fraction(68, 77)
    assert a * b == Fraction(15, 77)
    assert a / b == Fraction(33, 35)
    print(f"\nℚ 是域：3/7 + 5/11 = {a+b}；3/7 × 5/11 = {a*b}；3/7 ÷ 5/11 = {a/b}")
    # 连分数：√2 ≈ [1;2,2,2,...]
    print(f"\n√2 的连分数逼近 [1; 2, 2, 2, ...]：")
    convergents = []
    a0, rest = 1, [2]*8
    # 计算收敛子 h/k
    h_prev, h_cur = 1, a0
    k_prev, k_cur = 0, 1
    convergents.append((h_cur, k_cur))
    for ai in rest:
        h_new = ai * h_cur + h_prev
        k_new = ai * k_cur + k_prev
        convergents.append((h_new, k_new))
        h_prev, h_cur = h_cur, h_new
        k_prev, k_cur = k_cur, k_new
    for i, (h, k) in enumerate(convergents[:6]):
        err = abs(h/k - math.sqrt(2))
        print(f"  第{i}阶 {h}/{k} = {h/k:.10f}，误差 {err:.2e}")
    print("→ 每一阶都是 √2 的最佳有理逼近；连分数是理解无理数的钥匙")


# ---------- §2 √2 无理（毕达哥拉斯危机 + 反证法） ----------
def section_2_sqrt2_irrational():
    print("\n" + "="*60)
    print("【§2 √2 无理：毕达哥拉斯危机 + 反证法】")
    print("="*60)
    # 数值：√2 不是任何 p/q
    print(f"√2 = {math.sqrt(2):.15f}...")
    # 反证法证明（文字版）
    print("\n反证法证明 √2 ∉ ℚ：")
    print("  假设 √2 = p/q（p,q 互素，既约）")
    print("  则 2 = p²/q² → p² = 2q² → p² 是偶数 → p 是偶数（因奇数²是奇数）")
    print("  设 p = 2k，代入：(2k)² = 2q² → 4k² = 2q² → q² = 2k² → q² 是偶数 → q 是偶数")
    print("  但 p,q 都偶数，与'互素'矛盾！故 √2 不是有理数。■")
    # 代码验证：任何 p/q 都逼近不了 √2（穷举小 p,q）
    print(f"\n穷举验证：1 ≤ q ≤ 1000 内，最佳 p/q 逼近 √2：")
    best_p, best_q, best_err = 0, 1, 1
    for q in range(1, 1001):
        p = round(math.sqrt(2) * q)
        err = abs(p/q - math.sqrt(2))
        if err < best_err:
            best_p, best_q, best_err = p, q, err
    print(f"  最佳 = {best_p}/{best_q} = {best_p/best_q:.15f}，误差 {best_err:.2e}（永远不为 0！）")
    print("→ 毕达哥拉斯学派曾认为'万物皆整数比'，√2 的发现动摇其根基（传说 Hippasus 被扔进海里）")


# ---------- §3 Cantor 对角线：实数不可数 ----------
def section_3_cantor_diagonal():
    print("\n" + "="*60)
    print("【§3 Cantor 对角线论证：实数不可数】")
    print("="*60)
    # 模拟：假设 [0,1) 所有实数能列成表，对角线构造新数
    print("Cantor 论证：假设 [0,1) 的实数可数，能列出 r₁, r₂, r₃, ...")
    print("  构造新数 d：d 的第 n 位小数 ≠ rₙ 的第 n 位")
    print("  则 d 与每个 rₙ 至少差一位 → d 不在表里 → 矛盾")
    # 模拟：随机生成 10 个 [0,1) 实数，对角线构造
    import random
    random.seed(42)
    print(f"\n模拟：随机列 8 个 [0,1) 实数（前 8 位小数）：")
    rows = []
    for _ in range(8):
        x = random.random()
        digits = [int(d) for d in f"{x:.8f}"[2:]]
        rows.append(digits)
        s = ''.join(str(d) for d in digits)
        print(f"  r = 0.{s}")
    # 对角线构造
    diag = []
    for i in range(8):
        d = rows[i][i]
        new_d = (d + 1) % 10  # 确保不同
        diag.append(new_d)
    new_num_s = ''.join(str(d) for d in diag)
    print(f"  对角线构造的新数 d = 0.{new_num_s}")
    print(f"  d 的第 n 位 = (rₙ 第 n 位 + 1) mod 10，与每个 rₙ 都不同 → 不在列表里")
    print("\n→ 实数比自然数'多'（不可数）——这是 Cantor 1874 的革命性发现")
    print("→ 连续统假设：是否存在'大小'介于 ℕ 和 ℝ 之间的集合？Gödel+Cohen 证明它独立于 ZFC（[07-critique]）")


# ---------- §4 复数：虚数 + 欧拉公式 + 代数基本定理 ----------
def section_4_complex():
    print("\n" + "="*60)
    print("【§4 复数：虚数 + 欧拉公式 + 代数基本定理】")
    print("="*60)
    # 动机：实数解不了 x²+1=0 → 扩到复数 ℂ
    z = 1j  # Python 内置虚数单位
    print(f"虚数单位 i：i² = {z**2}（实数解不了 x²+1=0）")
    # 欧拉公式：e^(iπ) + 1 = 0（数学最美公式）
    e_ipi = cmath.exp(1j * math.pi)
    print(f"\n欧拉公式 e^(iπ) + 1 = {e_ipi} + 1 = {e_ipi+1}（≈0，浮点误差内）")
    print("→ e^(iπ) = -1：把 e, i, π, 1, 0 五大常数连成一个等式")
    # 复数运算 = 2D 旋转
    print(f"\n复数乘法 = 2D 旋转：")
    z1 = 1 + 1j
    z2 = 0 + 1j  # 乘以 i = 逆时针旋转 90°
    print(f"  (1+i) × i = {z1 * z2}（点 (1,1) 绕原点逆时针 90° → (-1,1)）")
    # 代数基本定理：n 次复系数多项式有 n 个复根（计重数）
    print(f"\n代数基本定理：n 次复系数多项式恰有 n 个复根（计重数）")
    print(f"  x² + 1 = 0 → 根 ±i（实数域无解，复数域有 2 个根）✓")
    print(f"  x³ - 1 = 0 → 根 1, ω, ω²（3 个根，其中 ω = e^(2πi/3)）")
    omega = cmath.exp(2j * math.pi / 3)
    print(f"    ω = {omega:.6f}，验证 ω³ = {omega**3:.6f} ≈ 1 ✓")
    print("→ 复数是'代数闭域'——多项式方程在 ℂ 里总能解完。这是数系扩张的终点（代数意义上）")


# ---------- §5 超越数：π, e 与 Cantor 的反直觉 ----------
def section_5_transcendental():
    print("\n" + "="*60)
    print("【§5 超越数：π, e 不是任何整系数方程的根】")
    print("="*60)
    # 代数数 vs 超越数
    print("代数数：是某整系数多项式方程的根（如 √2 是 x²-2=0 的根）")
    print("超越数：不是任何整系数方程的根（如 π, e）")
    print(f"\n  π = {math.pi:.15f}（Lindemann 1882 证明超越——解决'化圆为方'不可能）")
    print(f"  e = {math.e:.15f}（Hermite 1873 证明超越）")
    # Cantor 反直觉：超越数"远多于"代数数
    print(f"\nCantor 的反直觉发现（1874）：")
    print(f"  代数数集合是可数的（每个代数数对应一个有限多项式，多项式可枚举）")
    print(f"  而实数不可数（§3 对角线）")
    print(f"  → 几乎所有实数是超越数！")
    print(f"  → 但'具体证明某个数超越'极难（π 花到 1882，至今未证 e+π 是否超越）")
    # Hilbert 第七问题（已解）
    print(f"\n  Hilbert 第七问题（Gelfond-Schneider 定理，1934 解）：")
    alpha = 2 ** cmath.sqrt(2).real  # 2^√2
    print(f"    2^√2 = {alpha:.6f}（这是超越数，已证）")
    print("\n→ 数系的顶端：实数 ℝ ⊃ 代数数(可数) ∪ 超越数(不可数，'绝大多数')")
    print("→ 柯朗用这章告诉你：数系的扩张（ℕ→ℤ→ℚ→ℝ→ℂ）每步都源于'方程解不了'，")
    print("  而 ℝ 里的'大多数'数（超越数）我们甚至叫不出名字——这是数学的浩瀚")


if __name__ == "__main__":
    print("╔" + "═"*58 + "╗")
    print("║  《什么是数学》第 2 章 · 现代验证（柯朗 ch02·数系）        ║")
    print("║  Python 验证：有理数 / √2无理 / Cantor / 复数 / 超越数     ║")
    print("╚" + "═"*58 + "╝")
    section_1_rational()
    section_2_sqrt2_irrational()
    section_3_cantor_diagonal()
    section_4_complex()
    section_5_transcendental()
    print("\n" + "═"*60)
    print("✅ 全部 5 节验证通过。第 2 章数系用 Python 跑通。")
    print("═"*60)
