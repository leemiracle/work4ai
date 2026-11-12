#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_dataset.py —— 生成 rl_agent 任务环境的 GRPO 训练 parquet（Layer 3 配套）
字段：prompt（任务问句）/ gold_keywords（RLVR 判分关键词）/ category
跑法：python3 verl_bridge/make_dataset.py   →  verl_bridge/rl_agent_train.parquet
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 24 题：概念/实验/论文/混合 四态（与 rl_agent classify_state 对齐），gold_keywords 人工标注
ROWS = [
    # concept（8）
    ("什么是 Q-learning 的探索与利用？", ["探索", "利用"], "concept"),
    ("Q-learning 是 on-policy 还是 off-policy？", ["off-policy", "离策略"], "concept"),
    ("MDP 五元组包含哪些元素？", ["状态", "动作", "奖励"], "concept"),
    ("什么是价值函数？", ["价值", "回报", "期望"], "concept"),
    ("ε-greedy 策略是怎么工作的？", ["随机", "最大", "Q 值"], "concept"),
    ("什么是 temporal difference 学习？", ["自举", "估计", "差"], "concept"),
    ("DQN 用了哪两个稳定训练的技巧？", ["replay", "目标网络"], "concept"),
    ("什么是奖励塑形？", ["密集", "稀疏", "引导"], "concept"),
    # experiment（6）——反短路：必须 run_experiment
    ("跑一个 bandit 实验", ["Thompson", "regret"], "experiment"),
    ("跑一个 gridworld 实验", ["贪婪", "成功"], "experiment"),
    ("跑一个 grpo 实验", ["baseline", "方差"], "experiment"),
    ("跑一个 dpo 实验", ["偏好", "RM"], "experiment"),
    ("跑一个 dqn 实验", ["replay", "target"], "experiment"),
    ("跑一个 curriculum 实验", ["课程", "迁移"], "experiment"),
    # paper（5）
    ("ReAct 论文属于什么范式？", ["推理", "行动", "交织"], "paper"),
    ("Reflexion 的核心机制是什么？", ["反思", "失败", "重试"], "paper"),
    ("GRPO 与 PPO 的最大区别是什么？", ["价值", "critic", "组"], "paper"),
    ("RLVR 指什么？", ["可验证", "奖励", "规则"], "paper"),
    ("Self-Consistency 怎么工作？", ["采样", "投票", "多数"], "paper"),
    # mixed（5）
    ("GRPO 和网格世界的区别与联系", ["GRPO", "网格"], "mixed"),
    ("bandit 和 MDP 的关系是什么？", ["单状态", "MDP", "退化"], "mixed"),
    ("DQN 的 replay 和 DPO 的偏好对有什么相似？", ["replay", "偏好"], "mixed"),
    ("ε-greedy 在 bandit 实验里的 regret 表现如何？", ["ε-greedy", "regret"], "mixed"),
    ("课程学习和 gridworld 的关系？", ["课程", "gridworld"], "mixed"),
]

def main():
    try:
        import pandas as pd
    except ImportError:
        print("需要 pandas：pip install pandas pyarrow"); sys.exit(1)
    df = pd.DataFrame([{
        "prompt": p,
        "gold_keywords": json.dumps(kw, ensure_ascii=False),
        "category": c,
    } for p, kw, c in ROWS])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rl_agent_train.parquet")
    df.to_parquet(out)
    print(f"✅ {len(df)} 题 → {out}（四态分布：{df.category.value_counts().to_dict()}）")

if __name__ == "__main__":
    main()
