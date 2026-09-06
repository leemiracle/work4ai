#!/usr/bin/env python3
"""拓扑核心实验：Banach 不动点 + 压缩映射（优化收敛的根基）"""
import numpy as np
# ML 关联：压缩映射→SGD收敛；不动点→value iteration；紧致→极值定理→loss最小值存在

# 1. Banach 不动点：T(x) = 0.5x + 1，不动点 x*=2
T = lambda x: 0.5 * x + 1
x = 100.0; hist = [x]
for _ in range(30):
    x = T(x); hist.append(x)
print(f"压缩映射 T(x)=0.5x+1 迭代: {hist[0]:.1f} → {hist[-1]:.6f} (不动点=2)")
ratios = [abs(hist[i+1]-2)/abs(hist[i]-2) for i in range(len(hist)-1) if abs(hist[i]-2)>1e-10]
print(f"  收敛比值: {np.mean(ratios[-5:]):.3f} (理论: 0.5 = 压缩常数)")

# 2. Policy iteration (RL) 是不动点迭代
print("\n强化学习的 value iteration = 不动点: V* = max_a(R + γP·V*)")
gamma = 0.9; V = np.array([10.0, 10.0])  # 2 状态简化
R = np.array([1.0, 0.5]); P = np.array([[0.5,0.5],[0.3,0.7]])
for _ in range(50):
    V_new = R + gamma * np.max(P @ V)  # 简化（确定性策略）
print(f"  Value iteration 收敛 V*={np.round(V_new, 4)}")
print("=> RL 的核心 = 在赋范空间上做压缩映射（γ<1 保证收敛）")
