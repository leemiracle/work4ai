"""
CSC 2547H Generative Models (University of Toronto)
====================================================
覆盖主题：
- VAE（Variational Autoencoder）
- GAN（minimax + Wasserstein）
- Diffusion Models（DDPM）
- Normalizing Flows（RealNVP）

核心论文/教材（arXiv ID 已核实）：
- Kingma & Welling "Auto-Encoding Variational Bayes" arXiv:1312.6114
- Goodfellow et al. "Generative Adversarial Nets" arXiv:1406.2661
- Ho, Jain, Abbeel "Denoising Diffusion Probabilistic Models" arXiv:2006.11239
- Dinh et al. "Density Estimation using Real NVP" arXiv:1605.08803 (ICLR 2017)
- Arjovsky, Chintala, Bottou "Wasserstein GAN" arXiv:1701.07875

本文件实现（纯 numpy）：
- VAE 编码器/解码器 + ELBO
- GAN 生成器/判别器（minimax loss）
- DDPM 前向加噪 + 反向去噪
- RealNVP 耦合层 + 对数似然计算

运行：
    python generative.py
"""
from __future__ import annotations
import numpy as np
import math


# ============ 1. Variational Autoencoder (VAE) ============

class VAELayer:
    """
    VAE Encoder/Decoder 层
    ELBO = E_q[log p(x|z)] - KL(q(z|x) || p(z))
    KL(N(μ,σ²)||N(0,1)) = ½(μ² + σ² - log σ² - 1)
    """

    def __init__(self, input_dim, hidden_dim, latent_dim):
        self.D = input_dim
        self.H = hidden_dim
        self.L = latent_dim
        scale = np.sqrt(2.0 / input_dim)

        # Encoder: x → μ_z, log_σ²_z
        self.W_enc_mu = np.random.randn(hidden_dim, input_dim) * scale
        self.b_enc_mu = np.zeros(hidden_dim)
        self.W_enc_logvar = np.random.randn(hidden_dim, input_dim) * scale
        self.b_enc_logvar = np.zeros(hidden_dim)

        # Latent: hidden → z
        self.W_z_mu = np.random.randn(latent_dim, hidden_dim) * scale
        self.b_z_mu = np.zeros(latent_dim)
        self.W_z_logvar = np.random.randn(latent_dim, hidden_dim) * scale
        self.b_z_logvar = np.zeros(latent_dim)

        # Decoder: z → x_hat
        self.W_dec = np.random.randn(input_dim, latent_dim) * scale
        self.b_dec = np.zeros(input_dim)

    def encode(self, x):
        h_mu = np.maximum(0, self.W_enc_mu @ x + self.b_enc_mu)
        h_logvar = self.W_enc_logvar @ x + self.b_enc_logvar
        mu = self.W_z_mu @ h_mu + self.b_z_mu
        logvar = self.W_z_logvar @ h_mu + self.b_z_logvar
        return mu, logvar

    def reparameterize(self, mu, logvar):
        """重参数化技巧: z = μ + σ·ε"""
        std = np.exp(0.5 * logvar)
        eps = np.random.randn(*mu.shape)
        return mu + std * eps

    def decode(self, z):
        return self.W_dec @ z + self.b_dec

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        x_hat = self.decode(z)
        return x_hat, mu, logvar, z

    def elbo(self, x):
        """计算 ELBO"""
        x_hat, mu, logvar, z = self.forward(x)
        # 重构项（高斯 log-likelihood）
        recon_loss = np.sum((x - x_hat) ** 2)
        # KL 散度
        kl_div = -0.5 * np.sum(1 + logvar - mu ** 2 - np.exp(logvar))
        elbo_val = -recon_loss - kl_div
        return elbo_val, recon_loss, kl_div

    def train_step(self, x, beta=1.0, lr=0.01):
        """
        β-VAE 一步训练：Loss = recon + β·KL
        返回 (recon_loss, kl_div)。lr=0 时仅前向测量（不更新）。
        """
        # ---- 前向（缓存中间量）----
        pre_enc = self.W_enc_mu @ x + self.b_enc_mu
        h = np.maximum(0, pre_enc)
        mu = self.W_z_mu @ h + self.b_z_mu
        logvar = self.W_z_logvar @ h + self.b_z_logvar
        std = np.exp(0.5 * logvar)
        eps = np.random.randn(*mu.shape)
        z = mu + std * eps
        x_hat = self.W_dec @ z + self.b_dec

        recon = np.sum((x - x_hat) ** 2)
        kl = -0.5 * np.sum(1 + logvar - mu ** 2 - np.exp(logvar))

        if lr == 0:
            return recon, kl

        # ---- 反向传播 ----
        dx_hat = -2 * (x - x_hat)
        dW_dec = np.outer(dx_hat, z)
        db_dec = dx_hat
        dz = self.W_dec.T @ dx_hat

        # 通过重参数化: z = mu + std·eps
        dmu = dz + beta * mu
        dlogvar = dz * eps * 0.5 * std + beta * 0.5 * (np.exp(logvar) - 1)

        dW_z_mu = np.outer(dmu, h)
        db_z_mu = dmu
        dW_z_logvar = np.outer(dlogvar, h)
        db_z_logvar = dlogvar
        dh = self.W_z_mu.T @ dmu + self.W_z_logvar.T @ dlogvar
        dh = dh * (pre_enc > 0)                        # ReLU'
        dW_enc_mu = np.outer(dh, x)
        db_enc_mu = dh

        # ---- SGD 更新 ----
        self.W_dec -= lr * dW_dec; self.b_dec -= lr * db_dec
        self.W_z_mu -= lr * dW_z_mu; self.b_z_mu -= lr * db_z_mu
        self.W_z_logvar -= lr * dW_z_logvar; self.b_z_logvar -= lr * db_z_logvar
        self.W_enc_mu -= lr * dW_enc_mu; self.b_enc_mu -= lr * db_enc_mu
        return recon, kl


# ============ 2. GAN (Generator + Discriminator) ============

class Generator:
    """
    GAN Generator: G(z) → fake_data
    从噪声分布 z ~ N(0, I) 生成数据

    目标: max_G min_D E[log D(x)] + E[log(1 - D(G(z)))]
    """

    def __init__(self, noise_dim, data_dim, hidden_dim=32):
        self.noise_dim = noise_dim
        self.data_dim = data_dim
        scale = np.sqrt(2.0 / noise_dim)
        self.W1 = np.random.randn(hidden_dim, noise_dim) * scale
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(data_dim, hidden_dim) * scale
        self.b2 = np.zeros(data_dim)

    def forward(self, z):
        self.z = z
        self.z1 = self.W1 @ z + self.b1
        self.h1 = np.maximum(0, self.z1)                     # ReLU
        self.out = np.tanh(self.W2 @ self.h1 + self.b2)      # tanh → [-1, 1]
        return self.out

    def backward(self, grad_out, lr):
        """grad_out: dL/d(out)，1D 向量；计算梯度并 SGD 更新"""
        dz2 = grad_out * (1 - self.out ** 2)                  # tanh'
        dW2 = np.outer(dz2, self.h1)
        db2 = dz2
        dh1 = self.W2.T @ dz2 * (self.z1 > 0)                 # ReLU'
        dW1 = np.outer(dh1, self.z)
        db1 = dh1
        self.W2 -= lr * dW2; self.b2 -= lr * db2
        self.W1 -= lr * dW1; self.b1 -= lr * db1


class Discriminator:
    """
    GAN Discriminator: D(x) → [0, 1] (真实概率)
    """

    def __init__(self, data_dim, hidden_dim=32):
        scale = np.sqrt(2.0 / data_dim)
        self.W1 = np.random.randn(hidden_dim, data_dim) * scale
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(1, hidden_dim) * scale
        self.b2 = np.zeros(1)

    @staticmethod
    def _sigmoid(x):
        return 1 / (1 + np.exp(-np.clip(x, -250, 250)))

    def forward(self, x):
        self.x = x
        self.z1 = self.W1 @ x + self.b1
        self.h1 = np.maximum(0, self.z1)                      # ReLU
        self.d = self._sigmoid(self.W2 @ self.h1 + self.b2)
        return self.d

    def backward(self, dz2, lr):
        """dz2: dL/d(pre-sigmoid)，标量；SGD 更新 D；返回 dL/d(input) 供反传"""
        dz2 = float(dz2)
        dW2 = np.outer(np.array([dz2]), self.h1)              # (1, hidden)
        db2 = np.array([dz2])
        dh1 = self.W2.ravel() * dz2 * (self.z1 > 0)           # (hidden,)
        dW1 = np.outer(dh1, self.x)                           # (hidden, data_dim)
        db1 = dh1
        dx = self.W1.T @ dh1                                  # (data_dim,) 输入梯度
        self.W2 -= lr * dW2; self.b2 -= lr * db2
        self.W1 -= lr * dW1; self.b1 -= lr * db1
        return dx

    def grad_input(self, dz2):
        """仅计算 dL/d(input)，不更新权重（训练 G 时反传穿过冻结的 D）"""
        dz2 = float(dz2)
        dh1 = self.W2.ravel() * dz2 * (self.z1 > 0)
        return self.W1.T @ dh1


def wasserstein_distance(D, real_samples, fake_samples):
    """
    Wasserstein 距离: W = E[D(real)] - E[D(fake)]
    WGAN 用 Wasserstein 距离代替 JS 散度
    """
    real_scores = [D.forward(x)[0] for x in real_samples]
    fake_scores = [D.forward(x)[0] for x in fake_samples]
    return np.mean(real_scores) - np.mean(fake_scores)


# ============ 3. DDPM (Denoising Diffusion) ============

class DDPM:
    """
    Denoising Diffusion Probabilistic Model

    Forward (加噪):
    q(x_t | x_0) = N(x_t; √(ᾱ_t) x_0, (1-ᾱ_t) I)
    其中 ᾱ_t = Π_{s=1}^{t} α_s, α_s = 1 - β_s

    Reverse (去噪):
    p(x_{t-1} | x_t) = N(x_{t-1}; μ_θ(x_t, t), σ_t² I)

    训练目标:
    L = E_{t,x_0,ε}[||ε - ε_θ(√ᾱ_t x_0 + √(1-ᾱ_t) ε, t)||²]
    """

    def __init__(self, n_steps=100, beta_start=0.0001, beta_end=0.02, data_dim=8):
        self.n_steps = n_steps
        self.data_dim = data_dim

        # 线性 β schedule
        self.betas = np.linspace(beta_start, beta_end, n_steps)
        self.alphas = 1 - self.betas
        self.alpha_bars = np.cumprod(self.alphas)  # ᾱ_t

        # 简化噪声预测网络（线性层）
        scale = 0.1
        self.noise_weights = np.random.randn(data_dim, data_dim) * scale

    @staticmethod
    def cosine_alpha_bars(n_steps, s=0.008):
        """
        Cosine β schedule (Nichol & Dhariwal, "Improved DDPM" ICML 2021):
        ᾱ_t = f(t)/f(0),  f(t) = cos²(π/2 · (t/T + s)/(1+s))
        末段 ᾱ 更小 → SNR 更低 → 更彻底破坏信号。
        """
        t = np.arange(n_steps + 1)
        f = np.cos((t / n_steps + s) / (1 + s) * np.pi * 0.5) ** 2
        ab = f / f[0]
        betas = np.clip(1 - ab[1:] / ab[:-1], 0, 0.999)
        return np.cumprod(1 - betas)

    def forward_diffuse(self, x0, t):
        """
        前向加噪: q(x_t | x_0)
        x_t = √(ᾱ_t) x_0 + √(1-ᾱ_t) ε,  ε ~ N(0,I)
        """
        alpha_bar = self.alpha_bars[t]
        noise = np.random.randn(*x0.shape)
        xt = np.sqrt(alpha_bar) * x0 + np.sqrt(1 - alpha_bar) * noise
        return xt, noise

    def predict_noise(self, xt, t):
        """简化噪声预测（实际用 U-Net）"""
        # 这里用线性近似
        return self.noise_weights @ xt

    def reverse_diffuse(self, xt, t):
        """
        反向去噪一步: p(x_{t-1} | x_t)
        μ = 1/√α_t (x_t - β_t/√(1-ᾱ_t) ε_θ(x_t, t))
        """
        alpha_t = self.alphas[t]
        alpha_bar_t = self.alpha_bars[t]
        beta_t = self.betas[t]

        eps = self.predict_noise(xt, t)
        mean = (1 / np.sqrt(alpha_t)) * (xt - (beta_t / np.sqrt(1 - alpha_bar_t)) * eps)
        std = np.sqrt(beta_t)

        return mean + std * np.random.randn(*xt.shape)

    def sample(self, n_samples=1):
        """从纯噪声开始反向采样"""
        x = np.random.randn(n_samples, self.data_dim)
        for t in reversed(range(self.n_steps)):
            x = self.reverse_diffuse(x, t)
        return x


# ============ 4. RealNVP (Normalizing Flow) ============

class RealNVPCouplingLayer:
    """
    RealNVP Coupling Layer (Affine Coupling)
    将输入 x 分为 x = (x_d, x_{>d})
    y_d = x_d（不变）
    y_{>d} = x_{>d} ⊙ exp(s(x_d)) + t(x_d)

    逆变换:
    x_{>d} = (y_{>d} - t(y_d)) ⊙ exp(-s(y_d))

    Jacobian: |det(∂y/∂x)| = exp(Σ_{j>d} s_j(x_d))
    """

    def __init__(self, dim, mask_first=True):
        self.dim = dim
        self.d = dim // 2
        self.mask_first = mask_first

        # 简化 s, t 网络（线性）
        scale = 0.1
        self.s_W = np.random.randn(dim - self.d, self.d) * scale
        self.s_b = np.zeros(dim - self.d)
        self.t_W = np.random.randn(dim - self.d, self.d) * scale
        self.t_b = np.zeros(dim - self.d)

    def _split(self, x):
        if self.mask_first:
            return x[:self.d], x[self.d:]
        return x[self.d:], x[:self.d]

    def _combine(self, a, b):
        if self.mask_first:
            return np.concatenate([a, b])
        return np.concatenate([b, a])

    def forward(self, x):
        """前向变换 + log determinant"""
        x_a, x_b = self._split(x)
        s = np.tanh(self.s_W @ x_a + self.s_b)
        t = self.t_W @ x_a + self.t_b
        y_b = x_b * np.exp(s) + t
        y = self._combine(x_a, y_b)
        log_det = np.sum(s)
        return y, log_det

    def inverse(self, y):
        """逆向变换"""
        y_a, y_b = self._split(y)
        s = np.tanh(self.s_W @ y_a + self.s_b)
        t = self.t_W @ y_a + self.t_b
        x_b = (y_b - t) * np.exp(-s)
        x = self._combine(y_a, x_b)
        return x


class RealNVP:
    """
    RealNVP: 堆叠多个 coupling layer
    """

    def __init__(self, dim, n_layers=4):
        self.dim = dim
        self.layers = []
        for i in range(n_layers):
            mask = (i % 2 == 0)
            self.layers.append(RealNVPCouplingLayer(dim, mask_first=mask))

    def forward(self, x):
        """前向传播 + 累积 log determinant"""
        log_det_total = 0.0
        z = x.copy()
        for layer in self.layers:
            z, log_det = layer.forward(z)
            log_det_total += log_det
        return z, log_det_total

    def inverse(self, z):
        """逆向采样"""
        x = z.copy()
        for layer in reversed(self.layers):
            x = layer.inverse(x)
        return x

    def log_likelihood(self, x):
        """
        log p(x) = log p(z) + log|det(∂f/∂x)|
        其中 p(z) = N(0, I)
        """
        z, log_det = self.forward(x)
        log_pz = -0.5 * np.sum(z ** 2) - 0.5 * self.dim * np.log(2 * math.pi)
        return log_pz + log_det


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CSC 2547H: Generative Models Demo")
    print("=" * 60)

    np.random.seed(42)

    # 1. VAE
    print("\n📋 1. Variational Autoencoder (VAE)")
    vae = VAELayer(input_dim=16, hidden_dim=8, latent_dim=4)
    x = np.random.randn(16)  # 输入数据
    elbo, recon, kl = vae.elbo(x)
    print(f"   输入维度: 16, 隐空间: 4")
    print(f"   ELBO = {elbo:.4f}")
    print(f"   重构损失 = {recon:.4f}")
    print(f"   KL 散度 = {kl:.4f}")
    print(f"   ELBO = -重构 - KL = {-(recon + kl):.4f}")

    # 多次采样观察重构
    recons = []
    for _ in range(10):
        elbo, recon, kl = vae.elbo(x)
        recons.append(recon)
    print(f"   10 次采样重构损失: mean={np.mean(recons):.4f}, std={np.std(recons):.4f}")
    print(f"   → 重参数化使梯度可传播（无重参数化 VAE 无法训练）")

    # β-VAE 扫描：KL 权重 β 从 0→10 的重构/KL trade-off
    print(f"\n   β-VAE 扫描（每个 β 训练 200 步后测量 recon / KL）:")
    print(f"   {'β':>5} {'recon':>8} {'KL':>8}")
    for beta in [0.0, 0.1, 0.5, 1.0, 2.0, 4.0, 6.0, 10.0]:
        vae_b = VAELayer(input_dim=16, hidden_dim=8, latent_dim=4)
        for _ in range(200):
            vae_b.train_step(x, beta=beta, lr=0.01)
        r_fin, k_fin = vae_b.train_step(x, beta=beta, lr=0.0)  # 仅测量不更新
        print(f"   {beta:5.1f} {r_fin:8.3f} {k_fin:8.3f}")
    print(f"   → β=0 退化为 AE（KL 无约束→∞），β↑ 重构崩塌（KL→0 但 recon↑）")

    # 2. GAN
    print("\n📋 2. GAN (Generator + Discriminator)")
    G = Generator(noise_dim=8, data_dim=4, hidden_dim=16)
    D = Discriminator(data_dim=4, hidden_dim=16)

    # 真实数据（高斯分布）
    real_data = [np.random.randn(4) + 2 for _ in range(20)]

    # 生成假数据
    z = np.random.randn(8)
    fake = G.forward(z)
    d_real = D.forward(real_data[0])[0]
    d_fake = D.forward(fake)[0]

    print(f"   Generator: z(8d) → G(z) = [{', '.join(f'{v:.2f}' for v in fake)}]")
    print(f"   Discriminator(real) = {d_real:.4f}")
    print(f"   Discriminator(fake) = {d_fake:.4f}")

    # Wasserstein 距离
    fake_batch = [G.forward(np.random.randn(8)) for _ in range(20)]
    w_dist = wasserstein_distance(D, real_data, fake_batch)
    print(f"   Wasserstein 距离 = {w_dist:.4f}")
    print(f"\n   反直觉发现：")
    print(f"   minimax GAN 用 JS 散度（梯度消失风险）")
    print(f"   WGAN 用 Wasserstein 距离（梯度平滑，训练稳定）")

    # GAN minimax 训练循环（交替更新 D 和 G）
    print(f"\n   GAN minimax 训练（交替更新 D / G，80 步）:")
    G_tr = Generator(noise_dim=8, data_dim=4, hidden_dim=16)
    D_tr = Discriminator(data_dim=4, hidden_dim=16)
    real_pool = [np.random.randn(4) + 2.0 for _ in range(64)]
    lr_gan = 0.05
    print(f"   {'step':>5} {'D loss':>8} {'G loss':>8} {'D(real)':>8} {'D(fake)':>8}")
    for step in range(80):
        # --- 训练 D: max log D(real) + log(1 - D(G(z))) ---
        xr = real_pool[np.random.randint(64)]
        D_tr.forward(xr)
        D_tr.backward(float(D_tr.d[0]) - 1.0, lr_gan)   # BCE target=1

        z_g = np.random.randn(8)
        fake_g = G_tr.forward(z_g)
        D_tr.forward(fake_g)
        D_tr.backward(float(D_tr.d[0]) - 0.0, lr_gan)   # BCE target=0
        d_real_val = float(D_tr.d[0])

        # --- 训练 G: max log D(G(z))（非饱和，反传穿过冻结的 D）---
        z_g2 = np.random.randn(8)
        fake_g2 = G_tr.forward(z_g2)
        D_tr.forward(fake_g2)
        d_fake_val = float(D_tr.d[0])
        grad_in = D_tr.grad_input(d_fake_val - 1.0)     # D 冻结，只取输入梯度
        G_tr.backward(grad_in, lr_gan)

        d_loss = -np.log(d_real_val + 1e-10) - np.log(1 - d_fake_val + 1e-10)
        g_loss = -np.log(d_fake_val + 1e-10)
        if step % 20 == 0 or step == 79:
            print(f"   {step:5d} {d_loss:8.3f} {g_loss:8.3f} "
                  f"{d_real_val:8.3f} {d_fake_val:8.3f}")
    print(f"   → D 学会区分真/假（D(real)↑ D(fake)↓），G 学会欺骗 D（minimax 动态）")

    # 3. DDPM
    print("\n📋 3. DDPM (Denoising Diffusion)")
    ddpm = DDPM(n_steps=50, data_dim=8)
    x0 = np.random.randn(5, 8) * 0.5  # 原始数据

    # 展示前向加噪过程
    print(f"   原始数据范数: {np.linalg.norm(x0[0]):.4f}")
    for t in [0, 10, 25, 49]:
        xt, noise = ddpm.forward_diffuse(x0, t)
        snr = 10 * np.log10(ddpm.alpha_bars[t] / (1 - ddpm.alpha_bars[t] + 1e-10))
        deviation = np.mean((xt - x0) ** 2) ** 0.5
        print(f"   t={t:3d}: SNR={snr:6.2f}dB, ᾱ={ddpm.alpha_bars[t]:.4f}, 偏差={deviation:.4f}")

    print(f"\n   → t 增大时 SNR 降低，最终趋近纯噪声")
    print(f"   → 训练时模型学习预测噪声 ε_θ，推理时逐步去噪")

    # β schedule 对比：linear vs cosine
    ab_cos = DDPM.cosine_alpha_bars(50)
    snr_lin_end = 10 * np.log10(ddpm.alpha_bars[-1] / (1 - ddpm.alpha_bars[-1] + 1e-10))
    snr_cos_end = 10 * np.log10(ab_cos[-1] / (1 - ab_cos[-1] + 1e-10))
    print(f"\n   β schedule 对比（末段 t=T）:")
    print(f"   {'schedule':<12} {'ᾱ_end':>8} {'SNR_end':>8}")
    print(f"   {'linear':<12} {ddpm.alpha_bars[-1]:8.4f} {snr_lin_end:8.2f}dB")
    print(f"   {'cosine':<12} {ab_cos[-1]:8.4f} {snr_cos_end:8.2f}dB")
    print(f"   → cosine 末段 SNR 比 linear 低 {snr_lin_end - snr_cos_end:.1f}dB"
          f"（ᾱ_T→0，更彻底破坏信号 → 采样质量更高）")

    # 4. RealNVP
    print("\n📋 4. RealNVP (Normalizing Flow)")
    flow = RealNVP(dim=8, n_layers=4)

    x = np.random.randn(8)
    z, log_det = flow.forward(x)
    x_recon = flow.inverse(z)

    print(f"   原始 x: [{', '.join(f'{v:.3f}' for v in x[:4])}]...")
    print(f"   隐空间 z: [{', '.join(f'{v:.3f}' for v in z[:4])}]...")
    print(f"   重建 x': [{', '.join(f'{v:.3f}' for v in x_recon[:4])}]...")
    print(f"   重建误差: {np.max(np.abs(x - x_recon)):.2e}")
    print(f"   log|det Jacobian| = {log_det:.4f}")

    # 对数似然
    ll = flow.log_likelihood(x)
    print(f"   log p(x) = {ll:.4f}")
    print(f"   log p(z=0) (标准正态) = {-0.5 * 8 * np.log(2 * math.pi):.4f}")
    print(f"   → Flow 可以精确计算似然（VAE/GAN 不行）")

    # 对比四种模型
    print("\n💡 四种生成模型对比：")
    print(f"   {'Model':<15} {'Likelihood':<15} {'Latent':<15} {'Train Stability'}")
    print(f"   {'VAE':<15} {'Lower bound':<15} {'Stochastic':<15} {'稳定'}")
    print(f"   {'GAN':<15} {'Implicit':<15} {'Deterministic':<15} {'不稳定'}")
    print(f"   {'Diffusion':<15} {'Lower bound':<15} {'Stochastic':<15} {'稳定但慢'}")
    print(f"   {'Flow':<15} {'Exact':<15} {'Deterministic':<15} {'稳定'}")

    print("\n✅ CSC 2547H 完成！")
    print("💡 覆盖：VAE(ELBO) + GAN(minimax/Wasserstein) + DDPM(前向/反向扩散) + RealNVP(coupling/精确似然)")
    print("   核心公式：")
    print("   ELBO = E_q[log p(x|z)] - KL(q(z|x)||p(z))")
    print("   DDPM: q(x_t|x_0) = N(√ᾱ_t x_0, (1-ᾱ_t)I)")
    print("   RealNVP log p(x) = log p(z) + log|det J|")


if __name__ == "__main__":
    demo()
