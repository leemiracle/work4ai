# tinyrl — 强化学习系统

> 参照 OpenAI Spinning Up + Stable Baselines3 + InstructGPT，从零实现 RL 全栈。

## 模块清单

| 文件 | 参照 | 核心内容 |
|------|------|---------|
| `env.py` | OpenAI Gym | GridWorld + CartPole 环境接口 |
| `agent.py` | Sutton RL / Spinning Up | Q-Learning + REINFORCE + DQN（replay+target） |
| `train.py` | Stable Baselines3 | Trainer + Evaluator + 策略可视化 |
| `rlhf.py` | InstructGPT / Zephyr | Reward Model + PPO + RLHF 完整流程 |
| `demo.py` | — | 4 个端到端 demo |

## 端到端演示

```bash
python3 projects/tinyrl/demo.py
# Demo 1: Q-Learning 学 GridWorld（5×5 含陷阱）
# Demo 2: REINFORCE 学 GridWorld
# Demo 3: DQN 学 CartPole（1D 物理）
# Demo 4: RLHF 模拟（RM 训练 + PPO 微调）
```

## 算法覆盖

```
值函数法:  Q-Learning → DQN（+ replay + target network）
策略梯度法: REINFORCE → PPO（+ clipping）
对齐:     SFT → Reward Model → PPO = RLHF
```

## csdiy 知识交叉

- `rl-learning` skill — RL 全栈学习路径
- [nanoGPT 精读](../../source-reading/nanoGPT-读懂最小GPT.md) — RLHF 微调的目标模型
- ChatGPT/Claude/Gemini 都使用 RLHF 对齐人类偏好
