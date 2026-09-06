"""
讲透高维概率 02 章实验：次高斯分布验证。
"""
import numpy as np
from scipy import stats


def empirical_mgf(samples, lambs):
    """经验 mgf: E[exp(λX)]"""
    return np.array([np.mean(np.exp(l * samples)) for l in lambs])


def part1_mgf_comparison():
    print("=" * 65)
    print("[1] mgf 对比：E[exp(λX)] vs 次高斯上界 exp(σ²λ²/2)")
    print("=" * 65)
    np.random.seed(42)
    N = 100000
    lambs = np.linspace(0, 2, 21)

    distributions = [
        ("正态 N(0,1)", np.random.randn(N), 1.0),
        ("Rademacher ±1", np.random.choice([-1, 1], N), 1.0),
        ("均匀 U[-1,1]", np.random.uniform(-1, 1, N), 1.0),
    ]
    for name, samples, sigma2 in distributions:
        mgf = empirical_mgf(samples, lambs)
        bound = np.exp(sigma2 * lambs**2 / 2)
        ok = np.all(mgf <= bound * 1.01)  # 数值容差
        print(f"\n  {name}（σ² = {sigma2}）: 次高斯？{'✓' if ok else '✗'}")
        print(f"    λ=1: mgf={mgf[10]:.4f}, bound={bound[10]:.4f}, gap={bound[10]-mgf[10]:.4f}")
        print(f"    λ=2: mgf={mgf[20]:.4f}, bound={bound[20]:.4f}, gap={bound[20]-mgf[20]:.4f}")


def part2_hoeffding_lemma():
    print()
    print("=" * 65)
    print("[2] Hoeffding 引理：X ∈ [0,1] 是次高斯参数 1/4")
    print("=" * 65)
    np.random.seed(0)
    N = 100000
    samples = np.random.uniform(0, 1, N) - 0.5  # 中心化到 [-0.5, 0.5]
    # Hoeffding: X ∈ [a,b] ⟹ σ² = (b-a)²/4 = 1/4
    sigma2 = 0.25
    lambs = np.linspace(0, 3, 31)
    mgf = empirical_mgf(samples, lambs)
    bound = np.exp(sigma2 * lambs**2 / 2)
    violations = np.sum(mgf > bound * 1.01)
    print(f"  X ~ U[-0.5, 0.5], Hoeffding σ² = {sigma2}")
    print(f"  违反次数（λ ∈ [0,3]）= {violations} / {len(lambs)}")
    print(f"  → Hoeffding 引理验证 {'✓' if violations == 0 else '✗'}")


def part3_tail_comparison():
    print()
    print("=" * 65)
    print("[3] 尾部对比：P(|X| > t) vs 2exp(-t²/2)")
    print("=" * 65)
    np.random.seed(7)
    N = 1000000
    samples = np.random.randn(N)  # 标准正态
    print(f"  {'t':<6} {'实测 P(|X|>t)':<16} {'次高斯界 2e^(-t²/2)':<20} {'紧度'}")
    for t in [1, 2, 3, 4]:
        emp = np.mean(np.abs(samples) > t)
        bound = 2 * np.exp(-t**2 / 2)
        print(f"  {t:<6} {emp:<16.6f} {bound:<20.6f} {bound/max(emp,1e-12):.1f}x")


def part4_cauchy_not_subgaussian():
    print()
    print("=" * 65)
    print("[4] 反例：Cauchy 分布不是次高斯（重尾）")
    print("=" * 65)
    np.random.seed(11)
    N = 100000
    cauchy = np.random.standard_cauchy(N)
    # Cauchy 没有期望，mgf 在任何 λ>0 都是无穷
    print(f"  Cauchy 分布（重尾）：")
    for l in [0.1, 0.5, 1.0]:
        # E[exp(λX)] 应该爆炸
        val = np.mean(np.exp(l * cauchy))
        print(f"    E[exp({l}·X)] = {val:.4e}（理论 = ∞）")
    print("  → Cauchy 不是次高斯（尾部 ~ 1/t，比正态慢）")


def main():
    print("讲透高维概率 02 章实验：次高斯分布验证")
    part1_mgf_comparison()
    part2_hoeffding_lemma()
    part3_tail_comparison()
    part4_cauchy_not_subgaussian()
    print()
    print("=" * 65)
    print("✓ 次高斯验证完成。")
    print("  → 正态/Rademacher/均匀都是次高斯")
    print("  → Hoeffding 引理：有界 ⟹ 次高斯")
    print("  → Cauchy 反例：重尾不次高斯")
    print("=" * 65)


if __name__ == "__main__":
    main()
