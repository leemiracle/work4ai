"""
实验 07 — 三论统一：信息 × 控制 × 系统 综合演示
=================================================
把信息论（熵）、控制论（负反馈收敛）、系统论（自组织熵减）
放进一个脚本，展示三论如何描述同一个"学习"过程的不同层面。
跑法: python3 07_unification.py  (需 numpy, <1秒)
"""
import numpy as np
import math

print("=" * 60)
print("三论统一：一个'学习'过程的三层视角")
print("=" * 60)

# ── 信息论层：不确定性 ──
print("\n【信息论层】模型预测的不确定性（熵）")
# 模拟一个二分类，训练前后预测分布的熵
p_before = 0.5   # 随机猜
p_after = 0.95   # 训练后自信
H_before = -(p_before * math.log2(p_before) + (1 - p_before) * math.log2(1 - p_before))
H_after = -(p_after * math.log2(p_after) + (1 - p_after) * math.log2(1 - p_after))
print(f"  训练前: P(正)=0.5, 熵={H_before:.3f} bit（最大不确定）")
print(f"  训练后: P(正)=0.95, 熵={H_after:.3f} bit（几乎确定）")
print(f"  → 信息论视角：学习 = 降低预测熵")

# ── 控制论层：负反馈收敛 ──
print("\n【控制论层】训练的负反馈回路")
target = 0.0
x = 5.0  # 初始偏差
lr = 0.3
print(f"  目标={target}, 初始偏差={x}")
errors = [abs(x)]
for t in range(10):
    gradient = x  # 简化：梯度指向偏差
    x = x - lr * gradient  # 负反馈
    errors.append(abs(x))
print(f"  偏差序列: {[f'{e:.2f}' for e in errors[:6]]} ... → {errors[-1]:.4f}")
print(f"  → 控制论视角：SGD = 负反馈控制器（偏差→修正）")

# ── 系统论层：权重熵减（自组织）──
print("\n【系统论层】权重的自组织（熵减）")
np.random.seed(0)
# 模拟训练前后的权重分布
w_before = np.random.randn(1000)  # 高熵随机
w_after = w_before * 0.1  # 训练后大部分缩小（稀疏化）+ 少数放大（重要特征）
w_after[:50] *= 20  # 少数 hub 权重


def shannon_entropy(arr, bins=20):
    hist, _ = np.histogram(arr, bins=bins, density=True)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log2(hist) * (arr.max() - arr.min()) / bins)


E_before = shannon_entropy(w_before)
E_after = shannon_entropy(w_after)
print(f"  训练前权重熵: {E_before:.2f}（均匀随机）")
print(f"  训练后权重熵: {E_after:.2f}（少数大 + 多数小 = 结构化）")
print(f"  → 系统论视角：训练 = 权重自组织降熵")

# ── 统一 ──
print("\n" + "=" * 60)
print("【三论统一】同一个'学习'过程：")
print(f"  信息论：预测熵 {H_before:.2f}→{H_after:.2f}（不确定性降低）")
print(f"  控制论：偏差 {errors[0]:.2f}→{errors[-1]:.2f}（负反馈收敛）")
print(f"  系统论：权重熵 {E_before:.2f}→{E_after:.2f}（自组织结构化）")
print("=" * 60)
print("三者缺一不可：信息=地基层, 控制=骨架层, 系统=视角层")
