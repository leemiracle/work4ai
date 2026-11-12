"""
讲透生成模型 · 实验 02 —— VAE (变分自编码器)
============================================
VAE 属于『似然类』, 但不像 AR 逐位分解, 而是引入一个隐变量 z:
    x --encoder--> q(z|x) --采样z--> decoder --> x̂
训练目标 ELBO = 重构项 + KL项 (让 q(z|x) 靠近先验 N(0,I))

本实验用 two-moons 数据, 展示 VAE 三个核心机制:
  ① 重参数化 trick (让采样可反向传播)
  ② ELBO 两项的拉锯 (重构 vs KL)
  ③ β (KL 权重) 的影响: β 小→退化为AE(不规整); β 大→后验坍缩(生成糊/单一)

跑法:  python3 02_vae.py     (CPU 约 30 秒)
输出:  vae_beta.png  (3 个 β 的 latent 空间 + 生成对比)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)

# ------------------------------------------------------------------
# 1. two-moons 数据 (不依赖 sklearn, 自己合成)
# ------------------------------------------------------------------
def two_moons(n=2000):
    t = np.linspace(0, math.pi, n // 2)
    up = np.c_[np.cos(t), np.sin(t)]            + 0.05 * np.random.randn(len(t), 2)
    dn = np.c_[1 - np.cos(t), -np.sin(t) - 0.5] + 0.05 * np.random.randn(len(t), 2)
    return torch.tensor(np.r_[up, dn], dtype=torch.float32)

DATA = two_moons(2000)

# ------------------------------------------------------------------
# 2. VAE 模型
# ------------------------------------------------------------------
class VAE(nn.Module):
    def __init__(self, dim=2, hid=64, zdim=2):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(dim, hid), nn.ReLU(), nn.Linear(hid, hid), nn.ReLU())
        self.mu  = nn.Linear(hid, zdim)
        self.lv  = nn.Linear(hid, zdim)
        self.dec = nn.Sequential(nn.Linear(zdim, hid), nn.ReLU(), nn.Linear(hid, hid), nn.ReLU(), nn.Linear(hid, dim))
    def encode(self, x):
        h = self.enc(x); return self.mu(h), self.lv(h)
    def decode(self, z): return self.dec(z)
    def forward(self, x):
        mu, lv = self.encode(x)
        std = torch.exp(0.5 * lv)
        z = mu + std * torch.randn_like(std)      # ★ 重参数化 trick: z = μ + σ⊙ε, 梯度能穿过采样
        return self.decode(z), mu, lv

def elbo(x, model, beta):
    """ELBO = -重构误差 - beta·KL.  返回 (recon, kld)."""
    xhat, mu, lv = model(x)
    recon = ((xhat - x) ** 2).sum(1).mean()
    kld   = -0.5 * (1 + lv - mu.pow(2) - lv.exp()).sum(1).mean()
    loss  = recon + beta * kld
    return loss, recon, kld

def train_vae(beta, steps=1000):
    torch.manual_seed(0)
    m = VAE(); opt = torch.optim.Adam(m.parameters(), 1e-3)
    rec_hist, kld_hist = [], []
    n = len(DATA)
    for it in range(steps):
        idx = torch.randint(0, n, (256,))
        x = DATA[idx]
        loss, recon, kld = elbo(x, m, beta)
        opt.zero_grad(); loss.backward(); opt.step()
        if it % 200 == 0:
            rec_hist.append(recon.item()); kld_hist.append(kld.item())
    # 编码全部数据看 latent 分布 + 从先验采样生成
    with torch.no_grad():
        mu, lv = m.encode(DATA)
        z_gen = torch.randn(2000, 2)
        samples = m.decode(z_gen)
    return m, mu, samples, rec_hist, kld_hist

# ------------------------------------------------------------------
# 3. 跑三个 β, 对比
# ------------------------------------------------------------------
if __name__ == "__main__":
    betas = [0.01, 1.0, 10.0]
    results = {}
    for b in betas:
        print(f"  训练 β={b} ...", flush=True)
        t = time.time()
        m, mu, samples, rh, kh = train_vae(b)
        results[b] = (m, mu, samples, rh, kh)
        # 后验坍缩诊断: latent 是否还有信息? 看 mu 的方差 (方差≈0 说明所有 x 映射到同一个 z = 后验坍缩)
        mu_var = mu.var(0).mean().item()
        print(f"β={b:>5}: recon={rh[-1]:.3f}  KL={kh[-1]:.4f}  latent方差={mu_var:.3f}  ({time.time()-t:.0f}s)")
    print()
    print("解读:")
    print("  β=0.01 : KL几乎不计 → 退化为普通AE, latent 不规整 (偏离 N(0,I)), 从 N(0,I) 采样生成 = 乱点")
    print("  β=1.0  : 标准 VAE, 重构与 KL 平衡, latent 接近先验, 生成基本成形")
    print("  β=10   : KL 权重过大 → 后验坍缩 (latent 方差→0, decoder 忽略 z), 生成塌成一坨")

    # ---- 画图: 每行一个 β, 左=latent 空间(enc 后的 mu), 右=从先验生成 ----
    fig, axes = plt.subplots(2, len(betas), figsize=(13, 7))
    for j, b in enumerate(betas):
        m, mu, samples, rh, kh = results[b]
        axes[0, j].scatter(mu[:, 0].numpy(), mu[:, 1].numpy(), s=3, c=range(len(mu)), cmap="coolwarm")
        axes[0, j].set_title(f"β={b}\nlatent 空间 (enc 后 μ)\n方差={mu.var(0).mean():.3f}")
        axes[0, j].set_xlim(-4, 4); axes[0, j].set_ylim(-4, 4); axes[0, j].set_aspect("equal")
        axes[1, j].scatter(samples[:, 0].numpy(), samples[:, 1].numpy(), s=3, c="C2")
        axes[1, j].set_title(f"β={b}\n从 N(0,I) 采样生成")
        axes[1, j].set_xlim(-2, 2.5); axes[1, j].set_ylim(-1.8, 1.3); axes[1, j].set_aspect("equal")
    axes[0, 0].set_ylabel("latent 空间")
    axes[1, 0].set_ylabel("生成样本")
    fig.suptitle("VAE 的 β 拉锯: β 小→退化为AE(latent不规整); β 大→后验坍缩(生成塌掉); β=1 平衡", fontsize=12)
    fig.tight_layout(); fig.savefig("vae_beta.png", dpi=110)
    print("\n图已保存: vae_beta.png")
