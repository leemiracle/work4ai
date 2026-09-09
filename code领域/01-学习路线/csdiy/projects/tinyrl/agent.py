#!/usr/bin/env python3
"""
tinyrl/agent.py — RL 智能体

参照：Sutton RL / OpenAI Spinning Up / Stable Baselines3
csdiy 对应：rl-learning路径 + AI核心

智能体清单：
  QLearningAgent    — Q-Learning（值函数法）
  PolicyGradient    — REINFORCE（策略梯度法）
  DQN               — Deep Q-Network 概念版
"""
import random, math
from collections import defaultdict

class QLearningAgent:
    """Q-Learning（参照 Sutton §6.5 / Watkins 1989）
    Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]
    Off-policy TD 控制。"""
    def __init__(self, n_states, n_actions, lr=0.1, gamma=0.95, epsilon=0.1):
        self.Q = [[0.0] * n_actions for _ in range(n_states)]
        self.lr = lr; self.gamma = gamma; self.eps = epsilon
        self.n_actions = n_actions
    def act(self, state, explore=True):
        """ε-greedy 策略"""
        if explore and random.random() < self.eps:
            return random.randint(0, self.n_actions - 1)
        return max(range(self.n_actions), key=lambda a: self.Q[state][a])
    def learn(self, s, a, r, s2, done):
        """TD 更新"""
        future = 0 if done else self.gamma * max(self.Q[s2])
        self.Q[s][a] += self.lr * (r + future - self.Q[s][a])
    def policy_table(self):
        """提取贪心策略表"""
        return [max(range(self.n_actions), key=lambda a: self.Q[s][a])
                for s in range(len(self.Q))]

class PolicyGradientAgent:
    """REINFORCE（参照 Sutton §13.3 / Williams 1992）
    θ ← θ + α ∇log π(a|s) × G（累计回报）
    On-policy 策略梯度。"""
    def __init__(self, n_states, n_actions, lr=0.01, gamma=0.99):
        self.theta = [[random.gauss(0, 0.1) for _ in range(n_actions)] for _ in range(n_states)]
        self.lr = lr; self.gamma = gamma; self.n_actions = n_actions
        self.trajectory = []
    def _softmax(self, logits):
        mx = max(logits); exps = [math.exp(l - mx) for l in logits]; s = sum(exps)
        return [e / s for e in exps]
    def policy(self, state):
        """π(a|s) 概率分布"""
        return self._softmax(self.theta[state])
    def act(self, state, explore=True):
        probs = self.policy(state)
        r = random.random(); cum = 0
        for a, p in enumerate(probs):
            cum += p
            if r < cum: return a
        return self.n_actions - 1
    def remember(self, state, action, reward):
        """存储 transition（episode buffer）"""
        self.trajectory.append((state, action, reward))
    def learn(self):
        """REINFORCE 更新（episode 结束后调用）"""
        G = 0
        for state, action, reward in reversed(self.trajectory):
            G = reward + self.gamma * G
            probs = self.policy(state)
            # ∇log π = one_hot(a) - π
            for a in range(self.n_actions):
                grad = (1.0 if a == action else 0.0) - probs[a]
                self.theta[state][a] += self.lr * grad * G
        self.trajectory = []  # 清空 episode buffer

class DQNAgent:
    """DQN 概念版（参照 Mnih 2015 / DeepMind）
    用 Q 表模拟（真实 DQN 用神经网络）
    创新：experience replay + target network"""
    def __init__(self, n_states, n_actions, lr=0.1, gamma=0.95, epsilon=0.1):
        self.Q = [[0.0] * n_actions for _ in range(n_states)]
        self.Q_target = [row[:] for row in self.Q]  # target network
        self.lr = lr; self.gamma = gamma; self.eps = epsilon; self.n_actions = n_actions
        self.replay_buffer = []; self.buffer_size = 1000; self.target_update_freq = 50; self.step_count = 0
    def act(self, state, explore=True):
        if explore and random.random() < self.eps:
            return random.randint(0, self.n_actions - 1)
        return max(range(self.n_actions), key=lambda a: self.Q[state][a])
    def remember(self, s, a, r, s2, done):
        self.replay_buffer.append((s, a, r, s2, done))
        if len(self.replay_buffer) > self.buffer_size: self.replay_buffer.pop(0)
    def learn(self, batch_size=32):
        if len(self.replay_buffer) < batch_size: return
        batch = random.sample(self.replay_buffer, batch_size)
        for s, a, r, s2, done in batch:
            future = 0 if done else self.gamma * max(self.Q_target[s2])
            self.Q[s][a] += self.lr * (r + future - self.Q[s][a])
        self.step_count += 1
        if self.step_count % self.target_update_freq == 0:
            self.Q_target = [row[:] for row in self.Q]  # 同步 target network
