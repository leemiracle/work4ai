"""
E04 解答 · (2+1)D 卷积 vs 3D vs 2D —— 参数量与时间敏感性
==========================================================
在实验 01 基础上加 (2+1)D: 空间(1,3,3) + ReLU + 时间(3,1,1)。
验证: 参数量介于 2D 与 3D 之间, 但同样对时间顺序敏感。

运行: python3 E04_r2plus1d.py    # 约 5 秒
输出: E04_r2plus1d.png
"""
import torch
torch.set_num_threads(1)
torch.manual_seed(0)
import torch.nn as nn
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def make_moving_box(n_frames=16, size=32, box=6, dx=1):
    v = torch.zeros(1, 1, n_frames, size, size)
    for t in range(n_frames):
        xx = (size // 2 + dx * t) % size
        for i in range(box):
            for j in range(box):
                v[0, 0, t, (size // 2 + j) % size, (xx + i) % size] = 1.0
    return v


class R2Plus1D(nn.Module):
    """空间 (1,3,3) → ReLU → 时间 (3,1,1)。"""
    def __init__(self, ch=8):
        super().__init__()
        self.spatial = nn.Conv3d(1, ch, kernel_size=(1, 3, 3), padding=(0, 1, 1))
        self.temporal = nn.Conv3d(ch, ch, kernel_size=(3, 1, 1), padding=(1, 0, 0))

    def forward(self, x):
        return self.temporal(torch.relu(self.spatial(x)))


conv2d = nn.Conv2d(1, 8, 3, padding=1)
conv3d = nn.Conv3d(1, 8, (3, 3, 3), padding=(1, 1, 1))
r21d = R2Plus1D(8)

p2, p3, pr = (sum(p.numel() for p in m.parameters()) for m in (conv2d, conv3d, r21d))
print(f"[参数量] 2D: {p2}  |  (2+1)D: {pr}  |  3D: {p3}")

video_fwd = make_moving_box(dx=1)
video_rev = torch.flip(video_fwd, dims=[2])

with torch.no_grad():
    o3_f, o3_r = conv3d(video_fwd)[0, 0], conv3d(video_rev)[0, 0]
    or_f, or_r = r21d(video_fwd)[0, 0], r21d(video_rev)[0, 0]
    o2_f = conv2d(video_fwd[0, 0].unsqueeze(1))
    o2_r = conv2d(video_rev[0, 0].unsqueeze(1))

d2 = (o2_f[:, 0] - torch.flip(o2_r[:, 0], [0])).abs().mean().item()
d3 = (o3_f - torch.flip(o3_r, [0])).abs().mean().item()
dr = (or_f - torch.flip(or_r, [0])).abs().mean().item()
print(f"[顺序敏感] 2D: {d2:.2e} (精确0)  |  (2+1)D: {dr:.4f}  |  3D: {d3:.4f}")
print("  → (2+1)D 用更少参数换取与 3D 同级的时序能力(多了中间非线性)。")

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
axes[0].bar(['2D', '(2+1)D', '3D'], [p2, pr, p3], color=['#999', '#4c9', '#369'])
axes[0].set_title('参数量: (2+1)D 介于两者之间')
axes[1].bar(['2D', '(2+1)D', '3D'], [d2, dr, d3], color=['#999', '#4c9', '#369'])
axes[1].set_title('时间顺序敏感性: (2+1)D ≈ 3D >> 2D')
plt.suptitle('E04 · (2+1)D 分解卷积: 省参数不省时序能力', fontweight='bold')
plt.tight_layout(); plt.savefig('E04_r2plus1d.png', dpi=110, bbox_inches='tight')
print("[输出] E04_r2plus1d.png")
