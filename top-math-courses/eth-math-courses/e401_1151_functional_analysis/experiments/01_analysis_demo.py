#!/usr/bin/env python3
"""实分析核心实验：ε-δ 极限数值验证 + 4 种收敛模式可视化"""
import numpy as np
# ML 关联：ε-δ → 数值稳定性；收敛模式 → 大数定律/CLT → SGD 收敛

# 1. ε-δ 验证 lim_{x→2} x² = 4：给定 ε，找 δ
def verify_epsilon_delta(eps):
    delta = min(eps / 5, 1.0)  # δ = ε/5（因为 |x²-4|=|x-2||x+2|≤5|x-2| 当 |x-2|<1）
    xs = np.linspace(2 - delta, 2 + delta, 1000)
    xs = xs[xs != 2]
    max_err = np.max(np.abs(xs**2 - 4))
    return max_err < eps, max_err
for eps in [0.1, 0.01, 0.001]:
    ok, err = verify_epsilon_delta(eps)
    print(f"ε={eps}: δ={min(eps/5,1.0):.4f}, 最大误差={err:.6f}, 满足: {ok}")

# 2. 4 种收敛模式：X_n → 0
print("\n4 种收敛模式（X_n = 1/n + noise）：")
for n in [10, 100, 1000, 10000]:
    samples = 1/n + np.random.randn(10000) * (1/np.sqrt(n))
    prob = np.mean(np.abs(samples) > 0.5)
    print(f"  n={n:5d}: P(|X|>0.5)={prob:.4f} (in probability: →0)")
# a.s. 收敛更强（单样本路径 →0）；L^p 需 E|X_n|^p →0
print("\n=> a.s. → in prob → in distribution (蕴含链)")
