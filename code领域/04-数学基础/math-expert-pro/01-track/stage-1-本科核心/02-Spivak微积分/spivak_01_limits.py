"""
Spivak《Calculus》核心 1: 极限与 ε-δ
======================================
阶段1 / 模块02 / Spivak 第1弹 (阶段1的灵魂起点)
从「直觉极限」到「严格 ε-δ」— 数学成熟度的关键一跃
运行: python3 spivak_01_limits.py  (4 张 PNG)

§1 极限直觉: 函数趋近某点
§2 ε-δ 定义 + 程序自动找 δ (严格的「趋近」)
§3 极限运算法则 (和/积/商)
§4 陷阱: 震荡 (sin(1/x)) 与 0/0 不定式
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ═══════════════════════════════════════════════════════════════════
# §1  极限直觉
# ═══════════════════════════════════════════════════════════════════
def section_1_intuition():
    print("=" * 70)
    print("§1 极限直觉: 函数趋近某点")
    print("=" * 70)
    print("""
    直觉: 当 x「趋近」a 时, f(x)「趋近」L, 记 lim_{x→a} f(x) = L。
    关键: 不关心 x=a 处的值, 只关心 x 越来越靠近 a 时 f 的走向。

    例: f(x)=2x+1, 猜 lim_{x→3} f(x)=7。直觉对, 但数学家不满足于「猜」。
    挑战: 怎么「严格」定义「趋近」? 19 世纪数学家花了 100 年才想清楚 → ε-δ。
    """)
    f = lambda x: 2 * x + 1
    xs = np.linspace(2.5, 3.5, 400)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(xs, f(xs), 'C0', lw=2, label='f(x)=2x+1')
    ax.axvline(3, color='gray', ls=':', alpha=0.5)
    ax.axhline(7, color='gray', ls=':', alpha=0.5)
    ax.plot(3, 7, 'ro', ms=10, label='极限点 (3, 7)')
    ax.annotate('x→3 时 f(x)→7', xy=(3, 7), xytext=(3.15, 6.3), fontsize=11,
                arrowprops=dict(arrowstyle='->'))
    ax.set_xlabel('x'); ax.set_ylabel('f(x)'); ax.legend()
    ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('极限直觉: x 趋近 3 时, f(x)=2x+1 趋近 7\n但「趋近」要严格化 → ε-δ')
    plt.tight_layout(); plt.savefig('spivak_lim_s1.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_lim_s1.png")


# ═══════════════════════════════════════════════════════════════════
# §2  ε-δ 定义 + 程序验证
# ═══════════════════════════════════════════════════════════════════
def section_2_epsilon_delta():
    print("\n" + "=" * 70)
    print("§2 ε-δ 定义: 严格的「趋近」")
    print("=" * 70)
    print("""
    lim_{x→a} f(x) = L 的严格定义:
      ∀ ε > 0, ∃ δ > 0, 使得 0 < |x-a| < δ ⟹ |f(x)-L| < ε

    解读:
      ε = 你对 f(x) 偏离 L 的「容忍度」(任意小)
      δ = 我承诺的「x 必须多靠近 a」
      含义: 无论你给多小的 ε, 我都能找到 δ, 让 x 在 a 的 δ 邻域内时
            f(x) 一定落在 L 的 ε 邻域内。
      「你随便挑战 (ε), 我永远能应对 (δ)」 — 这就是「趋近」的严格化。

    例 f(x)=2x+1, a=3, L=7: |f(x)-7| = 2|x-3|。
      要 |f(x)-7|<ε ⟺ |x-3|<ε/2。所以 δ = ε/2。
    """)
    f = lambda x: 2 * x + 1
    a, L = 3, 7
    epsilons = [0.5, 0.2, 0.05]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, eps in zip(axes, epsilons):
        delta = eps / 2
        xs = np.linspace(a - 4 * delta, a + 4 * delta, 300)
        ax.plot(xs, f(xs), 'C0', lw=2)
        ax.axhspan(L - eps, L + eps, alpha=0.25, color='green', label=f'ε带 [{L-eps:.2f},{L+eps:.2f}]')
        ax.axvspan(a - delta, a + delta, alpha=0.25, color='orange', label=f'δ带 [{a-delta:.2f},{a+delta:.2f}]')
        ax.axvline(a, color='gray', ls=':'); ax.axhline(L, color='gray', ls=':')
        ax.plot(a, L, 'ro', ms=8)
        ax.set_title(f'ε={eps} → δ=ε/2={delta}\nx∈δ带 ⟹ f(x)∈ε带 ✓')
        ax.legend(fontsize=8); ax.grid(True, ls=':', alpha=0.3)
    plt.suptitle('ε-δ 定义可视化: 任意小 ε 都能找到 δ (f=2x+1 在 x→3)')
    plt.tight_layout(); plt.savefig('spivak_lim_s2.png', dpi=100, bbox_inches='tight')

    rng = np.random.default_rng(0)
    print(f"  程序验证 δ=ε/2 对随机 ε 成立 (100 测试点):")
    for eps in [rng.uniform(0.001, 1) for _ in range(5)]:
        delta = eps / 2
        test_xs = np.linspace(a - delta * 0.999, a + delta * 0.999, 100)
        ok = np.all(np.abs(f(test_xs) - L) < eps)
        print(f"    ε={eps:.4f}, δ={delta:.4f}, 全部满足? {ok}")
    print("  [图已保存] spivak_lim_s2.png")


# ═══════════════════════════════════════════════════════════════════
# §3  极限运算法则
# ═══════════════════════════════════════════════════════════════════
def section_3_rules():
    print("\n" + "=" * 70)
    print("§3 极限运算法则")
    print("=" * 70)
    print("""
    若 lim f = L, lim g = M (都存在), 则:
      和: lim(f+g) = L + M
      积: lim(f·g) = L · M
      商: lim(f/g) = L / M  (M ≠ 0)
    这三条让复杂极限可分解为简单极限。证明每条都要用 ε-δ (Spivak 第5章)。
    ⚠️ 前提: lim f 和 lim g 都存在! 否则法则失效。
    """)
    h = lambda x: x ** 2 + x
    approx = h(2 + 1e-8)
    print(f"  验证 lim_{{x→2}} (x²+x): 数值 ≈ {approx:.6f}, 法则 4+2=6 ✓")
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    xs = np.linspace(1.5, 2.5, 200)
    ax.plot(xs, xs ** 2 + xs, 'C0', lw=2, label='x²+x → 6 (和法则)')
    ax.plot(xs, xs ** 2 * xs, 'C2', lw=2, label='x²·x = x³ → 8 (积法则)')
    ax.axvline(2, color='gray', ls=':')
    ax.set_xlabel('x'); ax.legend(); ax.grid(True, ls=':', alpha=0.3)
    ax.set_title('极限运算法则: 和/积的极限 = 极限的和/积 (x→2)')
    plt.tight_layout(); plt.savefig('spivak_lim_s3.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_lim_s3.png")


# ═══════════════════════════════════════════════════════════════════
# §4  陷阱
# ═══════════════════════════════════════════════════════════════════
def section_4_traps():
    print("\n" + "=" * 70)
    print("§4 极限的陷阱: 震荡与 0/0")
    print("=" * 70)
    print("""
    陷阱 1: sin(1/x) 在 x→0 时无极限
      x→0 时 1/x→∞, sin(1/x) 在 -1 和 1 间无限震荡, 不趋近任何值。
      → 极限不存在。ε-δ 失败: 找不到 δ。

    陷阱 2: 0/0 不定式
      lim_{x→1} (x²-1)/(x-1): 分子分母都→0。
      但 (x²-1)/(x-1) = x+1 (x≠1), 极限 = 2。
      → 0/0 不代表「不存在」, 要化简。后续用洛必达/泰勒处理。
    """)
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    xs = np.linspace(-0.1, 0.1, 2000)
    xs = xs[xs != 0]
    axes[0].plot(xs, np.sin(1 / xs), 'C3', lw=0.8)
    axes[0].set_title('sin(1/x) 在 x→0: 无限震荡\n极限不存在 (ε-δ 找不到 δ)')
    axes[0].set_ylim(-1.2, 1.2); axes[0].axvline(0, color='gray', ls=':')
    axes[0].grid(True, ls=':', alpha=0.3)
    xs2 = np.linspace(0.5, 1.5, 200)
    axes[1].plot(xs2, (xs2 ** 2 - 1) / (xs2 - 1), 'C0', lw=2, label='(x²-1)/(x-1) = x+1')
    axes[1].plot(1, 2, 'ro', ms=10, label='x=1 处极限 = 2 (0/0 化简)')
    axes[1].legend(); axes[1].grid(True, ls=':', alpha=0.3)
    axes[1].set_title('0/0 不定式: 化简后极限存在\n(x²-1)/(x-1)=x+1 → 2')
    plt.tight_layout(); plt.savefig('spivak_lim_s4.png', dpi=100, bbox_inches='tight')
    print("  [图已保存] spivak_lim_s4.png")
    print("\n  💡 ε-δ 是数学家把「直觉」变成「严格」的典范。")
    print("     Spivak《Calculus》全书就是在训练这种严格性。")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("📈 Spivak 核心 1: 极限与 ε-δ  |  阶段1 / 模块02\n")
    section_1_intuition()
    section_2_epsilon_delta()
    section_3_rules()
    section_4_traps()
    print("\n" + "=" * 70)
    print("✅ 跑通! 读 spivak_01_limits.md, 做练习")
    print("=" * 70)
