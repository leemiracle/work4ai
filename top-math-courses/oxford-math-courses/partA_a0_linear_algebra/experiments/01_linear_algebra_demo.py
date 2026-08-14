#!/usr/bin/env python3
"""线性代数核心实验：SVD + PCA + LoRA 低秩近似（验证 Eckart-Young 定理）"""
import numpy as np
# ML 关联：SVD → PCA → LoRA(W ≈ W0 + BA)，Transformer 压缩

np.random.seed(42)
A = np.random.randn(8, 5)
U, s, Vt = np.linalg.svd(A, full_matrices=False)
print("奇异值:", np.round(s, 3))

# Eckart-Young: 最佳秩 k 近似
for k in [1, 2, 3]:
    A_k = U[:, :k] @ np.diag(s[:k]) @ Vt[:k, :]
    err = np.linalg.norm(A - A_k, "fro")
    lower = s[k] if k < len(s) else 0
    print(f"k={k}: 误差={err:.4f}  σ_{k+1}={lower:.4f}  (应相等)")

# PCA = 数据矩阵 SVD
X = np.random.randn(200, 3) @ np.random.randn(3, 5)
Xc = X - X.mean(0)
Ux, sx, Vtx = np.linalg.svd(Xc, full_matrices=False)
print("\nPCA 主成分解释方差比:", np.round(sx**2 / (sx**2).sum(), 3))

# LoRA: W ≈ W0 + BA (低秩更新)
W0 = np.random.randn(10, 10)
B = np.random.randn(10, 2) * 0.01
A = np.random.randn(2, 10) * 0.01
W_lora = W0 + B @ A
print(f"\nLoRA 更新 Frobenius 范数: {np.linalg.norm(B @ A):.4f} (vs W0: {np.linalg.norm(W0):.4f})")
print("=> LoRA 用秩 2 更新微调 10×10 矩阵，参数从 100 降到 20+20=40")
