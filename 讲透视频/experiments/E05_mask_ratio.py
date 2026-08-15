"""
E05 解答 · VideoMAE 掩码率消融: 为什么视频能遮 90%
====================================================
假设: 视频时空冗余高 → 即使只可见 10% tubelet, 也能推断被遮内容。
对照: 把视频换成无冗余的"噪声视频" → 高掩码率必然失败。

实现: tubelet 化(2,4,4) → 随机遮 r → 小 MLP 从可见 tubelet 值
      重建全部 tubelet 值(loss 只算被遮处)。

运行: python3 E05_mask_ratio.py    # 约 20 秒
输出: E05_mask_ratio.png
"""
import torch
torch.set_num_threads(1)
torch.manual_seed(0)
import torch.nn as nn
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ---------- 造"结构化视频"(移动方块) ----------
def make_video(dx=1):
    v = torch.zeros(8, 16, 16)
    for t in range(8):
        cx = (4 + dx * t) % 16
        v[t, 6:9, cx:cx + 3] = 1.0
    return v

videos = torch.stack([make_video(dx=d) for d in [-1, 0, 1]] * 40)  # (120,8,16,16)
noise_videos = torch.rand_like(videos)  # 无冗余对照

def tubeletize(v):  # (B,8,16,16) -> (B, 4*4*4=64) 每 tubelet 均值
    B = v.shape[0]
    v = v.view(B, 4, 2, 4, 4, 4, 4)      # (B,T',t,H',h,W',w)
    return v.mean(dim=(2, 4, 6)).reshape(B, -1)

data_struct = tubeletize(videos)
data_noise = tubeletize(noise_videos)
N_TOK = data_struct.shape[1]  # 64

class Reconstructor(nn.Module):
    def __init__(self, d=64):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(N_TOK, 128), nn.ReLU(),
                                 nn.Linear(128, 128), nn.ReLU(),
                                 nn.Linear(128, N_TOK))
    def forward(self, x):
        return self.net(x)

def run(data, ratio, steps=300):
    model = Reconstructor()
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    n_vis = max(1, int(N_TOK * (1 - ratio)))
    losses = []
    for s in range(steps):
        idx = torch.randint(0, data.shape[0], (32,))
        x = data[idx]
        # 随机遮: 可见处保留原值, 被遮处置 0
        vis = torch.zeros(32, N_TOK).bernoulli_(p=1 - ratio)
        vis[:, :n_vis] = 1  # 保证至少 n_vis 个可见(简化: 前 n_vis 恒可见)
        x_in = x * vis
        pred = model(x_in)
        loss = ((pred - x).pow(2) * (1 - vis)).sum() / (1 - vis).sum().clamp(min=1)
        opt.zero_grad(); loss.backward(); opt.step()
        losses.append(loss.item())
    return losses

ratios = [0.6, 0.75, 0.9]
results = {}
for name, data in [('结构化视频(冗余)', data_struct), ('噪声视频(无冗余)', data_noise)]:
    for r in ratios:
        L = run(data, r)
        results[(name, r)] = L[-1]
        print(f"[{name}] mask={r:.0%}  最终loss={L[-1]:.4f}  (初始{L[0]:.4f})")

# 结构化视频数据方差(归一化基准)
var_s, var_n = data_struct.var().item(), data_noise.var().item()
print(f"\n[数据方差] 结构化 {var_s:.4f} vs 噪声 {var_n:.4f}")

fig, ax = plt.subplots(figsize=(8.5, 4.2))
w = 0.35
xs = range(len(ratios))
struct_vals = [results[('结构化视频(冗余)', r)] for r in ratios]
noise_vals = [results[('噪声视频(无冗余)', r)] for r in ratios]
ax.bar([i - w / 2 for i in xs], struct_vals, w, label='结构化视频(时空冗余)', color='#4c9')
ax.bar([i + w / 2 for i in xs], noise_vals, w, label='噪声视频(无冗余)', color='#c66')
ax.set_xticks(list(xs)); ax.set_xticklabels([f'{r:.0%}' for r in ratios])
ax.set_xlabel('掩码率'); ax.set_ylabel('被遮 tubelet 重建 MSE')
ax.set_title('E05 · 冗余让高掩码率可学: 结构化视频 90% 遮罩仍低误差\n噪声视频任何掩码率都失败(误差≈数据方差, 即只能猜均值)')
ax.legend()
plt.tight_layout(); plt.savefig('E05_mask_ratio.png', dpi=110, bbox_inches='tight')
print("\n[输出] E05_mask_ratio.png")
print("  → 结论: VideoMAE 遮 90% 成立的前提是视频冗余; 噪声数据高掩码=不可学。")
