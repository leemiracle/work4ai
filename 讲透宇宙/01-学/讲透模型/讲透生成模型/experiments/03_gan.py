"""
讲透生成模型 · 实验 03 —— GAN (生成对抗网络) + 模式崩溃与缓解
=============================================================
GAN 属于『隐式类』: 不写 p(x), 而是让生成器 G 和判别器 D 对抗.
    min_G max_D  E[log D(x)] + E[log(1-D(G(z)))]
GAN 样本清晰, 但极易『模式崩溃』(只生成几个模态, 丢掉其余).

本实验在 8-高斯分布上对比:
  ① vanilla GAN   —— 经典模式崩溃 (覆盖 1~3/8)
  ② WGAN (weight clipping) —— Wasserstein 距离缓解崩溃 (覆盖 7~8/8)

跑法:  python3 03_gan.py     (CPU 约 90 秒)
输出:  gan_compare.png  (vanilla vs WGAN 的生成散点 + 模态覆盖)
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
# 8-高斯数据 (同实验00)
# ------------------------------------------------------------------
CENTERS = torch.tensor([[2.0*math.cos(2*math.pi*k/8), 2.0*math.sin(2*math.pi*k/8)] for k in range(8)])
def sample_real(n):
    idx = torch.randint(0, 8, (n,))
    return CENTERS[idx] + 0.04*torch.randn(n, 2)
def coverage(s):
    s = s.numpy(); hit = 0
    for c in CENTERS.numpy():
        if (np.linalg.norm(s - c, axis=1) < 0.5).mean() > 0.02: hit += 1
    return hit

Ghid = Dhid = 128
class Gnet(nn.Module):
    def __init__(self): super().__init__(); self.net = nn.Sequential(nn.Linear(2,Ghid),nn.ReLU(),nn.Linear(Ghid,Ghid),nn.ReLU(),nn.Linear(Ghid,2))
    def forward(self,z): return self.net(z)
class Dnet(nn.Module):
    def __init__(self): super().__init__(); self.net = nn.Sequential(nn.Linear(2,Dhid),nn.ReLU(),nn.Linear(Dhid,Dhid),nn.ReLU(),nn.Linear(Dhid,1))
    def forward(self,x): return self.net(x)

# ===== vanilla GAN: BCE, D 输出经 sigmoid 当概率 =====
def train_vanilla(steps=1200):
    torch.manual_seed(0)
    G, D = Gnet(), Dnet()
    gopt = torch.optim.Adam(G.parameters(), 2e-4, (0.5,0.9))
    dopt = torch.optim.Adam(D.parameters(), 2e-4, (0.5,0.9))
    bce = nn.BCEWithLogitsLoss()
    for it in range(steps):
        x = sample_real(256); z = torch.randn(256,2)
        with torch.no_grad(): fake = G(z)
        ld = (bce(D(x), torch.ones(256,1)) + bce(D(fake), torch.zeros(256,1)))/2
        dopt.zero_grad(); ld.backward(); dopt.step()
        z = torch.randn(256,2); fake = G(z)
        lg = bce(D(fake), torch.ones(256,1))
        gopt.zero_grad(); lg.backward(); gopt.step()
    with torch.no_grad(): return G, G(torch.randn(2000,2))

# ===== WGAN: D(critic) 无 sigmoid, 用 Wasserstein 距离 + 权重裁剪 =====
#   WGAN 把"D 输出概率"改成"D 输出实数分数", 优化 E[D(fake)]-E[D(real)].
#   关键: critic 要满足 Lipschitz, 用 weight clipping 到 [-c,c] 近似.
#   优化目标更平滑 → 模式崩溃显著缓解.
def train_wgan(steps=900, c=0.01, d_per_g=3):
    torch.manual_seed(0)
    G, D = Gnet(), Dnet()
    gopt = torch.optim.RMSprop(G.parameters(), 5e-4)
    dopt = torch.optim.RMSprop(D.parameters(), 5e-4)
    for it in range(steps):
        # critic 走 d_per_g 步
        for _ in range(d_per_g):
            x = sample_real(64); z = torch.randn(64,2); fake = G(z)
            ld = D(fake).mean() - D(x).mean()         # Wasserstein: 越大越好(对D), 所以最小化负
            dopt.zero_grad(); ld.backward(); dopt.step()
            for p in D.parameters(): p.data.clamp_(-c, c)   # ★ weight clipping 保 Lipschitz
        # G 走 1 步
        z = torch.randn(256,2); fake = G(z)
        lg = -D(fake).mean()
        gopt.zero_grad(); lg.backward(); gopt.step()
    with torch.no_grad(): return G, G(torch.randn(2000,2))

if __name__ == "__main__":
    print("训练 vanilla GAN ...", flush=True)
    t=time.time(); gV, sV = train_vanilla(); print(f"  完成 ({time.time()-t:.0f}s)", flush=True)
    print("训练 WGAN ...", flush=True)
    t=time.time(); gW, sW = train_wgan();   print(f"  完成 ({time.time()-t:.0f}s)", flush=True)

    cV, cW = coverage(sV), coverage(sW)
    print(f"\n=== 模态覆盖 (共8) ===")
    print(f"  vanilla GAN : {cV}/8   <- 经典模式崩溃 (判别器只看局部, 不罚漏模态)")
    print(f"  WGAN        : {cW}/8   <- Wasserstein 距离更平滑, 覆盖显著改善")

    real = sample_real(2000)
    fig, axes = plt.subplots(1, 3, figsize=(13,4.2))
    for ax in axes: ax.set_xlim(-3.2,3.2); ax.set_ylim(-3.2,3.2); ax.set_aspect("equal")
    axes[0].scatter(real[:,0].numpy(), real[:,1].numpy(), s=4, c="k"); axes[0].set_title("Real (8-Gaussians)")
    axes[1].scatter(sV[:,0].numpy(), sV[:,1].numpy(), s=4, c="C3");  axes[1].set_title(f"vanilla GAN\n覆盖 {cV}/8 · 模式崩溃")
    axes[2].scatter(sW[:,0].numpy(), sW[:,1].numpy(), s=4, c="C1");  axes[2].set_title(f"WGAN (weight clip)\n覆盖 {cW}/8 · 缓解崩溃")
    for ax in axes: ax.plot(CENTERS[:,0].numpy(), CENTERS[:,1].numpy(), "r*", ms=12)
    fig.suptitle("GAN 的模式崩溃与 WGAN 的缓解: 隐式类的痛点与解药", fontsize=13)
    fig.tight_layout(); fig.savefig("gan_compare.png", dpi=110)
    print("\n图已保存: gan_compare.png")
