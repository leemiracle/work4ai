#!/usr/bin/env python3
"""
tinygen/gan.py — GAN 生成对抗网络

参照：GAN (Goodfellow 2014) / DCGAN / StyleGAN
csdiy 对应：AI核心 + tinytorch + tinygen

数学核心（参照 Goodfellow 2014）：
  目标函数：min_G max_D E[log D(x)] + E[log(1 - D(G(z)))]
  Generator G(z)：噪声 z → 假数据
  Discriminator D(x)：数据 → 真/假概率
  纳什均衡：D=0.5（分不清真假）
"""
import math, random

class Generator:
    """生成器（参照 DCGAN Generator）
    z(latent) → 生成假数据
    本实现用简单线性变换模拟（真实场景用反卷积网络）"""
    def __init__(self, latent_dim, data_dim):
        self.latent_dim = latent_dim; self.data_dim = data_dim
        self.W = [[random.gauss(0, 0.1) for _ in range(latent_dim)] for _ in range(data_dim)]
        self.b = [0.0] * data_dim
    def forward(self, z):
        return [sum(self.W[i][j] * z[j] for j in range(self.latent_dim)) + self.b[i]
                for i in range(self.data_dim)]
    def params(self): return self.W, self.b

class Discriminator:
    """判别器（参照 DCGAN Discriminator）
    x(data) → 真/假概率（sigmoid 输出）"""
    def __init__(self, data_dim):
        self.data_dim = data_dim
        self.W = [random.gauss(0, 0.1) for _ in range(data_dim)]
        self.b = 0.0
    def forward(self, x):
        logit = sum(w * xi for w, xi in zip(self.W, x)) + self.b
        return 1 / (1 + math.exp(-logit)) if logit > -700 else 0.0
    def params(self): return self.W, self.b

class GAN:
    """GAN 训练器（参照 Goodfellow 2014 Algorithm 1）

    交替训练：
      ① 训练 D：max log D(real) + log(1 - D(G(z)))
      ② 训练 G：max log D(G(z))（欺骗 D）"""
    def __init__(self, latent_dim=4, data_dim=2, lr=0.01):
        self.G = Generator(latent_dim, data_dim)
        self.D = Discriminator(data_dim)
        self.lr = lr; self.history = {"d_loss": [], "g_loss": [], "d_real": [], "d_fake": []}

    def train_step(self, real_data_batch):
        """一次训练 step（参照 GAN 原始论文 Algorithm 1）"""
        d_losses = []; g_losses = []
        for real_data in real_data_batch:
            # ─── ① 训练判别器 D ───
            z = [random.gauss(0, 1) for _ in range(self.G.latent_dim)]
            fake_data = self.G.forward(z)
            d_real = self.D.forward(real_data)
            d_fake = self.D.forward(fake_data)
            # D 的损失：最大化 log D(real) + log(1-D(fake))
            d_loss = -(math.log(d_real + 1e-8) + math.log(1 - d_fake + 1e-8))
            # D 的梯度（简化：对 W 和 b 手动求导）
            grad_d_real = [-(1 - d_real) * x for x in real_data]
            grad_d_fake = [(1 - d_fake) * x for x in fake_data]  # 欺骗 D 的方向
            for i in range(self.D.data_dim):
                self.D.W[i] -= self.lr * (grad_d_real[i] + grad_d_fake[i])
            self.D.b -= self.lr * (-(1 - d_real) + (1 - d_fake))

            # ─── ② 训练生成器 G ───
            z = [random.gauss(0, 1) for _ in range(self.G.latent_dim)]
            fake_data = self.G.forward(z)
            d_fake_g = self.D.forward(fake_data)
            # G 的损失：最大化 log D(G(z))（让 D 认为 fake 是 real）
            g_loss = -math.log(d_fake_g + 1e-8)
            # G 的梯度（通过 D 反传）
            grad_g = d_fake_g * (1 - d_fake_g)  # sigmoid 导数
            for i in range(self.G.data_dim):
                for j in range(self.G.latent_dim):
                    self.G.W[i][j] += self.lr * grad_g * self.D.W[i] * z[j]
                self.G.b[i] += self.lr * grad_g * self.D.W[i]

            d_losses.append(d_loss); g_losses.append(g_loss)

        self.history["d_loss"].append(sum(d_losses)/len(d_losses))
        self.history["g_loss"].append(sum(g_losses)/len(g_losses))
        self.history["d_real"].append(d_real)
        self.history["d_fake"].append(d_fake_g)

    def generate(self, n_samples):
        """生成样本"""
        samples = []
        for _ in range(n_samples):
            z = [random.gauss(0, 1) for _ in range(self.G.latent_dim)]
            samples.append(self.G.forward(z))
        return samples


def demo():
    """GAN 演示"""
    print("\n┌─────────────────────────────────┐")
    print("│  tinygen: GAN 生成对抗网络      │")
    print("└─────────────────────────────────┘\n")
    random.seed(42)
    gan = GAN(latent_dim=4, data_dim=2, lr=0.01)
    # 真实数据：二维高斯分布 (mean=[1,1])
    real_dist = [[random.gauss(1, 0.3), random.gauss(1, 0.3)] for _ in range(100)]

    print(f"  真实分布: N(μ=[1,1], σ=0.3)")
    print(f"  训练 100 epochs × 100 samples/epoch\n")

    for epoch in range(100):
        gan.train_step(random.sample(real_dist, min(32, len(real_dist))))
        if epoch % 20 == 0 or epoch == 99:
            print(f"  epoch {epoch:3d}  D_loss={gan.history['d_loss'][-1]:.3f}  "
                  f"G_loss={gan.history['g_loss'][-1]:.3f}  "
                  f"D(real)={gan.history['d_real'][-1]:.2f}  D(fake)={gan.history['d_fake'][-1]:.2f}")

    # 生成样本
    samples = gan.generate(5)
    print(f"\n  生成样本（应接近 [1,1]）:")
    for s in samples: print(f"    {['%+.3f'%v for v in s]}")
    print(f"\n  纳什均衡: D→0.5（分不清真假）")
    print(f"  Mode collapse: GAN 的经典问题（所有样本塌缩到一个点）")
