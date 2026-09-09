#!/usr/bin/env python3
"""
tinygen/diffusion.py — DDPM 扩散模型

参照：DDPM (Ho et al. 2020) / Stable Diffusion / score-SDE
csdiy 对应：AI前沿 + tinydiffusion(原单文件升级) + tinytorch

数学核心（参照 DDPM 论文 §3-4）：
  前向（加噪）：q(x_t|x_0) = N(√ᾱ_t·x_0, (1-ᾱ_t)·I)
  反向（去噪）：p_θ(x_{t-1}|x_t) = N(μ_θ(x_t,t), σ_t²)
  训练目标：L = E[||ε - ε_θ(√ᾱ_t·x_0 + √(1-ᾱ_t)·ε, t)||²]
  采样：x_T~N(0,I) → 逐步去噪 → x_0
"""
import math, random

class DiffusionProcess:
    """DDPM 扩散过程（参照 Ho et al. 2020）

    超参数：
      betas: β_1...β_T 噪声调度（线性 or 余弦）
      alphas: α_t = 1 - β_t
      alpha_bars: ᾱ_t = ∏α_t（累积乘积）

    核心公式：
      x_t = √ᾱ_t · x_0 + √(1-ᾱ_t) · ε   （前向，ε~N(0,I)）
      μ_θ = 1/√α_t · (x_t - β_t/√(1-ᾱ_t) · ε_θ(x_t,t))   （反向均值）"""

    def __init__(self, T=1000, beta_start=1e-4, beta_end=0.02, schedule="linear"):
        self.T = T
        if schedule == "linear":
            self.betas = [beta_start + (beta_end - beta_start) * t / T for t in range(T)]
        else:  # cosine（参照 Improved DDPM）
            self.betas = [min(0.999, 1 - math.cos((t/T + 0.008)/1.008 * math.pi/2)**2 / 0.99**2)
                          for t in range(T)]
        self.alphas = [1 - b for b in self.betas]
        self.alpha_bars = [1.0] * T
        for t in range(1, T):
            self.alpha_bars[t] = self.alpha_bars[t-1] * self.alphas[t]

    def q_sample(self, x0, t, noise=None):
        """前向扩散 q(x_t|x_0)（参照 DDPM 公式 4）
        给定原始数据 x_0，采样时间步 t 的加噪版本"""
        if noise is None:
            noise = [random.gauss(0, 1) for _ in x0]
        abar = self.alpha_bars[t]
        x_t = [math.sqrt(abar) * x + math.sqrt(1 - abar) * e for x, e in zip(x0, noise)]
        return x_t, noise

    def p_sample_step(self, x_t, t, denoise_fn):
        """反向去噪一步 p_θ(x_{t-1}|x_t)（参照 DDPM 公式 7+11）
        denoise_fn: ε_θ(x_t, t) → 预测的噪声"""
        beta_t = self.betas[t]; alpha_t = self.alphas[t]; abar_t = self.alpha_bars[t]
        pred_noise = denoise_fn(x_t, t)
        # μ_θ = (1/√α_t) × (x_t - β_t/√(1-ᾱ_t) × ε_θ)
        denom = max(1e-8, math.sqrt(1 - abar_t))
        mean = [(1 / math.sqrt(alpha_t + 1e-8)) * (x - (beta_t / denom) * e)
                for x, e in zip(x_t, pred_noise)]
        if t > 0:
            sigma = math.sqrt(beta_t)
            z = [random.gauss(0, 1) * sigma for _ in x_t]
            return [m + zi for m, zi in zip(mean, z)]
        return mean

    def sample(self, denoise_fn, dim=2, save_trajectory=False):
        """完整采样（参照 DDPM Algorithm 2）
        x_T ~ N(0,I) → 逐步去噪 → x_0"""
        x = [random.gauss(0, 1) for _ in range(dim)]
        traj = [x[:]] if save_trajectory else None
        for t in reversed(range(self.T)):
            x = self.p_sample_step(x, t, denoise_fn)
            if save_trajectory and t % max(1, self.T // 10) == 0:
                traj.append(x[:])
        return x, traj

    def compute_loss(self, x0, t, denoise_fn):
        """训练损失（参照 DDPM 公式 14 简化版）
        L_simple = E[||ε - ε_θ(x_t, t)||²]"""
        x_t, noise = self.q_sample(x0, t)
        pred = denoise_fn(x_t, t)
        return sum((e - p) ** 2 for e, p in zip(noise, pred)) / len(noise)


def demo():
    """扩散模型演示"""
    print("┌─────────────────────────────────┐")
    print("│  tinygen: DDPM 扩散模型         │")
    print("└─────────────────────────────────┘\n")

    diff = DiffusionProcess(T=100)

    # 前向扩散：干净数据 → 噪声
    x0 = [0.5, -0.3, 0.8, -0.1, 0.6]
    print("  前向扩散（加噪过程）:")
    for t in [0, 25, 50, 75, 99]:
        x_t, _ = diff.q_sample(x0, t)
        print(f"    t={t:3d}: {['%+.3f'%v for v in x_t]}")

    # 简化去噪函数（真实场景用 U-Net）
    def simple_denoise(x_t, t):
        progress = t / diff.T  # 0=干净, 1=全噪声
        return [v * (0.1 + 0.4 * progress) for v in x_t]

    # 反向扩散：噪声 → 数据
    print(f"\n  反向扩散（去噪采样）:")
    result, traj = diff.sample(simple_denoise, dim=5, save_trajectory=True)
    for i, x in enumerate(traj[::max(1, len(traj)//5)]):
        print(f"    step {i*10}: {['%+.3f'%v for v in x]}")
    print(f"    最终: {['%+.3f'%v for v in result]}")

    # 训练损失示例
    loss = diff.compute_loss(x0, t=50, denoise_fn=simple_denoise)
    print(f"\n  训练损失 (t=50): {loss:.4f}")
    print(f"\n  Stable Diffusion = U-Net ε_θ + 文本条件(Cross-Attention) + VAE")
    print(f"  DDPM 核心: 前向加噪确定，反向去噪用网络学习")

if __name__ == "__main__":
    demo()
