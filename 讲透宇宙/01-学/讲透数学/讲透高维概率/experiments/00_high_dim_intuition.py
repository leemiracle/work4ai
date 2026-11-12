"""
讲透高维概率 00 章实验：4 大高维反直觉。
跑法：python3 -u experiments/00_high_dim_intuition.py
"""
import numpy as np


def part1_sphere_volume_shell():
    """反直觉 1：高维球体积集中在"外壳"（赤道附近）"""
    print("=" * 65)
    print("[1] 高维球体积：n 维单位球，体积集中在外壳")
    print("=" * 65)
    # 单位球内随机采样：n(0,I) 归一化方向 + 半径 r^(1/n)
    # 半径分布：r^n 均匀 → r = U^(1/n)，U 均匀 [0,1]
    for n in [2, 5, 10, 50, 100, 500]:
        np.random.seed(0)
        N = 100000
        # 球内均匀采样
        directions = np.random.randn(N, n)
        directions /= np.linalg.norm(directions, axis=1, keepdims=True)
        radii = np.random.rand(N) ** (1.0/n)
        points = directions * radii[:, None]
        # 在 r > 0.9 的"外壳"内的比例
        shell_ratio = np.mean(radii > 0.9)
        print(f"  n={n:<4}维: 体积在 r>0.9 外壳内的比例 = {shell_ratio:.4f}")
    print("  → n 越大，体积越集中在外壳（赤道）")


def part2_random_vectors_orthogonal():
    """反直觉 2：两个高维随机向量几乎正交"""
    print()
    print("=" * 65)
    print("[2] 两个随机单位向量的余弦相似度")
    print("=" * 65)
    for n in [2, 10, 100, 1000]:
        np.random.seed(42)
        N = 10000
        sims = []
        for _ in range(N):
            v1 = np.random.randn(n)
            v2 = np.random.randn(n)
            v1 /= np.linalg.norm(v1)
            v2 /= np.linalg.norm(v2)
            sims.append(np.dot(v1, v2))
        sims = np.array(sims)
        print(f"  n={n:<5}: 余弦相似度 mean={sims.mean():+.4f}, std={sims.std():.4f}, |max|={np.abs(sims).max():.4f}")
    print("  → n 越大，余弦相似度越接近 0（几乎正交）")
    print('  → 这解释了高维词嵌入的"默认距离"现象')


def part3_distance_collapse():
    """反直觉 3：高维下所有点距离差不多"""
    print()
    print("=" * 65)
    print("[3] 维度诅咒：高维下最近/最远距离比 → 1")
    print("=" * 65)
    for n in [2, 10, 100, 1000]:
        np.random.seed(7)
        N = 1000
        X = np.random.rand(N, n)  # 单位超立方体内
        # 计算点 0 到所有其他点的距离
        origin = X[0]
        dists = np.linalg.norm(X[1:] - origin, axis=1)
        ratio = dists.min() / dists.max()
        print(f"  n={n:<5}: 最近距离 / 最远距离 = {ratio:.4f}")
    print("  → n 越大，最近/最远距离比 → 1（距离'塌缩'）")
    print("  → k-NN 在高维失效的根源")


def part4_concentration():
    """反直觉 4（祝福）：集中现象"""
    print()
    print("=" * 65)
    print("[4] 集中现象（祝福）：n 个 iid 均值的方差下降")
    print("=" * 65)
    print("  X ~ Bernoulli(0.5), X̄ = (X_1+...+X_n)/n")
    print(f"  {'n':<8} {'理论 std':<14} {'实测 std':<14} {'偏离 > 0.1 的概率':<18}")
    np.random.seed(123)
    for n in [10, 100, 1000, 10000]:
        N_trials = 100000
        samples = np.random.binomial(n, 0.5, N_trials) / n  # 每次是 n 个 Bernoulli 的均值
        theory_std = np.sqrt(0.25 / n)
        empirical_std = samples.std()
        dev_prob = np.mean(np.abs(samples - 0.5) > 0.1)
        # Hoeffding 界: P(|X̄-0.5|>0.1) ≤ 2*exp(-2*n*0.01)
        hoeffding = 2 * np.exp(-2 * n * 0.01)
        print(f"  n={n:<6} {theory_std:<14.5f} {empirical_std:<14.5f} {dev_prob:<10.6f} (Hoeffding 界={min(hoeffding,1):.6f})")
    print("  → 实测偏离概率随 n 指数下降 ✓")
    print("  → 这就是 ML 泛化的数学基础")


def main():
    print("讲透高维概率 00 章实验：4 大高维反直觉")
    part1_sphere_volume_shell()
    part2_random_vectors_orthogonal()
    part3_distance_collapse()
    part4_concentration()
    print()
    print("=" * 65)
    print("✓ 4 个反直觉发现跑完。")
    print("  → 高维空间反直觉，但集中现象是 ML 的祝福")
    print("=" * 65)


if __name__ == "__main__":
    main()
