#!/usr/bin/env python3
"""微积分核心实验：梯度下降 + 链式法则（反向传播的根基）"""
import numpy as np
# ML 关联：梯度 ∇f → SGD → Adam；链式法则 → 反向传播

# 1. 梯度下降最小化 f(x,y) = x² + 3y²
f = lambda x, y: x**2 + 3*y**2
grad = lambda x, y: np.array([2*x, 6*y])
x = np.array([5.0, 5.0])
lr, hist = 0.1, [f(*x)]
for i in range(100):
    x = x - lr * grad(*x)
    hist.append(f(*x))
print(f"梯度下降 100 步: f={hist[-1]:.6f}, x={np.round(x,4)} (应→0)")

# 2. 链式法则 = 反向传播（数值验证）
W1 = np.random.randn(3, 4); W2 = np.random.randn(4, 1)
x = np.random.randn(3, 1); y = np.array([[1.0]])
def forward(W1, W2):
    h = np.tanh(W1 @ x); o = W2 @ h; loss = 0.5*(o - y)**2
    return h, o, loss.sum()
h, o, loss = forward(W1, W2)
# 解析梯度（链式法则）
do = (o - y); dW2 = do @ h.T; dh = W2.T @ do * (1 - h**2); dW1 = dh @ x.T
# 数值梯度（有限差分验证）
eps = 1e-5; dW1_num = np.zeros_like(W1)
for i in range(W1.shape[0]):
    for j in range(W1.shape[1]):
        W1[i,j] += eps; _, _, lp = forward(W1, W2)
        W1[i,j] -= 2*eps; _, _, lm = forward(W1, W2)
        W1[i,j] += eps; dW1_num[i,j] = (lp - lm) / (2*eps)
err = np.abs(dW1 - dW1_num).max()
print(f"\n反向传播梯度数值验证: 最大误差={err:.2e} (应 < 1e-6)")
