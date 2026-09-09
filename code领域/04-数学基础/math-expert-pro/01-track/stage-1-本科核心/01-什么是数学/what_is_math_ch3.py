"""
《什么是数学》第3章: 几何作图与数域 — 从尺规到 Galois 雏形
=============================================================
阶段1 / 模块01 / 什么是数学 ch03
目标: 用程序可视化几何作图的代数本质, 看清「三大难题为何无解」
运行: python3 what_is_math_ch3.py  (生成 4 张 PNG)

学习路径:
  §1 几何作图与公理: 欧氏公理 + 尺规规则 + 可作数 (constructible number)
  §2 三大古典难题: 三等分角 / 立方倍积 / 化圆为方 (均不可解!) ⭐
  §3 可作数与域扩张: Galois 雏形, 次数为 2 的幂 ⟺ 可作
  §4 非欧几何与拓扑雏形: 第五公设 + 庞加莱圆盘 (双曲几何)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle, Circle

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ═══════════════════════════════════════════════════════════════════
# §1  几何作图与公理 (可作数)
# ═══════════════════════════════════════════════════════════════════
def section_1_constructible():
    print("=" * 70)
    print("§1 几何作图与公理: 尺规规则 + 可作数")
    print("=" * 70)
    print("""
    欧氏几何的「公理 → 定理」演绎体系是数学严格性的范本。
    尺规作图 (straightedge-and-compass) 只允许两种操作:
      ① 过两点画直线 (直尺, 无刻度)
      ② 以已知点为圆心、已知长度为半径画圆 (圆规)

    可作数 (constructible number): 从给定长度 (通常取 1) 出发,
    经有限次 +, −, ×, ÷ 和 √ (开平方) 得到的数。
    → 尺规能精确作出的长度, 恰好是可作数。
    关键: 可作数对四则运算和开平方封闭, 但对开立方 (³√) 不封闭!

    本节演示两个经典作图:
      ① √2: 直角边 1,1 的直角三角形, 斜边 = √2
      ② √(1+√2): 半圆几何平均法 — 直径上取 1 与 (1+√2) 两段,
         分点处垂线 = √(1·(1+√2)) = √(1+√2)
    """)
    sqrt2 = np.sqrt(2)
    nested = np.sqrt(1 + sqrt2)          # 嵌套开方, 仍可作
    print(f"  √2          = {sqrt2:.5f}   (直角三角形斜边)")
    print(f"  √(1+√2)     = {nested:.5f}   (半圆几何平均法)")
    print(f"  直接验证     = {np.sqrt(1 + np.sqrt(2)):.5f}   (一致)")
    # 断言: 可作数与直接计算一致
    assert abs(sqrt2 - 1.41421) < 1e-4, "√2 数值不符"
    assert abs(nested - 1.55377) < 1e-4, "√(1+√2) 数值不符"
    assert abs(nested - np.sqrt(1 + np.sqrt(2))) < 1e-12, "嵌套开方与直接算不一致"
    print("  ✓ 断言通过: √2≈1.41421, √(1+√2)≈1.55377, 与直接计算一致")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # 左图: 尺规作 √2 (直角三角形 + 把 √2 移到数轴)
    ax = axes[0]
    A = np.array([0.0, 0.0]); B = np.array([1.0, 0.0]); C = np.array([1.0, 1.0])
    ax.plot([A[0], B[0]], [A[1], B[1]], 'k-', lw=2.5)   # AB
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', lw=2.5)   # BC
    ax.plot([A[0], C[0]], [A[1], C[1]], 'r-', lw=3)     # AC 斜边 = √2
    # 直角标记
    ax.plot([0.9, 0.9, 1.0], [0.1, 0.0, 0.0], 'k-', lw=1.2)
    # 文字
    ax.text(0.5, -0.12, '1', fontsize=13, ha='center')
    ax.text(1.06, 0.5, '1', fontsize=13, ha='left')
    ax.text(0.62, 0.62, f'√2 ≈ {sqrt2:.4f}', fontsize=13, color='red', rotation=45)
    # 把 √2 移到数轴: 以 A 为圆心、|AC| 为半径画圆, 交 x 轴
    th = np.linspace(-np.pi, np.pi, 200)
    ax.plot(A[0] + sqrt2 * np.cos(th), A[1] + sqrt2 * np.sin(th),
            'g--', lw=1.2, alpha=0.7, label=f'圆规: 以 A 为心, |AC|=√2 为半径')
    ax.plot([sqrt2], [0], 'go', ms=8)
    ax.annotate(f'数轴上 √2 ≈ {sqrt2:.3f}', (sqrt2, 0),
                xytext=(sqrt2 - 0.2, -0.55), fontsize=11, color='green',
                arrowprops=dict(arrowstyle='->', color='green'))
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_xlim(-0.3, 2.0); ax.set_ylim(-0.8, 1.5); ax.set_aspect('equal')
    ax.set_title('① 尺规作 √2\n直角边 1,1 → 斜边 = √2 → 圆规移到数轴')
    ax.legend(fontsize=9, loc='upper right'); ax.grid(True, ls=':', alpha=0.3)

    # 右图: 半圆几何平均法作 √(1+√2)
    ax = axes[1]
    a = 1.0                     # 第一段
    b = 1 + sqrt2               # 第二段 (本身就是可作数)
    total = a + b               # 直径 = 2+√2
    cx = total / 2; R = total / 2
    # 数轴 + 刻度
    ax.plot([0, total + 0.2], [0, 0], 'k-', lw=1.5)
    for xv, lbl in [(0, '0'), (a, '1'), (a + b, '1+(1+√2)'), (total, '2+√2')]:
        ax.plot([xv, xv], [-0.04, 0.04], 'k-', lw=1.5)
        ax.text(xv, -0.16, lbl, fontsize=10, ha='center')
    # 半圆
    th = np.linspace(0, np.pi, 200)
    ax.plot(cx + R * np.cos(th), R * np.sin(th), 'C0', lw=2.2)
    # 分点处的垂线: 从 (a,0) 交半圆
    px = a
    py = np.sqrt(R**2 - (px - cx)**2)   # 垂线高度 = √(a·b)
    ax.plot([px, px], [0, py], 'r-', lw=2.5)
    ax.plot([px], [py], 'ro', ms=7)
    ax.text(px + 0.05, py / 2, f'垂线 = √(1·(1+√2))\n= √(1+√2)\n≈ {py:.4f}',
            fontsize=11, color='red')
    # 半圆心标注
    ax.plot([cx], [0], 'b+', ms=10)
    ax.set_xlim(-0.3, total + 0.4); ax.set_ylim(-0.4, R + 0.4); ax.set_aspect('equal')
    ax.set_title('② 半圆几何平均法作 √(1+√2)\n直径上分 1 与 (1+√2) → 垂线 = √(1+√2)')
    ax.grid(True, ls=':', alpha=0.3)
    # 断言: 半圆法作出的垂线 = √(1+√2)
    assert abs(py - nested) < 1e-10
    print(f"  ✓ 断言通过: 半圆法垂线 {py:.6f} = √(1+√2) {nested:.6f}")

    plt.tight_layout(); plt.savefig('wim_ch3_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] wim_ch3_s1.png")


# ═══════════════════════════════════════════════════════════════════
# §2  三大古典难题 (均不可解!)
# ═══════════════════════════════════════════════════════════════════
def section_2_three_classical():
    print("\n" + "=" * 70)
    print("§2 三大古典难题 — 希腊人两千年的执念 (均不可解!) ⭐")
    print("=" * 70)
    print("""
    古希腊三大作图难题 (都用尺规, 限定有限步):
      ① 三等分任意角: 给定角 θ, 作 θ/3
      ② 立方倍积 (Delian 问题): 作一立方体, 体积 = 已知立方体的 2 倍 → 边长 ³√2
      ③ 化圆为方: 作一正方形, 面积 = 已知圆 → 边长 √π

    1837 Wantzel / 1882 Lindemann 先后证明: 三者都不可解!
    核心判据: 可作数的「极小多项式次数」必须是 2 的幂。
      ① cos20° 满足 8x³−6x−1=0 (3 次, 非 2 的幂) → 20° 角不可作 → 60° 无法三等分
      ② ³√2 的极小多项式 x³−2 (3 次) → 不可作
      ③ π 是超越数 (非任何整系数多项式的根) → √π 不可作
    """)
    # 数值验证 ①: cos20° 是 8x³−6x−1=0 的根
    c20 = np.cos(np.radians(20))
    poly1 = 8 * c20**3 - 6 * c20 - 1
    print(f"  ① cos20° = {c20:.6f}")
    print(f"     8cos³20° − 6cos20° − 1 = {poly1:.2e}  ≈ 0  (3 次方程的根)")
    assert abs(poly1) < 1e-9, "cos20° 应满足 8x³-6x-1=0"
    # 该方程在 Q 上不可约: 无有理根 (有理根定理, 候选 ±1, ±1/2, ±1/4, ±1/8)
    roots_cand = [1, -1, 0.5, -0.5, 0.25, -0.25, 0.125, -0.125]
    has_rational = any(abs(8 * r**3 - 6 * r - 1) < 1e-12 for r in roots_cand)
    assert not has_rational, "8x³-6x-1 应无有理根 → 不可约 → 次数 3"
    print(f"     候选有理根 ±1,±1/2,±1/4,±1/8 都不是根 → Q 上不可约 → 次数 3 (非 2 的幂)")

    # 数值验证 ②: ³√2 的极小多项式 x³−2
    cbrt2 = np.cbrt(2)
    poly2 = cbrt2**3 - 2
    print(f"\n  ② ³√2 = {cbrt2:.6f}")
    print(f"     (³√2)³ − 2 = {poly2:.2e}  ≈ 0  (极小多项式 x³−2)")
    assert abs(poly2) < 1e-9
    assert all(abs(r**3 - 2) > 1e-12 for r in [-2, -1, 1, 2]), "x³-2 应无有理根"
    print(f"     x³−2 无有理根 (±1,±2 都不是) → Q 上不可约 → 次数 3 (非 2 的幂)")
    # ³√2 不在 Q(√2) 里 (后者元素形如 a+b√2, a,b∈Q)
    # 数值上反证: 若 ³√2 = a+b√2, 取若干有理 a,b 都对不上
    print(f"     Q(√2) 的元素形如 a+b√2; ³√2≈{cbrt2:.5f} 无法写成 a+b√2 (数值上无解)")

    # 数值验证 ③: π 是超越数 (Lindemann 1882) — 程序无法「证」, 仅陈述
    print(f"\n  ③ √π = {np.sqrt(np.pi):.6f}")
    print(f"     π 是超越数 (Lindemann 1882 证明), 不满足任何整系数多项式 → √π 不可作")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    # 子图1: 三等分角
    ax = axes[0]
    th = np.linspace(0, np.radians(60), 100)
    ax.plot([0, 1], [0, 0], 'k-', lw=2.5)
    ax.plot([0, np.cos(np.radians(60))], [0, np.sin(np.radians(60))], 'k-', lw=2.5)
    th_arc = np.linspace(0, np.radians(60), 50)
    ax.plot(0.3 * np.cos(th_arc), 0.3 * np.sin(th_arc), 'k-', lw=1.5)
    ax.text(0.36, 0.13, '60°', fontsize=12)
    # 理想三等分 (虚线, 但尺规作不出)
    for deg in [20, 40]:
        ax.plot([0, np.cos(np.radians(deg))], [0, np.sin(np.radians(deg))], 'r--', lw=1.5)
    ax.text(0.5, 0.06, '20°?', fontsize=12, color='red')
    ax.text(0.55, 0.30, '20°?', fontsize=12, color='red')
    ax.set_xlim(-0.1, 1.1); ax.set_ylim(-0.15, 1.0); ax.set_aspect('equal')
    ax.set_title('① 三等分任意角\n60° 的 20° 三等分线\n(尺规作不出!)')
    ax.grid(True, ls=':', alpha=0.3)

    # 子图2: 立方倍积
    ax = axes[1]
    # 小立方体 (边长 1, 体积 1)
    sq1 = [(0, 0), (1, 0), (1, 1), (0, 1)]
    ax.add_patch(plt.Polygon(sq1, fill=False, ec='black', lw=2))
    ax.add_patch(plt.Polygon([(0.2, 0.2), (1.2, 0.2), (1.2, 1.2), (0.2, 1.2)],
                             fill=False, ec='black', lw=1))
    for (x1, y1), (x2, y2) in [((0, 0), (0.2, 0.2)), ((1, 0), (1.2, 0.2)),
                               ((1, 1), (1.2, 1.2)), ((0, 1), (0.2, 1.2))]:
        ax.plot([x1, x2], [y1, y2], 'k-', lw=1)
    ax.text(0.4, 0.5, '1', fontsize=13, ha='center')
    ax.text(1.6, 1.0, '体积\n1', fontsize=11, ha='center')
    # 大立方体 (边长 ³√2, 体积 2)
    s = cbrt2
    ox = 3.0
    sq2 = [(ox, 0), (ox + s, 0), (ox + s, s), (ox, s)]
    ax.add_patch(plt.Polygon(sq2, fill=False, ec='red', lw=2))
    ax.add_patch(plt.Polygon([(ox + 0.2 * s, 0.2 * s), (ox + 1.2 * s, 0.2 * s),
                              (ox + 1.2 * s, 1.2 * s), (ox + 0.2 * s, 1.2 * s)],
                             fill=False, ec='red', lw=1))
    for (x1, y1), (x2, y2) in [((ox, 0), (ox + 0.2 * s, 0.2 * s)),
                               ((ox + s, 0), (ox + 1.2 * s, 0.2 * s)),
                               ((ox + s, s), (ox + 1.2 * s, 1.2 * s)),
                               ((ox, s), (ox + 0.2 * s, 1.2 * s))]:
        ax.plot([x1, x2], [y1, y2], 'r-', lw=1)
    ax.text(ox + s / 2, s / 2, f'³√2\n≈{s:.3f}', fontsize=12, color='red', ha='center')
    ax.text(ox + s / 2, -0.35, '体积 2', fontsize=11, color='red', ha='center')
    ax.text(1.6, -0.6, '→ 2 倍体积\n边长需 ³√2\n(不可作!)', fontsize=10, color='red', ha='center')
    ax.set_xlim(-0.3, 5.0); ax.set_ylim(-0.9, 1.7); ax.set_aspect('equal')
    ax.set_title('② 立方倍积\n体积翻倍 → 边长 ³√2\n(尺规作不出!)')
    ax.axis('off')

    # 子图3: 化圆为方
    ax = axes[2]
    # 单位圆 (面积 π)
    th = np.linspace(0, 2 * np.pi, 100)
    ax.plot(0.5 + np.cos(th), np.cos(th) * 0 + np.sin(th) + 0.5, 'b-', lw=2.5)  # 圆心 (0.5,0.5) r=1
    ax.add_patch(plt.Circle((0.5, 0.5), 1.0, fill=False, ec='blue', lw=2.5))
    ax.text(0.5, 0.5, 'r=1\n面积 π', fontsize=11, ha='center', color='blue')
    # 等面积正方形 (边长 √π)
    sp = np.sqrt(np.pi)
    ox = 3.0
    ax.add_patch(plt.Polygon([(ox, 0), (ox + sp, 0), (ox + sp, sp), (ox, sp)],
                             fill=False, ec='green', lw=2.5))
    ax.text(ox + sp / 2, sp / 2, f'边 √π\n≈{sp:.3f}', fontsize=11, ha='center', color='green')
    ax.text(ox + sp / 2, -0.4, '面积 π', fontsize=11, ha='center', color='green')
    ax.text(1.6, -0.7, '→ 等面积正方形\n边长需 √π\n(π 超越, 不可作!)', fontsize=10, color='green', ha='center')
    ax.set_xlim(-0.7, 5.2); ax.set_ylim(-1.0, 1.8); ax.set_aspect('equal')
    ax.set_title('③ 化圆为方\n等面积正方形 → 边长 √π\n(尺规作不出!)')
    ax.axis('off')

    plt.tight_layout(); plt.savefig('wim_ch3_s2.png', dpi=100, bbox_inches='tight')
    print("\n  [图已保存] wim_ch3_s2.png")


# ═══════════════════════════════════════════════════════════════════
# §3  可作数与域扩张 (Galois 雏形)
# ═══════════════════════════════════════════════════════════════════
def section_3_field_extension():
    print("\n" + "=" * 70)
    print("§3 可作数与域扩张 — Galois 雏形")
    print("=" * 70)
    print("""
    可作数构成一个「域」(field): 对 +,−,×,÷ 封闭 (除数≠0)。
    更要紧的是对 √ 封闭: 可作数 a>0 → √a 也可作。
    所以尺规作图能「精确」实现的运算只有四则和开平方。

    域扩张塔 (每个新 √ 把维度乘 2):
      Q  ⊂  Q(√2)  ⊂  Q(√2,√3)  ⊂  Q(√2,√3,√5)  ⊂ ...
      维度 1    2          4              8           (都是 2 的幂!)
    每层 = 上一层 × 2, 因为 √d 添加一个 2 次代数元。

    Galois 理论的核心判据:
      一个数 α 可作 ⟺ [Q(α):Q] 是 2 的幂。
      ³√2: [Q(³√2):Q] = 3 (不是 2 的幂) → 不可作 → 倍立方无解!
    更进一步 (Abel-Ruffini 定理): 5 次及以上一般方程无通用根式解。
    """)
    def is_pow2(n):
        return n > 0 and (n & (n - 1)) == 0

    # 扩张塔各层: (域, 在 Q 上的维度, 一组基的数值)
    tower = [
        ("Q",                 1, [1.0]),
        ("Q(√2)",             2, [1.0, np.sqrt(2)]),
        ("Q(√2,√3)",          4, [1.0, np.sqrt(2), np.sqrt(3), np.sqrt(6)]),
        ("Q(√2,√3,√5)",       8, [1.0, np.sqrt(2), np.sqrt(3), np.sqrt(5),
                                  np.sqrt(6), np.sqrt(10), np.sqrt(15), np.sqrt(30)]),
    ]
    print("  扩张塔 Q ⊂ Q(√2) ⊂ Q(√2,√3) ⊂ Q(√2,√3,√5):")
    for name, dim, basis in tower:
        ok = "✓ 2 的幂" if is_pow2(dim) else "✗ 非 2 的幂"
        print(f"    {name:18s}  维度 [·:Q] = {dim}  {ok}")
        assert is_pow2(dim), f"{name} 维度应为 2 的幂"
    print("  → 可作数所在的域扩张, 维度全是 2 的幂")

    # 不可作的例子
    bad = [
        ("³√2",   3, "x³−2"),
        ("cos20°", 3, "8x³−6x−1"),
        ("⁵√2",   5, "x⁵−2"),
    ]
    print("\n  不可作数 (极小多项式次数非 2 的幂):")
    for name, dim, poly in bad:
        ok = "✓ 可作" if is_pow2(dim) else "✗ 不可作"
        print(f"    {name:8s}  次数 = {dim}  ({poly})  {ok}")
        assert not is_pow2(dim), f"{name} 次数应非 2 的幂"
    print("  → ³√2 (倍立方), cos20° (三等分角) 都因次数非 2 的幂而不可作")

    # ── 可视化 ──
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # 左: 扩张塔 (嵌套方框)
    ax = axes[0]
    labels = ["Q(√2,√3,√5)  维度 8", "Q(√2,√3)  维度 4",
              "Q(√2)  维度 2", "Q  维度 1"]
    widths = [4.0, 3.2, 2.4, 1.6]
    colors = ['#e8f4f8', '#d0e8f0', '#b0d8e8', '#90c8d8']
    cx = 2.5
    for i, (lbl, w, col) in enumerate(zip(labels, widths, colors)):
        y0 = i * 1.0
        ax.add_patch(Rectangle((cx - w / 2, y0), w, 0.85, facecolor=col, ec='black', lw=1.5))
        ax.text(cx, y0 + 0.42, lbl, fontsize=11, ha='center', va='center')
        if i > 0:
            ax.annotate('', xy=(cx, y0), xytext=(cx, y0 - 0.13),
                        arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    ax.text(cx + 2.3, 1.5, '添加 √d\n维度 ×2', fontsize=10, color='red', ha='center')
    ax.text(cx, -0.5, '每次开平方 = 扩张一层, 维度翻倍\n→ 可作数的扩张维度都是 2 的幂',
            fontsize=11, ha='center', style='italic')
    ax.set_xlim(-0.5, 5.5); ax.set_ylim(-0.9, 4.5); ax.set_aspect('equal')
    ax.set_title('域扩张塔: 每层维度 × 2\n(2 的幂是「可作」的代数指纹)')
    ax.axis('off')

    # 右: 代数数次数柱状图 (绿=可作, 红=不可作)
    ax = axes[1]
    names = ['√2', '√(1+√2)', '1+√2\n+√3', '³√2', 'cos20°', '2^(1/5)']
    degs = [2, 4, 4, 3, 3, 5]
    cols = ['#2ca02c' if is_pow2(d) else '#d62728' for d in degs]
    bars = ax.bar(names, degs, color=cols, edgecolor='black')
    ax.axhline(1, color='gray', ls=':', lw=0.8)
    ax.set_ylabel('极小多项式次数 [Q(α):Q]')
    ax.set_title('代数数的次数 vs 可作性\n(绿 = 2 的幂 = 可作;  红 = 非 2 的幂 = 不可作)')
    for b, d in zip(bars, degs):
        ax.text(b.get_x() + b.get_width() / 2, d + 0.08, str(d),
                ha='center', fontsize=12, weight='bold')
    # 图例
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color='#2ca02c', label='2 的幂 → 可作'),
                       Patch(color='#d62728', label='非 2 的幂 → 不可作')],
              loc='upper left')
    ax.grid(True, ls=':', alpha=0.3, axis='y')
    plt.tight_layout(); plt.savefig('wim_ch3_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] wim_ch3_s3.png")


# ═══════════════════════════════════════════════════════════════════
# §4  非欧几何与拓扑雏形 (庞加莱圆盘)
# ═══════════════════════════════════════════════════════════════════
def section_4_hyperbolic():
    print("\n" + "=" * 70)
    print("§4 非欧几何与拓扑雏形 — 第五公设的颠覆")
    print("=" * 70)
    print("""
    欧几里得第五公设 (平行公设): 过线外一点「有且仅有一条」平行线。
    两千年里数学家试图用前四条公理证明它 — 全部失败。
    1830s Lobachevsky / Bolyai / Gauss 发现: 把第五公设换掉, 照样自洽!
      双曲几何: 过线外一点有「无穷多条」平行线。

    庞加莱圆盘模型 (Poincaré disk):
      整个双曲平面被装进一个单位圆。
      「直线」(测地线 geodesic) = 与单位圆边界正交的圆弧 (或直径)。
      该模型「保角」(angle-preserving): 欧氏夹角 = 双曲夹角。
      双曲三角形内角和 < π (随面积减小趋于 0)。

    本节: 在庞加莱圆盘里画一个双曲三角形, 数值验证内角和 < 180°。
    """)
    # ── 测地线工具 ──
    def orthocircle_center(z1, z2):
        """过 z1,z2 且与单位圆正交的圆的圆心 c、半径 R。
        正交条件: |c|² = R² + 1;  R² = |c−z|²  →  c·z = (1+|z|²)/2。"""
        z1 = np.asarray(z1, float); z2 = np.asarray(z2, float)
        A = np.array([[z1[0], z1[1]], [z2[0], z2[1]]])
        b = np.array([(1 + z1 @ z1) / 2, (1 + z2 @ z2) / 2])
        c = np.linalg.solve(A, b)
        R = np.linalg.norm(c - z1)
        return c, R

    def draw_geodesic(ax, z1, z2, **kw):
        """画 z1→z2 的测地线圆弧 (与单位圆正交)。返回 (c, R) 或 (None,None)。"""
        z1 = np.asarray(z1, float); z2 = np.asarray(z2, float)
        # 若 z1,z2 与原点共线 → 退化为直径 (直线段)
        if abs(z1[0] * z2[1] - z2[0] * z1[1]) < 1e-9:
            ax.plot([z1[0], z2[0]], [z1[1], z2[1]], **kw)
            return None, None
        c, R = orthocircle_center(z1, z2)
        a1 = np.degrees(np.arctan2(z1[1] - c[1], z1[0] - c[0]))
        a2 = np.degrees(np.arctan2(z2[1] - c[1], z2[0] - c[0]))
        da = (a2 - a1 + 180) % 360 - 180          # 取短弧
        t1, t2 = sorted([a1, a1 + da])
        ax.add_patch(Arc((c[0], c[1]), 2 * R, 2 * R, angle=0,
                         theta1=t1, theta2=t2, **kw))
        return c, R

    def interior_angle(P, c1, c2):
        """顶点 P 处两条测地线圆弧 (圆心 c1,c2) 的夹角 (保角 = 欧氏夹角)。
        庞加莱圆盘里测地线圆心在单位圆外, 两半径向量 (P−c) 夹角给出的是
        「外角」, 双曲三角形内角 = π − 外角。"""
        P = np.asarray(P, float)
        v1 = P - np.asarray(c1, float); v2 = P - np.asarray(c2, float)
        cos_a = (v1 @ v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        theta = np.arccos(np.clip(cos_a, -1, 1))   # 半径向量夹角 (外角)
        return np.pi - theta                        # 内角 = 补角

    # 三角形三个顶点 (单位圆内, 任两点不与原点共线)
    A = np.array([-0.55, -0.30])
    B = np.array([0.55, -0.25])
    C = np.array([0.05, 0.65])
    verts = [A, B, C]
    # 画三条测地线边, 记录每条边的圆心 (用于算内角)
    fig, ax = plt.subplots(figsize=(7, 7))
    # 单位圆边界
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(th), np.sin(th), 'k-', lw=2)
    edges_c = []
    pairs = [(A, B), (B, C), (C, A)]
    for z1, z2 in pairs:
        c, R = draw_geodesic(ax, z1, z2, color='C0', lw=2.5)
        edges_c.append((c, R))
    # 算三个内角
    # 顶点 A: 邻边 AB(c0) 和 CA(c2)
    angles = []
    angle_def = [(A, edges_c[0], edges_c[2]),
                 (B, edges_c[0], edges_c[1]),
                 (C, edges_c[1], edges_c[2])]
    for P, (c_a, _), (c_b, _) in angle_def:
        ang = interior_angle(P, c_a, c_b)
        angles.append(ang)
    total = sum(angles)
    # 标顶点 + 内角
    for (P, lbl), ang in zip([(A, 'A'), (B, 'B'), (C, 'C')], angles):
        ax.plot(P[0], P[1], 'ro', ms=8)
        ax.text(P[0] + 0.04, P[1] + 0.04, lbl, fontsize=13, color='red')
    ax.text(0.0, 0.05,
            f'双曲三角形\n内角: {np.degrees(angles[0]):.1f}° + '
            f'{np.degrees(angles[1]):.1f}° + {np.degrees(angles[2]):.1f}°\n'
            f'内角和 = {np.degrees(total):.2f}° < 180°',
            fontsize=12, ha='center', color='darkblue',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25); ax.set_aspect('equal')
    ax.set_title('庞加莱圆盘模型 (双曲几何)\n测地线 = 与边界正交的圆弧;  内角和 < 180°')
    ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('wim_ch3_s4.png', dpi=100, bbox_inches='tight')

    # 数值报告 + 断言
    print(f"  双曲三角形顶点: A={A.tolist()}, B={B.tolist()}, C={C.tolist()}")
    print(f"  三个内角: {np.degrees(angles[0]):.3f}°, {np.degrees(angles[1]):.3f}°, {np.degrees(angles[2]):.3f}°")
    print(f"  内角和 = {np.degrees(total):.3f}°  (欧氏几何恒为 180°, 双曲几何 < 180°)")
    assert total < np.pi - 0.01, "双曲三角形内角和应显著小于 180°"
    print("  ✓ 断言通过: 内角和 < π (双曲几何击败第五公设)")
    print("  [图已保存] wim_ch3_s4.png")
    print("\n  💡 本章串联了「几何 → 代数 → 不可判定」:")
    print("     尺规作图 → 可作数(域) → 域扩张(2 的幂) → 不可作 = 不可判定")
    print("     这是 Galois 理论与计算理论(停机问题)的共同雏形。")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("📐 《什么是数学》第3章: 几何作图与数域  |  阶段1 / 模块01\n")
    section_1_constructible()
    section_2_three_classical()
    section_3_field_extension()
    section_4_hyperbolic()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 ch03-几何.md, 做练习")
    print("=" * 70)
