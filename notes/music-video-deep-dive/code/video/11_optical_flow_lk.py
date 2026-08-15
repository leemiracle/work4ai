"""
11_optical_flow_lk.py
=====================
经典 CV：Lucas-Kanade 光流（1981）。

光流 = 两帧之间每个像素的运动向量。
- Lucas-Kanade: 局部窗口假设流恒定，用最小二乘解
- 是所有现代光流（RAFT, GMFlow）的基础
- 在视频编码里和"运动估计"是同一件事的两种视角

也实现 Horn-Schunck（全局变分）对比。
"""
import numpy as np


def lucas_kanade(I1, I2, window=15):
    """
    Lucas-Kanade 光流。
    假设：在 window×window 窗口内，所有像素有相同的 (u, v)。
    解：A^T A [u; v] = A^T b（最小二乘）

    I1, I2: [H, W] 灰度图，float
    返回: U, V [H, W] 每个 pixel 的 (u, v)
    """
    # 梯度
    Ix = np.gradient(I1, axis=1)
    Iy = np.gradient(I1, axis=0)
    It = I2 - I1

    H, W = I1.shape
    U = np.zeros_like(I1)
    V = np.zeros_like(I1)

    half = window // 2
    for y in range(half, H - half):
        for x in range(half, W - half):
            # 取窗口
            ix = Ix[y-half:y+half+1, x-half:x+half+1].flatten()
            iy = Iy[y-half:y+half+1, x-half:x+half+1].flatten()
            it = It[y-half:y+half+1, x-half:x+half+1].flatten()
            # A = [ix, iy], b = -it
            A = np.stack([ix, iy], axis=1)
            b = -it
            # 最小二乘解
            try:
                ATA = A.T @ A
                if np.linalg.det(ATA) < 1e-6:
                    continue
                uv = np.linalg.solve(ATA, A.T @ b)
                U[y, x] = uv[0]
                V[y, x] = uv[1]
            except np.linalg.LinAlgError:
                continue
    return U, V


def make_moving_pattern(H=64, W=64, dx=2.0, dy=1.0):
    """合成：第二帧是第一帧平移 (dx, dy)"""
    np.random.seed(0)
    yy, xx = np.meshgrid(np.arange(H), np.arange(W), indexing='ij')
    # 平滑的随机纹理
    base = np.random.rand(H, W)
    from scipy.ndimage import gaussian_filter
    base = gaussian_filter(base, 2.0)
    I1 = base.astype(np.float32)
    # 用 scipy 平移
    from scipy.ndimage import shift
    I2 = shift(I1, (dy, dx), order=1).astype(np.float32)
    return I1, I2, (dy, dx)


def evaluate_flow(U, V, true_dy, true_dx):
    """评估估计精度（在有估计的区域）"""
    mask = (np.abs(U) + np.abs(V)) > 1e-3
    if mask.sum() == 0:
        return None
    u_err = V[mask] - true_dy  # 注意 U/V 与 dx/dy 的对应
    v_err = U[mask] - true_dx
    rmse = np.sqrt(np.mean(u_err**2 + v_err**2))
    return rmse, mask.sum()


if __name__ == "__main__":
    print("=" * 60)
    print("Lucas-Kanade 光流")
    print("=" * 60)

    I1, I2, (dy, dx) = make_moving_pattern(dx=2.0, dy=1.0)
    print(f"  真值光流: dx={dx}, dy={dy}")

    print("\n[Lucas-Kanade] window=15...")
    U, V = lucas_kanade(I1, I2, window=15)
    res = evaluate_flow(U, V, dy, dx)
    if res:
        rmse, n = res
        print(f"  RMSE = {rmse:.3f} pixels (在 {n} 个有效像素上)")
        # 中位数（更稳健）
        mask = (np.abs(U) + np.abs(V)) > 1e-3
        u_med = np.median(V[mask]); v_med = np.median(U[mask])
        print(f"  中位数估计: dx={v_med:.3f}, dy={u_med:.3f}")

    print("\n[对比 window 大小]")
    for w in [7, 11, 15, 21, 31]:
        U, V = lucas_kanade(I1, I2, window=w)
        res = evaluate_flow(U, V, dy, dx)
        if res:
            rmse, n = res
            print(f"  window={w:>2}: RMSE={rmse:.3f}, 有效像素={n}")

    try:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(I1, cmap='gray'); axes[0].set_title("frame 1")
        axes[1].imshow(I2, cmap='gray'); axes[1].set_title("frame 2 (shifted)")
        # 光流场（每 4 个像素画一个箭头）
        U2, V2 = lucas_kanade(I1, I2, window=15)
        yy, xx = np.meshgrid(np.arange(64), np.arange(64), indexing='ij')
        axes[2].imshow(I1, cmap='gray', alpha=0.5)
        axes[2].quiver(xx[::4, ::4], yy[::4, ::4], U2[::4, ::4], V2[::4, ::4], color='r', scale=50)
        axes[2].set_title("optical flow (LK)")
        for ax in axes: ax.axis('off')
        plt.tight_layout(); plt.savefig("optical_flow.png", dpi=80); print("\n[saved] optical_flow.png")
    except ImportError:
        pass

    print("\n" + "=" * 60)
    print("现代光流：")
    print("  - Horn-Schunck (1981): 全局能量最小化")
    print("  - FlowNet (2015): CNN 端到端")
    print("  - RAFT (ECCV 2020): 循环 all-pairs correlation, SOTA 多年")
    print("  - GMFlow (2022): Transformer global matching")
    print("\n和视频编码的关系：")
    print("  - 视频编码的'运动估计' ≈ 光流（块级，离散 MV）")
    print("  - 光流是逐像素连续的（更细，但码率大）")
    print("  - HEVC 的 AFFINE 模式 = 介于两者之间")
    print("=" * 60)
