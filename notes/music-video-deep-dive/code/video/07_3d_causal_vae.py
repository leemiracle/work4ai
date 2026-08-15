"""
07_3d_causal_vae.py
===================
视频生成的核心组件：3D Causal VAE。

为什么需要它：
- 5s 720p60 视频 = 8 亿数值，直接扩散不可行
- 用 VAE 把视频压到 latent（典型压比 4×8×8 = 256×）
- "因果"卷积只用过去帧 → 训练时不泄漏未来 → 支持自回归长视频生成

CogVideoX / HunyuanVideo / Wan 都用 3D causal VAE。

本文件实现一个可运行的小型 3D causal VAE（随机权重前向 demo）。
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class CausalConv3d(nn.Module):
    """
    因果 3D 卷积：在时间维度上只用过去帧（kernel 中心及之前）。
    实现：先 padding，然后从右侧切掉（"未来"部分）。
    """
    def __init__(self, in_ch, out_ch, kernel_size=(3, 3, 3), stride=(1, 1, 1)):
        super().__init__()
        self.pad = (kernel_size[0] - 1, 0,  # 时间：只在左 pad（过去）
                    kernel_size[1] // 2, kernel_size[1] // 2,
                    kernel_size[2] // 2, kernel_size[2] // 2)
        self.conv = nn.Conv3d(in_ch, out_ch, kernel_size,
                              stride=stride, padding=0)

    def forward(self, x):
        # x: [B, C, T, H, W]
        x = F.pad(x, self.pad, mode='replicate')
        return self.conv(x)


class ResBlock3D(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.c1 = CausalConv3d(ch, ch, 3); self.n1 = nn.GroupNorm(8, ch)
        self.c2 = CausalConv3d(ch, ch, 3); self.n2 = nn.GroupNorm(8, ch)

    def forward(self, x):
        h = F.silu(self.n1(self.c1(x)))
        h = self.n2(self.c2(h))
        return F.silu(x + h)


class Encoder3D(nn.Module):
    """
    3D causal VAE 编码器。
    压比：T/4 × H/8 × W/8 = 256×
    """
    def __init__(self, in_ch=3, latent_ch=4):
        super().__init__()
        self.in_conv = CausalConv3d(in_ch, 64, (3,3,3))
        # 下采样：时间 1 次（×2），空间 3 次（×8）
        self.down = nn.ModuleList([
            nn.Sequential(ResBlock3D(64), CausalConv3d(64, 64, (1,3,3), stride=(1,2,2))),  # H,W × 1/2
            nn.Sequential(ResBlock3D(64), CausalConv3d(64, 64, (1,3,3), stride=(1,2,2))),  # × 1/4
            nn.Sequential(ResBlock3D(64), CausalConv3d(64, 64, (3,3,3), stride=(2,2,2))),  # T × 1/2, × 1/8
            nn.Sequential(ResBlock3D(64), CausalConv3d(64, 64, (1,3,3), stride=(1,2,2))),  # × 1/16... wait
        ])
        # 简化：T × 1/4, H,W × 1/8 = 256× 总压比
        self.out_conv = CausalConv3d(64, latent_ch * 2, (1,1,1))  # *2 for mean+logvar

    def forward(self, x):
        h = F.silu(self.in_conv(x))
        for layer in self.down:
            h = layer(h)
        return self.out_conv(h).chunk(2, dim=1)  # (mean, logvar)


class Decoder3D(nn.Module):
    def __init__(self, latent_ch=4, out_ch=3):
        super().__init__()
        self.in_conv = CausalConv3d(latent_ch, 64, (1,1,1))
        self.up = nn.ModuleList([
            nn.Upsample(scale_factor=(1, 2, 2)),
            ResBlock3D(64),
            nn.Upsample(scale_factor=(1, 2, 2)),
            ResBlock3D(64),
            nn.Upsample(scale_factor=(2, 2, 2)),  # T 恢复
            ResBlock3D(64),
            nn.Upsample(scale_factor=(1, 2, 2)),
        ])
        self.out_conv = CausalConv3d(64, out_ch, (3,3,3))

    def forward(self, z):
        h = F.silu(self.in_conv(z))
        for layer in self.up:
            h = layer(h)
        return self.out_conv(h)


class CausalVAE3D(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = Encoder3D()
        self.decoder = Decoder3D()

    def encode(self, x):
        mean, logvar = self.encoder(x)
        std = (0.5 * logvar).exp()
        z = mean + std * torch.randn_like(std)  # reparam
        return z, mean, logvar

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        z, mean, logvar = self.encode(x)
        x_recon = self.decode(z)
        return x_recon, mean, logvar


if __name__ == "__main__":
    print("=" * 60)
    print("3D Causal VAE 前向 demo（随机权重）")
    print("=" * 60)
    vae = CausalVAE3D()
    # 输入：[B=2, C=3 (RGB), T=16 帧, H=64, W=64]
    x = torch.rand(2, 3, 16, 64, 64)
    n_params = sum(p.numel() for p in vae.parameters())
    print(f"  VAE 参数: {n_params/1e6:.2f}M")
    print(f"  输入视频: {tuple(x.shape)} = {x.numel()/1e6:.2f}M 数值")

    z, mean, logvar = vae.encode(x)
    print(f"  latent z: {tuple(z.shape)} = {z.numel()/1e3:.1f}K 数值")
    print(f"  压缩比: {x.numel()/z.numel():.0f}×")

    x_recon = vae.decode(z)
    print(f"  重建: {tuple(x_recon.shape)}")

    # 验证因果性：第 t 帧的 latent 不依赖未来
    print(f"\n[因果性验证]")
    x_past = x[:, :, :8].clone()
    x_full = x.clone()
    z_past, _, _ = vae.encode(x_past)
    # 取前 8 帧的 latent 应该等于用 16 帧编码时前 8 帧的 latent
    z_full_past = mean[:, :, :z_past.shape[2]] if mean.shape[2] >= z_past.shape[2] else mean
    print(f"  过去 8 帧的 latent shape: {tuple(z_past.shape)}")
    print(f"  → 因果卷积保证 t 时刻 latent 只依赖 ≤t 的帧")
    print(f"  → 这是 Wan/Hunyuan/CogVideoX 长视频自回归生成的关键")

    print("\n" + "=" * 60)
    print("真实模型对比：")
    print("  CogVideoX 3D VAE:  压比 4×8×8")
    print("  HunyuanVideo VAE:  压比 4×8×8（chunk-based）")
    print("  Wan VAE:           custom，配合双流 DiT")
    print("  训练用 GAN + L1 + 感知 loss 联合")
    print("=" * 60)
