#!/usr/bin/env python3
"""rl_smoke.py — L3 训练冒烟：纯标准库 toy RL，断言"学习方向正确"。

为什么存在：RL 代码最容易的失败不是崩溃，而是**静默不学习**（循环空转/reward 恒 0/
探索退化）。本冒烟用两个最小算法验证数据流三要素：状态→动作→奖励闭环 + 值更新生效。
诚实边界：toy 规模（几百步）只证明"学得动"，不证明超参合理（对应记忆铁律：玩具看不出
量化损失，价值在链路验证）。
"""
import random
import statistics
import sys


def bandit(eps=0.1, steps=400, seed=42):
    """ε-greedy 3 臂 bandit：前 50 步均值 vs 后 50 步均值必须显著改善"""
    rng = random.Random(seed)
    true = [0.1, 0.5, 0.9]
    counts = [0, 0, 0]
    values = [0.0, 0.0, 0.0]
    rewards = []
    for t in range(steps):
        if rng.random() < eps:
            a = rng.randrange(3)
        else:
            a = max(range(3), key=lambda i: values[i])
        r = 1.0 if rng.random() < true[a] else 0.0
        counts[a] += 1
        values[a] += (r - values[a]) / counts[a]  # 增量均值
        rewards.append(r)
    early = statistics.mean(rewards[:50])
    late = statistics.mean(rewards[-50:])
    return early, late, values


def q_learning(episodes=300, seed=42, grid=5):
    """表格 Q-learning 网格世界（到达角+0 奖励，每步-004）：
    后 50 回合平均回报必须优于前 50 回合（学得动的方向性证据）"""
    rng = random.Random(seed)
    goal = (grid - 1, grid - 1)
    Q = {}          # (r,c,a) -> value
    eps, alpha, gamma = 0.2, 0.1, 0.95
    returns = []
    for ep in range(episodes):
        s = (0, 0)
        G = 0.0
        for _ in range(100):
            if rng.random() < eps:
                a = rng.randrange(4)
            else:
                a = max(range(4), key=lambda x: Q.get((*s, x), 0.0))
            dr, dc = [(-1, 0), (1, 0), (0, -1), (0, 1)][a]
            s2 = (max(0, min(grid - 1, s[0] + dr)), max(0, min(grid - 1, s[1] + dc)))
            r = -0.04
            if s2 == goal:
                r = 1.0
            best2 = max(Q.get((*s2, x), 0.0) for x in range(4))
            Q[(*s, a)] = Q.get((*s, a), 0.0) + alpha * (r + gamma * best2 - Q.get((*s, a), 0.0))
            G += r
            s = s2
            if s == goal:
                break
        returns.append(G)
    early = statistics.mean(returns[:50])
    late = statistics.mean(returns[-50:])
    greedy_len = 0
    s = (0, 0)
    for _ in range(grid * grid * 2):    # 贪心走位验证策略
        a = max(range(4), key=lambda x: Q.get((*s, x), 0.0))
        dr, dc = [(-1, 0), (1, 0), (0, -1), (0, 1)][a]
        s = (max(0, min(grid - 1, s[0] + dr)), max(0, min(grid - 1, s[1] + dc)))
        greedy_len += 1
        if s == goal:
            break
    return early, late, greedy_len


def main():
    fails = []
    e, l, values = bandit()
    print(f"[bandit ε-greedy] 前50步均值={e:.3f} 后50步均值={l:.3f} 估计值={[round(v,2) for v in values]}")
    if not l > e + 0.15:
        fails.append(f"bandit 无改善：{e:.3f}→{l:.3f}")
    if not values[2] > values[0]:
        fails.append("bandit 值序错：最优臂未识别")

    e, l, gl = q_learning()
    print(f"[Q-learning 网格] 前50回合={e:.2f} 后50回合={l:.2f} 贪心步数={gl}（最优={2*(5-1)}）")
    if not l > e + 0.3:
        fails.append(f"Q-learning 无改善：{e:.2f}→{l:.2f}")
    if gl > 2 * (5 - 1) + 2:
        fails.append(f"贪心策略未收敛：{gl} 步到达")

    if fails:
        print("SMOKE FAIL:", "; ".join(fails))
        return 1
    print("SMOKE PASS: 学习方向性验证通过（闭环/更新/策略三要素在位）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
