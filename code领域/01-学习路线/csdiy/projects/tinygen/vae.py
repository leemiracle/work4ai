#!/usr/bin/env python3
"""
tinygen/vae.py — 变分自编码器

参照：VAE (Kingma & Welling 2013) / Auto-Encoding Variational Bayes
csdiy 对应：AI核心 + tinytorch + tinygen

数学核心（参照 Kingma 2013 §2）：
  编码器 q_φ(z|x)：x → (μ, σ) → z = μ + σ·ε  (重参数化技巧)
  解码器 p_θ(x|z)：z → x̂
  损失 = 重建损失 + KL(q(z|x) || N(0,I))
       = ||x - x̂||² + 0.5 × Σ(μ² + σ² - ln(σ²) - 1)

重参数化技巧（参照 Kingma 2013 §2.3）：
  z = μ + σ ⊙ ε,  ε ~ N(0, I)
  → 让随机采样可微分（梯度能通过 z 传回 μ 和 σ）
"""
import math, random

class Encoder:
    """编码器 x → (μ, σ)（参照 VAE 的 inference network）"""
    def __init__(self, input_dim, latent_dim):
        self.latent_dim = latent_dim; self.input_dim = input_dim
        self.W_mu = [[random.gauss(0, 0.1) for _ in range(input_dim)] for _ in range(latent_dim)]
        self.W_logvar = [[random.gauss(0, 0.1) for _ in range(input_dim)] for _ in range(latent_dim)]
    def forward(self, x):
        mu = [sum(self.W_mu[i][j] * x[j] for j in range(self.input_dim)) for i in range(self.latent_dim)]
        logvar = [sum(self.W_logvar[i][j] * x[j] for j in range(self.input_dim)) for i in range(self.latent_dim)]
        return mu, logvar

class Decoder:
    """解码器 z → x̂（参照 VAE 的 generative network）"""
    def __init__(self, latent_dim, output_dim):
        self.W = [[random.gauss(0, 0.1) for _ in range(latent_dim)] for _ in range(output_dim)]
        self.b = [0.0] * output_dim
    def forward(self, z):
        return [sum(self.W[i][j] * z[j] for j in range(len(z))) + self.b[i]
                for i in range(len(self.W))]

class VAE:
    """变分自编码器（参照 Kingma 2013）

    重参数化：z = μ + σ · ε
    损失 = E[||x-x̂||²] + KL(q(z|x)||N(0,I))"""
    def __init__(self, input_dim, latent_dim, lr=0.01):
        self.encoder = Encoder(input_dim, latent_dim)
        self.decoder = Decoder(latent_dim, input_dim)
        self.latent_dim = latent_dim; self.input_dim = input_dim; self.lr = lr
        self.history = {"recon_loss": [], "kl_loss": [], "total_loss": []}

    def reparameterize(self, mu, logvar):
        """重参数化技巧（参照 Kingma 2013 §2.3）
        z = μ + σ · ε,  ε ~ N(0,I)
        关键：让随机采样对 μ 和 σ 可微"""
        sigma = [math.exp(0.5 * lv) for lv in logvar]
        eps = [random.gauss(0, 1) for _ in range(len(mu))]
        return [m + s * e for m, s, e in zip(mu, sigma, eps)], sigma

    def forward(self, x):
        """前向：编码 → 采样 → 解码"""
        mu, logvar = self.encoder.forward(x)
        z, sigma = self.reparameterize(mu, logvar)
        x_hat = self.decoder.forward(z)
        return x_hat, mu, logvar, sigma

    def compute_loss(self, x, x_hat, mu, logvar):
        """ELBO 损失 = 重建损失 + KL 散度（参照 Kingma 2013 公式 10）"""
        # 重建损失（MSE）
        recon = sum((xi - xhi) ** 2 for xi, xhi in zip(x, x_hat)) / len(x)
        # KL(q(z|x) || N(0,I)) = 0.5 × Σ(μ² + σ² - ln(σ²) - 1)
        kl = 0.5 * sum(m ** 2 + math.exp(lv) - lv - 1 for m, lv in zip(mu, logvar))
        return recon, kl, recon + kl

    def generate(self, n_samples):
        """从先验 N(0,I) 采样 → 解码生成（参照 VAE 生成流程）"""
        samples = []
        for _ in range(n_samples):
            z = [random.gauss(0, 1) for _ in range(self.latent_dim)]
            samples.append(self.decoder.forward(z))
        return samples

    def reconstruct(self, x):
        """重建测试（编码→解码）"""
        x_hat, _, _, _ = self.forward(x)
        return x_hat

    def interpolate(self, x1, x2, alpha=0.5):
        """潜空间插值（参照 VAE 的核心能力之一）
        encode(x1) → z1, encode(x2) → z2
        z_interp = α·z1 + (1-α)·z2 → decode → 插值结果"""
        mu1, _ = self.encoder.forward(x1)
        mu2, _ = self.encoder.forward(x2)
        z_interp = [a * alpha + b * (1 - alpha) for a, b in zip(mu1, mu2)]
        return self.decoder.forward(z_interp)


def demo():
    """VAE 演示"""
    print("\n┌─────────────────────────────────┐")
    print("│  tinygen: VAE 变分自编码器      │")
    print("└─────────────────────────────────┘\n")
    random.seed(42)
    vae = VAE(input_dim=4, latent_dim=2, lr=0.01)
    # 模拟数据：4维向量
    data = [[1, 0, 0.5, -0.3], [0.8, 0.1, 0.6, -0.2], [1.1, -0.1, 0.4, -0.4],
            [0.9, 0.2, 0.55, -0.25], [1.0, 0.0, 0.5, -0.3]]
    print(f"  输入维度: {vae.input_dim}, 潜在维度: {vae.latent_dim}")
    print(f"  训练数据: {len(data)} 个 4D 样本\n")
    # "训练"（简化版：不做梯度更新，只展示概念）
    for epoch in range(5):
        for x in data:
            x_hat, mu, logvar, _ = vae.forward(x)
            recon, kl, total = vae.compute_loss(x, x_hat, mu, logvar)
            if epoch == 0 and x == data[0]:
                print(f"  样本损失: recon={recon:.3f}, kl={kl:.3f}, total={total:.3f}")
                print(f"  μ={mu}, logvar={logvar}")
    # 重建
    test = data[0]
    recon = vae.reconstruct(test)
    print(f"\n  重建测试:")
    print(f"    原始: {['%+.3f'%v for v in test]}")
    print(f"    重建: {['%+.3f'%v for v in recon]}")
    # 生成
    generated = vae.generate(3)
    print(f"\n  生成样本（从 N(0,I) 采样→解码）:")
    for g in generated: print(f"    {['%+.3f'%v for v in g]}")
    # 插值
    interp = vae.interpolate(data[0], data[1], 0.5)
    print(f"\n  潜空间插值(α=0.5): {['%+.3f'%v for v in interp]}")
    print(f"\n  VAE 核心: 编码→分布→重参数化→解码")
    print(f"  重参数化技巧让随机采样可微分（z=μ+σ·ε）")
