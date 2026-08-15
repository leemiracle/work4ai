"""
09_encodec_rvq.py
=================
EnCodec (Meta 2023) 的核心：Residual Vector Quantization (RVQ)。

为什么需要它：
- LLM 需要 token，但音频是连续波形
- 单一 VQ 表达能力有限
- RVQ 用多级 codebook 残差堆叠：第一个 codebook 编主要信息，
  第二个编残差，第三个编更细的残差……
- 推理时按码率选择用几个 codebook（1.5-24 kbps 可调）

本文件实现一个简化版 RVQ，并可视化残差逐步减小的过程。
依赖：numpy, torch（用 torch.nn.Parameter 简化 codebook 学习）
"""
import numpy as np
import torch
import torch.nn as nn


class VectorQuantizer(nn.Module):
    """单个 VQ codebook"""
    def __init__(self, dim, n_codes=512, beta=0.25):
        super().__init__()
        self.dim = dim
        self.n_codes = n_codes
        self.beta = beta  # commitment loss 权重
        self.codebook = nn.Parameter(torch.randn(n_codes, dim) * 0.1)

    def forward(self, x):
        # x: [B, dim]
        # 找最近邻
        dist = torch.cdist(x.unsqueeze(0), self.codebook.unsqueeze(0)).squeeze(0)
        idx = dist.argmin(dim=1)
        quantized = self.codebook[idx]
        # straight-through estimator：前向用 quantized，反向传给 x
        commit_loss = torch.mean((x - quantized.detach()) ** 2)
        codebook_loss = torch.mean((quantized - x.detach()) ** 2)
        loss = codebook_loss + self.beta * commit_loss
        quantized = x + (quantized - x).detach()
        return quantized, idx, loss


class RVQ(nn.Module):
    """
    Residual Vector Quantization：多级残差量化。
    每一级量化上一级的残差。
    """
    def __init__(self, dim, n_levels=4, n_codes=512):
        super().__init__()
        self.levels = nn.ModuleList([
            VectorQuantizer(dim, n_codes) for _ in range(n_levels)
        ])

    def forward(self, x):
        """
        x: [B, dim]
        返回: (quantized_sum, [indices per level], total_loss)
        """
        residual = x
        total_q = torch.zeros_like(x)
        all_idx = []
        total_loss = 0
        for level in self.levels:
            q, idx, loss = level(residual)
            total_q = total_q + q
            residual = residual - q  # 残差
            all_idx.append(idx)
            total_loss = total_loss + loss
        return total_q, all_idx, total_loss


def demo_rvq_progressive():
    """演示 RVQ 多级逐步逼近"""
    torch.manual_seed(42)
    np.random.seed(42)

    dim = 32
    n_levels = 6
    rvq = RVQ(dim, n_levels=n_levels, n_codes=128)

    # 训练数据：随机连续向量（模拟音频 latent）
    X = torch.randn(1000, dim)

    # 训练 codebook
    opt = torch.optim.Adam(rvq.parameters(), lr=1e-2)
    print("[训练] 在 1000 个 32 维向量上训练 RVQ 6 级 codebook...")
    for epoch in range(500):
        opt.zero_grad()
        q, idx, loss = rvq(X)
        loss.backward()
        opt.step()
        if epoch % 100 == 0:
            with torch.no_grad():
                err = ((X - q) ** 2).mean().item()
            print(f"  epoch {epoch}: recon MSE = {err:.4f}")

    # 演示：用 1, 2, ..., 6 级 codebook 重建的误差
    print("\n[RVQ 渐进码率] 用 1-N 级 codebook 重建误差：")
    with torch.no_grad():
        residual = X
        cumul_q = torch.zeros_like(X)
        for i, level in enumerate(rvq.levels):
            q, idx, _ = level(residual)
            cumul_q = cumul_q + q
            residual = residual - q
            err = ((X - cumul_q) ** 2).mean().item()
            # 每级用 log2(128) = 7 bits/frame 表示
            bitrate_per_level = (i + 1) * 7
            print(f"  级数 {i+1}: bits/frame={bitrate_per_level:>3}  recon MSE={err:.4f}")

    print("\n  → 级数越多，码率越高，重建越准")
    print("  → 这就是 EnCodec 在 1.5-24 kbps 之间灵活切换的原理")
    print("  → 也是 Suno/Udio/Jasco 等音频 LLM 用'多码本自回归'的根基")


if __name__ == "__main__":
    demo_rvq_progressive()
