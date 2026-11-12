"""
讲透高维概率 01 章实验：集中不等式验证。
跑法：python3 -u experiments/01_concentration.py
"""
import numpy as np


def verify_hoeffding(distribution, dist_name, n_range, eps=0.1, trials=20000):
    """对每个 n，实测偏离概率 vs Hoeffding 上界"""
    print(f"\n  [{dist_name}] ε = {eps}")
    print(f"  {'n':<8} {'实测 P(|X̄-μ|>ε)':<22} {'Hoeffding 界':<18} {'紧度（界/实测）'}")
    for n in n_range:
        # 生成 trials 组，每组 n 个样本
        samples = distribution(size=(trials, n))
        means = samples.mean(axis=1)
        mu = samples.mean()  # 估计期望（或解析给）
        dev = np.mean(np.abs(means - mu) > eps)
        # Hoeffding 界（假设 [0,1] 区间）
        hoeff = 2 * np.exp(-2 * n * eps**2)
        tightness = hoeff / max(dev, 1e-12)
        print(f"  n={n:<6} {dev:<22.6f} {hoeff:<18.6f} {tightness:<.1f}x")


def part1_hoeffding_bernoulli():
    print("=" * 65)
    print("[1] Bernoulli(0.5) 的 Hoeffding 验证")
    print("=" * 65)
    verify_hoeffding(
        lambda size: np.random.binomial(1, 0.5, size=size).astype(float),
        "Bernoulli(0.5)",
        n_range=[10, 50, 100, 500, 1000],
        eps=0.1,
    )


def part2_hoeffding_uniform():
    print()
    print("=" * 65)
    print("[2] Uniform[0,1] 的 Hoeffding 验证")
    print("=" * 65)
    verify_hoeffding(
        lambda size: np.random.uniform(0, 1, size=size),
        "Uniform[0,1]",
        n_range=[10, 50, 100, 500, 1000],
        eps=0.1,
    )


def part3_generalization_bound():
    """ML 泛化界：样本数 n vs 误差界"""
    print()
    print("=" * 65)
    print("[3] ML 泛化界：固定 δ=0.05，n 越大误差界越小")
    print("=" * 65)
    delta = 0.05
    print(f"  δ = {delta}（置信度 95%）")
    print(f"  {'n':<10} {'泛化界 √(log(2/δ)/(2n))':<28} {'含义'}")
    for n in [100, 1000, 10000, 100000, 1000000]:
        bound = np.sqrt(np.log(2/delta) / (2*n))
        print(f"  n={n:<8} {bound:<28.6f} {'需 ' + str(int(1/bound**2)) + ' 样本达 1% 精度'}")


def part4_chernoff_vs_bernstein():
    """比较 Hoeffding vs Bernstein（后者用方差信息更紧）"""
    print()
    print("=" * 65)
    print("[4] Hoeffding vs Bernstein（Bernstein 用方差更紧）")
    print("=" * 65)
    print("  X ~ Bernoulli(0.1)（稀疏，方差小 0.09）")
    print(f"  {'n':<8} {'实测偏离':<14} {'Hoeffding':<14} {'Bernstein':<14} {'Bernstein 紧度'}")
    p = 0.1
    var = p * (1 - p)
    eps = 0.05
    for n in [100, 500, 1000, 5000]:
        samples = np.random.binomial(1, p, size=(20000, n)).astype(float)
        means = samples.mean(axis=1)
        dev = np.mean(np.abs(means - p) > eps)
        hoeff = 2 * np.exp(-2 * n * eps**2)
        bern = 2 * np.exp(-n * eps**2 / (2*var + 2*eps/3))
        print(f"  n={n:<6} {dev:<14.6f} {hoeff:<14.6f} {bern:<14.6f} {hoeff/max(bern,1e-12):<.2f}x")


def main():
    np.random.seed(42)
    print("讲透高维概率 01 章实验：集中不等式验证")
    part1_hoeffding_bernoulli()
    part2_hoeffding_uniform()
    part3_generalization_bound()
    part4_chernoff_vs_bernstein()
    print()
    print("=" * 65)
    print("✓ 集中不等式验证完成。")
    print("  → Hoeffding 是上界，实测远小于界（保守 10-1000 倍）")
    print("  → Bernstein 用方差信息更紧")
    print("  → ML 泛化误差 ∝ 1/√n")
    print("=" * 65)


if __name__ == "__main__":
    main()
