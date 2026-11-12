"""
实验 06 — AI 建模新范式：PINN 外推对比
=========================================
对比"纯数据拟合"vs"数据+物理约束"的外推能力。
真实规律: y = sin(x)（满足 y'' + y = 0）
训练数据只在 [0, 3]，外推到 [3, 6]。
跑法: python3 06_ai_modeling.py  (需 numpy, <1秒)
"""
import numpy as np

np.random.seed(0)
# 训练数据（只在 [0, 3]）
x_train = np.linspace(0, 3, 15)
y_train = np.sin(x_train) + np.random.normal(0, 0.05, 15)

# 外推区间 [3, 6]
x_ext = np.linspace(3, 6, 30)
y_true = np.sin(x_ext)

# 方案1: 纯多项式拟合（无物理约束）
c_pure = np.polyfit(x_train, y_train, 5)
err_pure = np.mean((np.polyval(c_pure, x_ext) - y_true) ** 2)

# 方案2: "PINN" 近似 —— 选一组基 {sin, cos}（物理归纳偏置）
# y = a*sin(x) + b*cos(x)，只学 a, b（2 参数 vs 6 参数）
A = np.vstack([np.sin(x_train), np.cos(x_train)]).T
coef, *_ = np.linalg.lstsq(A, y_train, rcond=None)
y_ext_pinn = coef[0] * np.sin(x_ext) + coef[1] * np.cos(x_ext)
err_pinn = np.mean((y_ext_pinn - y_true) ** 2)

print("=" * 58)
print("PINN 外推对比（真实 y=sin(x), 训练[0,3], 外推[3,6]）")
print("=" * 58)
print(f"纯多项式(5阶, 6参数):  外推 MSE = {err_pure:.4f}  [外推差]")
print(f"物理基{{sin,cos}}(2参数): 外推 MSE = {err_pinn:.4f}  [外推强]")
print(f"差距: 纯数据误差是 PINN 的 {err_pure/max(err_pinn,1e-9):.0f} 倍")
print()
print("结论: 机理已知(sin/cos 基)时, 物理归纳偏置让外推质量暴增")
print("      这就是 PINN 的核心价值——把物理定律当约束塞进学习")
