#!/usr/bin/env python3
"""凸优化核心实验：梯度下降收敛速率 + KKT 条件（SVM 推导）"""
import numpy as np
# ML 关联：凸优化→SVM/Lasso；KKT→约束优化；收敛速率→Adam 调参

# 1. 强凸函数 f(x) = x² 的梯度下降：线性收敛
x = 10.0; lr = 0.1; hist = []
for i in range(50):
    hist.append(abs(x)); x = x - lr * 2 * x
ratios = [hist[i+1]/hist[i] for i in range(len(hist)-1) if hist[i] > 1e-10]
print(f"强凸 f=x² 梯度下降收敛速率: 比值≈{np.mean(ratios[-10:]):.3f} (理论: |1-2lr|={abs(1-2*lr):.3f})")

# 2. SVM 的 KKT: min 0.5||w||² s.t. y_i(w·x_i+b)≥1
# 对偶: max Σα_i - 0.5ΣΣ α_iα_j y_i y_j x_i·x_j, s.t. α_i≥0, Σα_i y_i=0
# 简单 2D 例子
X = np.array([[1,2],[2,3],[3,1],[4,1]]); y = np.array([1,1,-1,-1])
# 解析 SVM（暴力简化：找最大间隔方向）
from itertools import combinations
best_margin, best_w = 0, None
for i, j in combinations(range(4), 2):
    if y[i] != y[j]:
        d = X[i] - X[j]; w = d / np.linalg.norm(d)
        margin = abs(np.dot(w, X[i]) - np.dot(w, X[j])) / 2
        if margin > best_margin: best_margin, best_w = margin, w
print(f"\nSVM 最大间隔: {best_margin:.4f}, 法向量: {np.round(best_w, 4)}")
print("=> 间隔最大化 = 凸二次规划 + KKT 互补松弛 α_i(y_i(w·x_i+b)-1)=0")
