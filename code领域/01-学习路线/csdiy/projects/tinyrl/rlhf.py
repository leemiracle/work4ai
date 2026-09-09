#!/usr/bin/env python3
"""
tinyrl/rlhf.py — RLHF（Reinforcement Learning from Human Feedback）

参照：InstructGPT (Ouyang 2022) / Zephyr / Constitutional AI
csdiy 对应：AI前沿 + tinyrl + tinyllm

RLHF 三阶段：
  1. SFT（Supervised Fine-Tuning）— 用人类标注微调
  2. Reward Model — 训练奖励模型（学习人类偏好）
  3. PPO — 用 RM 的奖励做强化学习微调
"""
import random, math

class RewardModel:
    """奖励模型（参照 InstructGPT §3.2）
    输入 (prompt, response) → 输出标量奖励
    训练数据：人类标注的偏好对 (chosen > rejected)"""
    def __init__(self, n_features=10):
        self.weights = [random.gauss(0, 0.1) for _ in range(n_features)]
        self.bias = 0.0
    def score(self, features):
        """评分（参照 Bradley-Terry 模型）"""
        return sum(w * f for w, f in zip(self.weights, features)) + self.bias
    def train(self, preference_pairs, lr=0.01, epochs=100):
        """从偏好对训练（参照 InstructGPT RM loss）
        loss = -log(σ(r(chosen) - r(rejected)))"""
        for _ in range(epochs):
            for chosen_feat, rejected_feat in preference_pairs:
                r_chosen = self.score(chosen_feat)
                r_rejected = self.score(rejected_feat)
                # Bradley-Terry 梯度
                diff = r_chosen - r_rejected
                sigmoid = 1 / (1 + math.exp(-diff))
                error = 1 - sigmoid  # chosen 应该 > rejected
                for i in range(len(self.weights)):
                    grad = (chosen_feat[i] - rejected_feat[i]) * error
                    self.weights[i] += lr * grad
                self.bias += lr * error
    def preference_accuracy(self, pairs):
        """偏好准确率"""
        correct = sum(1 for c, r in pairs if self.score(c) > self.score(r))
        return correct / len(pairs) if pairs else 0

class PPOSimulator:
    """PPO 简化模拟器（参照 Schulman 2017）
    真实 PPO 对 LLM 做策略梯度更新，这里用表格模拟。
    核心：clip(ratio, 1-ε, 1+ε) × advantage"""
    def __init__(self, n_states, n_actions, clip_ratio=0.2, lr=0.01, gamma=0.99):
        self.theta = [[random.gauss(0, 0.1) for _ in range(n_actions)] for _ in range(n_states)]
        self.old_theta = [row[:] for row in self.theta]
        self.clip = clip_ratio; self.lr = lr; self.gamma = gamma
    def _softmax(self, logits):
        mx = max(logits); exps = [math.exp(l - mx) for l in logits]; s = sum(exps)
        return [e / s for e in exps]
    def collect_rollout(self, env, reward_fn, steps=50):
        """收集 rollout（参照 InstructGPT §3.3）"""
        trajectory = []; state = env.reset()
        for _ in range(steps):
            probs = self._softmax(self.theta[state])
            action = max(range(len(probs)), key=lambda i: probs[i])
            next_state, _, done, _ = env.step(action)
            # 用 RM 打分（不是环境的原生 reward）
            reward = reward_fn(state, action)
            trajectory.append((state, action, reward, probs[action]))
            state = next_state
            if done: state = env.reset()
        return trajectory
    def update(self, trajectory):
        """PPO 更新（参照 Schulman 2017 §4）"""
        G = 0
        for state, action, reward, old_prob in reversed(trajectory):
            G = reward + self.gamma * G  # 累计回报
            new_probs = self._softmax(self.theta[state])
            new_prob = new_probs[action]
            # PPO ratio
            ratio = new_prob / (old_prob + 1e-8)
            # Clipped surrogate objective
            clipped = max(1 - self.clip, min(1 + self.clip, ratio))
            objective = min(ratio * G, clipped * G)
            # 策略梯度
            for a in range(len(self.theta[state])):
                grad = (1.0 if a == action else 0.0) - new_probs[a]
                self.theta[state][a] += self.lr * grad * objective
    def act(self, state):
        probs = self._softmax(self.theta[state])
        return max(range(len(probs)), key=lambda i: probs[i])

def simulate_rlhf():
    """完整 RLHF 流程模拟（参照 InstructGPT Figure 2）"""
    from .env import GridWorld
    print("┌─────────────────────────────────┐")
    print("│  RLHF 模拟（参照 InstructGPT）   │")
    print("└─────────────────────────────────┘\n")

    # Stage 2: 训练 Reward Model
    print("  Stage 2: Reward Model 训练")
    rm = RewardModel(n_features=4)
    # 模拟偏好数据（"好的回答"特征 > "差的回答"特征）
    pairs = []
    for _ in range(50):
        good = [random.uniform(0.5, 1.0) for _ in range(4)]
        bad = [random.uniform(0.0, 0.5) for _ in range(4)]
        pairs.append((good, bad))
    rm.train(pairs, epochs=50)
    acc = rm.preference_accuracy(pairs)
    print(f"    偏好准确率: {acc:.0%}")

    # Stage 3: PPO 微调
    print("\n  Stage 3: PPO 微调")
    env = GridWorld(size=4)
    ppo = PPOSimulator(env.n_states, env.n_actions)

    def reward_fn(state, action):
        """用 RM 给奖励（替代环境的原生 reward）"""
        # 简化：用 state/action 编码为特征
        features = [state / env.n_states, action / 4, 0.5, 0.3]
        return rm.score(features)

    for iteration in range(5):
        rollout = ppo.collect_rollout(env, reward_fn, steps=30)
        avg_reward = sum(r for _, _, r, _ in rollout) / len(rollout)
        ppo.update(rollout)
        print(f"    iteration {iteration}: avg_reward = {avg_reward:.3f}")

    print(f"\n  RLHF = SFT → RM → PPO（三阶段对齐人类偏好）")
    print(f"  ChatGPT/Claude/Gemini 都用这个流程")
