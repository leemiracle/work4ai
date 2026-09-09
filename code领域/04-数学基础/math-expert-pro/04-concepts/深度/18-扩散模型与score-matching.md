# 扩散模型：SDE 的 AI 革命

> 2022-2026 最重要的 AI 突破——DDPM 把 SDE 变成了图像生成器。

## DDPM 前向过程
q(xₜ|x₀) = N(√(ᾱₜ)x₀, (1-ᾱₜ)I)
→ 逐步加噪（数据→纯噪声 T 步后）
= 离散化的 Ornstein-Uhlenbeck 过程

## DDPM 反向过程
p(xₜ₋₁|xₜ) = N(μ_θ(xₜ,t), σ²ₜI)
→ 学习"去噪"（噪声→数据）

训练目标 = 预测噪声 ε：
L = E[‖ε - ε_θ(xₜ,t)‖²]

## 连续时间（Score-Based, Song et al. 2021）
前向 SDE: dx = f(x,t)dt + g(t)dW
反向 SDE: dx = [f - g²∇log p_t]dt + g dW̃

→ 只需学习 score function s_θ(x,t) ≈ ∇log p_t(x)
→ Score matching 训练

## 概率流 ODE
dx/dt = f - ½g²∇log p_t（确定性版本）
→ 精确似然计算 / 可控生成

## 关联
- [百科-18-ML数学](../百科-18-机器学习数学.md)
- [代码库 26-SDE](../../15-applications/代码库/26-随机微分方程_SDE.py)
- [百科-12-动力系统](../百科-12-动力系统.md)
