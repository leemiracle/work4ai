"""
讲透实分析 00 章 Python 实验：感受微积分的"原罪"。
- 反直觉 1：Leibniz 伪导数在 dx 太小时崩坏（浮点精度极限）
- 反直觉 2：有理数逼近 sqrt(2) 但永远到不了（Q 有洞）
- 反直觉 3：Weierstrass 处处连续处处不可微函数

跑法：
    cd 讲透实分析
    python3 -u experiments/00_irrational_density.py
"""
import numpy as np


def part1_leibniz_derivative():
    """反直觉 1：Leibniz 伪导数的崩坏"""
    print("=" * 65)
    print("[1] Leibniz 伪导数：f(x)=x² 在 x=2 的伪导数（理论值=4）")
    print("=" * 65)
    print(f"  {'dx':<12} {'伪导数':<25} {'偏差':<15}")
    print(f"  {'-'*12} {'-'*25} {'-'*15}")
    for exp in [-1, -2, -4, -8, -10, -12, -14, -15, -16, -18, -20]:
        dx = 10.0 ** exp
        pseudo = (2.0 + dx) ** 2 - 2.0 ** 2
        pseudo /= dx
        print(f"  1e{exp:<10} {pseudo:<25.15f} {pseudo - 4:<+15.2e}")
    print()
    print("  → dx=1e-10 附近伪导数最接近 4")
    print("  → dx 更小（1e-15+）时浮点精度崩溃，伪导数偏离甚至变 0")
    print("  → 这就是 Newton/Leibniz '无穷小'的逻辑漏洞")
    print("  → ε-δ 定义绕开此漏洞：'对任意 ε>0, 存在 δ>0'")


def part2_rational_holes():
    """反直觉 2：有理数逼近 sqrt(2) 但永不到达"""
    print()
    print("=" * 65)
    print("[2] 有理数逼近 sqrt(2)：Q 在数轴上有'洞'")
    print("=" * 65)
    # sqrt(2) 的有理逼近（来自连分数 / 牛顿法）
    approximations = [
        (1, 1), (14, 10), (141, 100), (1414, 1000),
        (14142, 10000), (141421, 100000), (1414213, 1000000),
    ]
    print(f"  {'r (有理数)':<20} {'r²':<22} {'离 2 的差':<15}")
    print(f"  {'-'*20} {'-'*22} {'-'*15}")
    for p, q in approximations:
        r = p / q
        squared = r * r
        diff = squared - 2
        print(f"  {p}/{q} = {r:<10.6f}  {squared:<22.12f} {diff:<+15.2e}")
    print()
    print("  → 每个 r 都是有理数，但 r² 永远不等于 2（Pythagoras 悖论）")
    print("  → 序列是 Cauchy（收敛），但极限 sqrt(2) 不在 Q 里")
    print("  → Q 不完备 → 必须扩充到 R（Dedekind cut 填洞）")


def part3_weierstrass():
    """反直觉 3：Weierstrass 处处连续处处不可微函数"""
    print()
    print("=" * 65)
    print("[3] Weierstrass 函数：处处连续但处处不可微")
    print("=" * 65)
    # W(x) = Σ a^n cos(b^n π x), a=0.5, b=11（奇整数）
    a, b = 0.5, 11
    def W(x, n_terms=50):
        return sum(a ** n * np.cos(b ** n * np.pi * x) for n in range(n_terms))

    # 在 x=0.5 附近用不同 dx 计算伪导数
    x0 = 0.5
    print(f"  W(x) = Σ (0.5)^n cos(11^n π x), 取 50 项")
    print(f"  在 x = {x0} 附近，用不同 dx 计算伪导数 [W(x+dx)-W(x-dx)]/(2dx)：")
    print()
    print(f"  {'dx':<12} {'伪导数':<25}")
    print(f"  {'-'*12} {'-'*25}")
    for exp in [-1, -2, -3, -4, -6, -8, -10, -12]:
        dx = 10.0 ** exp
        pseudo = (W(x0 + dx) - W(x0 - dx)) / (2 * dx)
        print(f"  1e{exp:<10} {pseudo:<+25.6f}")
    print()
    print("  → dx 减小时，伪导数不收敛（震荡加剧）")
    print("  → 这说明 W 处处不可微（导数不存在）")
    print("  → 但 W 处处连续（级数一致收敛 → 连续）")
    print("  → 反直觉：'连续 ≠ 光滑'，Weierstrass 1872 颠覆了直觉")

    # 生成图像（保存到 png）
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x = np.linspace(0, 2, 5000)
        y = np.array([W(xi, n_terms=30) for xi in x])
        plt.figure(figsize=(10, 5))
        plt.plot(x, y, linewidth=0.5)
        plt.title("Weierstrass Function: continuous everywhere, differentiable nowhere")
        plt.xlabel("x")
        plt.ylabel("W(x)")
        plt.grid(True, alpha=0.3)
        import os
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weierstrass.png")
        plt.savefig(out, dpi=80, bbox_inches="tight")
        print(f"\n  📊 图像已保存：{out}")
    except Exception as e:
        print(f"\n  (matplotlib 不可用：{e})")


def main():
    print("讲透实分析 00 章实验：微积分的'原罪'")
    print()
    part1_leibniz_derivative()
    part2_rational_holes()
    part3_weierstrass()
    print()
    print("=" * 65)
    print("✓ 三个反直觉发现跑完。")
    print("  下一步：读 01-实数构造.md 看 Dedekind 怎么填洞。")
    print("=" * 65)


if __name__ == "__main__":
    main()
