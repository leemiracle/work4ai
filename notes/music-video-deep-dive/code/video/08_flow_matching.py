"""
08_flow_matching.py
===================
Flow Matching / Rectified Flow：取代 DDPM 的最新生成范式。

为什么用 Flow Matching：
- DDPM 推理需要 50-1000 步去噪（慢）
- Flow Matching 直接学一个向量场，把噪声"沿直线"流到数据
- 训练更稳、推理更快（rectified flow 几步即可）
- 所有 2024-2025 主流视频模型用：Stable Diffusion 3、Wan、HunyuanVideo

数学：
    给定噪声 z_0 ~ N(0, I) 和数据 z_1
    定义 z_t = (1-t)·z_0 + t·z_1,  t ∈ [0, 1]
    目标向量场 v(z_t, t) = z_1 - z_0
    训练：网络 v_θ 预测这个向量场
    推理：从 z_0 用 Euler 法积分到 z_1
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleFlowNet(nn.Module):
    """演示用的小型向量场网络（实际视频模型是 DiT）"""
    def __init__(self, dim, hidden=128, cond_dim=64):
        super().__init__()
        self.time_mlp = nn.Sequential(nn.Linear(1, hidden), nn.SiLU(), nn.Linear(hidden, hidden))
        self.cond_mlp = nn.Sequential(nn.Linear(cond_dim, hidden), nn.SiLU(), nn.Linear(hidden, hidden))
        self.net = nn.Sequential(
            nn.Linear(dim + hidden * 2, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, dim)
        )

    def forward(self, z, t, cond):
        # z: [B, dim], t: [B, 1], cond: [B, cond_dim]
        t_emb = self.time_mlp(t)
        c_emb = self.cond_mlp(cond)
        h = torch.cat([z, t_emb, c_emb], dim=-1)
        return self.net(h)


def flow_matching_loss(net, z1_data, cond):
    """
    Flow Matching 训练目标。
    z1_data: 真实数据（latent）
    cond: 条件（如文本 embedding）
    """
    B = z1_data.shape[0]
    # 1. 采样 t ~ U[0, 1]
    t = torch.rand(B, 1, device=z1_data.device)
    # 2. 采样噪声 z0 ~ N(0, I)
    z0 = torch.randn_like(z1_data)
    # 3. 插值 z_t = (1-t) z0 + t z1
    z_t = (1 - t) * z0 + t * z1_data
    # 4. 目标向量场 = z1 - z0
    target_v = z1_data - z0
    # 5. 网络预测
    pred_v = net(z_t, t, cond)
    # 6. MSE loss
    return F.mse_loss(pred_v, target_v)


@torch.no_grad()
def flow_matching_sample(net, cond, dim, n_steps=10, schedule="linear"):
    """
    Flow Matching 推理：从 z_0 ~ N(0,I) 用 Euler 法积分到 z_1。
    rectified flow 的关键：少步数即可（10 步就够）。
    """
    B = cond.shape[0]
    z = torch.randn(B, dim, device=cond.device)  # z_0
    # 时间步调度
    if schedule == "linear":
        ts = torch.linspace(0, 1, n_steps + 1, device=cond.device)
    elif schedule == "cosine":  # 更细在 t 接近 1
        ts = 1 - torch.cos(torch.linspace(0, 1, n_steps + 1, device=cond.device) * torch.pi / 2)
    # Euler 积分
    for i in range(n_steps):
        t_now = ts[i:i+1].expand(B, 1)
        v = net(z, t_now, cond)
        dt = ts[i+1] - ts[i]
        z = z + v * dt  # Euler step
    return z  # z_1 ≈ 数据


def make_synthetic_dataset(n=512, dim=16, cond_dim=8):
    """合成一个简单的"模态"数据：每个条件对应一个高斯中心"""
    torch.manual_seed(0)
    centers = torch.randn(8, dim) * 3  # 8 个模态中心
    conds = torch.eye(8)
    data = []
    conds_list = []
    for _ in range(n):
        i = torch.randint(0, 8, (1,)).item()
        z = centers[i] + torch.randn(dim) * 0.3
        data.append(z)
        conds_list.append(conds[i])
    return torch.stack(data), torch.stack(conds_list)


if __name__ == "__main__":
    print("=" * 60)
    print("Flow Matching 训练 + 采样 demo")
    print("=" * 60)

    dim, cond_dim = 16, 8
    net = SimpleFlowNet(dim, cond_dim=cond_dim)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)

    data, conds = make_synthetic_dataset(n=512, dim=dim, cond_dim=cond_dim)
    print(f"  数据集: {len(data)} 样本, dim={dim}")

    # 训练
    print("\n[训练] Flow Matching...")
    for epoch in range(500):
        idx = torch.randperm(len(data))
        for i in range(0, len(data), 64):
            b_idx = idx[i:i+64]
            loss = flow_matching_loss(net, data[b_idx], conds[b_idx])
            opt.zero_grad(); loss.backward(); opt.step()
        if epoch % 100 == 0:
            print(f"  epoch {epoch}: loss = {loss.item():.4f}")

    # 采样：对每个条件生成 100 个样本，看是否落到对应模态
    print("\n[采样] 每个条件 10 步 Euler...")
    net.eval()
    n_per_cond = 50
    test_cond = torch.eye(8).repeat_interleave(n_per_cond, dim=0)
    samples = flow_matching_sample(net, test_cond, dim, n_steps=10)

    # 检查：每个条件生成的样本均值是否接近对应模态中心
    centers = make_synthetic_dataset(dim=dim, cond_dim=cond_dim)[0].reshape(-1, 8, dim).mean(dim=0)
    # 重新拿模态中心
    torch.manual_seed(0)
    centers_true = torch.randn(8, dim) * 3
    print("\n  每条件生成样本均值 vs 真实中心（前 4 维）：")
    for i in range(8):
        gen_mean = samples[i*n_per_cond:(i+1)*n_per_cond].mean(0)
        true_c = centers_true[i]
        err = (gen_mean - true_c).norm().item()
        print(f"    cond {i}: err = {err:.3f}")

    print("\n" + "=" * 60)
    print("真实视频模型用：")
    print("  - DiT 作为 net（不是 MLP）")
    print("  - cond = T5 文本 embedding")
    print("  - z = 3D VAE latent")
    print("  - 加 Classifier-Free Guidance:")
    print("    v_guided = v_cond + w·(v_cond - v_uncond)")
    print("  - rectified flow: 通过'拉直'轨迹让 4 步采样即可")
    print("=" * 60)
