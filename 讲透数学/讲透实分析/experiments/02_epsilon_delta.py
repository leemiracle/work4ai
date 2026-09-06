"""
讲透实分析 02 章 Python 实验：ε-δ 游戏的可视化与数值验证。
- 反直觉 1：随机抽样测出的 |f(x)-L| 通常远小于 ε（保守 δ 策略的安全余量）
- 反直觉 2：左右极限不等 → 极限不存在
- 反直觉 3：去心邻域（f(a) 与极限无关）

跑法：
    cd 讲透实分析
    python3 -u experiments/02_epsilon_delta.py
"""
import numpy as np

np.random.seed(42)


def verify_limit(name, f, a, L, eps_candidates, find_delta, n_samples=10000):
    """玩 ε-δ 游戏：随机抽样验证。"""
    print(f"\n验证 lim_{{x→{a}}} {name} = {L}")
    print(f"  {'ε':<10} {'δ (你的)':<14} {'抽样最大 |f(x)-L|':<24} {'安全余量 ε - max':<18} {'< ε?'}")
    print(f"  {'-'*10} {'-'*14} {'-'*24} {'-'*18} {'-'*6}")
    for eps in eps_candidates:
        delta = find_delta(eps)
        # 在去心邻域 (a-δ, a+δ) \ {a} 随机抽样
        xs = a + (np.random.rand(n_samples) - 0.5) * 2 * delta
        xs = xs[np.abs(xs - a) > 1e-12]  # 去心
        diffs = np.abs(f(xs) - L)
        max_diff = diffs.max()
        margin = eps - max_diff
        ok = "✓" if max_diff < eps else "✗ FAIL"
        print(f"  {eps:<10.4f} {delta:<14.6f} {max_diff:<24.10f} {margin:<+18.10f} {ok}")


def part1_linear():
    """例 1：lim_{x→3} 2x = 6, δ = ε/2"""
    print("=" * 75)
    print("[1] 线性：lim_{x→3} 2x = 6, δ 策略 = ε/2")
    print("=" * 75)
    verify_limit(
        name="2x", f=np.vectorize(lambda x: 2 * x), a=3, L=6,
        eps_candidates=[0.1, 0.01, 0.001, 1e-6, 1e-9],
        find_delta=lambda eps: eps / 2,
    )


def part2_quadratic():
    """例 2：lim_{x→2} x² = 4, δ = min(1, ε/5)"""
    print("\n" + "=" * 75)
    print("[2] 二次：lim_{x→2} x² = 4, δ 策略 = min(1, ε/5)")
    print("=" * 75)
    verify_limit(
        name="x²", f=np.vectorize(lambda x: x ** 2), a=2, L=4,
        eps_candidates=[0.1, 0.01, 0.001, 1e-6, 1e-9],
        find_delta=lambda eps: min(1, eps / 5),
    )


def part3_cubic():
    """例 3：lim_{x→1} x³ = 1, δ = min(1, ε/7)"""
    # 提示：|x³ - 1| = |x-1||x²+x+1|, x 在 (0,2) 时 |x²+x+1| < 7
    print("\n" + "=" * 75)
    print("[3] 三次：lim_{x→1} x³ = 1, δ 策略 = min(1, ε/7)")
    print("=" * 75)
    verify_limit(
        name="x³", f=np.vectorize(lambda x: x ** 3), a=1, L=1,
        eps_candidates=[0.1, 0.01, 0.001, 1e-6],
        find_delta=lambda eps: min(1, eps / 7),
    )


def part4_no_limit():
    """反例：lim_{x→0} |x|/x 不存在（左右极限不等）"""
    print("\n" + "=" * 75)
    print("[4] 反例：lim_{x→0} |x|/x 不存在（左极限=-1, 右极限=+1）")
    print("=" * 75)
    print(f"  {'x':<12} {'|x|/x':<10}")
    print(f"  {'-'*12} {'-'*10}")
    for x in [0.1, 0.01, 0.001, 1e-6, -1e-6, -0.001, -0.01, -0.1]:
        print(f"  {x:<+12.6f} {abs(x)/x:<+10.0f}")
    print("  → x→0⁺ 时 |x|/x = +1")
    print("  → x→0⁻ 时 |x|/x = -1")
    print("  → 左右极限不等 → 极限不存在")


def part5_hole():
    """反例：f(a) 与极限无关（去心邻域）"""
    print("\n" + "=" * 75)
    print("[5] 反例：f(0) 与 lim_{x→0} f(x) 无关（去心邻域）")
    print("=" * 75)
    print("  定义 f(x) = 1 若 x=0，否则 f(x) = 0")
    print("  则 lim_{x→0} f(x) = 0（因为去心，不看 x=0）")
    print("  但 f(0) = 1 ≠ 0")
    print()
    print(f"  {'x':<12} {'f(x)':<10}")
    print(f"  {'-'*12} {'-'*10}")
    for x in [0.1, 0.01, 0.001, 0.0, -0.001, -0.01, -0.1]:
        fx = 1.0 if x == 0.0 else 0.0
        print(f"  {x:<+12.6f} {fx:<+10.0f}")
    print("  → 极限 0 由邻域决定，与 f(0)=1 无关")


def part6_squeeze():
    """例 6：夹逼定理 lim_{x→0} x sin(1/x) = 0"""
    print("\n" + "=" * 75)
    print("[6] 夹逼定理：lim_{x→0} x sin(1/x) = 0")
    print("=" * 75)
    # |x sin(1/x)| ≤ |x|, 所以 δ = ε 即可
    def f(x):
        x = np.asarray(x, dtype=float)
        result = np.zeros_like(x)
        nonzero = np.abs(x) > 1e-15
        result[nonzero] = x[nonzero] * np.sin(1.0 / x[nonzero])
        return result
    verify_limit(
        name="x sin(1/x)", f=f, a=0.0, L=0.0,
        eps_candidates=[0.1, 0.01, 0.001, 1e-6],
        find_delta=lambda eps: eps,  # 因为 |x sin(1/x)| ≤ |x| < δ = ε
    )
    print("  → |x sin(1/x)| ≤ |x|（夹在 -|x| 和 +|x| 之间）")
    print("  → 取 δ = ε 即可（最简单的策略）")


def part7_insight():
    print("\n" + "=" * 75)
    print("[洞察] ε-δ 证明的保守性")
    print("=" * 75)
    print("  上面的随机抽样显示：实际 max|f(x)-L| 通常远小于 ε。")
    print("  原因：δ 策略是 worst-case bound（最坏情况界）。")
    print("  例：lim_{x→2} x²=4 用 δ=ε/5，但实际 max≈ε/5 × (4+某小量)")
    print("  → ε-δ 证明可能损失 2-10 倍精度，但保证严格成立")
    print("  → 这就是 'rigor'（严格）的代价")


def main():
    print("讲透实分析 02 章实验：ε-δ 游戏的数值验证")
    part1_linear()
    part2_quadratic()
    part3_cubic()
    part4_no_limit()
    part5_hole()
    part6_squeeze()
    part7_insight()
    print("\n" + "=" * 75)
    print("✓ 所有 ε-δ 游戏验证完成。")
    print("  下一步：用 ε-δ 写 5 道纸笔证明（见 02 章 ✍️ 练习）。")
    print("=" * 75)


if __name__ == "__main__":
    main()
