"""
E08 解答 · 扩散采样步数消融: 质量-速度权衡
============================================
两组测量(同一训练好的 3D 去噪网络):
  (1) 条件还原: 真实样本加噪到 t=99, K 步 strided DDIM 还原 → MSE(x0_hat,x0)
  (2) 纯噪声生成: 从 N(0,I) 出发 → 与最近训练样本余弦

预期现象(已实测): K=1,2 极端少步明显崩塌; K≥4 的 DDIM 中段稳健;
这正是 CausVid 蒸馏的价值点: 在极端少步(4步)区间保住质量。

运行: python3 E08_step_ablation.py    # 约 70 秒
输出: E08_step_ablation.png
"""
import torch
torch.set_num_threads(min(4, torch.get_num_threads()))
torch.manual_seed(0)
import torch.nn as nn
import torch.nn.functional as F
import time
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

T, H, W = 8, 16, 16


def make_trajectory(batch=64):
    x = torch.zeros(batch, 1, T, H, W)
    px = torch.randint(2, H - 2, (batch,)).float()
    py = torch.randint(2, W - 2, (batch,)).float()
    dx = torch.randn(batch) * 0.8
    dy = torch.randn(batch) * 0.8
    for t in range(T):
        cx = (px + dx * t).long().clamp(0, H - 1)
        cy = (py + dy * t).long().clamp(0, W - 1)
        x[torch.arange(batch), 0, t, cx, cy] = 1.0
        for ddx in [-1, 0, 1]:
            for ddy in [-1, 0, 1]:
                xi, yi = (cx + ddx).clamp(0, H - 1), (cy + ddy).clamp(0, W - 1)
                cur = x[torch.arange(batch), 0, t, xi, yi]
                x[torch.arange(batch), 0, t, xi, yi] = cur.maximum(torch.tensor(0.4))
    return x


data = make_trajectory(256)

n_steps = 100
betas = torch.linspace(1e-4, 0.02, n_steps)
alphas = 1 - betas
bar_alpha = torch.cumprod(alphas, 0)


def q_sample(x0, t, eps=None):
    if eps is None:
        eps = torch.randn_like(x0)
    ba = bar_alpha[t].view(-1, 1, 1, 1, 1)
    return ba.sqrt() * x0 + (1 - ba).sqrt() * eps, eps


class TinyDenoise3D(nn.Module):
    def __init__(self, ch=16):
        super().__init__()
        self.conv1 = nn.Conv3d(1, ch, 3, padding=1)
        self.conv2 = nn.Conv3d(ch, ch, 3, padding=1)
        self.conv3 = nn.Conv3d(ch, 1, 3, padding=1)
        self.t_mlp = nn.Sequential(nn.Linear(1, ch), nn.ReLU(), nn.Linear(ch, ch))

    def forward(self, xt, t):
        h = torch.relu(self.conv1(xt))
        h = h + self.t_mlp(t.view(-1, 1).float() / n_steps).view(-1, h.shape[1], 1, 1, 1)
        h = torch.relu(self.conv2(h))
        return self.conv3(h)


net = TinyDenoise3D()
opt = torch.optim.Adam(net.parameters(), lr=2e-3)
for step in range(1200):
    idx = torch.randint(0, data.shape[0], (64,))
    t = torch.randint(0, n_steps, (64,))
    xt, eps = q_sample(data[idx], t)
    loss = ((net(xt, t) - eps) ** 2).mean()
    opt.zero_grad(); loss.backward(); opt.step()
print(f"[训练完成] 噪声预测 loss {loss.item():.4f}")


@torch.no_grad()
def ddim(x_start, K, t_from, seed):
    """K 步 strided DDIM, 从 t_from 出发。x_start 为初始张量(含噪样本或纯噪声)。"""
    g = torch.Generator().manual_seed(seed)
    if x_start is None:
        x = torch.randn(1, 1, T, H, W, generator=g)
    else:
        x = x_start + 0  # 已构造好的加噪样本
    ts = torch.linspace(t_from, 0, max(K, 1)).long().tolist()
    t0 = time.time()
    for i, t in enumerate(ts):
        tt = torch.full((1,), t)
        eps_pred = net(x, tt)
        x0_hat = ((x - (1 - bar_alpha[t]).sqrt() * eps_pred) / bar_alpha[t].sqrt()).clamp(-1, 2)
        if i + 1 < len(ts):
            ba_next = bar_alpha[ts[i + 1]]
            x = ba_next.sqrt() * x0_hat + (1 - ba_next).sqrt() * eps_pred
        else:
            x = x0_hat
    return x, (time.time() - t0) * 1000


def quality_gen(gen):
    """与最近训练样本的最大余弦(生成结构质量代理)。"""
    g = gen.flatten()
    best = -1
    for i in range(0, 256, 4):
        best = max(best, F.cosine_similarity(g, data[i].flatten(), dim=0).item())
    return best


test = data[torch.randperm(256)[:16]]
Ks = [1, 2, 4, 8, 16, 32]
cond_mse, gen_q, times = [], [], []
for K in Ks:
    # (1) 条件还原: 真实样本 → t=99
    mses, dts = [], []
    for i in range(16):
        x0 = test[i:i + 1]
        g = torch.Generator().manual_seed(100 + i)
        eps = torch.randn(x0.shape, generator=g)
        ba = bar_alpha[99]
        xt = ba.sqrt() * x0 + (1 - ba).sqrt() * eps
        xh, dt = ddim(xt, K, t_from=99, seed=i)
        mses.append(((xh - x0) ** 2).mean().item())
        dts.append(dt)
    cond_mse.append(sum(mses) / 16)
    times.append(sum(dts) / 16)
    # (2) 纯噪声生成
    qs = [quality_gen(ddim(None, K, t_from=n_steps - 1, seed=s)[0]) for s in range(8)]
    gen_q.append(sum(qs) / 8)
    print(f"K={K:3d} | 还原MSE {cond_mse[-1]:.4f} | 生成质量 {gen_q[-1]:.3f} | 耗时 {times[-1]:.1f}ms")

fig, axes = plt.subplots(1, 3, figsize=(13, 4))
axes[0].plot(Ks, cond_mse, 'o-', color='#369')
axes[0].set_xlabel('采样步数 K'); axes[0].set_ylabel('还原 MSE')
axes[0].set_title('条件还原: K=1,2 极端少步明显崩塌\nK≥4 的 DDIM 中段稳健')
axes[0].set_xscale('log', base=2); axes[0].grid(ls=':')
axes[1].plot(Ks, gen_q, 's-', color='#4c9')
axes[1].set_xlabel('采样步数 K'); axes[1].set_ylabel('生成质量(最大余弦)')
axes[1].set_title('纯噪声生成: 同样在极端少步崩塌\n(弱模型+长链还有误差累积, 见K=32)')
axes[1].set_xscale('log', base=2); axes[1].grid(ls=':')
axes[2].plot(Ks, times, '^-', color='#c66')
axes[2].set_xlabel('采样步数 K'); axes[2].set_ylabel('耗时 (ms)')
axes[2].set_title('延迟 ∝ K —— 交互场景必须压步数')
axes[2].set_xscale('log', base=2); axes[2].grid(ls=':')
plt.suptitle('E08 · 步数消融: 极端少步崩塌 + 中段稳健 → 蒸馏[CausVid]专攻极端少步区间', fontweight='bold')
plt.tight_layout(); plt.savefig('E08_step_ablation.png', dpi=110, bbox_inches='tight')
print("\n[输出] E08_step_ablation.png")
