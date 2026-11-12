"""
E10 解答 · 真伪世界模型判别: L5 反事实测试(合成演示)
=====================================================
构造两个"视频世界模型"(合成):
  A. 物理模型: 参数化仿真器 y_{t+1}=y_t+v_t·dt, v←v-g·dt (g 可条件化)
  B. 查表模型: 从"地球重力训练库"检索最相似场景, 返回库存轨迹(无视 g)

L5 反事实测试: 命令 g=1.62 (月球)。真世界模型应产生慢速抛体;
查表模型会返回地球轨迹 → 与月球真值发散。

运行: python3 E10_counterfactual.py    # 约 2 秒
输出: E10_counterfactual.png
"""
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def simulate(g, v0y=8.0, v0x=3.0, n=60, dt=0.03, y0=0.1, floor=0.0, rest=0.6):
    """带地面反弹的抛体仿真。返回 (x, y) 轨迹。"""
    x, y = [0.0], [y0]
    vx, vy = v0x, v0y
    for _ in range(n - 1):
        vy -= g * dt
        nx, ny = x[-1] + vx * dt, y[-1] + vy * dt
        if ny < floor:            # 反弹
            ny = floor + (floor - ny)
            vy = -vy * rest
        x.append(nx); y.append(ny)
    return np.array(x), np.array(y)


class PhysicsModel:
    """真世界模型(假设): 内部有可条件化的物理。"""
    def __init__(self):
        self.name = "物理模型"
    def rollout(self, g, v0y=8.0):
        return simulate(g, v0y=v0y)

class LookupModel:
    """伪世界模型: 检索训练库(全部地球重力 g=9.8), 返回最近轨迹。"""
    def __init__(self):
        self.name = "查表模型"
        self.lib = [simulate(9.8, v0y=v) for v in np.linspace(5, 11, 13)]  # 地球库
    def rollout(self, g, v0y=8.0):
        query = simulate(1.62, v0y=v0y)  # 无论 g 是多少, 只会匹配形状最像的地球轨迹
        qy = query[1]
        best, bd = None, 1e9
        for (lx, ly) in self.lib:
            d = np.linalg.norm(ly[:len(qy)] - qy)
            if d < bd:
                bd, best = d, (lx, ly)
        return best


G_MOON = 1.62
gt = simulate(G_MOON)                    # 月球真值
pm, lm = PhysicsModel(), LookupModel()
pa = pm.rollout(G_MOON)
lb = lm.rollout(G_MOON)

def div(traj, ref):
    return np.linalg.norm(traj[1][:len(ref[1])] - ref[1]) / len(ref[1])

print(f"[L5 反事实测试] 命令: g = {G_MOON} (月球重力), 初速 v0y=8")
print(f"  月球真值: 峰高 {gt[1].max():.2f}, 反弹 {np.sum(np.diff(gt[1]) > 0)} 次变向")
print(f"  物理模型 rollout: 峰高 {pa[1].max():.2f}  → 与真值平均偏差 {div(pa, gt):.3f}")
print(f"  查表模型 rollout: 峰高 {lb[1].max():.2f}  → 与真值平均偏差 {div(lb, gt):.3f}")
thr = 0.15
print(f"\n  判定(阈值 {thr}): 物理模型 {'✅ 通过 L5' if div(pa, gt) < thr else '❌'}  |  查表模型 {'✅' if div(lb, gt) < thr else '❌ 未通过 L5 —— 只是模式匹配'}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(gt[0], gt[1], 'k-', lw=2, label='月球真值 (g=1.62)')
axes[0].plot(pa[0], pa[1], 'g--', lw=1.5, label=f'物理模型 (偏差{div(pa, gt):.3f})')
axes[0].plot(lb[0], lb[1], 'r:', lw=1.5, label=f'查表模型 (偏差{div(lb, gt):.3f})')
axes[0].set_xlabel('x'); axes[0].set_ylabel('y')
axes[0].set_title('L5 反事实: 命令 g=月球重力')
axes[0].legend(fontsize=9)
axes[1].bar(['物理模型', '查表模型'], [div(pa, gt), div(lb, gt)], color=['#4c9', '#c66'])
axes[1].axhline(thr, ls='--', c='k'); axes[1].text(0.5, thr + 0.01, '判定阈值', fontsize=9)
axes[1].set_ylabel('与月球真值的平均偏差')
axes[1].set_title('反事实偏差: 查表模型无法条件化 g')
plt.suptitle('E10 · 真伪世界模型判别实验 (L5 反事实, 合成演示)', fontweight='bold')
plt.tight_layout(); plt.savefig('E10_counterfactual.png', dpi=110, bbox_inches='tight')
print("\n[输出] E10_counterfactual.png")
print("  对真实模型(如 Wan 1.3B): 同一 prompt 改重力描述, 抽轨迹做同样的偏差检验。")
