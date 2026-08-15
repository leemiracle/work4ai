"""
06_pensieve_abr.py
==================
Pensieve (Mao et al., MIT, SIGCOMM 2017) 的核心：用强化学习 (A3C) 学 ABR 策略。

Pensieve 是 ABR 算法的里程碑——首次证明 RL 在生产级网络问题上有用。

本文件实现：
1. ABR 环境的状态/动作/奖励定义（Pensieve 原版）
2. 一个简化的 A2C 策略网络（actor-critic）
3. 短训练 + 评估

注意：完整 Pensieve 用 A3C + 大量网络轨迹数据。
本文件是教学版，证明 RL ABR 的原理可行。
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import deque
import random


# ============ ABR 环境 ============
class ABREnv:
    """
    Pensieve 状态空间（每个 chunk 决策时）：
      - 过去 8 个 chunk 的下载时间 / 吞吐量
      - 当前 buffer 大小
      - 下个 chunk 在各码率下的字节数
      - 上次选的码率
      - 已下载 chunk 数 / 剩余 chunk 数
    动作：选 0..K-1 码率
    奖励：QoE = quality - 4.3*rebuf_penalty - abs(switch_penalty)
    """
    def __init__(self, bitrates, throughput_trace, chunk_dur=4.0, buffer_max=20.0):
        self.bitrates = sorted(bitrates)
        self.K = len(bitrates)
        self.trace = throughput_trace
        self.chunk_dur = chunk_dur
        self.buffer_max = buffer_max
        self.reset()

    def reset(self):
        self.t = 0
        self.buffer = 5.0
        self.last_br = 0
        self.history = deque([1e6] * 8, maxlen=8)  # 过去 8 个吞吐量
        return self._state()

    def _state(self):
        # 状态向量（Pensieve 风格）
        past_tp = np.array(list(self.history)) / 1e6  # 归一化
        next_sizes = np.array([self.bitrates[i] * self.chunk_dur / 8 / 1e6
                               for i in range(self.K)])  # MB
        s = np.concatenate([
            past_tp,                          # 8
            [self.buffer / self.buffer_max],  # 1
            next_sizes,                       # K
            np.eye(self.K)[self.last_br],     # K (one-hot)
            [self.t / len(self.trace)]        # 1
        ]).astype(np.float32)
        return s

    def step(self, action):
        br = self.bitrates[action]
        size_bits = br * self.chunk_dur
        tp = self.trace[self.t]
        download_time = size_bits / max(tp, 1)

        # 卡顿
        rebuf = max(0, download_time - self.buffer)
        self.buffer = max(0, self.buffer - download_time) + self.chunk_dur
        self.buffer = min(self.buffer, self.buffer_max)

        # QoE 奖励（Pensieve 风格）
        quality = np.log(br / self.bitrates[0]) / np.log(self.bitrates[-1] / self.bitrates[0] + 1e-6)
        switch_pen = abs(np.log(br) - np.log(self.bitrates[self.last_br])) / np.log(10)
        rebuf_pen = 4.3 * rebuf / self.chunk_dur
        reward = quality - rebuf_pen - switch_pen

        self.last_br = action
        self.history.append(tp)
        self.t += 1
        done = self.t >= len(self.trace)
        return self._state(), reward, done, {"bitrate": br, "rebuf": rebuf}


# ============ Actor-Critic 网络 ============
class ABRPolicy(nn.Module):
    """Pensieve 用 1D CNN + LSTM + FC。教学版用简单 MLP。"""
    def __init__(self, state_dim, n_actions):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.actor = nn.Linear(128, n_actions)
        self.critic = nn.Linear(128, 1)

    def forward(self, x):
        h = F.relu(self.fc1(x))
        h = F.relu(self.fc2(h))
        return self.actor(h), self.critic(h)


def train_a2c(env, n_episodes=300, gamma=0.99, lr=1e-3):
    state_dim = len(env.reset())
    policy = ABRPolicy(state_dim, env.K)
    opt = torch.optim.Adam(policy.parameters(), lr=lr)

    rewards_log = []
    for ep in range(n_episodes):
        state = env.reset()
        log_probs, values, rewards = [], [], []
        done = False
        while not done:
            s = torch.from_numpy(state).unsqueeze(0)
            logits, value = policy(s)
            probs = F.softmax(logits, dim=-1)
            a = torch.multinomial(probs, 1).item()
            next_state, r, done, _ = env.step(a)
            log_probs.append(torch.log_softmax(logits, dim=-1)[0, a])
            values.append(value.squeeze())
            rewards.append(r)
            state = next_state

        # 计算 returns
        returns = []
        R = 0
        for r in reversed(rewards):
            R = r + gamma * R
            returns.insert(0, R)
        returns = torch.tensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-6)

        # Actor-Critic loss
        log_probs = torch.stack(log_probs)
        values = torch.stack(values)
        advantage = returns - values.detach()
        actor_loss = -(log_probs * advantage).mean()
        critic_loss = F.mse_loss(values, returns)
        loss = actor_loss + 0.5 * critic_loss

        opt.zero_grad(); loss.backward(); opt.step()
        rewards_log.append(sum(rewards))
        if ep % 50 == 0:
            print(f"  episode {ep}: avg reward={np.mean(rewards):.3f}, total={sum(rewards):.2f}")

    return policy


def evaluate(policy, env):
    state = env.reset()
    total_qoe = 0; total_rebuf = 0; bitrates_used = []
    done = False
    while not done:
        s = torch.from_numpy(state).unsqueeze(0)
        with torch.no_grad():
            logits, _ = policy(s)
            a = logits.argmax(dim=-1).item()
        state, r, done, info = env.step(a)
        total_qoe += r
        total_rebuf += info["rebuf"]
        bitrates_used.append(info["bitrate"])
    return total_qoe, total_rebuf, bitrates_used


if __name__ == "__main__":
    print("=" * 60)
    print("Pensieve-style RL ABR (A2C 教学版)")
    print("=" * 60)

    bitrates = [300e3, 800e3, 1.5e6, 3e6, 6e6]
    # 合成训练轨迹（多种带宽场景）
    np.random.seed(0)
    traces = []
    for _ in range(20):
        base = np.random.choice([500e3, 1e6, 2e6, 5e6, 8e6])
        trace = np.abs(base + np.random.randn(30) * base * 0.3)
        traces.append(trace)

    env = ABREnv(bitrates, traces[0])
    print("\n[训练] A2C on 合成轨迹...")
    policy = train_a2c(env, n_episodes=300)

    print("\n[评估] 测试轨迹：")
    test_traces = [
        ("稳定 5 Mbps", np.full(30, 5e6)),
        ("通勤波动", np.concatenate([np.full(10, 8e6), np.full(10, 1e6), np.full(10, 4e6)])),
        ("极差 0.5 Mbps", np.full(30, 0.5e6)),
    ]
    for name, trace in test_traces:
        env_test = ABREnv(bitrates, trace)
        qoe, rebuf, brs = evaluate(policy, env_test)
        avg_br = np.mean(brs) / 1e6
        print(f"  [{name}] QoE={qoe:.2f}  avg bitrate={avg_br:.2f}Mbps  rebuf={rebuf:.1f}s")

    print("\n" + "=" * 60)
    print("真实 Pensieve：")
    print("  - 用 A3C（异步 advantage actor-critic）")
    print("  - 在数百万条真实网络轨迹上训练（FCC, Norway, Oboe 数据集）")
    print("  - 在所有测试场景下超越 BOLA/MPC/BB")
    print("  - 后续：Puffer (Stanford 2019+) 用在线 RL + Bayesian NN（Fugu）")
    print("=" * 60)
