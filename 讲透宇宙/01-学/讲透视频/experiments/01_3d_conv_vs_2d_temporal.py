"""
实验 01 · 3D 卷积 vs (2D 卷积 + 时间池化)：视频建模的两条起点
================================================================
视频比图像多一个"时间"维度。最早的问题就是：
  怎么让网络"看见"运动？

两条最古老的路线：
  (A) 3D 卷积 (C3D, I3D)   —— 卷积核本身就是 (t,h,w) 的立方体，一次性扫时空
  (B) 2D 卷积 + 时间        —— 每帧用 2D 卷积，再在时间维上做池化/注意力

本实验在同一组"移动方块"合成视频上，对比两种路线：
  · 参数量
  · 感受野（能否捕捉到运动方向）
  · 对"运动方向翻转"的响应差异（3D 卷积应敏感于时间顺序）

运行:  python3 01_3d_conv_vs_2d_temporal.py     # CPU 约 5 秒
输出:  exp01_3d_vs_2d.png
"""
import torch
torch.set_num_threads(1)   # 小张量单线程更快(线程争抢>计算, 见 README)
torch.manual_seed(0)
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ---------- 1. 造一段"移动方块"视频 ----------
def make_moving_box(n_frames=16, size=32, box=6, dx=1, dy=0):
    """一个方块在画面里平移。返回 (1,1,T,H,W) 张量。"""
    v = torch.zeros(1, 1, n_frames, size, size)
    x = y = size // 2
    for t in range(n_frames):
        xx = (x + dx * t) % size
        yy = (y + dy * t) % size
        for i in range(box):
            for j in range(box):
                v[0, 0, t, (yy + j) % size, (xx + i) % size] = 1.0
    return v


def count_params(m):
    return sum(p.numel() for p in m.parameters())


# ---------- 2. 两个网络 ----------
# (A) 3D 卷积：核 (3,3,3)，天然看时间
conv3d = nn.Conv3d(1, 8, kernel_size=(3, 3, 3), padding=(1, 1, 1))
# (B) 2D 卷积：每帧独立卷积，核 (3,3)，不看时间
conv2d = nn.Conv2d(1, 8, kernel_size=(3, 3), padding=(1, 1))

p3d, p2d = count_params(conv3d), count_params(conv2d)
print(f"[参数量] 3D Conv: {p3d}   |   2D Conv: {p2d}   (3D/2D = {p3d/p2d:.1f}x)")
# 3D 核 3*3*3*8 + 8 = 224 ; 2D 核 3*3*8 + 8 = 80 ; 比值 2.8x


# ---------- 3. 对"运动方向翻转"的响应 ----------
video_fwd = make_moving_box(dx=1)                      # 向右移动
video_rev = torch.flip(make_moving_box(dx=1), dims=[2])  # 时间倒放(向左)

with torch.no_grad():
    out3d_fwd = conv3d(video_fwd)[0, 0]   # (T,H,W)
    out3d_rev = conv3d(video_rev)[0, 0]
    # 2D 每帧独立: 直接 (T,1,H,W) 输入 (干净布局, 避免 permute+reshape 混乱)
    out2d_fwd = conv2d(video_fwd[0, 0].unsqueeze(1))   # (T,8,H,W)
    out2d_rev = conv2d(video_rev[0, 0].unsqueeze(1))   # (T,8,H,W)

out3d_rev_flipped = torch.flip(out3d_rev, dims=[0])
out2d_rev_flipped = torch.flip(out2d_rev[:, 0], dims=[0])   # 取第0通道, 时间翻转
diff3d = (out3d_fwd - out3d_rev_flipped).abs().mean().item()
diff2d = (out2d_fwd[:, 0] - out2d_rev_flipped).abs().mean().item()
print(f"[顺序敏感性] 3D Conv: 正放 vs (倒放再倒) 差异 = {diff3d:.4f}  (>0: 对时间顺序敏感)")
print(f"             2D Conv: 正放 vs (倒放再倒) 差异 = {diff2d:.2e}  (≈0: 每帧独立, 无视顺序)")
print("  → 结论: 2D 卷积对运动方向'无感'; 3D 卷积因跨时间耦合而对顺序敏感。")


# ---------- 4. 画图 ----------
fig, axes = plt.subplots(2, 3, figsize=(11, 6.5))
mid = 8
axes[0, 0].imshow(video_fwd[0, 0, 0], cmap='gray'); axes[0, 0].set_title('第 0 帧'); axes[0, 0].axis('off')
axes[0, 1].imshow(video_fwd[0, 0, mid], cmap='gray'); axes[0, 1].set_title(f'第 {mid} 帧'); axes[0, 1].axis('off')
# 时间差分(像素级光流的雏形): 运动处有响应
axes[0, 2].imshow((video_fwd[0, 0, 1] - video_fwd[0, 0, 0]).abs(), cmap='inferno')
axes[0, 2].set_title('帧差 |f1-f0| (运动信号)'); axes[0, 2].axis('off')

# 3D 卷积第0通道在中间帧的激活
axes[1, 0].imshow(out3d_fwd[mid], cmap='viridis'); axes[1, 0].set_title(f'3D Conv 激活 (第{mid}帧)\n看见了"运动边缘"'); axes[1, 0].axis('off')
# 3D 卷积对正放 vs (倒放再倒)的差异图
axes[1, 1].imshow((out3d_fwd - out3d_rev_flipped).abs()[mid], cmap='magma')
axes[1, 1].set_title('3D Conv: 正放-(倒放再倒)差异\n(对时间顺序敏感)'); axes[1, 1].axis('off')
# 2D 卷积: 正放-(倒放再倒)差异(应接近全黑)
axes[1, 2].imshow((out2d_fwd[:, 0] - out2d_rev_flipped).abs()[mid], cmap='magma')
axes[1, 2].set_title('2D Conv: 正放-(倒放再倒)差异\n(全黑=每帧独立)'); axes[1, 2].axis('off')

plt.suptitle('实验01 · 3D 卷积看见运动，2D 卷积对时间无感', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('exp01_3d_vs_2d.png', dpi=110, bbox_inches='tight')
print("\n[输出] exp01_3d_vs_2d.png")
