---
card_id: SW-03
title: "第 3 幕 · 代码：最小 boids swarm 仿真"
universe: 讲透群体智能
arc_position: 第 3 幕（代码/转变）
status: draft
next_card: SW-04
---

# 💻 第 3 幕 · 代码：最小 boids swarm 仿真

用 numpy 实现 Reynolds 三规则（分离/对齐/聚合），观察群体涌现。

```python
import numpy as np

def boids_step(pos, vel, sep_w=1.5, align_w=1.0, coh_w=1.0, max_speed=0.5):
    """一步 boids 更新. pos/vel: [N, 2]."""
    N = len(pos)
    # 两两距离
    diff = pos[:, None, :] - pos[None, :, :]  # [N,N,2]
    dist = np.linalg.norm(diff, axis=2) + 1e-6  # [N,N]
    np.fill_diagonal(dist, np.inf)

    # 1. 分离: 远离太近的邻居 (< r_sep)
    r_sep = 0.5
    close_mask = dist < r_sep
    sep_force = (diff * close_mask[..., None]).sum(axis=1) / (r_sep**2)
    sep_force = sep_force / (np.linalg.norm(sep_force, axis=1, keepdims=True) + 1e-6)

    # 2. 对齐: 朝邻居平均速度
    neighbor_mask = dist < 1.5
    cnt = neighbor_mask.sum(axis=1) + 1e-6
    avg_vel = (vel[:, None, :] * neighbor_mask[..., None]).sum(axis=1) / cnt[:, None]
    align_force = avg_vel - vel

    # 3. 聚合: 朝邻居中心
    center = (pos[:, None, :] * neighbor_mask[..., None]).sum(axis=1) / cnt[:, None]
    coh_force = center - pos

    # 合成
    new_vel = vel + sep_w*sep_force + align_w*align_force + coh_w*coh_force
    # 限速
    speed = np.linalg.norm(new_vel, axis=1, keepdims=True)
    new_vel = np.where(speed > max_speed, new_vel * max_speed/speed, new_vel)
    new_pos = pos + new_vel
    # 边界回绕
    new_pos = new_pos % 10.0
    return new_pos, new_vel

def coherence(pos):
    """群体相干性: std 越小越聚."""
    return np.std(pos, axis=0).mean()

# ===== 跑通: 观察涌现 =====
if __name__ == "__main__":
    np.random.seed(0)
    N = 50
    pos = np.random.rand(N, 2) * 10
    vel = (np.random.rand(N, 2) - 0.5) * 0.3
    print(f"初始相干性 (std, 越小越聚): {coherence(pos):.3f}")
    print("\n=== 演化 100 步 ===")
    for step in [10, 30, 50, 100]:
        for _ in range(step - (step-10 if step>10 else 0)):
            pos, vel = boids_step(pos, vel)
        c = coherence(pos)
        # 平均速度方向一致性 (对齐度)
        v_mean = np.mean(vel, axis=0)
        align = np.linalg.norm(v_mean) / (np.mean(np.linalg.norm(vel, axis=1)) + 1e-6)
        print(f"  step {step}: 相干性={c:.3f}, 对齐度={align:.3f} (1.0=完全同向)")
    print("\n洞察: 没有任何规则说'群体要同步', 但对齐度自动上升——这就是涌现.")
    print("调 sep_w=0 看碰撞, 调 coh_w=0 看散开——每条规则的贡献可隔离验证.")
```

## 这段代码教什么

1. **三规则全是局部**：每个 boid 只看 1.5 距离内的邻居
2. **涌现**：没有任何全局指令，但对齐度自动上升
3. **可调参数**：`sep_w/align_w/coh_w` 分别控制三种力——调零看效果，验证每条规则的作用
4. **群体相干性**：用位置 std 衡量聚合度，用速度一致性衡量对齐度

**延伸**：加 stigmergy（boids 留「信息素」轨迹，其他 boids 跟随）→ 变成蚁群 ACO。

📌 **下一张卡** → `04-不足-涌现的黑暗面.md`
