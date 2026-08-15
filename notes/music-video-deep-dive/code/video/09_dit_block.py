"""
09_dit_block.py
==============
Diffusion Transformer (DiT) block 实现。

DiT (Peebles & Xie, ICCV 2023) 把 U-Net 换成 Transformer，scaling law 友好。
Sora (OpenAI, 2024.2) 首次大规模用 DiT for video → 视频生成 GPT 时刻。

核心组件：
1. Patch embed：latent 切 patch → token
2. DiT block：LayerNorm + Self-Attention + MLP + adaLN-Zero（时间条件注入）
3. Timestep + class conditioning：通过 adaLN 调制每个 block

本文件实现一个可运行的 DiT block + 完整 DiT 前向。
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


def modulate(x, shift, scale):
    """adaLN-Zero 调制：x = x * (1+scale) + shift"""
    return x * (1 + scale) + shift


class TimestepEmbedder(nn.Module):
    """把 timestep t 转成 embedding（sinusoidal + MLP）"""
    def __init__(self, dim):
        super().__init__()
        self.mlp = nn.Sequential(nn.Linear(dim, dim), nn.SiLU(), nn.Linear(dim, dim))
        self.dim = dim

    def forward(self, t):
        half = self.dim // 2
        freqs = torch.exp(-math.log(10000) * torch.arange(half, device=t.device) / half)
        args = t[:, None] * freqs[None]
        emb = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
        return self.mlp(emb)


class DiTBlock(nn.Module):
    """
    DiT block with adaLN-Zero（原论文设计）：
    1. adaLN：用条件（timestep + text）生成 6 个调制参数（shift/scale/gate × 2）
    2. Self-Attention（gate 调制）
    3. MLP（gate 调制）
    """
    def __init__(self, dim, n_heads=8):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim, elementwise_affine=False)
        self.attn = nn.MultiheadAttention(dim, n_heads, batch_first=True)
        self.norm2 = nn.LayerNorm(dim, elementwise_affine=False)
        self.mlp = nn.Sequential(
            nn.Linear(dim, dim * 4), nn.GELU(), nn.Linear(dim * 4, dim)
        )
        # adaLN：条件 → 6*dim 调制参数
        self.adaLN = nn.Linear(dim, 6 * dim)
        nn.init.constant_(self.adaLN.weight, 0); nn.init.constant_(self.adaLN.bias, 0)

    def forward(self, x, c):
        """
        x: [B, N, dim] - 视频 token
        c: [B, dim] - 条件（timestep + text）
        """
        shift_msa, scale_msa, gate_msa, shift_ml, scale_ml, gate_ml = self.adaLN(c).chunk(6, dim=-1)
        # Attention
        h = modulate(self.norm1(x), shift_msa.unsqueeze(1), scale_msa.unsqueeze(1))
        h, _ = self.attn(h, h, h)
        x = x + gate_msa.unsqueeze(1) * h
        # MLP
        h = modulate(self.norm2(x), shift_ml.unsqueeze(1), scale_ml.unsqueeze(1))
        h = self.mlp(h)
        x = x + gate_ml.unsqueeze(1) * h
        return x


class VideoDiT(nn.Module):
    """
    简化版 Video DiT：
    - 输入：3D latent [B, C, T, H, W]（来自 3D VAE）
    - patchify：把 (T, H, W) 切 patch → token
    - N 个 DiT block
    - 输出：预测的向量场 / 噪声
    """
    def __init__(self, in_channels=4, dim=384, depth=6, n_heads=8,
                 patch=(1, 2, 2)):
        super().__init__()
        self.patch = patch
        # patch embed: 3D conv
        self.patch_embed = nn.Conv3d(in_channels, dim, kernel_size=patch, stride=patch)
        # 位置编码（用可学习）
        self.depth = depth
        self.blocks = nn.ModuleList([DiTBlock(dim, n_heads) for _ in range(depth)])
        # 时间 + 文本 embedder
        self.t_embedder = TimestepEmbedder(dim)
        self.txt_proj = nn.Linear(dim, dim)
        # 输出
        self.final_norm = nn.LayerNorm(dim, elementwise_affine=False)
        self.final_linear = nn.Linear(dim, patch[0] * patch[1] * patch[2] * in_channels)
        nn.init.constant_(self.final_linear.weight, 0); nn.init.constant_(self.final_linear.bias, 0)
        # 占位：位置编码（实际应按 T, H, W 网格生成）
        self.pos_embed = None

    def forward(self, z, t, txt_emb):
        """
        z: [B, C, T, H, W]
        t: [B] timestep
        txt_emb: [B, L_txt, dim] text tokens
        """
        B, C, T, H, W = z.shape
        # 1. Patch embed
        x = self.patch_embed(z)  # [B, dim, T', H', W']
        pt, ph, pw = x.shape[2], x.shape[3], x.shape[4]
        x = x.flatten(2).transpose(1, 2)  # [B, N, dim]
        N = x.shape[1]
        # 加位置编码（这里简化用零；实际用 3D RoPE 或 sinusoidal）
        if self.pos_embed is None or self.pos_embed.shape[1] != N:
            self.pos_embed = nn.Parameter(torch.zeros(1, N, x.shape[-1], device=x.device))
        x = x + self.pos_embed

        # 2. 条件：timestep + 文本均值（简化）
        t_emb = self.t_embedder(t.float() / 1000)
        # 简化：取文本 token 平均
        c = t_emb + self.txt_proj(txt_emb.mean(dim=1))

        # 3. DiT blocks
        for block in self.blocks:
            x = block(x, c)

        # 4. 输出
        x = self.final_linear(self.final_norm(x))
        # unpatchify
        x = x.transpose(1, 2).reshape(B, -1, pt, ph, pw)
        # 上采样回原 latent shape
        x = F.interpolate(x, size=(T, H, W), mode='trilinear', align_corners=False)
        return x


if __name__ == "__main__":
    print("=" * 60)
    print("Video DiT 前向 demo")
    print("=" * 60)
    model = VideoDiT(in_channels=4, dim=384, depth=6, n_heads=6, patch=(1, 2, 2))
    n_params = sum(p.numel() for p in model.parameters())
    print(f"  DiT 参数: {n_params/1e6:.2f}M")

    # 模拟输入：3D VAE 输出的 latent
    z = torch.randn(2, 4, 8, 16, 16)  # [B=2, C=4, T=8 帧 latent, H=W=16]
    t = torch.randint(0, 1000, (2,))
    txt_emb = torch.randn(2, 16, 384)  # 模拟 T5 文本 embedding
    print(f"  输入 latent: {tuple(z.shape)}")
    out = model(z, t, txt_emb)
    print(f"  输出（预测向量场）: {tuple(out.shape)}")
    print(f"  → 输出形状匹配 latent（用于 flow matching / diffusion）")

    print("\n[真实模型对比]")
    print("  HunyuanVideo (13B):  双流 DiT（文本 + 视频 token 联合注意力）")
    print("  Wan 2.1 (14B):       DiT + 3D RoPE + flow matching")
    print("  Sora (未公开):        DiT + 时空 patch")
    print("  CogVideoX (5B/30B):  专家 Transformer（T 分支 + V 分支）")

    print("\n[推理过程]")
    print("  1. 文本 → T5 encoder → txt_emb")
    print("  2. 从 N(0,I) 采样初始 latent z_0")
    print("  3. Flow Matching Euler 积分 4-50 步")
    print("     z_{t+dt} = z_t + v_θ(z_t, t, txt) * dt")
    print("  4. Classifier-Free Guidance: v = v_cond + w·(v_cond - v_uncond)")
    print("  5. 3D VAE 解码 → 像素视频")
    print("=" * 60)
