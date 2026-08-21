"""
讲透生成模型 · 实验 00 —— 统一视角的「黄金对比」
=================================================
用三大范式 (VAE / GAN / Diffusion) 学**同一个** 8-高斯分布，
一次看清生成模型三大流派 (似然类 / 隐式类 / 分数类) 的本质差异：

  - VAE (似然类):  覆盖全 (8/8 模态) 但样本偏模糊 —— "宁可摊薄也要全覆盖"
  - GAN (隐式类):  样本清晰但容易模式崩溃 (只占 2~5 个模态) —— "只跟判别器较劲"
  - Diffusion (分数类): 兼顾清晰与覆盖 —— 代价是采样要一步步去噪 (慢)

跑法:  python3 00_unified_view.py     (CPU 约 1~2 分钟)
输出:  unified_view.png               +  控制台打印模态覆盖统计
"""
import math, time
import numpy as np
import torch
import torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.manual_seed(0); np.random.seed(0)
DEV = torch.device("cpu")
torch.set_num_threads(1)   # 小矩阵上多线程争抢反而慢, 单线程快约 4 倍 (见 bench.py)

# ------------------------------------------------------------------
# 1. 目标分布: 8 个高斯团, 等分在半径 2.0 的圆上 (生成模型经典 benchmark)
# ------------------------------------------------------------------
CENTERS = np.array([[2.0 * math.cos(2 * math.pi * k / 8),
                     2.0 * math.sin(2 * math.pi * k / 8)] for k in range(8)])
CENTERS_T = torch.tensor(CENTERS, dtype=torch.float32, device=DEV)   # 纯 tensor, 避免每步 numpy 转换

def sample_real(n):
    """从真实 8-高斯分布采 n 个点 (每个团 std=0.04)."""
    idx = torch.randint(0, 8, (n,), device=DEV)
    return CENTERS_T[idx] + 0.04 * torch.randn(n, 2, device=DEV)

# 统计生成样本覆盖了几个模态 (落在本中心 0.5 半径内算命中)
def modality_coverage(samples):
    s = samples.detach().cpu().numpy()
    hit = 0
    for c in CENTERS:
        d = np.linalg.norm(s - c, axis=1)
        if (d < 0.5).mean() > 0.02:   # 该模态至少分到 2% 的样本才算"被覆盖"
            hit += 1
    return hit

# ==================================================================
# 范式一: VAE (变分自编码器 —— 似然类的代表)
# ==================================================================
class VAE(nn.Module):
    def __init__(self, dim=2, hid=128, z=2):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(dim, hid), nn.ReLU(), nn.Linear(hid, hid), nn.ReLU())
        self.mu  = nn.Linear(hid, z)
        self.lv  = nn.Linear(hid, z)
        self.dec = nn.Sequential(nn.Linear(z, hid), nn.ReLU(), nn.Linear(hid, hid), nn.ReLU(), nn.Linear(hid, dim))
    def encode(self, x):
        h = self.enc(x); return self.mu(h), self.lv(h)
    def decode(self, z):
        return self.dec(z)
    def forward(self, x):
        mu, lv = self.encode(x)
        std = torch.exp(0.5 * lv)
        z = mu + std * torch.randn_like(std)          # 重参数化 reparameterization trick
        return self.decode(z), mu, lv

def train_vae(steps=3000):
    m = VAE().to(DEV); opt = torch.optim.Adam(m.parameters(), 1e-3)
    for it in range(steps):
        x = sample_real(256)
        xhat, mu, lv = m(x)
        recon = ((xhat - x) ** 2).sum(1).mean()       # 重构项 (似然, 假设高斯)
        kld   = -0.5 * (1 + lv - mu.pow(2) - lv.exp()).sum(1).mean()  # KL(q(z|x)||N(0,I))
        loss  = recon + kld
        opt.zero_grad(); loss.backward(); opt.step()
    # 采样: 先验 z~N(0,I), 再解码
    with torch.no_grad():
        z = torch.randn(2000, 2, device=DEV)
        samples = m.decode(z)
    return m, samples

# ==================================================================
# 范式二: GAN (生成对抗网络 —— 隐式类的代表)
# ==================================================================
class G(nn.Module):   # 生成器
    def __init__(self, z=2, hid=128, dim=2):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(z, hid), nn.ReLU(), nn.Linear(hid, hid), nn.ReLU(), nn.Linear(hid, dim))
    def forward(self, z): return self.net(z)

class D(nn.Module):   # 判别器
    def __init__(self, dim=2, hid=128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(dim, hid), nn.ReLU(), nn.Linear(hid, hid), nn.ReLU(), nn.Linear(hid, 1))
    def forward(self, x): return self.net(x)

def train_gan(steps=3000):
    Gnet, Dnet = G().to(DEV), D().to(DEV)
    gopt = torch.optim.Adam(Gnet.parameters(), 2e-4, betas=(0.5, 0.9))
    dopt = torch.optim.Adam(Dnet.parameters(), 2e-4, betas=(0.5, 0.9))
    bce  = nn.BCEWithLogitsLoss()
    for it in range(steps):
        # --- 判别器走 1 步 ---
        x = sample_real(256)
        z = torch.randn(256, 2, device=DEV)
        with torch.no_grad(): fake = Gnet(z)
        dreal = Dnet(x); dfake = Dnet(fake)
        ld = (bce(dreal, torch.ones_like(dreal)) + bce(dfake, torch.zeros_like(dfake))) / 2
        dopt.zero_grad(); ld.backward(); dopt.step()
        # --- 生成器走 1 步 ---
        z = torch.randn(256, 2, device=DEV); fake = Gnet(z)
        lg = bce(Dnet(fake), torch.ones_like(dreal))   # G 想让 D 把假的说成真
        gopt.zero_grad(); lg.backward(); gopt.step()
    with torch.no_grad():
        z = torch.randn(2000, 2, device=DEV); samples = Gnet(z)
    return Gnet, samples

# ==================================================================
# 范式三: Diffusion (DDPM —— 分数类的代表, 当今图像/视频生成霸主)
#   前向:  x_t = sqrt(abar_t) x_0 + sqrt(1-abar_t) eps
#   反向:  学一个网络预测 eps, 再一步步去噪
# ==================================================================
T = 100
betas = torch.linspace(1e-4, 2e-2, T, device=DEV)
alphas = 1.0 - betas
abar   = torch.cumprod(alphas, 0)                       # \bar{alpha}_t

class DiffNet(nn.Module):
    """输入 (x_t[2], t_norm[1]) -> 预测 eps[2]."""
    def __init__(self, dim=2, hid=128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(dim + 1, hid), nn.ReLU(),
                                 nn.Linear(hid, hid), nn.ReLU(), nn.Linear(hid, dim))
    def forward(self, xt, t):
        return self.net(torch.cat([xt, (t.float() / T)[:, None]], dim=1))

def train_diff(steps=4000):
    net = DiffNet().to(DEV); opt = torch.optim.Adam(net.parameters(), 1e-3)
    for it in range(steps):
        x0 = sample_real(256)
        t  = torch.randint(0, T, (256,), device=DEV)
        eps = torch.randn_like(x0)
        ab  = abar[t][:, None]
        xt  = ab.sqrt() * x0 + (1 - ab).sqrt() * eps     # 前向加噪到 t
        pred = net(xt, t)
        loss = ((pred - eps) ** 2).mean()                # 预测噪声
        opt.zero_grad(); loss.backward(); opt.step()
    # 反向采样: 从纯噪声 x_T 逐步去噪回 x_0
    net.eval()
    with torch.no_grad():
        x = torch.randn(2000, 2, device=DEV)
        for t in reversed(range(T)):
            tt = torch.full((2000,), t, device=DEV, dtype=torch.long)
            eps_pred = net(x, tt)
            mean = (1.0 / alphas[t].sqrt()) * (x - (betas[t] / (1 - abar[t]).sqrt()) * eps_pred)
            if t > 0:
                mean = mean + betas[t].sqrt() * torch.randn_like(mean)   # 加随机噪声 (除最后一步)
            x = mean
        samples = x
    return net, samples

# ==================================================================
# 主程序: 训练三个模型 + 画对比图 + 打印模态覆盖
# ==================================================================
if __name__ == "__main__":
    real = sample_real(2000)
    print(f"真实数据: 8 个模态, 共 {len(CENTERS)} 个高斯团\n")

    t0 = time.time(); vae_m,  vae_s  = train_vae();  print(f"[VAE]        训练完成 ({time.time()-t0:.0f}s)")
    t0 = time.time(); gan_m,  gan_s  = train_gan();  print(f"[GAN]        训练完成 ({time.time()-t0:.0f}s)")
    t0 = time.time(); dif_m,  dif_s  = train_diff(); print(f"[Diffusion]  训练完成 ({time.time()-t0:.0f}s)")

    print("\n=== 模态覆盖统计 (命中 8 个高斯团中的几个) ===")
    print(f"  VAE       : {modality_coverage(vae_s)}/8   <- 似然类: 覆盖全, 样本偏模糊")
    print(f"  GAN       : {modality_coverage(gan_s)}/8   <- 隐式类: 易模式崩溃 (缺模态)")
    print(f"  Diffusion : {modality_coverage(dif_s)}/8   <- 分数类: 兼顾覆盖与清晰, 代价是采样慢 (T={T} 步)")

    # ---- 画图 ----
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    for ax in axes:
        ax.set_xlim(-3.2, 3.2); ax.set_ylim(-3.2, 3.2); ax.set_aspect("equal")
    axes[0].scatter(real[:, 0].numpy(), real[:, 1].numpy(), s=4, c="k"); axes[0].set_title("Real (8-Gaussians)")
    axes[1].scatter(vae_s[:, 0].numpy(), vae_s[:, 1].numpy(), s=4, c="C0");  axes[1].set_title(f"VAE  (似然类)\n覆盖 {modality_coverage(vae_s)}/8 · 偏模糊")
    axes[2].scatter(gan_s[:, 0].numpy(), gan_s[:, 1].numpy(), s=4, c="C3");  axes[2].set_title(f"GAN  (隐式类)\n覆盖 {modality_coverage(gan_s)}/8 · 易模式崩溃")
    axes[3].scatter(dif_s[:, 0].numpy(), dif_s[:, 1].numpy(), s=4, c="C2");  axes[3].set_title(f"Diffusion (分数类)\n覆盖 {modality_coverage(dif_s)}/8 · 慢但好")
    for ax in axes:
        ax.plot(CENTERS[:, 0], CENTERS[:, 1], "r*", ms=12)   # 标出真模态中心
    fig.suptitle("三大生成范式学同一个 8-高斯分布: 似然类(VAE) / 隐式类(GAN) / 分数类(Diffusion)", fontsize=13)
    fig.tight_layout(); fig.savefig("unified_view.png", dpi=110)
    print("\n图已保存: unified_view.png")
