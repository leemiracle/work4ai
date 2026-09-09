"""
熵的本质演示脚本
配合 08-cross-cutting/entropy.md 学习

运行：python3 entropy_demo.py
"""
import numpy as np
from collections import Counter


def shannon_entropy(probs):
    """香农熵 H = -sum(p * log2(p))，单位 bit"""
    probs = np.array(probs, dtype=float)
    probs = probs[probs > 0]  # 排除 0（0*log0 定义为 0）
    return -np.sum(probs * np.log2(probs))


def kl_divergence(p, q):
    """KL 散度 D(P||Q) = sum p * log(p/q)"""
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    mask = p > 0
    return np.sum(p[mask] * np.log2(p[mask] / q[mask]))


def cross_entropy(p, q):
    """交叉熵 H(P, Q) = -sum p * log q = H(P) + D(P||Q)"""
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    mask = p > 0
    return -np.sum(p[mask] * np.log2(q[mask]))


print("=" * 60)
print("实验 1: 熵 = 不确定性的度量")
print("=" * 60)
print(f"确定性事件 [1, 0, 0]        H = {shannon_entropy([1, 0, 0]):.3f} bit")
print(f"硬币 [0.5, 0.5]             H = {shannon_entropy([0.5, 0.5]):.3f} bit")
print(f"均匀 6 面骰子               H = {shannon_entropy([1/6]*6):.3f} bit")
print(f"均匀 26 字母                H = {shannon_entropy([1/26]*26):.3f} bit")
print(f"偏倚硬币 [0.99, 0.01]       H = {shannon_entropy([0.99, 0.01]):.3f} bit")
print(f"极偏硬币 [0.9999, 0.0001]   H = {shannon_entropy([0.9999, 0.0001]):.4f} bit")
print()
print("观察: 分布越均匀 -> 熵越高; 越确定 -> 熵越低")

print()
print("=" * 60)
print("实验 2: 英文文本的熵 (字母分布不均匀)")
print("=" * 60)
text = ("the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs " * 50)
text_clean = text.replace(" ", "").replace(".", "")
freq = Counter(text_clean)
total = sum(freq.values())
probs = [c/total for c in freq.values()]
H_text = shannon_entropy(probs)
print(f"英文样本字符熵           H ≈ {H_text:.3f} bit/char")
print(f"理论均匀分布(26 字母)    H = {shannon_entropy([1/26]*26):.3f} bit/char")
print(f"香农 1948 年实测英文     H ≈ 4.03 bit/char (考虑字符频率)")
print(f"考虑词级冗余后           H ≈ 1.0-1.5 bit/char")
print()
print("观察: 英文远非均匀 -> 可被压缩约 50%-70%")

print()
print("=" * 60)
print("实验 3: KL 散度 — 衡量两个分布的差异")
print("=" * 60)
p = [0.5, 0.5]
q_close = [0.49, 0.51]
q_far = [0.01, 0.99]
print(f"D(P||Q_close)  = {kl_divergence(p, q_close):.4f}  (两个分布很近)")
print(f"D(P||Q_far)    = {kl_divergence(p, q_far):.4f}  (两个分布很远)")
print(f"D(Q_close||P)  = {kl_divergence(q_close, p):.4f}  (反方向)")
print(f"D(Q_far||P)    = {kl_divergence(q_far, p):.4f}  (反方向)")
print()
print("观察: KL 不对称！方向不同结果不同。")
print("      这就是为什么分类任务用交叉熵: 它 = H(P) + D(P||Q)")

print()
print("=" * 60)
print("实验 4: 交叉熵 vs 真实熵 (模拟分类训练)")
print("=" * 60)
# 假设真实标签是 one-hot [1, 0, 0]
true = [1.0, 0.0, 0.0]
# 模型预测的不同阶段
preds = {
    "完美预测":       [1.0, 0.0, 0.0],
    "稍偏":           [0.7, 0.2, 0.1],
    "更偏":           [0.4, 0.4, 0.2],
    "完全乱猜":       [0.33, 0.33, 0.34],
    "反向预测":        [0.1, 0.8, 0.1],
}
H_true = shannon_entropy(true)
print(f"真实分布的熵: H(P) = {H_true:.3f} bit (one-hot 是确定事件)")
print()
for name, pred in preds.items():
    ce = cross_entropy(true, pred)
    kl = kl_divergence(true, pred)
    print(f"{name:12s} 预测={pred}  交叉熵={ce:.3f}  KL={kl:.3f}")
print()
print("观察: 预测越接近真实, 交叉熵越小; KL = 交叉熵 - H(P) = 交叉熵 - 0")
print("      训练神经网络分类器, 最小化交叉熵 = 最小化 KL = 让模型分布拟合数据")

print()
print("=" * 60)
print("实验 5: 最大熵原理 — 为什么高斯分布如此常见")
print("=" * 60)
# 已知均值=0, 方差=1 的所有分布里, 高斯的熵最大
import math
gauss_diff_entropy = 0.5 * math.log(2 * math.pi * math.e * 1.0)  # 单位 nat
print(f"高斯分布 N(0,1) 的微分熵: {gauss_diff_entropy:.4f} nat")
print("已知均值和方差的所有分布中, 高斯熵最大 (Jaynes 最大熵原理)")
print("这就是为什么自然现象经常是高斯的 (中心极限定理 + 最大熵)")

print()
print("=" * 60)
print("总结: 这些'熵'共享同一个数学骨架")
print("=" * 60)
print("• 玻尔兹曼熵: S = k * ln W")
print("• 香农熵:     H = -sum p log p")
print("• 交叉熵:     H(P,Q) = -sum p log q")
print("• KL 散度:    D(P||Q) = sum p log(p/q) = H(P,Q) - H(P)")
print()
print("同一个公式在不同学科的'投影' —— 这是世界深层统一性的证据。")
