# -*- coding: utf-8 -*-
"""
perceptron_xor_demo.py —— 学科史上最著名的 5 行反例
对应章：00-体系结构（一/三节：1969 冻结期起点；美之时刻①）

剧情：
  A 段：单层感知机 + 感知机学习规则，在 XOR 上训练 2000 轮 —— 必败
        （Minsky & Papert《Perceptrons》1969：线性不可分 → 第一次 AI 寒冬起点）
  B 段：两层 MLP（4 隐单元 tanh）+ 手写反向传播，训练 —— 必成
        （Rumelhart-Hinton-Williams 1986：反向传播复活连接主义）

断言：A 段训练后仍存在错分点；B 段四点全对（误差 < 1e-2）。
运行：python perceptron_xor_demo.py
"""
import numpy as np

np.random.seed(0)

X = np.array([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
Y = np.array([[0.], [1.], [1.], [0.]])          # XOR

print("═" * 62)
print("A 段：单层感知机 vs XOR（1969，Minsky-Papert 反例现场）")
print("═" * 62)

w = np.zeros(2); b = 0.0                          # 感知机从零权重开始
for epoch in range(2000):
    errors = 0
    for xi, yi in zip(X, Y):
        pred = 1.0 if (xi @ w + b) > 0 else 0.0
        if pred != yi[0]:                         # 感知机学习规则：错则更新
            w += (yi[0] - pred) * xi
            b += (yi[0] - pred)
            errors += 1
    if errors == 0:
        break

preds = (X @ w + b > 0).astype(float)
n_wrong = int((preds.reshape(-1) != Y.reshape(-1)).sum())
print(f"训练 {epoch+1} 轮后权重 w={w}, b={b:.2f}")
print(f"预测 {preds.reshape(-1)} vs 真值 {Y.reshape(-1)} → 错分 {n_wrong} 点")
assert n_wrong > 0, "断言失败：单层感知机竟学会了 XOR（数学上不可能）"
print("断言通过：单层感知机在 XOR 上必败——一条直线分不开对角（线性不可分）\n")

print("═" * 62)
print("B 段：两层 MLP（4 隐单元）+ 反向传播（1986，连接主义复活）")
print("═" * 62)

W1 = np.random.randn(2, 4) * 0.5; b1 = np.zeros(4)
W2 = np.random.randn(4, 1) * 0.5; b2 = 0.0
lr = 0.1
eps = 1e-12                                        # 防 log(0)

def forward(X):
    h = np.tanh(X @ W1 + b1)                       # 隐层 tanh
    p = 1.0 / (1.0 + np.exp(-(h @ W2 + b2)))       # 输出 sigmoid（概率）
    return h, p

for epoch in range(1, 50001):
    h, p = forward(X)
    if np.abs(p - Y).max() < 1e-2:
        break
    d_p = (p - Y) / (p * (1 - p) + eps)            # BCE 梯度（无 /N：全批量）
    d_p = np.clip(d_p, -5, 5)                      # 梯度裁剪防初期爆炸
    d_h = (d_p @ W2.T) * (1 - h ** 2)              # tanh 导数
    W2 -= lr * h.T @ d_p; b2 -= lr * d_p.sum()
    W1 -= lr * X.T @ d_h;      b1 -= lr * d_h.sum()

_, p = forward(X)
preds = (p > 0.5).astype(float)
print(f"训练 {epoch-1} 轮后输出概率 {p.reshape(-1).round(4)}")
print(f"预测 {preds.reshape(-1)} vs 真值 {Y.reshape(-1)}")
assert np.abs(p - Y).max() < 1e-2, "断言失败：MLP 未收敛"
print("断言通过：两层网络 4 个隐单元装下 XOR——深度不是能不能，而是多有效地能\n")

print("═" * 62)
print("收束：从 A 到 B 只加了一层隐藏层——AI 寒冬(1969)与复活(1986)之间")
print("      隔的不是算力，是一个会被求导的隐藏层。")
