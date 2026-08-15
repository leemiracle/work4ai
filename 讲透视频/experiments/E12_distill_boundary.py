"""
E12 解答 · 蒸馏的边界: 什么时候"扩散→自回归"会失败
=====================================================
CausVid 用 teacher 的 ODE 轨迹初始化学生。该做法的隐含假设:
  噪声→数据的配对覆盖了分布的所有模态。
失败场景(合成演示): 双模态分布(两个高斯) + 轨迹太少 →
  学生回归到"条件均值" → 模式坍缩到两模态之间(哪个都不像)。

运行: python3 E12_distill_boundary.py    # 约 8 秒
输出: E12_distill_boundary.png
"""
import torch
torch.set_num_threads(1)
torch.manual_seed(0)
import torch.nn as nn
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ---------- 1. teacher 分布: 双模态 (±3, 0) ----------
def sample_teacher(n):
    mode = torch.randint(0, 2, (n,))
    centers = torch.stack([torch.where(mode == 0, -3.0, 3.0), torch.zeros(n)], 1)
    return centers + 0.4 * torch.randn(n, 2)


class Student(nn.Module):
    def __init__(self, d=64):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(2, d), nn.Tanh(),
                                 nn.Linear(d, d), nn.Tanh(),
                                 nn.Linear(d, 2))

    def forward(self, z):
        return self.net(z)


def distill(n_traj, steps=1500, lr=5e-3):
    """轨迹蒸馏(简化): z~N(0,I), x=teacher样本(配对), 学生学 z→x 回归。"""
    z = torch.randn(n_traj, 2)
    x = sample_teacher(n_traj)          # 每条"ODE轨迹"的终点
    s = Student()
    opt = torch.optim.Adam(s.parameters(), lr=lr)
    for _ in range(steps):
        # 随机重播轨迹(小数据时反复看同样的配对 → 记忆而非泛化/或平均)
        idx = torch.randint(0, n_traj, (128,))
        loss = ((s(z[idx]) - x[idx]) ** 2).sum(1).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return s


def mode_coverage(s, n=500, r=1.0):
    """采样并统计: 落在两个模态半径 r 内的比例 + 坍缩到中点(±0.75)的比例。"""
    with torch.no_grad():
        out = s(torch.randn(n, 2))
    dA = torch.norm(out - torch.tensor([-3.0, 0.0]), dim=1)
    dB = torch.norm(out - torch.tensor([3.0, 0.0]), dim=1)
    coverA = (dA < r).float().mean().item()
    coverB = (dB < r).float().mean().item()
    mid = (torch.minimum(dA, dB) > 0.75).float().mean().item()  # 离两模态都远=模式平均
    return out, coverA, coverB, mid


teacher_data = sample_teacher(1500)
print(f"{'轨迹数':<10}{'覆盖模态A':>10}{'覆盖模态B':>10}{'坍缩中点':>10}   判定")
results = []
for n_traj in [400, 60, 12]:
    s = distill(n_traj)
    out, cA, cB, mid = mode_coverage(s)
    verdict = "✅ 双模态保留" if (cA > 0.3 and cB > 0.3) else ("△ 部分覆盖" if max(cA, cB) > 0.3 else "❌ 模式坍缩")
    print(f"{n_traj:<10}{cA:>10.2f}{cB:>10.2f}{mid:>10.2f}   {verdict}")
    results.append((n_traj, out, cA, cB, mid))

fig, axes = plt.subplots(1, 4, figsize=(14, 3.5))
axes[0].scatter(teacher_data[:, 0], teacher_data[:, 1], s=8, alpha=0.5, c='k')
axes[0].set_title('Teacher 分布(双模态)')
for ax, (n, out, cA, cB, mid) in zip(axes[1:], results):
    ax.scatter(out[:, 0], out[:, 1], s=10, alpha=0.6, c='#369')
    ax.set_title(f'{n} 条轨迹\n覆盖A={cA:.2f} B={cB:.2f} 坍缩={mid:.2f}', fontsize=10)
    ax.set_xlim(-5, 5); ax.set_ylim(-2, 2)
plt.suptitle('E12 · 蒸馏失败边界: 轨迹不足 → 学生回归到条件均值 → 模式坍缩', fontweight='bold')
plt.tight_layout(); plt.savefig('E12_distill_boundary.png', dpi=110, bbox_inches='tight')
print("\n[输出] E12_distill_boundary.png")
print("  对应真实场景: CausVid 蒸馏视频时若 teacher 轨迹未覆盖某类运动/场景,")
print("  学生在该类上会「平均化」——生成多种运动的混合糊。")
