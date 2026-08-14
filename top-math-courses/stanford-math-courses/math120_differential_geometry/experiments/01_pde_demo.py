#!/usr/bin/env python3
"""偏微分方程实验：扩散方程 + heat kernel（diffusion model 的根基）"""
import numpy as np
# ML 关联：扩散方程→DDPM；heat kernel=高斯卷积；PINN=PDE+神经网络

# 1. 一维扩散方程 ∂u/∂t = D ∂²u/∂x²（有限差分）
D, dx, dt = 0.1, 0.05, 0.001
x = np.linspace(-2, 2, 81); u = np.exp(-x**2 / 0.1)  # 初始 δ-like
n_steps = 500
for step in range(n_steps):
    u_new = u.copy()
    u_new[1:-1] = u[1:-1] + D * dt / dx**2 * (u[2:] - 2*u[1:-1] + u[:-2])
    u = u_new
# 理论解: u(x,T) = 高斯卷积
T_final = n_steps * dt
theory = 1/np.sqrt(4*np.pi*D*T_final + 0.1) * np.exp(-x**2/(4*D*T_final + 0.1))
theory = theory / theory.max() * u.max()  # 归一化对比
err = np.abs(u - theory).mean()
print(f"扩散方程数值解 vs 理论高斯: 平均误差={err:.4f}")
print("=> heat kernel = 高斯; 扩散方程平滑化 = 信息损失（熵增）")

# 2. 扩散模型: 前向加噪 = 离散化扩散方程
print("\n扩散模型 (DDPM):")
x0 = np.array([1.0, -1.0, 2.0])  # 3 个"图像"
for t, alpha_bar in [(0.1, 0.99), (0.5, 0.5), (0.9, 0.01)]:
    noise = np.random.randn(3)
    xt = np.sqrt(alpha_bar) * x0 + np.sqrt(1-alpha_bar) * noise
    print(f"  t={t}: α̅={alpha_bar}, x_t={np.round(xt, 3)} ({'≈原图' if alpha_bar>0.9 else '≈纯噪声' if alpha_bar<0.1 else '混合'})")
