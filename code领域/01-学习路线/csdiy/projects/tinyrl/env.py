#!/usr/bin/env python3
"""
tinyrl/env.py — 强化学习环境接口

参照：OpenAI Gym / Gymnasium / RLlib
csdiy 对应：rl-learning路径 + tinyrl

环境清单：
  Env        — 基类（reset/step/render）
  GridWorld  — 网格世界（参照 Sutton Example 3.5）
  CartPole1D — 简化版倒立摆（1D 物理模拟）
"""
import math, random

class Env:
    """环境基类（参照 gym.Env）"""
    def reset(self):
        """重置环境 → 返回初始状态"""
        raise NotImplementedError
    def step(self, action):
        """执行动作 → 返回 (next_state, reward, done, info)"""
        raise NotImplementedError
    @property
    def n_states(self): raise NotImplementedError
    @property
    def n_actions(self): raise NotImplementedError
    def render(self): pass

class GridWorld(Env):
    """网格世界（参照 Sutton RL §3.1 + §4.1）
    N×N 网格，起点(0,0)，终点(N-1,N-1)
    4 个动作：0=上 1=下 2=左 3=右
    奖励：到终点+1，每步-0.01（鼓励快速到达）"""
    def __init__(self, size=4):
        self.size = size; self.goal = (size-1, size-1); self._pos = (0, 0)
        self._traps = set()
    def add_trap(self, r, c): self._traps.add((r, c))
    def reset(self):
        self._pos = (0, 0); return self._encode(self._pos)
    def step(self, action):
        r, c = self._pos
        if action == 0 and r > 0: r -= 1      # ↑
        elif action == 1 and r < self.size-1: r += 1  # ↓
        elif action == 2 and c > 0: c -= 1    # ←
        elif action == 3 and c < self.size-1: c += 1  # →
        self._pos = (r, c)
        if (r, c) == self.goal: return self._encode((r, c)), 1.0, True, {"event": "goal"}
        if (r, c) in self._traps: return self._encode((r, c)), -1.0, True, {"event": "trap"}
        return self._encode((r, c)), -0.01, False, {}
    def _encode(self, pos): return pos[0] * self.size + pos[1]
    def _decode(self, s): return (s // self.size, s % self.size)
    @property
    def n_states(self): return self.size * self.size
    @property
    def n_actions(self): return 4
    def render(self, agent=None):
        """ASCII 可视化（参照 gym render）"""
        arrows = ["↑", "↓", "←", "→"]
        for r in range(self.size):
            row = ""
            for c in range(self.size):
                if (r, c) == self.goal: row += " 🎯"
                elif (r, c) in self._traps: row += " 💀"
                elif (r, c) == self._pos: row += " 🤖"
                elif agent:
                    s = self._encode((r, c))
                    a = max(range(4), key=lambda i: agent.Q[s][i]) if hasattr(agent, 'Q') else 0
                    row += f" {arrows[a]}"
                else: row += " ·"
            print(f"  {row}")

class CartPole1D(Env):
    """简化版 CartPole（1D 物理，参照 gym CartPole）
    状态：[位置, 速度]  动作：0=左推 1=右推
    目标：保持位置在 [-2.4, 2.4] 范围内"""
    def __init__(self):
        self.gravity = 0.5; self.force = 0.3; self.max_pos = 2.4
        self.pos = 0.0; self.vel = 0.0; self.steps = 0; self.max_steps = 200
    def reset(self):
        self.pos = random.uniform(-0.1, 0.1); self.vel = 0.0; self.steps = 0
        return self._discretize()
    def step(self, action):
        force = self.force if action == 1 else -self.force
        self.vel += force - self.gravity * 0.1; self.pos += self.vel * 0.1
        self.steps += 1
        done = abs(self.pos) > self.max_pos or self.steps >= self.max_steps
        reward = 1.0 if not done else 0.0
        info = {"pos": self.pos, "vel": self.vel, "steps": self.steps}
        return self._discretize(), reward, done, info
    def _discretize(self, bins=10):
        """连续状态 → 离散化（参照 tile coding 简化版）"""
        p = min(bins-1, max(0, int((self.pos + self.max_pos) / (2*self.max_pos) * bins)))
        v = min(bins-1, max(0, int((self.vel + 2) / 4 * bins)))
        return p * bins + v
    @property
    def n_states(self): return 100  # 10×10
    @property
    def n_actions(self): return 2
