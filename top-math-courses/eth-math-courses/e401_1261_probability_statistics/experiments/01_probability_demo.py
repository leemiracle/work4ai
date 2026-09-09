#!/usr/bin/env python3
"""概率论核心实验：大数定律 + CLT + KL 散度（ML 的数学根基）"""
import numpy as np
# ML 关联：LLN→SGD收敛；CLT→BatchNorm/置信区间；KL→VAE/RLHF/cross-entropy

np.random.seed(42)
# 1. 大数定律：样本均值 → 期望
print("大数定律: 样本均值 → E[X]=0.5 (uniform[0,1])")
for n in [10, 100, 1000, 10000, 100000]:
    mean = np.random.uniform(0, 1, n).mean()
    print(f"  n={n:6d}: 均值={mean:.5f}, 偏差={abs(mean-0.5):.5f}")

# 2. CLT: (样本均值 - 期望) * sqrt(n) → N(0, σ²)
print("\n中心极限定理: √n × (均值 - 0.5) → N(0, 1/12)")
scaled_means = []
for _ in range(10000):
    m = np.random.uniform(0, 1, 100).mean()
    scaled_means.append(np.sqrt(100) * (m - 0.5))
sm = np.array(scaled_means)
print(f"  实测: 均值={sm.mean():.4f} (应≈0), 方差={sm.var():.4f} (应≈1/12={1/12:.4f})")

# 3. KL 散度非对称
p = np.array([0.5, 0.5]); q = np.array([0.9, 0.1])
kl_pq = np.sum(p * np.log(p / q))
kl_qp = np.sum(q * np.log(q / p))
print(f"\nKL(p‖q)={kl_pq:.4f}, KL(q‖p)={kl_qp:.4f} (不对称!)")
print("=> cross-entropy = H(p) + KL(p‖q); VAE ELBO = 重建 - KL; RLHF = max E[r] - β·KL(π‖πref)")
