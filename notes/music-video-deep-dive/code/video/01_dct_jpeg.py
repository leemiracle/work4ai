"""
01_dct_jpeg.py
==============
2D DCT 是 JPEG 和所有视频编码（H.264/265/AV1）的基础变换。

核心性质：
- 自然图像的能量集中在低频（左上角）
- 量化时高频丢掉，视觉损失小

本文件实现：
1. 从零写 2D DCT-II（不依赖库）
2. JPEG 流程：DCT → 量化 → 反量化 → 重建
3. 可视化能量集中性
"""
import numpy as np


def dct_matrix(N=8):
    """构造 N×N DCT-II 正交矩阵"""
    M = np.zeros((N, N))
    for k in range(N):
        for n in range(N):
            M[k, n] = np.cos(np.pi * (2 * n + 1) * k / (2 * N))
    M *= np.sqrt(2 / N)
    M[0, :] *= 1 / np.sqrt(2)
    return M


def dct2(block, M=None):
    """2D DCT = M @ block @ M^T"""
    if M is None: M = dct_matrix(block.shape[0])
    return M @ block @ M.T


def idct2(coeffs, M=None):
    """2D IDCT"""
    if M is None: M = dct_matrix(coeffs.shape[0])
    return M.T @ coeffs @ M


def standard_jpeg_quant_table(quality=50):
    """
    JPEG 标准亮度量化表（quality=50 时的默认）。
    高频（右下）除以大数 → 高频系数被压成 0。
    """
    table = np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68, 109, 103, 77],
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99],
    ], dtype=np.float32)
    # quality 调整：quality 越大，表越小，质量越高
    if quality < 50:
        s = 5000 / quality
    else:
        s = 200 - 2 * quality
    table = np.floor((s * table + 50) / 100)
    return np.clip(table, 1, 255)


def jpeg_compress_block(block, q_table):
    """单 8×8 块的 JPEG 压缩流程"""
    # 1. level shift（-128）
    b = block - 128
    # 2. DCT
    C = dct2(b)
    # 3. 量化
    Q = np.round(C / q_table).astype(np.int32)
    return Q


def jpeg_decompress_block(Q, q_table):
    """反流程"""
    C = Q * q_table
    b = idct2(C)
    block = b + 128
    return np.clip(block, 0, 255)


if __name__ == "__main__":
    # 合成一个 8×8 块（模拟一段平滑图像区域，低频为主）
    np.random.seed(0)
    # 用低频主导的合成
    xx, yy = np.meshgrid(np.arange(8), np.arange(8))
    block = 128 + 60 * np.cos(np.pi * xx / 8) + 30 * np.cos(np.pi * yy / 4) + np.random.randn(8, 8) * 5

    # 标准 JPEG 流程
    q = standard_jpeg_quant_table(quality=50)
    Q = jpeg_compress_block(block, q)
    recon = jpeg_decompress_block(Q, q)

    mse = np.mean((block - recon) ** 2)
    nonzero = (Q != 0).sum()

    print("[2D DCT] 单 8×8 块压缩演示")
    print(f"  原始能量: {np.sum(block**2):.0f}")
    print(f"  量化后 DCT 非零系数: {nonzero}/64 ({nonzero/64*100:.0f}%)")
    print(f"  重建 MSE: {mse:.2f}（每像素误差约 {np.sqrt(mse):.1f}/255）")

    print("\n[DCT 系数矩阵（量化后）]")
    print(Q)
    print("\n  → 左上角 DC/低频非零，右下角高频为 0（能量集中性）")

    # 能量集中性验证
    C = dct2(block - 128)
    cum_energy = np.cumsum(np.sort(np.abs(C).flatten())[::-1]) / np.sum(C ** 2)
    for frac in [0.5, 0.9, 0.99]:
        k = np.searchsorted(cum_energy, frac) + 1
        print(f"  保留 {k} 个系数（共 64）即可覆盖 {frac*100:.0f}% 能量")

    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        axes[0].imshow(block, cmap='gray'); axes[0].set_title("original")
        axes[1].imshow(np.log1p(np.abs(C)), cmap='viridis'); axes[1].set_title("DCT (log |·|)")
        axes[2].imshow(recon, cmap='gray'); axes[2].set_title(f"recon (MSE={mse:.1f})")
        for ax in axes: ax.axis('off')
        plt.tight_layout(); plt.savefig("dct_demo.png", dpi=80); print("\n[saved] dct_demo.png")
    except ImportError:
        pass
