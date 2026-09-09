"""
《什么是数学》第2章: 数系 — 从有理数到复数的扩张
==================================================
阶段1 / 模块01 / 第2章
目标: 用程序可视化数系扩张的逻辑: 有理→无理→实数(完备)→复数(代数封闭)
运行: python3 what_is_math_ch2.py  (生成 4 张 PNG)

学习路径:
  §1 有理数: 稠密但「有洞」(√2 填不进去)
  §2 √2 无理: 数学史最经典反证法 + 几何不可公度
  §3 Cantor 对角线: 实数不可数 (颠覆"有限/无限"直觉)
  §4 复数与欧拉公式: e^(iπ)+1=0 (数学最美等式)
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ═══════════════════════════════════════════════════════════════════
# §1  有理数
# ═══════════════════════════════════════════════════════════════════
def section_1_rationals():
    print("=" * 70)
    print("§1 有理数: 稠密但「有洞」")
    print("=" * 70)
    print("""
    有理数 = p/q (p,q 整数, q≠0)。可化为有限/无限循环小数。
    稠密性: 任意两个有理数之间还有有理数 (取中点 (a+b)/2)。
    但有理数轴「有洞」: √2, π, e 都不是有理 → 必须扩张到实数。
    """)
    from fractions import Fraction
    a, b = Fraction(1, 3), Fraction(1, 2)
    print(f"  例: {a} 和 {b} 之间有理数 (二分中点法):")
    mid = (a + b) / 2
    for i in range(5):
        print(f"    第 {i+1} 次: {mid} ≈ {float(mid):.6f}")
        mid = (a + mid) / 2
    print("  → 永远能再插一个有理数, 但始终填不满 √2 ≈ 1.4142 那个点 (洞!)")

    # 可视化: [1,2] 上有理数 p/q (q≤N) 的分布
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    N = 50
    rats = set()
    for q in range(1, N + 1):
        for p in range(q, 2 * q + 1):
            from math import gcd
            g = gcd(p, q)
            rats.add(Fraction(p // g, q // g))
    rats = sorted(rats)
    vals = [float(r) for r in rats if 1 <= float(r) <= 2]
    axes[0].plot([1, 2], [0, 0], 'k-', lw=1)
    axes[0].scatter(vals, np.zeros_like(vals), s=8, color='steelblue')
    axes[0].axvline(np.sqrt(2), color='red', lw=2, label=f'√2 ≈ {np.sqrt(2):.4f} (洞!)')
    axes[0].set_yticks([]); axes[0].set_xlim(1, 2)
    axes[0].set_xlabel('数'); axes[0].set_title(f'[1,2] 上分母 ≤{N} 的有理数 ({len(vals)} 个)\n看起来连续, 但 √2 处是「洞」')
    axes[0].legend(); axes[0].grid(True, ls=':', alpha=0.3)
    # 右: √2 的连分数逼近 (越来越准)
    def continued_fraction_sqrt2(iters):
        # √2 = [1;2,2,2,...]
        approx = [1]
        for _ in range(iters):
            approx = [2] + approx
            approx = [1] + approx
        return approx
    # 用递推 1 + 1/(2+1/(2+...))
    convergents = []
    a_n = 1  # 起点
    for k in range(1, 11):
        # 第 k 个渐近分数: p_k/q_k
        # √2 连分数 [1;2,2,...] 渐近分数递推
        pass
    # 简单: 直接用 numpy 算 √2 的有理逼近序列
    p0, q0 = 1, 1   # 1
    p1, q1 = 3, 2   # 1.5
    conv = [(p0, q0), (p1, q1)]
    for _ in range(8):
        p2 = 2 * p1 + p0
        q2 = 2 * q1 + q0
        conv.append((p2, q2))
        p0, q0, p1, q1 = p1, q1, p2, q2
    errs = [abs(p/q - np.sqrt(2)) for p, q in conv]
    axes[1].semilogy(range(len(conv)), errs, 'o-', color='C2')
    axes[1].set_xlabel('连分数渐近分数序号'); axes[1].set_ylabel('|p/q - √2| (log)')
    axes[1].set_title('√2 的连分数逼近: 越来越准\n√2 = [1;2,2,2,...] (无限不循环 → 无理)')
    axes[1].grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('wim_ch2_section1_rationals.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] wim_ch2_section1_rationals.png")


# ═══════════════════════════════════════════════════════════════════
# §2  √2 无理 (反证法)
# ═══════════════════════════════════════════════════════════════════
def section_2_sqrt2():
    print("\n" + "=" * 70)
    print("§2 √2 无理 — 数学史最经典反证法")
    print("=" * 70)
    print("""
    定理: √2 不是有理数。
    反证法 (归谬法):
      假设 √2 = p/q, 其中 p,q 互素 (既约分数)。
      则 2q² = p²
        → p² 是偶数 → p 是偶数 → 设 p = 2k
      代入: 2q² = 4k² → q² = 2k²
        → q² 是偶数 → q 是偶数
      但 p, q 都偶 与「互素」矛盾!
      所以假设错, √2 无理。QED.

    历史冲击: 古希腊毕达哥拉斯学派信仰「万物皆整数之比」,
    √2 无理的发现动摇了他们的信仰 (传说发现者被扔进海里)。
    几何含义: 单位正方形对角线 = √2, 不能用任何有理数度量 → 「不可公度」。
    """)
    # 程序「验证」: 找最好的有理逼近 p/q, 误差永远不为 0
    best = None; best_err = 1
    for q in range(1, 10001):
        p = round(np.sqrt(2) * q)
        err = abs(p / q - np.sqrt(2))
        if err < best_err:
            best_err = err; best = (p, q)
    print(f"  q≤10000 最佳有理逼近: {best[0]}/{best[1]} = {best[0]/best[1]:.10f}")
    print(f"  √2 = {np.sqrt(2):.10f}")
    print(f"  误差 = {best_err:.2e} (永远不为 0, 因为 √2 无理)")

    # 几何: 单位正方形对角线 = √2
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    sq = plt.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)], fill=False, ec='black', lw=2)
    ax.add_patch(sq)
    ax.plot([0, 1], [0, 1], 'r-', lw=2.5, label=f'对角线 = √2 ≈ {np.sqrt(2):.4f}')
    ax.text(0.5, 0.45, '1', fontsize=14, ha='center')
    ax.text(0.55, 0.05, '1', fontsize=14, ha='center')
    ax.text(0.6, 0.6, f'√2', fontsize=14, color='red')
    ax.set_xlim(-0.2, 1.3); ax.set_ylim(-0.2, 1.3); ax.set_aspect('equal')
    ax.set_title('√2 = 单位正方形对角线\n古希腊: 这条线无法用任何分数度量 (不可公度)')
    ax.legend(loc='upper left'); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('wim_ch2_section2_sqrt2.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] wim_ch2_section2_sqrt2.png")


# ═══════════════════════════════════════════════════════════════════
# §3  Cantor 对角线 (实数不可数)
# ═══════════════════════════════════════════════════════════════════
def section_3_cantor():
    print("\n" + "=" * 70)
    print("§3 Cantor 对角线法 — 实数不可数 (颠覆直觉)")
    print("=" * 70)
    print("""
    康托尔 1891: [0,1] 上的实数「比」自然数「多」— 不可数。
    对角线证明 (反证法):
      假设 [0,1] 实数可列: r₁, r₂, r₃, ... 每个写成无限小数
        r₁ = 0.d₁₁ d₁₂ d₁₃ ...
        r₂ = 0.d₂₁ d₂₂ d₂₃ ...
        ...
      构造新数 s = 0.e₁ e₂ e₃ ..., 其中 e_n ≠ d_nn (对角线变)
      则 s ≠ r₁ (第1位不同), s ≠ r₂ (第2位不同), ...
      但 s ∈ [0,1], 应在列表里 → 矛盾!
      所以 [0,1] 实数不可数。QED.

    哲学冲击: 「无限」也有大小之分。自然数/整数/有理数是同一级 (可数),
    实数是更大的无限。这彻底改变了数学家对「无穷」的理解。
    """)
    # 有限版演示: 假设 8 个 8 位小数构成"完整列表", 对角线构造一个不在列表里的
    np.random.seed(42)
    N = 8
    table = np.random.randint(0, 9, (N, N))   # 假装这是 [0,1] 实数列表的前 N 位
    print(f"  假设 {N} 个 {N} 位小数构成「完整列表」:")
    for i in range(N):
        s = ''.join(str(d) for d in table[i])
        print(f"    r{i+1} = 0.{s}...")
    # 对角线构造
    diag = [table[i, i] for i in range(N)]
    s_digits = [(d + 1) % 10 for d in diag]   # 第 n 位 ≠ d_nn
    s_str = ''.join(str(d) for d in s_digits)
    print(f"\n  对角线元素: {diag}")
    print(f"  构造的 s = 0.{s_str}... (每位 e_n = (d_nn+1) mod 10)")
    # 验证 s 不等于任何 r_i (前 N 位)
    differs = [s_digits[i] != table[i, i] for i in range(N)]
    print(f"  s 与每个 r_i 第 i 位不同? {all(differs)} → s 不在列表里!")

    # 可视化
    fig, ax = plt.subplots(figsize=(7, 5.5))
    tbl = ax.table(cellText=table.tolist(), loc='center', cellLoc='center')
    tbl.auto_set_font_size(False); tbl.set_fontsize(11); tbl.scale(1.2, 1.8)
    for i in range(N):
        tbl[i, i].set_facecolor('#ffcccc')   # 对角线高亮
        tbl[i, i].get_text().set_color('red')
        tbl[i, i].get_text().set_weight('bold')
    ax.set_title(f'对角线法: {N}×{N} 假列表\n改红字对角线 → 造出不在列表里的新数 s')
    ax.axis('off')
    plt.tight_layout(); plt.savefig('wim_ch2_section3_cantor.png', dpi=100, bbox_inches='tight')
    print(f"  [图已保存] wim_ch2_section3_cantor.png  (红色对角线被「改造」)")


# ═══════════════════════════════════════════════════════════════════
# §4  复数与欧拉公式
# ═══════════════════════════════════════════════════════════════════
def section_4_complex():
    print("\n" + "=" * 70)
    print("§4 复数与欧拉公式 — 数学最美等式")
    print("=" * 70)
    print("""
    复数 z = a + bi (i² = -1)。几何: 平面上的点 (a, b)。
    乘法 = 旋转 + 缩放。这是复数的几何灵魂。

    欧拉公式 (最深刻等式之一):
        e^(iθ) = cos θ + i sin θ
    特例 θ=π:
        e^(iπ) = -1   或   e^(iπ) + 1 = 0
    把数学最重要的 5 个常数 (0,1,π,e,i) 用一个等式串起!

    代数基本定理: 任何 n 次多项式在复数域有 n 个根 (含重根)。
    → 复数是「代数封闭」的, 数系扩张到此终结。
    """)
    # 欧拉公式可视化: e^(iθ) 在单位圆上转
    theta = np.linspace(0, 2 * np.pi, 200)
    re = np.cos(theta); im = np.sin(theta)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    axes[0].plot(re, im, 'C0', lw=2)
    for t_deg, c in [(0, 'red'), (90, 'green'), (180, 'purple'), (270, 'orange')]:
        t = np.deg2rad(t_deg)
        axes[0].arrow(0, 0, np.cos(t), np.sin(t), head_width=0.05, color=c, lw=2,
                      length_includes_head=True,
                      label=f'θ={t_deg}°: e^(iθ)={np.cos(t):.1f}+{np.sin(t):.1f}i')
    axes[0].axhline(0, color='gray', lw=0.5); axes[0].axvline(0, color='gray', lw=0.5)
    axes[0].set_aspect('equal'); axes[0].set_xlim(-1.3, 1.3); axes[0].set_ylim(-1.3, 1.3)
    axes[0].set_title('欧拉公式: e^(iθ) 在单位圆上\n乘法 = 旋转 (复数的几何灵魂)')
    axes[0].legend(fontsize=9, loc='upper left', bbox_to_anchor=(1.02, 1))
    axes[0].grid(True, ls=':', alpha=0.3)

    # 右: 复数乘法 = 旋转
    ax = axes[1]
    z1 = 1 + 1j   # 45°
    z2 = 0 + 1j   # 90°
    z3 = z1 * z2  # 乘以 i = 转 90°
    for z, c, lbl in [(z1, 'C0', f'z = {z1}'), (z2, 'C2', f'w = {z2} (i)'),
                      (z3, 'C3', f'z×w = {z3} (=z 旋转 90°)')]:
        ax.arrow(0, 0, z.real, z.imag, head_width=0.05, color=c, lw=2.5,
                 length_includes_head=True, label=lbl)
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
    ax.set_aspect('equal'); ax.set_xlim(-0.3, 2); ax.set_ylim(-0.3, 2)
    ax.set_title('复数乘法 = 旋转:\nz×i 把 z 逆时针转 90°')
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('wim_ch2_section4_complex.png', dpi=100, bbox_inches='tight')

    # 数值验证 e^(iπ) = -1
    e_ipi = np.exp(1j * np.pi)
    print(f"  数值验证: e^(iπ) = {e_ipi.real:.6f} + {e_ipi.imag:.6f}i ≈ -1  ✓")
    print(f"  [图已保存] wim_ch2_section4_complex.png")
    print("\n  💡 数系扩张的逻辑链到此完成:")
    print("     自然数 → 整数 → 有理数 → 实数(完备) → 复数(代数封闭)")
    print("     每步扩张都为「填补某种不足」: 减法→负数, 除法→分数, 极限→无理, 开方→复数。")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🔢 《什么是数学》第2章: 数系  |  阶段1 / 模块01\n")
    section_1_rationals()
    section_2_sqrt2()
    section_3_cantor()
    section_4_complex()
    print("\n" + "=" * 70)
    print("✅ 第2章跑通! 下一步: 读 ch02-数系.md 笔记, 做 exercises.md")
    print("=" * 70)
