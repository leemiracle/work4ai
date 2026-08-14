#!/usr/bin/env python3
"""随机微分方程实验：Euler-Maruyama + Itô 引理 + 扩散模型前向"""
import numpy as np
# ML 关联：Itô→Black-Scholes；反向 SDE→Diffusion model；Langevin→MCMC

np.random.seed(42)
# 1. Geometric Brownian Motion dX = μX dt + σX dW（Black-Scholes 基础）
T, N, mu, sigma, X0 = 1.0, 1000, 0.1, 0.3, 100.0
dt = T / N; n_paths = 1000
dW = np.random.randn(n_paths, N) * np.sqrt(dt)
X = np.zeros((n_paths, N+1)); X[:, 0] = X0
for i in range(N):
    X[:, i+1] = X[:, i] + mu*X[:, i]*dt + sigma*X[:, i]*dW[:, i]
print(f"GBM 终值: 实测均值={X[:,-1].mean():.2f}, 理论 E[X_T]={X0*np.exp(mu*T):.2f}")
print(f"  实测方差={X[:,-1].var():.2f}, 理论 Var≈={(X0**2)*np.exp(2*mu*T)*(np.exp(sigma**2*T)-1):.2f}")

# 2. Itô 引理: d(ln X) = (μ - σ²/2)dt + σdW
log_X_final = np.log(X[:, -1])
theoretical = np.log(X0) + (mu - sigma**2/2)*T + sigma*np.sqrt(T)*np.random.randn(n_paths)
print(f"\nItô 引理验证: d(lnX) 均值差={abs(log_X_final.mean()-theoretical.mean()):.4f}")
print("=> Itô 项 (1/2)σ² 是 Black-Scholes 公式的关键")

# 3. Diffusion 前向: x_t = √α̅_t x_0 + √(1-α̅_t) ε（DDPM）
print("\nDiffusion 前向 (DDPM, arXiv:2006.11239):")
x0 = np.random.randn(1000)
alpha_bar = 0.5  # 某个时间步
xt = np.sqrt(alpha_bar) * x0 + np.sqrt(1 - alpha_bar) * np.random.randn(1000)
print(f"  α̅={alpha_bar}: x_t 均值={xt.mean():.3f}(应≈0), 方差={xt.var():.3f}(应≈1)")
