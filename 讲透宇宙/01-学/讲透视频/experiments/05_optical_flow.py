"""
实验 05 · 光流: 视频理解的"前深度学习"基石
============================================
在深度学习之前, 怎么描述"运动"? —— 光流 (optical flow):
  对每个像素, 估计它在下一帧移动到了哪里 (dx, dy)。

经典的 Two-Stream 网络(2014)就靠两条腿:
  · 空间流: 看单帧(外观)
  · 时间流: 看预计算的光流(运动)

本实验用最经典的 Lucas-Kanade 局部法, 在合成运动上估计光流,
展示"运动 = 像素位移场"这个直觉, 并与现代"隐式运动表示"对比。

运行:  python3 05_optical_flow.py    # CPU 约 2 秒
输出:  exp05_optical_flow.png
"""
import torch
torch.set_num_threads(1)
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ---------- 1. 造两帧: 一个圆盘平移 ----------
H = W = 48
yy, xx = np.mgrid[0:H, 0:W]
cx, cy, r = 18, 24, 10
disk = ((xx - cx) ** 2 + (yy - cy) ** 2) < r ** 2
I1 = disk.astype(np.float32)
# 平移 (dx=2, dy=1)
I2 = np.zeros_like(I1)
for i in range(H):
    for j in range(W):
        ni, nj = i - 1, j - 2     # 反向映射
        if 0 <= ni < H and 0 <= nj < W:
            I2[i, j] = I1[ni, nj]
true_dx, true_dy = 2.0, 1.0

I1t = torch.from_numpy(I1)
I2t = torch.from_numpy(I2)


# ---------- 2. Lucas-Kanade: 局部最小二乘估 (dx,dy) ----------
def lucas_kanade(I1, I2, window=9):
    """亮度守恒: I2(x) ≈ I1(x - d). 一阶泰勒:
       I2 - I1 ≈ -d·∇I1  →  局部窗口内最小二乘解 d."""
    # 梯度 (用差分)
    Iy, Ix = np.gradient(I1)
    It = I2 - I1
    H_, W_ = I1.shape
    flow = np.zeros((H_, W_, 2))
    half = window // 2
    for i in range(half, H_ - half):
        for j in range(half, W_ - half):
            Ixw = Ix[i - half:i + half + 1, j - half:j + half + 1].flatten()
            Iyw = Iy[i - half:i + half + 1, j - half:j + half + 1].flatten()
            Itw = It[i - half:i + half + 1, j - half:j + half + 1].flatten()
            A = np.stack([Ixw, Iyw], axis=1)
            # 最小二乘: d = (A^T A)^-1 A^T (-It)
            ATA = A.T @ A
            if np.linalg.cond(ATA) < 1 / 1e-6:
                d = np.linalg.lstsq(A, -Itw, rcond=None)[0]
                flow[i, j] = d
    return flow


flow = lucas_kanade(I1, I2, window=9)
# 在圆盘内部取平均, 得到估计的位移
mask = disk.copy()   # 裁边后用于取均值
est_dx = flow[..., 0][disk & (flow[..., 0] != 0)].mean()
est_dy = flow[..., 1][disk & (flow[..., 1] != 0)].mean()
print(f"[真值] 位移 dx={true_dx}, dy={true_dy}")
print(f"[LK估计] dx={est_dx:.2f}, dy={est_dy:.2f}")


# ---------- 3. 画图 ----------
fig, axes = plt.subplots(1, 4, figsize=(14, 3.6))
axes[0].imshow(I1, cmap='gray'); axes[0].set_title('帧 I₁'); axes[0].axis('off')
axes[1].imshow(I2, cmap='gray'); axes[1].set_title('帧 I₂ (圆盘平移)'); axes[1].axis('off')
axes[2].imshow(It := (I2 - I1), cmap='seismic', vmin=-1, vmax=1)
axes[2].set_title('时间差分 I₂−I₁\n(运动边缘信号)'); axes[2].axis('off')

# 光流箭头
ax = axes[3]
ax.imshow(I1, cmap='gray', alpha=0.5)
step = 3
sub = flow[::step, ::step]
ys, xs = np.mgrid[0:H:step, 0:W:step]
ax.quiver(xs, ys, sub[..., 0], sub[..., 1], color='red', scale=40, width=0.006)
ax.set_title(f'Lucas-Kanade 光流\n估计 d≈({est_dx:.1f},{est_dy:.1f})')
ax.axis('off')

plt.suptitle('实验05 · 光流: 运动=像素位移场 (Two-Stream网络的时间流输入)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('exp05_optical_flow.png', dpi=110, bbox_inches='tight')
print("\n[输出] exp05_optical_flow.png")
print("  → 现代视频模型(FIM/VideoMAE)不再显式算光流, 而让网络隐式学到运动表示。")
