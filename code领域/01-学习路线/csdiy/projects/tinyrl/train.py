#!/usr/bin/env python3
"""
tinyrl/train.py — 训练循环 + 评估 + 可视化

参照：Stable Baselines3 / OpenAI Spinning Up
csdiy 对应：rl-learning路径 + tinyrl

核心：
  Trainer    — 封装训练循环（episode 循环 + 日志 + 统计）
  Evaluator  — 评估（成功率/平均回报/策略可视化）
"""
import time, math

class Trainer:
    """训练器（参照 Stable Baselines3 learn()）"""
    def __init__(self, agent, env, max_episodes=500, log_interval=50, verbose=True):
        self.agent = agent; self.env = env
        self.max_episodes = max_episodes; self.log_interval = log_interval
        self.verbose = verbose
        self.history = {"rewards": [], "steps": [], "success": []}
    def train(self):
        """训练循环（参照 SB3 Agent.learn）"""
        t0 = time.perf_counter()
        for episode in range(self.max_episodes):
            state = self.env.reset()
            total_reward = 0; steps = 0; done = False

            while not done:
                action = self.agent.act(state)
                next_state, reward, done, info = self.env.step(action)
                # Q-Learning / DQN：在线学习
                if hasattr(self.agent, 'learn') and not hasattr(self.agent, 'trajectory'):
                    self.agent.learn(state, action, reward, next_state, done)
                # DQN：存入 replay buffer + 在线学习
                if hasattr(self.agent, 'replay_buffer'):
                    self.agent.remember(state, action, reward, next_state, done)
                    if len(self.agent.replay_buffer) > 32:
                        self.agent.learn()
                # Policy Gradient：存储 transition（3参数）
                elif hasattr(self.agent, 'trajectory'):
                    self.agent.remember(state, action, reward)
                # Q-Learning：在线学习
                elif hasattr(self.agent, 'learn'):
                    self.agent.learn(state, action, reward, next_state, done)
                state = next_state; total_reward += reward; steps += 1

            # Policy Gradient：episode 结束后学习
            if hasattr(self.agent, 'trajectory') and self.agent.trajectory:
                self.agent.learn()

            success = info.get("event") == "goal"
            self.history["rewards"].append(total_reward)
            self.history["steps"].append(steps)
            self.history["success"].append(success)

            if self.verbose and (episode % self.log_interval == 0 or episode == self.max_episodes - 1):
                recent = self.history["rewards"][-self.log_interval:]
                recent_success = sum(self.history["success"][-self.log_interval:]) / len(recent)
                print(f"  episode {episode:4d}  reward={total_reward:+.3f}  "
                      f"steps={steps:3d}  success_rate={recent_success:.0%}")

        elapsed = time.perf_counter() - t0
        return {"episodes": self.max_episodes, "elapsed": elapsed,
                "avg_reward": sum(self.history["rewards"]) / len(self.history["rewards"]),
                "success_rate": sum(self.history["success"]) / len(self.history["success"])}

class Evaluator:
    """评估器（参照 SB3 evaluate_policy）"""
    @staticmethod
    def evaluate(agent, env, n_episodes=20, explore=False):
        """评估策略（不探索）"""
        rewards = []; successes = 0
        for _ in range(n_episodes):
            state = env.reset(); total = 0; done = False
            while not done:
                action = agent.act(state, explore=explore)
                state, reward, done, info = env.step(action)
                total += reward
                if info.get("event") == "goal": successes += 1
            rewards.append(total)
        return {"avg_reward": sum(rewards) / len(rewards), "success_rate": successes / n_episodes,
                "max_reward": max(rewards), "min_reward": min(rewards)}

    @staticmethod
    def render_policy(agent, env):
        """策略可视化（参照 Sutton §4.1 图）"""
        arrows = ["↑", "↓", "←", "→"]
        print("  学到的策略（greedy）：")
        for r in range(env.size):
            row = ""
            for c in range(env.size):
                s = r * env.size + c
                if (r, c) == env.goal: row += " 🎯"
                elif (r, c) in getattr(env, '_traps', set()): row += " 💀"
                else:
                    if hasattr(agent, 'Q'):
                        a = max(range(4), key=lambda i: agent.Q[s][i])
                    elif hasattr(agent, 'theta'):
                        probs = agent.policy(s)
                        a = max(range(4), key=lambda i: probs[i])
                    else: a = 0
                    row += f" {arrows[a]}"
            print(f"   {row}")
