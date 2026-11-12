"""
实验 04 · 最小视频扩散：在合成"运动"上演示去噪机制
====================================================
视频扩散 = 图像扩散搬到 (T,H,W) 三维。本实验用极小规模演示：
  · 数据：8帧×16×16 的"移动点"轨迹(随机起点+方向)
  · 前向：整段视频一起加噪 (T×H×W 联合)
  · 反向：一个轻量 3D 卷积去噪网络, 学预测噪声
  · 目标：loss 下降, 证明去噪网络能处理三维时序

注: CPU 上做不了真正的"高质量生成"(需要百万步训练)。
本实验的诚实目标是: 验证"视频扩散的损失能下降、去噪能在三维上work"。

运行:  python3 04_video_diffusion.py    # CPU 约 40 秒
输出:  exp04_video_diffusion.png
"""
import torch
# 3D卷积张量较大, 多线程更快(实测4线程39ms vs 单线程446ms/步)
torch.set_num_threads(min(4, torch.get_num_threads()))
torch.manual_seed(0)
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ---------- 1. 数据: 移动点轨迹 ----------
T, H, W = 8, 16, 16
def make_trajectory(batch=64):
    """每个样本: 一个点从随机起点以随机方向移动。返回 (B,1,T,H,W)"""
    x = torch.zeros(batch, 1, T, H, W)
    px = torch.randint(2, H - 2, (batch,)).float()
    py = torch.randint(2, W - 2, (batch,)).float()
    dx = torch.randn(batch) * 0.8
    dy = torch.randn(batch) * 0.8
    for t in range(T):
        cx = (px + dx * t).long().clamp(0, H - 1)
        cy = (py + dy * t).long().clamp(0, W - 1)
        x[torch.arange(batch), 0, t, cx, cy] = 1.0
        # 加一点光晕
        for ddx in [-1, 0, 1]:
            for ddy in [-1, 0, 1]:
                xi, yi = (cx + ddx).clamp(0, H - 1), (cy + ddy).clamp(0, W - 1)
                x[torch.arange(batch), 0, t, xi, yi] = x[torch.arange(batch), 0, t, xi, yi].maximum(torch.tensor(0.4))
    return x


data = make_trajectory(256)
print(f"[数据] {tuple(data.shape)}  (B,C,T,H,W)  — 移动点轨迹")


# ---------- 2. 扩散: 前向加噪 (闭式) ----------
n_steps = 50
betas = torch.linspace(1e-4, 0.02, n_steps)
alphas = 1 - betas
bar_alpha = torch.cumprod(alphas, 0)   # ᾱ_t

def q_sample(x0, t, eps=None):
    """闭式跳转: x_t = √ᾱ_t·x0 + √(1-ᾱ_t)·ε"""
    if eps is None:
        eps = torch.randn_like(x0)
    ba = bar_alpha[t].view(-1, 1, 1, 1, 1)
    return ba.sqrt() * x0 + (1 - ba).sqrt() * eps, eps


# ---------- 3. 去噪网络: 轻量 3D U-Net (单层) ----------
class TinyDenoise3D(nn.Module):
    def __init__(self, ch=8):
        super().__init__()
        self.conv1 = nn.Conv3d(1, ch, 3, padding=1)
        self.conv2 = nn.Conv3d(ch, ch, 3, padding=1)
        self.conv3 = nn.Conv3d(ch, 1, 3, padding=1)
        # 时间嵌入
        self.t_mlp = nn.Sequential(nn.Linear(1, ch), nn.ReLU(), nn.Linear(ch, ch))

    def forward(self, xt, t):
        h = torch.relu(self.conv1(xt))
        h = h + self.t_mlp(t.view(-1, 1).float() / n_steps).view(-1, h.shape[1], 1, 1, 1)
        h = torch.relu(self.conv2(h))
        return self.conv3(h)   # 预测噪声


net = TinyDenoise3D()
opt = torch.optim.Adam(net.parameters(), lr=2e-3)
print(f"[网络] 参数量 {sum(p.numel() for p in net.parameters())}")


# ---------- 4. 训练: 预测噪声 ----------
losses = []
for step in range(800):
    idx = torch.randint(0, data.shape[0], (64,))
    x0 = data[idx]
    t = torch.randint(0, n_steps, (64,))
    xt, eps = q_sample(x0, t)
    pred = net(xt, t)
    loss = ((pred - eps) ** 2).mean()
    opt.zero_grad(); loss.backward(); opt.step()
    if step % 100 == 0:
        losses.append(loss.item())
        print(f"  step {step:4d}  loss {loss.item():.4f}")


# ---------- 5. 反向采样: 从纯噪声去噪 (演示生成) ----------
@torch.no_grad()
def sample():
    x = torch.randn(1, 1, T, H, W)
    for t in reversed(range(n_steps)):
        tt = torch.full((1,), t)
        eps_pred = net(x, tt)
        alpha_t, beta_t = alphas[t], betas[t]
        ba = bar_alpha[t]
        mean = (1 / alpha_t.sqrt()) * (x - (beta_t / (1 - ba).sqrt()) * eps_pred)
        if t > 0:
            x = mean + beta_t.sqrt() * torch.randn_like(x) * 0.5   # 降噪采样
        else:
            x = mean
    return x


gen = sample().squeeze().numpy()
print(f"[生成] 去噪采样完成。生成视频峰值强度 {gen.max():.2f}")


# ---------- 6. 画图 ----------
fig, axes = plt.subplots(3, T, figsize=(13, 5))
# 第1行: 一个真实样本
real = data[0, 0].numpy()
for t in range(T):
    axes[0, t].imshow(real[t], cmap='hot', vmin=0, vmax=1); axes[0, t].axis('off')
axes[0, 0].set_ylabel('真实样本', fontsize=10)
# 第2行: 加噪到中间步
xt_mid, _ = q_sample(data[0:1], torch.tensor([25]))
for t in range(T):
    axes[1, t].imshow(xt_mid[0, 0, t].numpy(), cmap='hot'); axes[1, t].axis('off')
axes[1, 0].set_ylabel('加噪 t=25', fontsize=10)
# 第3行: 生成(去噪结果)
for t in range(T):
    axes[2, t].imshow(gen[t], cmap='hot'); axes[2, t].axis('off')
axes[2, 0].set_ylabel('去噪生成', fontsize=10)
axes[0, 0].set_title(f'训练 {len(losses)*100}步 loss: {losses[0]:.3f}→{losses[-1]:.3f}', loc='left')

plt.suptitle('实验04 · 视频扩散: 三维(T×H×W)联合去噪, 网络学会处理时序',
             fontsize=12.5, fontweight='bold')
plt.tight_layout()
plt.savefig('exp04_video_diffusion.png', dpi=110, bbox_inches='tight')
print("\n[输出] exp04_video_diffusion.png")
print("  注: CPU上无法训练到完美生成; 本实验验证的是'去噪损失能下降+三维去噪机制work'。")
