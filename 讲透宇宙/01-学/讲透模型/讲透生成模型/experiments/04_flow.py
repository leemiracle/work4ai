"""
讲透生成模型 · 实验 04 —— 标准化流 Flow (RealNVP)
==================================================
Flow 属于『似慎类』, 用一串『可逆变换』把简单分布 N(0,I) 变成数据分布:
    z ~ N(0,I)  --inverse(多层 coupling)--> x ~ p_data
核心: 因为变换可逆且雅可比行列式好算, 能算出【精确】对数似然 log p(x).

本实验用最小 RealNVP (6 层 coupling) 学 two-moons:
  ① 训练时最大化精确 log p(x)
  ② 展示 base 空间 N(0,I) ↔ data 空间 的双向变换
  ③ 从 N(0,I) 采样 → 反向变换 → 生成的 two-moons

跑法:  python3 04_flow.py     (CPU 约 40 秒)
输出:  flow_transform.png  (base ↔ data 双向可视化 + 精确似然)
"""
import math, time
import numpy as np
import torch, torch.nn as nn
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt

torch.set_num_threads(1); torch.manual_seed(0); np.random.seed(0)
LOG2PI = math.log(2*math.pi)

# ------------------------------------------------------------------
# 1. two-moons 数据
# ------------------------------------------------------------------
def two_moons(n=2000):
    t = np.linspace(0, math.pi, n//2)
    up = np.c_[np.cos(t), np.sin(t)] + 0.05*np.random.randn(len(t),2)
    dn = np.c_[1-np.cos(t), -np.sin(t)-0.5] + 0.05*np.random.randn(len(t),2)
    return torch.tensor(np.r_[up,dn], dtype=torch.float32)
DATA = two_moons(2000)

# ------------------------------------------------------------------
# 2. RealNVP coupling layer (2D): 改一半, 依赖另一半, 可逆
#    x = [x1, x2].  令 y1 = x1 (不动), y2 = x2*exp(s(x1)) + t(x1)
#    雅可比是三角阵, 行列式 = exp(s), 故 log|det J| = s
# ------------------------------------------------------------------
class Coupling(nn.Module):
    def __init__(self, flip):
        super().__init__()
        self.flip = flip
        self.st = nn.Sequential(nn.Linear(1,64),nn.ReLU(),nn.Linear(64,64),nn.ReLU(),nn.Linear(64,2))
    def _st(self, a):
        out = self.st(a)
        return torch.tanh(out[:,0:1]), out[:,1:2]      # s 用 tanh 限幅, t 不限
    def forward(self, x):        # data -> latent  (返回 y, logdet)
        x = x[:, [1,0]] if self.flip else x
        x1, x2 = x[:,0:1], x[:,1:2]
        s, t = self._st(x1)
        y2 = x2*torch.exp(s) + t
        y = torch.cat([x1, y2], 1)
        logdet = s.sum(1)
        return (y[:, [1,0]] if self.flip else y), logdet
    def inverse(self, y):        # latent -> data  (生成用)
        y = y[:, [1,0]] if self.flip else y
        y1, y2 = y[:,0:1], y[:,1:2]
        s, t = self._st(y1)
        x2 = (y2 - t)*torch.exp(-s)
        x = torch.cat([y1, x2], 1)
        return x[:, [1,0]] if self.flip else x

class RealNVP(nn.Module):
    def __init__(self, n_layers=6):
        super().__init__()
        self.layers = nn.ModuleList([Coupling(i % 2 == 1) for i in range(n_layers)])
    def forward(self, x):        # data -> z, 返回 z 和总 logdet
        logdet = torch.zeros(x.shape[0])
        for l in self.layers:
            x, ld = l(x); logdet = logdet + ld
        return x, logdet
    def inverse(self, z):        # z -> data (生成)
        for l in reversed(self.layers):
            z = l.inverse(z)
        return z

# ------------------------------------------------------------------
# 3. 训练: 最大化【精确】 log p(x)
#    log p(x) = log N(z;0,I) + log|det dz/dx|,  其中 z=f(x), logdet=log|det|
# ------------------------------------------------------------------
model = RealNVP()
opt = torch.optim.Adam(model.parameters(), 1e-3)
n = len(DATA)
print("训练 RealNVP (最大化精确对数似然)...", flush=True)
t = time.time()
for it in range(1500):
    idx = torch.randint(0, n, (256,))
    x = DATA[idx]
    z, logdet = model(x)
    logpz = -0.5*(z**2).sum(1) - LOG2PI          # log N(z;0,I), 2维
    logpx = logpz + logdet                        # ★ 变量替换: 精确似然
    loss = -logpx.mean()                          # 负对数似然
    opt.zero_grad(); loss.backward(); opt.step()
    if it % 300 == 0: print(f"  step {it}: NLL={loss.item():.3f}", flush=True)
print(f"  step 1500: NLL={loss.item():.3f}  ({time.time()-t:.0f}s)")

# 精确似然 vs VAE: VAE 只能给下界 ELBO, Flow 给的是真·似然
with torch.no_grad():
    z_all, ld_all = model(DATA)
    logpx_all = (-0.5*(z_all**2).sum(1) - LOG2PI + ld_all)
    print(f"\n精确平均对数似然 log p(x) = {logpx_all.mean().item():.3f}  (Flow 能算精确值, VAE 只能算下界)")

    # 生成: 从 N(0,I) 采样, 反向变换
    z_new = torch.randn(2000, 2)
    x_gen = model.inverse(z_new)

    # 也看 base->data 的变换轨迹: 把一个网格点跑一遍
    grid = torch.tensor([[a,b] for a in np.linspace(-3,3,15) for b in np.linspace(-3,3,15)], dtype=torch.float32)
    grid_data = model.inverse(grid)

# ------------------------------------------------------------------
# 4. 画图: base 空间 ↔ data 空间
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(14,4.5))
axes[0].scatter(z_all[:,0].numpy(), z_all[:,1].numpy(), s=4, c="C0")
axes[0].set_title(f"编码后的 latent z=f(x)\n(应接近 N(0,I))"); axes[0].set_xlim(-3.5,3.5); axes[0].set_ylim(-3.5,3.5); axes[0].set_aspect("equal")
axes[1].scatter(DATA[:,0].numpy(), DATA[:,1].numpy(), s=4, c="k"); axes[1].set_title("真实 two-moons")
axes[1].set_xlim(-1.5,2.5); axes[1].set_ylim(-1.5,1.3); axes[1].set_aspect("equal")
axes[2].scatter(x_gen[:,0].numpy(), x_gen[:,1].numpy(), s=4, c="C2")
axes[2].set_title(f"从 N(0,I) 采样→inverse 生成\n精确 log p(x)={logpx_all.mean().item():.2f}")
axes[2].set_xlim(-1.5,2.5); axes[2].set_ylim(-1.5,1.3); axes[2].set_aspect("equal")
fig.suptitle("标准化流: 可逆变换让 N(0,I) ↔ two-moons, 且能算精确对数似然", fontsize=12)
fig.tight_layout(); fig.savefig("flow_transform.png", dpi=110)
print("图已保存: flow_transform.png")
