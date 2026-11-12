"""
实验 03 · 因子化的时空注意力：视频 Transformer 的核心算子
==========================================================
视频 token = (空间位置 × 时间位置)。全时空注意力复杂度 O((THW)^2),
对 16×16×16=4096 token 就是 1600 万对, 吃不消。

解决: 因子化 (factorised)
  · 空间注意力: 帧内, token 只 attend 同帧 HW 个 → O(T·(HW)^2)
  · 时间注意力: 同位置跨 T 帧 → O(HW·T^2)

这是 ViViT "Factorised Encoder" / TimeSformer "Divided Space-Time" 的本质。

本实验对比三种注意力的 FLOPs(解析公式) 与小规模实测耗时。
运行:  python3 03_temporal_attention.py    # CPU 约 5 秒
输出:  exp03_temporal_attention.png
"""
import torch
torch.set_num_threads(1)
torch.manual_seed(0)
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
import time

D = 384
HEADS = 4
HS = D // HEADS


# ---------- 1. FLOPs 解析公式 (无需运行重型注意力) ----------
def flops_joint(T, H, W, B=1):
    N = T * H * W
    return B * HEADS * N * N * HS * 2     # qk@ + attn@v

def flops_factorised(T, H, W, B=1):
    sp = B * HEADS * T * (H * W) * (H * W) * HS * 2   # 空间
    tp = B * HEADS * (H * W) * T * T * HS * 2          # 时间
    return sp + tp

def flops_spatial(T, H, W, B=1):
    return B * HEADS * T * (H * W) * (H * W) * HS * 2   # 只帧内


print(f"{'规模(T×H×W)':<18}{'全时空 GFLOP':>14}{'因子化 GFLOP':>15}{'纯空间 GFLOP':>14}{'加速比':>8}")
results = []
configs = [(4, 8, 8), (8, 14, 14), (16, 16, 16), (16, 22, 22), (32, 16, 16)]
for (T, H, W) in configs:
    N = T * H * W
    fj, ff, fs = flops_joint(T, H, W), flops_factorised(T, H, W), flops_spatial(T, H, W)
    print(f"{f'{T}×{H}×{W}={N:<6}':<18}{fj/1e9:>14.3f}{ff/1e9:>15.4f}{fs/1e9:>14.4f}{fj/max(ff,1):>8.1f}x")
    results.append((N, fj/1e9, ff/1e9))


# ---------- 2. 真实小规模实现 + 实测 (仅 8×8×8) ----------
def joint_attn(x, T, H, W):
    B, N, D = x.shape
    q = x.reshape(B, N, HEADS, HS).transpose(1, 2)
    attn = (q @ q.transpose(-2, -1)) / HS ** 0.5
    out = (F.softmax(attn, dim=-1) @ q).transpose(1, 2).reshape(B, N, D)
    return out

def factorised_attn(x, T, H, W):
    B, _, D = x.shape
    xs = x.reshape(B, T, H * W, D)
    q = xs.reshape(B, T, H * W, HEADS, HS).permute(0, 3, 1, 2, 4)
    attn = F.softmax((q @ q.transpose(-2, -1)) / HS ** 0.5, dim=-1)
    xs = (attn @ q).permute(0, 2, 3, 1, 4).reshape(B, T, H * W, D)
    xt = xs.reshape(B, H * W, T, D).permute(0, 2, 1, 3)
    q = xt.reshape(B, T, H * W, HEADS, HS).permute(0, 3, 1, 2, 4)
    attn = F.softmax((q @ q.transpose(-2, -1)) / HS ** 0.5, dim=-1)
    out = (attn @ q).permute(0, 2, 3, 1, 4).reshape(B, T, H * W, D)
    return out.reshape(B, T * H * W, D)


T, H, W = 8, 8, 8
x = torch.randn(16, T * H * W, D)


def bench(fn, n=30):
    fn(x.clone(), T, H, W)
    t = time.time()
    for _ in range(n):
        fn(x.clone(), T, H, W)
    return (time.time() - t) / n * 1000


tj = bench(joint_attn)
tf = bench(factorised_attn)
print(f"\n[实测耗时 8×8×8, batch=16] 全时空 {tj:.2f}ms  |  因子化 {tf:.2f}ms  |  加速 {tj/tf:.1f}x")


# ---------- 3. 画图 ----------
results = np.array(results)
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
ax = axes[0]
ax.loglog(results[:, 0], results[:, 1], 'o-', lw=2, ms=8, label='全时空 Joint  $O((THW)^2)$')
ax.loglog(results[:, 0], results[:, 2], 's-', lw=2, ms=8, label='因子化 Factorised  $O(T(HW)^2{+}HWT^2)$')
ax.set_xlabel('token 数 N = T×H×W')
ax.set_ylabel('单层注意力 GFLOP (batch=1)')
ax.set_title('复杂度: 因子化随 N 增长远慢于全注意力')
ax.legend(); ax.grid(True, which='both', ls=':')

ax = axes[1]; ax.axis('off')
txt = (
    "三种注意力的'谁看谁' (●=有连接)\n\n"
    "全时空 Joint  (N×N):\n"
    "  每个 token 看所有 token\n"
    "  → 任意两帧两位置直接耦合\n"
    "  但 $O(N^2)$, N=4096 已 1600万对\n\n"
    "因子化 Factorised (ViViT/TimeSformer):\n"
    "  第1层 帧内 (T 个 HW×HW) → 学空间结构\n"
    "  第2层 跨帧 (HW 个 T×T)  → 学运动时序\n"
    "  → 跨帧耦合需'两跳', 省 ~T 倍\n\n"
    "纯空间 Spatial-only:\n"
    "  完全不跨帧(等价图像ViT), 看不到运动\n"
)
ax.text(0.02, 0.5, txt, fontsize=10.5, family='monospace', va='center',
        bbox=dict(boxstyle='round', fc='#f5f5f5'))

plt.suptitle(f'实验03 · 因子化时空注意力: 用 ~1/T 的代价换来跨帧能力 (实测 {tj/tf:.1f}x)',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('exp03_temporal_attention.png', dpi=110, bbox_inches='tight')
print("\n[输出] exp03_temporal_attention.png")
