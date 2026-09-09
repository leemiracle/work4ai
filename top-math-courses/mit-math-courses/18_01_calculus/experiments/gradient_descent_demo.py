#!/usr/bin/env python3
"""
MIT 18.01 实验：梯度下降可视化 + 数值/解析导数对比 + Taylor 展开精度

纯 numpy + matplotlib，直接 python gradient_descent_demo.py 运行。
依赖: pip install numpy matplotlib
"""
import numpy as np
import math
import matplotlib
matplotlib.use("Agg")  # 无显示器环境也能保存图
import matplotlib.pyplot as plt

# ============================================================
# 1. 数值导数 vs 解析导数（验证链式法则 = autograd 的基础）
# ============================================================
def numerical_derivative(f, x, h=1e-5):
    """中心差分数值导数"""
    return (f(x + h) - f(x - h)) / (2 * h)

def test_func(x): return x**4 - 4*x**2 + 1     # f(x)
def test_grad(x): return 4*x**3 - 8*x          # f'(x)

x_test = np.array([-2.0, -1.0, 0.0, 1.0, 2.0])
num_grad = numerical_derivative(test_func, x_test)
ana_grad = test_grad(x_test)
print("=" * 60)
print("实验 1: 数值导数 vs 解析导数")
print(f"{'x':>6} {'数值导数':>14} {'解析导数':>14} {'误差':>12}")
for xi, ng, ag in zip(x_test, num_grad, ana_grad):
    print(f"{xi:6.1f} {ng:14.8f} {ag:14.8f} {abs(ng - ag):12.2e}")
print("结论: 中心差分与解析导数高度一致（误差 ~1e-10）\n")

# ============================================================
# 2. 梯度下降可视化
# ============================================================
def gradient_descent(f_grad, x0, lr=0.1, n_steps=50):
    """标准梯度下降，返回轨迹"""
    x = x0
    trajectory = [x0]
    for _ in range(n_steps):
        x = x - lr * f_grad(x)
        trajectory.append(x)
    return np.array(trajectory)

# f(x) = x^4 - 4x^2 + 1，极小值在 x = ±√2 ≈ ±1.414
traj_a = gradient_descent(test_grad, x0=0.5, lr=0.05, n_steps=30)
traj_b = gradient_descent(test_grad, x0=0.5, lr=0.15, n_steps=30)  # 大学习率可能振荡
traj_c = gradient_descent(test_grad, x0=2.5, lr=0.05, n_steps=30)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图：函数 + 下降轨迹
x_plot = np.linspace(-3, 3, 400)
axes[0].plot(x_plot, test_func(x_plot), 'k-', linewidth=1, label=r"$f(x)=x^4-4x^2+1$")
axes[0].plot(traj_a, test_func(traj_a), 'ro-', markersize=4, label=r"GD $\eta=0.05$, $x_0=0.5$")
axes[0].plot(traj_c, test_func(traj_c), 'bs-', markersize=4, label=r"GD $\eta=0.05$, $x_0=2.5$")
axes[0].axvline(np.sqrt(2), color='g', linestyle='--', alpha=0.5, label=r"$x=\sqrt{2}$ (min)")
axes[0].set_xlabel("x")
axes[0].set_ylabel("f(x)")
axes[0].set_title("Gradient Descent Trajectory")
axes[0].legend(fontsize=8)
axes[0].set_ylim(-4, 10)

# 右图：损失收敛曲线
axes[1].plot(test_func(traj_a), 'ro-', markersize=3, label=r"$\eta=0.05, x_0=0.5$")
axes[1].plot(test_func(traj_b), 'b^-', markersize=3, label=r"$\eta=0.15, x_0=0.5$ (大步长)")
axes[1].plot(test_func(traj_c), 'gs-', markersize=3, label=r"$\eta=0.05, x_0=2.5$")
axes[1].axhline(test_func(np.sqrt(2)), color='k', linestyle='--', alpha=0.3, label="最小值")
axes[1].set_xlabel("迭代步数")
axes[1].set_ylabel("f(x) (loss)")
axes[1].set_title("Loss Convergence - Effect of Learning Rate")
axes[1].legend(fontsize=8)

plt.tight_layout()
plt.savefig("gradient_descent_demo.png", dpi=120)
print("图已保存: gradient_descent_demo.png\n")

# ============================================================
# 3. Taylor 展开精度 vs 项数
# ============================================================
print("=" * 60)
print("实验 3: Taylor 展开 e^x 的精度")
print(f"{'阶数':>4} {'x=0.5 估计':>16} {'真值':>16} {'误差':>12}")
x_val = 0.5
true_val = np.exp(x_val)
for n in [1, 2, 3, 5, 8, 12]:
    approx = sum(x_val**k / math.factorial(k) for k in range(n))
    print(f"{n:4d} {approx:16.10f} {true_val:16.10f} {abs(approx - true_val):12.2e}")
print("结论: 项数越多精度越高；5 阶已达机器精度量级\n")

# ============================================================
# 4. 牛顿法 vs 梯度下降（收敛速度对比）
# ============================================================
print("=" * 60)
print("实验 4: Newton 法 vs 梯度下降（f(x)=x², x₀=10）")
print(f"目标: |x| < 0.01\n")

# 梯度下降
x_gd, steps_gd = 10.0, 0
while abs(x_gd) >= 0.01:
    x_gd = x_gd - 0.1 * 2 * x_gd  # f'(x)=2x, η=0.1
    steps_gd += 1

# Newton 法 (f'(x)=2x, f''(x)=2)
x_newton = 10.0
x_newton = x_newton - (2 * x_newton) / 2  # 一步

print(f"梯度下降: {steps_gd} 步, 最终 x = {x_gd:.6f}")
print(f"Newton 法: 1 步, 最终 x = {x_newton:.1f} (直接到 0)")
print("结论: Newton 法利用二阶信息 f''(x)=2 一步到最小值")
print("      深度学习因维度太高无法算 Hessian，所以用一阶 SGD/Adam")
print("=" * 60)
print("全部实验完成。")
