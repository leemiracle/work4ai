"""
03_chroma_subsampling.py
========================
色彩子采样（Chroma Subsampling）：视频压缩的第二大杠杆（仅次于运动补偿）。

人眼对亮度（Y）细节敏感、对色度（Cb/Cr）细节不敏感。
→ Y 全分辨率，Cb/Cr 减半（4:2:0）→ 数据量砍 50%，肉眼几乎看不出。

本文件演示：RGB → YCbCr → 4:2:0 → RGB 重建，量化失真。
"""
import numpy as np


def rgb_to_ycbcr(rgb):
    """RGB [H,W,3] → YCbCr [H,W,3]，BT.601"""
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cb = -0.168736 * R - 0.331264 * G + 0.5 * B + 128
    Cr = 0.5 * R - 0.418688 * G - 0.081312 * B + 128
    return np.stack([Y, Cb, Cr], axis=-1)


def ycbcr_to_rgb(ycbcr):
    Y, Cb, Cr = ycbbr_to_planes(ycbcr)
    Cb = Cb - 128; Cr = Cr - 128
    R = Y + 1.402 * Cr
    G = Y - 0.344136 * Cb - 0.714136 * Cr
    B = Y + 1.772 * Cb
    return np.stack([R, G, B], axis=-1)


def ycbbr_to_planes(ycbcr):
    return ycbcr[..., 0], ycbcr[..., 1], ycbcr[..., 2]


def subsample_420(ycbcr):
    """4:2:0 子采样：Cb/Cr 在水平和垂直都减半（取 2×2 平均）"""
    Y, Cb, Cr = ycbbr_to_planes(ycbcr)
    H, W = Y.shape
    # 取 2×2 平均
    Cb_sub = (Cb[0::2, 0::2] + Cb[1::2, 0::2] + Cb[0::2, 1::2] + Cb[1::2, 1::2]) / 4
    Cr_sub = (Cr[0::2, 0::2] + Cr[1::2, 0::2] + Cr[0::2, 1::2] + Cr[1::2, 1::2]) / 4
    return Y, Cb_sub, Cr_sub


def upsample_420(Y, Cb_sub, Cr_sub):
    """4:2:0 上采样（最近邻）：把 Cb/Cr 放回 Y 大小"""
    H, W = Y.shape
    Cb = np.repeat(np.repeat(Cb_sub, 2, axis=0), 2, axis=1)[:H, :W]
    Cr = np.repeat(np.repeat(Cr_sub, 2, axis=0), 2, axis=1)[:H, :W]
    return np.stack([Y, Cb, Cr], axis=-1)


def compare_subsampling(rgb):
    """端到端：RGB → YCbCr → 420 → 重建 → RGB，比较失真"""
    ycbcr = rgb_to_ycbcr(rgb)
    Y, Cb_sub, Cr_sub = subsample_420(ycbcr)
    ycbcr_recon = upsample_420(Y, Cb_sub, Cr_sub)
    rgb_recon = np.clip(ycbcr_to_rgb(ycbcr_recon), 0, 255)
    mse = np.mean((rgb - rgb_recon) ** 2)
    # 数据量对比
    H, W = Y.shape
    full = 3 * H * W
    sub420 = H * W + 2 * (H // 2) * (W // 2)  # Y + Cb + Cr
    return rgb_recon, mse, full, sub420


if __name__ == "__main__":
    # 合成一张彩色图（渐变 + 几个色块）
    H, W = 64, 64
    xx, yy = np.meshgrid(np.arange(W), np.arange(H))
    rgb = np.zeros((H, W, 3))
    rgb[..., 0] = (xx * 4) % 256  # R 渐变
    rgb[..., 1] = (yy * 4) % 256  # G 渐变
    rgb[..., 2] = ((xx + yy) * 2) % 256  # B 渐变
    # 加色块
    rgb[10:30, 10:30] = [220, 30, 30]
    rgb[40:60, 40:60] = [30, 200, 50]

    recon, mse, full, sub420 = compare_subsampling(rgb)
    print("[色彩子采样 4:2:0]")
    print(f"  原始数据量 (4:4:4): {full} bytes")
    print(f"  子采样后 (4:2:0):  {sub420} bytes")
    print(f"  节省: {(1 - sub420/full)*100:.0f}%")
    print(f"  重建 MSE: {mse:.2f}  (每通道误差约 {np.sqrt(mse):.1f}/255)")
    print(f"\n  → 砍掉一半数据，肉眼几乎看不出（人眼对色度细节天然不敏感）")
    print(f"  → 这就是所有主流视频编码（H.264/265/AV1）默认 4:2:0 的原因")

    # 也试试 4:2:2 对比（Cb/Cr 只水平减半）
    print("\n对比 4:2:2（仅水平减半，专业视频用）：")
    ycbcr = rgb_to_ycbcr(rgb)
    Y, Cb, Cr = ycbbr_to_planes(ycbcr)
    Cb_422 = Cb[:, ::2]
    Cr_422 = Cr[:, ::2]
    sub422 = H * W + 2 * H * (W // 2)
    print(f"  数据量: {sub422} bytes（节省 {(1 - sub422/full)*100:.0f}%）")

    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        axes[0].imshow(rgb.astype(np.uint8)); axes[0].set_title("original RGB")
        axes[1].imshow(recon.astype(np.uint8)); axes[1].set_title(f"4:2:0 recon (MSE={mse:.1f})")
        diff = np.abs(rgb - recon) * 3  # 放大 3 倍便于看见
        axes[2].imshow(diff.astype(np.uint8)); axes[2].set_title("|diff| × 3")
        for ax in axes: ax.axis('off')
        plt.tight_layout(); plt.savefig("chroma_subsampling.png", dpi=80); print("\n[saved] chroma_subsampling.png")
    except ImportError:
        pass
