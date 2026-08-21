"""
讲透生成模型 · 实验 05 —— 扩散模型 Diffusion (DDPM) ★当代霸主
================================================================
Diffusion 属于『分数类』, 思路:
  前向: 一点点给数据加高斯噪声, 直到变成纯噪声 (固定的, 不学)
  反向: 训一个网络, 学会"从噪声里一点点把噪声去掉"还原数据 (这是要学的)
数学上, 这个"去噪网络"等价于在估计数据分布的【分数】∇log p(x) (见第6章).

本实验在 Swiss-roll 上跑最小 DDPM, 可视化:
  ① 前向加噪轨迹: 数据 t=0 → 纯噪声 t=T (一条直线路径)
  ② 反向去噪轨迹: 纯噪声 t=T → 数据 t=0 (生成过程!)
  ③ 噪声预测网络训练 loss

跑法:  python3 05_diffusion.py     (CPU 约 90 秒)
输出:  diffusion_process.png  (前向+反向轨迹对比)
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
# 1. Swiss-roll 数据 (连续流形, 去噪过程视觉效果好)
# ------------------------------------------------------------------
def swiss_roll(n=2000):
    t = 1.5*math.pi*(1+2*np.random.rand(n))
    return torch.tensor(np.c_[t*np.cos(t), t*np.sin(t)]/4, dtype=torch.float32)
DATA = swiss_roll(2000)

# ------------------------------------------------------------------
# 2. DDPM 前向过程 (固定, 不学): x_t = sqrt(abar_t) x_0 + sqrt(1-abar_t) ε
# ------------------------------------------------------------------
T = 100
betas  = torch.linspace(1e-4, 2e-2, T)
alphas = 1.0 - betas
abar   = torch.cumprod(alphas, 0)

# ------------------------------------------------------------------
# 3. 噪声预测网络: 输入 (x_t, t) 预测 ε. (训练目标 = 学会去噪)
#    第6章会证明: 预测噪声 等价于 估计分数 ∇log p(x)
# ------------------------------------------------------------------
class DiffNet(nn.Module):
    def __init__(self, hid=128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(3,hid),nn.ReLU(),nn.Linear(hid,hid),nn.ReLU(),nn.Linear(hid,2))
    def forward(self, xt, t):
        return self.net(torch.cat([xt, (t.float()/T)[:,None]], 1))
net = DiffNet()
opt = torch.optim.Adam(net.parameters(), 1e-3)

# ------------------------------------------------------------------
# 4. 训练: 随机 t, 前向加噪到 t, 让网络预测那个加的噪声 ε
# ------------------------------------------------------------------
print("训练 DDPM 噪声预测网络...", flush=True)
t0 = time.time()
n = len(DATA)
for it in range(2500):
    idx = torch.randint(0, n, (256,))
    x0 = DATA[idx]
    t  = torch.randint(0, T, (256,))
    eps = torch.randn_like(x0)
    ab  = abar[t][:,None]
    xt  = ab.sqrt()*x0 + (1-ab).sqrt()*eps        # 前向加噪到 t
    pred = net(xt, t)
    loss = ((pred - eps)**2).mean()                # 预测噪声
    opt.zero_grad(); loss.backward(); opt.step()
    if it % 500 == 0: print(f"  step {it}: MSE={loss.item():.4f}", flush=True)
print(f"  step 2500: MSE={loss.item():.4f}  ({time.time()-t0:.0f}s)")

# ------------------------------------------------------------------
# 5. 反向采样 (生成): 从纯噪声 x_T 一步步去噪回 x_0
# ------------------------------------------------------------------
@torch.no_grad()
def sample(n_sample=2000, save_frames=None):
    x = torch.randn(n_sample, 2)
    frames = {T: x.clone()}
    for t in reversed(range(T)):
        tt = torch.full((n_sample,), t, dtype=torch.long)
        eps_pred = net(x, tt)
        mean = (1.0/alphas[t].sqrt())*(x - (betas[t]/(1-abar[t]).sqrt())*eps_pred)
        if t > 0:
            mean = mean + betas[t].sqrt()*torch.randn_like(mean)   # 随机性 (除最后一步)
        x = mean
        if save_frames is not None and t in save_frames:
            frames[t] = x.clone()
    return x, frames

print("反向采样生成...", flush=True)
snapshots = {T, int(T*0.75), int(T*0.5), int(T*0.25), 0}
samples, frames = sample(2000, snapshots)

# ------------------------------------------------------------------
# 6. 可视化: 上行=前向加噪(数据→噪声), 下行=反向去噪(噪声→数据)
# ------------------------------------------------------------------
def fwd_at(x0, t):
    if t >= T: return torch.randn_like(x0)        # t=T 时已是纯噪声
    ab = abar[t]
    return ab.sqrt()*x0 + (1-ab).sqrt()*torch.randn_like(x0)
ts_plot = [0, int(T*0.25), int(T*0.5), int(T*0.75), T]

fig, axes = plt.subplots(2, 5, figsize=(18, 7))
for j, t in enumerate(ts_plot):
    with torch.no_grad():
        xt = fwd_at(DATA, t) if t > 0 else DATA
    axes[0, j].scatter(xt[:,0].numpy(), xt[:,1].numpy(), s=4, c="C3")
    axes[0, j].set_title(f"前向加噪 t={t}\n{'数据' if t==0 else ('纯噪声' if t==T else '中间')}")
    axes[0, j].set_xlim(-3.5,3.5); axes[0, j].set_ylim(-3.5,3.5); axes[0, j].set_aspect("equal")
    xt2 = frames[t]
    axes[1, j].scatter(xt2[:,0].numpy(), xt2[:,1].numpy(), s=4, c="C0")
    axes[1, j].set_title(f"反向去噪 t={t}\n{'生成结果' if t==0 else ''}")
    axes[1, j].set_xlim(-3.5,3.5); axes[1, j].set_ylim(-3.5,3.5); axes[1, j].set_aspect("equal")
axes[0,0].set_ylabel("前向 (固定, 不学)")
axes[1,0].set_ylabel("反向 (生成, 要学)")
fig.suptitle("扩散模型: 上行=一点点加噪毁掉数据; 下行=一点点去噪重建数据 (生成)", fontsize=13)
fig.tight_layout(); fig.savefig("diffusion_process.png", dpi=110)
print("图已保存: diffusion_process.png")
print("\n要点: 训练只需学『预测噪声』这一个简单任务, 却能得到高质量生成器 —— 这是扩散的精髓.")
