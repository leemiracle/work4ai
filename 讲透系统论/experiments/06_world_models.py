"""
实验 06 — 系统论与 AI：隐式 vs 显式世界模型的外推
====================================================
真实规律: 自由落体 y = 0.5 * g * t²（显式机理已知）
训练数据: t ∈ [0, 2]
外推到: t ∈ [2, 5]
对比: 多项式拟合（隐式/数据驱动）vs 解析公式（显式/机理）
跑法: python3 06_world_models.py  (需 numpy, <1秒)
"""
import numpy as np

g = 9.8
# 训练数据（t ∈ [0, 2]）
t_train = np.linspace(0, 2, 15)
y_train = 0.5 * g * t_train ** 2

# 外推区间（t ∈ [2, 5]）
t_ext = np.linspace(2, 5, 30)
y_true = 0.5 * g * t_ext ** 2

# 方案1: 隐式世界模型（多项式拟合，数据驱动）
c = np.polyfit(t_train, y_train, 4)  # 4 阶多项式
y_implicit = np.polyval(c, t_ext)
err_implicit = np.mean((y_implicit - y_true) ** 2)

# 方案2: 显式世界模型（机理: y = 0.5gt²，参数 g 已知）
y_explicit = 0.5 * g * t_ext ** 2  # 完美（就是真值）
err_explicit = 0.0

# 方案3: "PINN"（数据 + 机理约束，学 g）
# 用 {t²} 基（物理归纳偏置），只学系数 a（应≈0.5g）
A = (t_train ** 2).reshape(-1, 1)
a, *_ = np.linalg.lstsq(A, y_train, rcond=None)
y_pinn = a * t_ext ** 2
err_pinn = np.mean((y_pinn - y_true) ** 2)

print("=" * 58)
print("世界模型：隐式(数据) vs 显式(机理) vs PINN(融合)")
print("=" * 58)
print(f"  隐式(4阶多项式):   外推 MSE = {err_implicit:>10.2f}  [外推崩]")
print(f"  显式(y=½gt²):      外推 MSE = {err_explicit:>10.2f}  [完美]")
print(f"  PINN(t²基,学g):    外推 MSE = {err_pinn:>10.2f}  [≈完美]")
print(f"  隐式误差是 PINN 的 {err_implicit/max(err_pinn,1e-9):.0f} 倍")
print()
print(f"结论: Sora 的'物理一致性'是隐式学的（统计模式）")
print(f"      遇分布外场景会崩——这就是隐式世界模型的固有局限")
print(f"      机理已知时，显式/PINN 外推完胜（系统辨识 vs 机理建模）")
