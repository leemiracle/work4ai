"""
Spivak《Calculus》核心 3: 积分与微积分基本定理
================================================
阶段1 / 模块02 / Spivak 第3弹 (微积分的顶峰)
积分 = 黎曼和的极限; 微积分基本定理 = 积分与导数互逆
运行: python3 spivak_03_integral.py  (4 张 PNG)

§1 定积分 = 黎曼和的极限 (矩形逼近面积)
§2 微积分基本定理: ∫ 与 d 互逆 (微积分的顶峰)
§3 数值积分: 梯形 / Simpson (误差对比)
§4 应用: 概率密度积分 / 累积分布 / 期望
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# §1 黎曼和
def section_1_riemann():
    print("=" * 70)
    print("§1 定积分 = 黎曼和的极限")
    print("=" * 70)
    print("""
    定积分 ∫_a^b f(x) dx 的严格定义 (黎曼):
      把 [a,b] 切成 n 份, 每份宽 Δx, 取左端点 f(x_i)·Δx 求和,
      让 n→∞ (Δx→0), 这个和的极限就是积分。
      ∫ = 「无限细分割 + 求和」的极限。
    几何: f 曲线下方的面积。
    """)
    f = lambda x: x ** 2
    a, b = 0, 2
    exact = b ** 3 / 3 - a ** 3 / 3   # ∫x² = x³/3
    print(f"  ∫_0^2 x² dx 真值 = {exact:.6f}")
    print(f"  黎曼和逼近 (左端点):")
    for n in [5, 20, 100, 1000]:
        dx = (b - a) / n
        xs = np.linspace(a, b - dx, n)
        approx = (f(xs) * dx).sum()
        print(f"    n={n:>5}: 黎曼和={approx:.6f}, 误差={abs(approx-exact):.2e}")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, n in zip(axes, [4, 16, 64]):
        xs_plot = np.linspace(a, b, 200)
        ax.plot(xs_plot, f(xs_plot), 'C0', lw=2)
        dx = (b - a) / n
        xs = np.linspace(a, b - dx, n)
        ax.bar(xs, f(xs), width=dx * 0.95, color='orange', alpha=0.6, align='edge')
        approx = (f(xs) * dx).sum()
        ax.set_title(f'n={n}: 黎曼和={approx:.3f}\n真值={exact:.3f}')
        ax.grid(True, ls=':', alpha=0.3)
    plt.suptitle('黎曼和: 矩形越来越细 → 逼近真面积 (x² 在 [0,2])')
    plt.tight_layout(); plt.savefig('spivak_int_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_int_s1.png")


# §2 微积分基本定理
def section_2_ftc():
    print("\n" + "=" * 70)
    print("§2 微积分基本定理 — 微积分的顶峰")
    print("=" * 70)
    print("""
    微积分基本定理 (FTC): 导数和积分是「互逆运算」!
      若 F'(x) = f(x), 则 ∫_a^b f(x) dx = F(b) - F(a)
    含义: 不用算黎曼和极限, 找一个原函数 F, 算两端点值之差即可。
    这是微积分最深刻的定理, 连接了「导数(变化率)」和「积分(累积)」。
    """)
    # 验证: ∫_0^2 x² dx = [x³/3]_0^2 = 8/3
    # 导数 (x³/3)' = x² = f
    f = lambda x: x ** 2
    F = lambda x: x ** 3 / 3
    a, b = 0, 2
    print(f"  例: f(x)=x², 原函数 F(x)=x³/3 (因 F'=f)")
    print(f"  ∫_0^2 x² dx = F(2)-F(0) = {F(b)} - {F(a)} = {F(b)-F(a):.6f}")
    dn = (b - a) / 10000
    print(f"  黎曼和(n=10000) = {(f(np.linspace(a, b - dn, 10000)) * dn).sum():.6f}")
    # 多个例子
    cases = [(lambda x: x, lambda x: x**2/2, 0, 1, '∫x dx = x²/2'),
             (lambda x: np.cos(x), lambda x: np.sin(x), 0, np.pi, '∫cos = sin'),
             (lambda x: 1/x, lambda x: np.log(x), 1, np.e, '∫1/x = ln')]
    print(f"\n  FTC 验证:")
    for f, F, a, b, name in cases:
        approx = (f(np.linspace(a, b - 1e-6, 100000)) * (b-a)/100000).sum()
        exact = F(b) - F(a)
        print(f"    {name} [{a},{b}]: FTC={exact:.6f}, 黎曼和={approx:.6f}, 一致? {np.isclose(exact, approx, atol=1e-4)}")

    fig, ax = plt.subplots(figsize=(8, 5))
    xs = np.linspace(0, 2, 200)
    ax.fill_between(xs, f(xs), alpha=0.3, color='steelblue', label=f'∫_0^2 x² dx = {F(b)-F(a):.3f}')
    ax.plot(xs, F(xs), 'C2', lw=2.5, label='F(x)=x³/3 (原函数, F\'=x²)')
    ax.plot(xs, f(xs), 'C0', lw=2, label='f(x)=x² (被积函数)')
    ax.axhline(0, color='gray', lw=0.5)
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('微积分基本定理: F\'=f ⟹ ∫f = F(b)-F(a)\n(导数与积分互逆)')
    plt.tight_layout(); plt.savefig('spivak_int_s2.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_int_s2.png")


# §3 数值积分
def section_3_numerical():
    print("\n" + "=" * 70)
    print("§3 数值积分: 梯形法 / Simpson")
    print("=" * 70)
    print("""
    找不到原函数时 (如 ∫e^(-x²) dx, 无初等原函数), 用数值方法。
      梯形法:  每段用梯形 (两端点平均), 误差 O(1/n²)
      Simpson: 每两段用抛物线拟合, 误差 O(1/n⁴) — 快得多!
    """)
    f = lambda x: np.exp(-x ** 2)   # 高斯函数, 无初等原函数
    a, b = 0, 2
    # 真值 (用 scipy 或高精度)
    from scipy.integrate import quad
    exact, _ = quad(f, a, b)

    def trapezoid(n):
        xs = np.linspace(a, b, n + 1)
        return np.trapz(f(xs), xs)
    def simpson(n):
        from scipy.integrate import simpson as sp
        xs = np.linspace(a, b, n + 1)
        return sp(f(xs), xs)

    print(f"  ∫_0^2 e^(-x²) dx 真值 = {exact:.8f}")
    print(f"  {'n':>6} {'梯形':>12} {'误差':>10} | {'Simpson':>12} {'误差':>10}")
    for n in [10, 50, 200]:
        t, s = trapezoid(n), simpson(n)
        print(f"  {n:>6} {t:>12.8f} {abs(t-exact):>10.2e} | {s:>12.8f} {abs(s-exact):>10.2e}")
    print("  → Simpson 误差远小于梯形 (相同 n), 因抛物线拟合更准")

    fig, ax = plt.subplots(figsize=(8, 5))
    ns = [4, 8, 16, 32, 64, 128, 256]
    trap_err = [abs(trapezoid(n) - exact) for n in ns]
    simp_err = [abs(simpson(n) - exact) for n in ns]
    ax.loglog(ns, trap_err, 'o-', label='梯形 (O(1/n²))')
    ax.loglog(ns, simp_err, 's-', label='Simpson (O(1/n⁴))')
    ax.set_xlabel('n (分段数)'); ax.set_ylabel('误差 (log)')
    ax.set_title('数值积分收敛: Simpson 远快于梯形\n(相同 n, Simpson 误差小 ~1000 倍)')
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('spivak_int_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_int_s3.png")


# §4 应用
def section_4_apps():
    print("\n" + "=" * 70)
    print("§4 应用: 概率密度 / 累积分布 / 期望")
    print("=" * 70)
    print("""
    概率论里积分无处不在 (W5/W6 概率模块的严格根基):
      - 概率密度 f 满足 ∫f = 1 (总概率)
      - P(a≤X≤b) = ∫_a^b f(x) dx
      - 期望 E[X] = ∫ x·f(x) dx
      - 方差 Var(X) = ∫ (x-μ)²·f(x) dx
    这是阶段 2「概率严格化」(测度论) 的预告。
    """)
    # 标准正态 N(0,1) 的积分验证
    f = lambda x: np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi)
    xs = np.linspace(-4, 4, 1000)
    total = np.trapz(f(xs), xs)
    p_neg1_1 = np.trapz(f(xs[(xs >= -1) & (xs <= 1)]), xs[(xs >= -1) & (xs <= 1)])
    # 期望 E[X]
    xs2 = np.linspace(-5, 5, 2000)
    EX = np.trapz(xs2 * f(xs2), xs2)
    EX2 = np.trapz(xs2 ** 2 * f(xs2), xs2)
    var = EX2 - EX ** 2
    print(f"  标准正态 N(0,1):")
    print(f"    ∫f = {total:.6f} (应=1, 总概率)")
    print(f"    P(-1≤X≤1) = {p_neg1_1:.4f} (应≈0.6827, 68 规则)")
    print(f"    E[X] = {EX:.6f} (应=0)")
    print(f"    Var(X) = {var:.6f} (应=1)")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(xs, f(xs), 'C0', lw=2.5, label='N(0,1) 密度 f')
    ax.fill_between(xs[(xs >= -1) & (xs <= 1)], f(xs[(xs >= -1) & (xs <= 1)]),
                    alpha=0.3, color='orange', label=f'P(-1≤X≤1)≈{p_neg1_1:.3f}')
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_xlabel('x'); ax.set_ylabel('密度')
    ax.set_title('积分算概率: 概率密度曲线下的面积 = 概率\nP(-1≤X≤1)≈0.683 (正态的「68 规则」)')
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    plt.tight_layout(); plt.savefig('spivak_int_s4.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_int_s4.png")


if __name__ == "__main__":
    print("∫ Spivak 核心 3: 积分与微积分基本定理  |  阶段1 / 模块02\n")
    section_1_riemann()
    section_2_ftc()
    section_3_numerical()
    section_4_apps()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 spivak_03_integral.md, 做练习。微积分三件套(极限/导数/积分)完成!")
    print("=" * 70)
