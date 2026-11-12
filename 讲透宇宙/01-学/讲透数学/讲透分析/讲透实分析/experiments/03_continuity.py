"""
讲透实分析 03 章实验：连续性 + 一致连续 + 极值定理 + Lipschitz。
跑法：python3 -u experiments/03_continuity.py
反直觉发现：
  1. 连续 ≠ 光滑（Weierstrass，已在 00 章验证）
  2. 连续 ≠ 一致连续（1/x 在 (0,1]）
  3. 闭区间定理在开区间失效
  4. Lipschitz 是 ML 泛化的钥匙
"""
import numpy as np


def part1_continuous_vs_discontinuous():
    """对比连续 / 不连续 / Dirichlet"""
    print("=" * 65)
    print("[1] 连续 vs 不连续 vs Dirichlet（在 x=0 附近）")
    print("=" * 65)
    xs = np.array([-0.5, -0.1, -0.01, -0.001, 0.0, 0.001, 0.01, 0.1, 0.5])
    print(f"  {'x':<10} {'x² (连续)':<14} {'sin(1/x)':<14} {'Dirichlet*':<12}")
    for x in xs:
        f_cont = x ** 2
        f_disc = np.sin(1.0/x) if abs(x) > 1e-9 else 0.0
        f_dir = 1.0  # 浮点数都是有理，所以 Dirichlet 恒 1
        print(f"  {x:<+10.4f} {f_cont:<+14.4f} {f_disc:<+14.4f} {f_dir:<12.0f}")
    print("  * Dirichlet 函数无法用浮点表示（所有浮点都是有理），只能想象")
    print("  → sin(1/x) 在 0 附近震荡，极限不存在 → 不连续")


def part2_uniform_continuity():
    """一致连续 vs 不一致连续"""
    print()
    print("=" * 65)
    print("[2] 一致连续性：固定 ε=0.1，找每个 x 需要的 δ")
    print("=" * 65)
    eps = 0.1

    print(f"\n  [A] f(x) = x² on [0, 1]，ε = {eps}")
    print(f"  {'x':<8} {'需要的 δ':<18}")
    for x in [0.0, 0.5, 1.0]:
        for delta_exp in range(-1, -12, -1):
            delta = 10.0 ** delta_exp
            if abs((x + delta) ** 2 - x ** 2) < eps:
                print(f"  {x:<8.2f} δ ≈ {delta:<18.2e}")
                break
    print("  → δ 的下界 ≈ 0.05（在 x=1 处）→ 一致连续 ✓")

    print(f"\n  [B] f(x) = 1/x on (0, 1]，ε = {eps}")
    print(f"  {'x':<8} {'需要的 δ':<18} {'趋势'}")
    for x in [1.0, 0.1, 0.01, 0.001, 0.0001]:
        for delta_exp in range(-1, -20, -1):
            delta = 10.0 ** delta_exp
            if x + delta > 0 and abs(1.0/(x + delta) - 1.0/x) < eps:
                print(f"  {x:<8.5f} δ ≈ {delta:<18.2e} {'δ 越小'}")
                break
    print("  → x→0 时 δ→0 无下界 → 不一致连续 ✗")


def part3_extreme_value_theorem():
    """极值定理：闭区间连续函数取到极值"""
    print()
    print("=" * 65)
    print("[3] 极值定理：闭区间 ✓ vs 开区间 ✗")
    print("=" * 65)

    xs_closed = np.linspace(0, 1, 1001)
    f_closed = xs_closed ** 2
    print(f"\n  [A] f(x)=x² on [0, 1] (闭区间)")
    print(f"      max = {f_closed.max():.4f} at x={xs_closed[f_closed.argmax()]:.4f}")
    print(f"      min = {f_closed.min():.4f} at x={xs_closed[f_closed.argmin()]:.4f}")
    print(f"      → 极值取到 ✓")

    xs_open = np.linspace(0.001, 0.999, 999)
    f_open = xs_open ** 2
    print(f"\n  [B] f(x)=x² on (0, 1) (开区间)")
    print(f"      数值采样 max ≈ {f_open.max():.4f}, min ≈ {f_open.min():.4f}")
    print(f"      但 sup=1 和 inf=0 都不在区间内 → 极值取不到 ✗")

    print(f"\n  [C] f(x)=1/x on (0, 1] (无界)")
    print(f"      x→0 时 f→∞ → 无最大值 → 有界性定理失效 ✗")


def part4_lipschitz_ml():
    """应用：Lipschitz 连续在 ML"""
    print()
    print("=" * 65)
    print("[4] ML 应用：Lipschitz 连续 → 泛化界")
    print("=" * 65)
    print("  Lipschitz 连续：∃ L > 0, ∀ x, y: |f(x) - f(y)| ≤ L |x - y|")
    print("  → 比一致连续更强（δ = ε/L 不依赖点）")
    print()
    print("  常见激活函数的 Lipschitz 常数：")
    print("    ReLU(x) = max(0, x)       L = 1")
    print("    sigmoid(x) = 1/(1+e^-x)   L = 1/4 (最大斜率在 x=0)")
    print("    tanh(x)                   L = 1")
    print()

    # 验证 sigmoid 的 Lipschitz 常数 = max|f'|
    xs = np.linspace(-10, 10, 100000)
    s = 1.0 / (1.0 + np.exp(-xs))
    sigmoid_deriv = s * (1 - s)
    print(f"  验证：sigmoid 导数 max = {sigmoid_deriv.max():.6f} (理论 0.25) ✓")
    print()
    print("  ML 理论：神经网络是 L-Lipschitz ⟹ 泛化误差 ≤ L · R (R=数据半径)")
    print("  → 控制 Lipschitz 常数 = 控制泛化（spectral normalization / weight clip）")


def main():
    print("讲透实分析 03 章实验：连续性 + 一致连续 + 极值定理 + Lipschitz")
    part1_continuous_vs_discontinuous()
    part2_uniform_continuity()
    part3_extreme_value_theorem()
    part4_lipschitz_ml()
    print()
    print("=" * 65)
    print("✓ 4 个反直觉发现跑完。")
    print("  → 连续 ≠ 光滑（Weierstrass）")
    print("  → 连续 ≠ 一致连续（1/x 在 (0,1]）")
    print("  → 闭区间定理在开区间失效")
    print("  → Lipschitz 是 ML 泛化的钥匙")
    print("=" * 65)


if __name__ == "__main__":
    main()
