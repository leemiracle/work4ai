#!/usr/bin/env python3
"""
tinyrl/demo.py — RL 系统端到端演示

4 个 demo：
  1. Q-Learning 学 GridWorld
  2. Policy Gradient 学 GridWorld
  3. DQN 学 CartPole（简化版）
  4. RLHF 完整流程（Reward Model + PPO）
"""
import sys, os, time, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tinyrl.env import GridWorld, CartPole1D
from tinyrl.agent import QLearningAgent, PolicyGradientAgent, DQNAgent
from tinyrl.train import Trainer, Evaluator
from tinyrl.rlhf import simulate_rlhf

def demo_qlearning():
    print("┌─────────────────────────────────┐")
    print("│  Demo 1: Q-Learning (GridWorld) │")
    print("└─────────────────────────────────┘\n")
    random.seed(42)
    env = GridWorld(size=5)
    env.add_trap(2, 2); env.add_trap(3, 1)  # 添加陷阱
    agent = QLearningAgent(env.n_states, env.n_actions, lr=0.2, gamma=0.95, epsilon=0.2)
    trainer = Trainer(agent, env, max_episodes=300, log_interval=100)
    stats = trainer.train()
    print(f"\n  训练结果: {stats['episodes']} episodes, {stats['success_rate']:.0%} success, {stats['elapsed']:.1f}s")
    eval = Evaluator.evaluate(agent, env, n_episodes=20)
    print(f"  评估: avg_reward={eval['avg_reward']:.3f}, success={eval['success_rate']:.0%}")
    Evaluator.render_policy(agent, env)

def demo_policy_gradient():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 2: REINFORCE (GridWorld)  │")
    print("└─────────────────────────────────┘\n")
    random.seed(42)
    env = GridWorld(size=4)
    agent = PolicyGradientAgent(env.n_states, env.n_actions, lr=0.01, gamma=0.99)
    trainer = Trainer(agent, env, max_episodes=500, log_interval=100)
    trainer.train()
    eval = Evaluator.evaluate(agent, env, n_episodes=20)
    print(f"  评估: avg_reward={eval['avg_reward']:.3f}, success={eval['success_rate']:.0%}")
    Evaluator.render_policy(agent, env)

def demo_dqn():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 3: DQN (CartPole 1D)      │")
    print("└─────────────────────────────────┘\n")
    random.seed(42)
    env = CartPole1D()
    agent = DQNAgent(env.n_states, env.n_actions, lr=0.1, gamma=0.95, epsilon=0.15)
    print(f"  环境: CartPole 1D ({env.n_states} states, {env.n_actions} actions)")
    print(f"  Agent: DQN (replay buffer + target network)\n")
    for episode in range(200):
        state = env.reset(); total = 0; done = False
        while not done:
            action = agent.act(state)
            next_s, reward, done, info = env.step(action)
            agent.remember(state, action, reward, next_s, done)
            if len(agent.replay_buffer) > 32: agent.learn(batch_size=32)
            state = next_s; total += reward
        if episode % 50 == 0 or episode == 199:
            print(f"  episode {episode:3d}  reward={total:.1f}  steps={info['steps']}  pos={info['pos']:.2f}")
    print(f"\n  DQN 创新: experience replay + target network（DeepMind 2015）")

def demo_rlhf():
    print("\n┌─────────────────────────────────┐")
    print("│  Demo 4: RLHF 模拟              │")
    print("└─────────────────────────────────┘\n")
    simulate_rlhf()

def main():
    print("=" * 60)
    print("  tinyrl — 强化学习系统 端到端演示")
    print("  参照 OpenAI Spinning Up + Stable Baselines3 + InstructGPT")
    print("=" * 60)
    t0 = time.time()
    demo_qlearning()
    demo_policy_gradient()
    demo_dqn()
    demo_rlhf()
    print(f"\n{'='*60}")
    print(f"  全部完成 ({time.time()-t0:.1f}s)")
    print(f"  tinyrl = env.py + agent.py + train.py + rlhf.py + demo.py")
    print(f"  覆盖: Q-Learning → REINFORCE → DQN → RLHF")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
