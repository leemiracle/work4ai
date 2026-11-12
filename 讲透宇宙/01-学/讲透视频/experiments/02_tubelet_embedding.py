"""
实验 02 · Tubelet Embedding：视频如何变成一串 token
====================================================
ViT 把图像切成 patch 再线性投影成 token。视频多一维时间，
于是把视频切成"小管子"(tubelet = t×h×w 的小立方块)，
用一个 3D 卷积一步把它变成 token。

这就是 ViViT / TimeSformer / VideoMAE 的输入层。

本实验：
  · 把 (3, 16, 224, 224) 的视频切成 tubelet
  · 展示 token 序列长度 = (T/t) × (H/h) × (W/w)
  · 可视化"一个 tubelet token 对应视频的哪一块"

运行:  python3 02_tubelet_embedding.py     # CPU 约 2 秒
输出:  exp02_tubelet.png
"""
import torch
torch.set_num_threads(1)
import torch.nn as nn
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
import matplotlib.patches as patches


# ---------- 1. 造一个带运动的合成视频 (3, T=16, H=W=64) ----------
T, H, W, C = 16, 64, 64, 3
video = torch.zeros(C, T, H, W)
for t in range(T):
    cx = 12 + t * 2          # 红方块向右移动
    cy = 32
    video[0, t, cy-4:cy+4, int(cx)-4:int(cx)+4] = 0.9   # R 通道
    bx = 48 - t              # 蓝方块向左移动
    by = 16
    video[2, t, by-4:by+4, int(bx)-4:int(bx)+4] = 0.9   # B 通道
# 转成 (1, C, T, H, W)
video = video.unsqueeze(0)


# ---------- 2. Tubelet Embedding = 3D 卷积 ----------
t_t, h_t, w_t = 2, 16, 16      # tubelet 尺寸: 时间2, 空间16
embed_dim = 192
tubelet = nn.Conv3d(C, embed_dim, kernel_size=(t_t, h_t, w_t),
                    stride=(t_t, h_t, w_t))

tokens = tubelet(video)         # (1, embed_dim, T', H', W')
Nt, Nh, Nw = tokens.shape[2], tokens.shape[3], tokens.shape[4]
seq_len = Nt * Nh * Nw
print(f"[输入] 视频 {tuple(video.shape)}  (C,T,H,W)")
print(f"[Tubelet] 尺寸 (t,h,w)=({t_t},{h_t},{w_t})")
print(f"[输出] token 网格 (T',H',W') = ({Nt},{Nh},{Nw})  →  序列长度 = {seq_len}")
print(f"[每个 token] 维度 = {embed_dim}")
print(f"  → 16×224×224 的视频若用同样设置: seq_len = (16/2)*(224/16)^2 = {8*14*14} tokens")


# ---------- 3. 可视化: 每个 token 对应视频哪一块 ----------
fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))
# 帧 0 / 帧 8 / token 网格
def to_img(t):
    return t.permute(1, 2, 0).numpy()
axes[0].imshow(to_img(video[0, :, 0])); axes[0].set_title('第 0 帧'); axes[0].axis('off')
axes[1].imshow(to_img(video[0, :, 8])); axes[1].set_title('第 8 帧(方块已移动)'); axes[1].axis('off')

ax = axes[2]
frame = to_img(video[0, :, 8]).copy()
frame[:] = frame * 0.4   # 变暗以凸显网格
ax.imshow(frame)
for i in range(Nw + 1):
    ax.axhline(i * h_t, color='lime', lw=0.8)
    ax.axvline(i * w_t, color='lime', lw=0.8)
# 标出几个 tubelet token 编号
for ih in range(Nh):
    for iw in range(Nw):
        ax.text(iw * w_t + w_t / 2, ih * h_t + h_t / 2, f'{ih*Nw+iw}',
                color='yellow', ha='center', va='center', fontsize=7)
ax.set_title(f'Tubelet 网格 ({Nh}×{Nw}={Nh*Nw} 块/帧)\n绿格=1个token的空间范围')
ax.set_xlim(0, W); ax.set_ylim(H, 0)

plt.suptitle(f'实验02 · Tubelet Embedding: 视频→{seq_len}个token (Conv3D一步完成)', fontsize=12.5, fontweight='bold')
plt.tight_layout()
plt.savefig('exp02_tubelet.png', dpi=110, bbox_inches='tight')
print("\n[输出] exp02_tubelet.png")
