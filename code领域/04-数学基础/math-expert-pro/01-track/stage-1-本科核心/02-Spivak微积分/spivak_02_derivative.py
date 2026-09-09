"""
Spivak《Calculus》核心 2: 导数与泰勒展开
==========================================
阶段1 / 模块02 / Spivak 第2弹
导数 = 极限定义的严格对象; 泰勒 = 多项式逼近任意光滑函数
运行: python3 spivak_02_derivative.py  (4 张 PNG)

§1 导数的极限定义: f'(a) = lim_{x→a} (f(x)-f(a))/(x-a) (割线→切线)
§2 求导法则: 幂/积/商/链式 (附数值验证)
§3 泰勒展开: 用多项式逼近任意光滑函数 (Spivak 的皇冠)
§4 应用: 极值 (f'=0) 与牛顿法求根
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ═══════════════════════════════════════════════════════════════════
# §1  导数的极限定义
# ═══════════════════════════════════════════════════════════════════
def section_1_def():
    print("=" * 70)
    print("§1 导数 = 极限的产物 (割线 → 切线)")
    print("=" * 70)
    print("""
    导数严格定义 (Spivak 第 9 章):
        f'(a) = lim_{x→a} (f(x) - f(a)) / (x - a)
              = lim_{h→0} (f(a+h) - f(a)) / h
    几何: 割线斜率 (两点) → 切线斜率 (一点的极限)。
    程序员: 这就是数值求导 (W4 学过), 但 Spivak 强调它是「极限定义的严格对象」。
    """)
    f = lambda x: x ** 2
    df_exact = lambda x: 2 * x
    a = 2
    print(f"  f(x)=x², f'(2) 解析 = {df_exact(a)}")
    print(f"  数值导数 (h 越小越准, 但太小有浮点误差):")
    for h in [1e-2, 1e-4, 1e-6, 1e-8, 1e-12]:
        num = (f(a + h) - f(a - h)) / (2 * h)
        print(f"    h={h:.0e}: f'≈{num:.8f}, 误差={abs(num - df_exact(a)):.2e}")

    # 可视化: 割线 → 切线
    fig, ax = plt.subplots(figsize=(8, 5))
    xs = np.linspace(-0.5, 3.5, 200)
    ax.plot(xs, f(xs), 'C0', lw=2, label='f(x)=x²')
    for h, c in [(1.5, 'red'), (0.8, 'orange'), (0.3, 'green')]:
        slope = (f(a + h) - f(a)) / h
        secant = slope * (xs - a) + f(a)
        ax.plot(xs, secant, '--', color=c, alpha=0.7, lw=1.5,
                label=f'割线 h={h}, 斜率={slope:.2f}')
    slope = df_exact(a)
    ax.plot(xs, slope * (xs - a) + f(a), 'k-', lw=2.5,
            label=f'切线 h→0, 斜率={slope}')
    ax.plot(a, f(a), 'ko', ms=8)
    ax.set_xlabel('x'); ax.set_ylabel('y'); ax.legend(fontsize=9)
    ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('导数 = 割线斜率的极限: h→0 时割线 → 切线\nf(x)=x² 在 x=2, f\'(2)=4')
    plt.tight_layout(); plt.savefig('spivak_drv_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_drv_s1.png")


# ═══════════════════════════════════════════════════════════════════
# §2  求导法则
# ═══════════════════════════════════════════════════════════════════
def section_2_rules():
    print("\n" + "=" * 70)
    print("§2 求导法则 (都用极限定义证明)")
    print("=" * 70)
    print("""
    幂法则:    (x^n)' = n·x^(n-1)
    和法则:    (f+g)' = f' + g'
    积法则:    (fg)' = f'·g + f·g'
    商法则:    (f/g)' = (f'·g - f·g') / g²
    链式法则:  (f(g(x)))' = f'(g(x))·g'(x)  ← 反向传播的灵魂 (W4 学过)
    每条都用 ε-δ / 极限定理证明。Spivak 第 9-10 章。
    """)
    # 数值验证积法则: f=x², g=sin(x), (fg)' = 2x·sin(x) + x²·cos(x)
    f = lambda x: x ** 2
    g = lambda x: np.sin(x)
    df = lambda x: 2 * x
    dg = lambda x: np.cos(x)
    prod_deriv = lambda x: df(x) * g(x) + f(x) * dg(x)
    h = 1e-6
    print(f"  积法则验证 (f=x², g=sin(x)):")
    for x in [0.5, 1.0, 2.0]:
        num = ((f(x + h) * g(x + h)) - (f(x - h) * g(x - h))) / (2 * h)
        ana = prod_deriv(x)
        print(f"    x={x}: 数值={num:.6f}, 解析(积法则)={ana:.6f}, 一致? {np.isclose(num, ana)}")
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    xs = np.linspace(-1, 3, 200)
    ax.plot(xs, prod_deriv(xs), 'C0', lw=2.5, label="(fg)' = f'g + fg' (积法则)")
    ax.plot(xs, df(xs) * g(xs), 'C1--', lw=1.5, label="f'·g 部分")
    ax.plot(xs, f(xs) * dg(xs), 'C2--', lw=1.5, label="f·g' 部分")
    ax.axhline(0, color='gray', lw=0.5)
    ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    ax.set_title("积法则: (fg)' = f'·g + f·g' (两项相加)")
    plt.tight_layout(); plt.savefig('spivak_drv_s2.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_drv_s2.png")


# ═══════════════════════════════════════════════════════════════════
# §3  泰勒展开 ⭐ Spivak 的皇冠
# ═══════════════════════════════════════════════════════════════════
def section_3_taylor():
    print("\n" + "=" * 70)
    print("§3 泰勒展开: 多项式逼近任意光滑函数")
    print("=" * 70)
    print("""
    泰勒定理 (微积分的皇冠): 任何「足够光滑」的函数在 a 附近可写成
        f(x) = Σ_{n=0}^{∞} f^(n)(a)/n! · (x-a)^n
    即「无穷多项式」。

    例 sin(x) 在 a=0 的泰勒级数:
        sin(x) = x - x³/3! + x⁵/5! - x⁷/7! + ...
    项数越多, 逼近越准, 适用范围越广。

    工程意义: 计算 sin 用多项式 (计算机只会 + - × ÷)!
    """)
    def taylor_sin(x, N):
        """sin(x) 的 N 阶泰勒逼近 (取到 x^(2N+1) 项)"""
        s = 0.0
        for n in range(N + 1):
            s += ((-1) ** n) * x ** (2 * n + 1) / np.math.factorial(2 * n + 1)
        return s

    xs = np.linspace(-2 * np.pi, 2 * np.pi, 400)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, np.sin(xs), 'k-', lw=3, label='真 sin(x)', zorder=5)
    colors = ['red', 'orange', 'green', 'blue', 'purple']
    for N, c in zip([1, 2, 3, 5, 8], colors):
        approx = np.array([taylor_sin(x, N) for x in xs])
        ax.plot(xs, approx, '--', color=c, lw=1.5, alpha=0.8,
                label=f'Taylor {2*N+1} 阶 (n≤{N})')
    ax.axhline(0, color='gray', lw=0.5); ax.set_ylim(-2, 2)
    ax.set_xlabel('x'); ax.legend(fontsize=8, ncol=2); ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('泰勒展开: 多项式阶数↑ → 逼近 sin 越准越远\n计算机算 sin 就是这么做的')
    plt.tight_layout(); plt.savefig('spivak_drv_s3.png', dpi=100, bbox_inches='tight')

    # 数值: sin(0.5) 的逼近过程
    print(f"  sin(0.5) 真值 = {np.sin(0.5):.10f}")
    for N in [1, 2, 3, 5]:
        print(f"    泰勒 n≤{N}: {taylor_sin(0.5, N):.10f}, 误差={abs(taylor_sin(0.5,N)-np.sin(0.5)):.2e}")
    print("  [图已保存] spivak_drv_s3.png")


# ═══════════════════════════════════════════════════════════════════
# §4  应用: 极值 + 牛顿法
# ═══════════════════════════════════════════════════════════════════
def section_4_apps():
    print("\n" + "=" * 70)
    print("§4 应用: 极值 (f'=0) 与牛顿法求根")
    print("=" * 70)
    print("""
    极值定理 (Fermat): 若 f 在 x=a 有局部极值且可导, 则 f'(a) = 0。
    → 找极值 = 解 f'(x) = 0。

    牛顿法求根 (导数的杀手级应用): 解 f(x) = 0
        x_{n+1} = x_n - f(x_n)/f'(x_n)
    几何: 沿切线找与 x 轴交点, 迭代逼近根。收敛极快 (二次收敛)。
    """)
    # 牛顿法求 √2: 解 f(x)=x²-2=0, f'=2x, x_{n+1}=x_n-(x_n²-2)/(2x_n)
    def newton_sqrt2(x0, iters=10):
        traj = [x0]
        x = x0
        for _ in range(iters):
            x = x - (x ** 2 - 2) / (2 * x)
            traj.append(x)
        return traj

    traj = newton_sqrt2(2.0)
    print(f"  牛顿法求 √2 (解 x²-2=0), 起点 x₀=2:")
    for i, x in enumerate(traj[:7]):
        err = abs(x - np.sqrt(2))
        print(f"    第{i}步: x={x:.12f}, 误差={err:.2e}")
    print(f"  → 二次收敛! 5 步达 1e-12 精度 (每步误差平方)")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    # 左: 牛顿法收敛
    axes[0].semilogy(range(len(traj)), [abs(x - np.sqrt(2)) for x in traj], 'o-', color='C3')
    axes[0].set_xlabel('迭代步'); axes[0].set_ylabel('|x_n - √2| (log)')
    axes[0].set_title('牛顿法求 √2: 二次收敛\n(每步误差 → 误差的平方)')
    axes[0].grid(True, ls=':', alpha=0.3)
    # 右: 极值 f'=0
    f = lambda x: x ** 3 - 3 * x
    df = lambda x: 3 * x ** 2 - 3
    xs = np.linspace(-2.5, 2.5, 200)
    axes[1].plot(xs, f(xs), 'C0', lw=2.5, label='f(x)=x³-3x')
    axes[1].plot(xs, df(xs), 'C1--', lw=1.5, label="f'(x)=3x²-3")
    axes[1].scatter([-1, 1], [f(-1), f(1)], color='red', s=100, zorder=5,
                    label="f'=0: 极值点 (-1,2) 极大, (1,-2) 极小")
    axes[1].axhline(0, color='gray', lw=0.5)
    axes[1].legend(fontsize=9); axes[1].grid(True, ls=':', alpha=0.3)
    axes[1].set_title("极值定理: f'=0 处是极值候选\n(还要二阶导判极大/极小)")
    plt.tight_layout(); plt.savefig('spivak_drv_s4.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_drv_s4.png")
    print("\n  💡 导数不只是「变化率」, 更是「优化」的工具:")
    print("     f'=0 找极值 → 机器学习的梯度下降 (W8) 的严格根基")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("📏 Spivak 核心 2: 导数与泰勒展开  |  阶段1 / 模块02\n")
    section_1_def()
    section_2_rules()
    section_3_taylor()
    section_4_apps()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 spivak_02_derivative.md, 做练习")
    print("=" * 70)
