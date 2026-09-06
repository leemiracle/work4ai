#!/usr/bin/env python3
"""数值分析核心实验：QR 分解 + 条件数（数值稳定性）"""
import numpy as np
# ML 关联：条件数→训练稳定性；QR→最小二乘→线性回归；浮点→PyTorch 反向传播

# 1. Gram-Schmidt QR 分解
A = np.array([[1.0, 1.0, 0.0], [1.0, 3.0, 1.0], [2.0, -1.0, 1.0]])
Q = np.zeros_like(A); R = np.zeros((A.shape[1], A.shape[1]))
for j in range(A.shape[1]):
    v = A[:, j].copy()
    for i in range(j):
        R[i, j] = Q[:, i] @ A[:, j]
        v -= R[i, j] * Q[:, i]
    R[j, j] = np.linalg.norm(v)
    Q[:, j] = v / R[j, j]
print("手写 QR - Q 正交性误差:", np.round(np.linalg.norm(Q.T @ Q - np.eye(3)), 15))
print("手写 QR - A=QR 重构误差:", np.round(np.linalg.norm(Q @ R - A), 15))

# 2. 条件数：良态 vs 病态
print("\n条件数（越大越病态）:")
for name, M in [("正交", np.random.randn(5,5)/np.sqrt(5)), ("Hilbert", np.array([[1/(i+j+1) for j in range(5)] for i in range(5)]))]:
    cond = np.linalg.cond(M)
    print(f"  {name}矩阵: κ={cond:.1f}")
print("=> Hilbert 矩阵病态：数值求解 Ax=b 时小扰动→大误差")
