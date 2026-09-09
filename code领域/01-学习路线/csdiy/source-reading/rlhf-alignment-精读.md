# RLHF 深度精读：从预训练到 ChatGPT 的对齐之路

> 参照：InstructGPT (Ouyang 2022) / Constitutional AI / DPO
>
> csdiy 对应：tinyrl/rlhf.py + AI前沿 + tinyllm

---

## 一、为什么需要 RLHF

### 预训练模型的问题

GPT-3 有 175B 参数，但预训练只学了"预测下一个 token"。它不会：
- 遵循指令（你问它"写首诗"，它可能继续补全你的句子）
- 拒绝有害请求（它可能教你怎么造炸弹）
- 承认不知道（它倾向于编造答案 = 幻觉）

**RLHF 的目标**：让模型的行为对齐人类偏好（有帮助、无害、诚实）。

---

## 二、RLHF 三阶段（参照 InstructGPT Figure 2）

```
┌─────────────────────────────────────────────────┐
│ Stage 1: SFT (Supervised Fine-Tuning)          │
│   预训练模型 + 人工标注的指令-回复对              │
│   → 能遵循基本指令的模型                          │
├─────────────────────────────────────────────────┤
│ Stage 2: Reward Model (RM)                     │
│   SFT 模型生成多个回复 → 人工排序                 │
│   → 训练打分模型 RM(prompt, response) → score   │
├─────────────────────────────────────────────────┤
│ Stage 3: PPO (Proximal Policy Optimization)   │
│   SFT 模型生成回复 → RM 打分 → PPO 优化          │
│   → 对齐人类偏好的最终模型                        │
└─────────────────────────────────────────────────┘
```

---

## 三、Stage 2: Reward Model 详解

### 数据收集

给同一个 prompt 生成 K 个回复 → 人工排序 → 得到偏好对。

```
Prompt: "Explain quantum computing"

Response A (rank 1): "Quantum computing uses quantum bits..."
Response B (rank 2): "It's like regular computing but faster..."
Response C (rank 3): "idk lol"
```

### Bradley-Terry 模型（参照 InstructGPT §3.2）

RM 的训练目标：学习一个打分函数 r(x, y)，使得：

```
P(A > B) = σ(r(A) - r(B)) = 1 / (1 + e^{-(r(A)-r(B))})
```

损失（最大化偏好对的对数似然）：
```
L = -log σ(r(prompt, chosen) - r(prompt, rejected))
```

### 你的 tinyrl/rlhf.py 实现了这个

```python
# RewardModel.train() 的核心梯度
diff = r_chosen - r_rejected
sigmoid = 1 / (1 + exp(-diff))
error = 1 - sigmoid  # chosen 应该 > rejected
weights[i] += lr * (chosen_feat[i] - rejected_feat[i]) * error
```

---

## 四、Stage 3: PPO 详解

### 为什么不用普通梯度下降

用 RM 的分数做损失 → 模型会找到 RM 的漏洞（reward hacking）而非真正改善回复质量。

PPO 的核心：**限制策略更新幅度**，防止一步走太远。

### PPO Clipped Objective（参照 Schulman 2017）

```
ratio = π_new(a|s) / π_old(a|s)   # 新旧策略的概率比
advantage = RM 回报 - 基线（KL 惩罚）

L = min(ratio × advantage, clip(ratio, 1-ε, 1+ε) × advantage)
```

**clip 的作用**：如果 ratio > 1+ε（新策略大幅偏离旧策略），截断梯度 → 防止崩溃。

### RLHF 版 PPO 的额外约束

```
total_reward = RM_score - β × KL(π_new || π_SFT)
```

KL 惩罚项防止模型偏离 SFT 太远（保持语言能力）。

---

## 五、DPO：RLHF 的简化替代

### 问题：PPO 太复杂

PPO 需要 4 个模型同时运行（Actor、Critic、RM、Reference）→ 显存巨大。

### DPO (Direct Preference Optimization, Rafailov 2023)

**核心洞察**：可以跳过 RM，直接从偏好数据训练策略。

```
L_DPO = -log σ(β · (log π(y_w|x)/π_ref(y_w|x) - log π(y_l|x)/π_ref(y_l|x)))
```

- y_w = 偏好的回复（chosen）
- y_l = 不偏好的回复（rejected）
- π_ref = SFT 模型（冻结）
- β = 温度参数

### RLHF vs DPO 对比

| 维度 | RLHF (PPO) | DPO |
|------|-----------|-----|
| 需要的模型数 | 4 个 | 2 个（策略+参考） |
| 训练方式 | 在线 RL（生成→打分→更新） | 离线（直接从偏好数据训练） |
| 稳定性 | 不稳定（PPO 超参敏感） | 稳定（标准交叉熵） |
| 效果 | 略好（在线探索更多） | 接近 PPO |
| 代表 | ChatGPT/GPT-4 | Zephyr/Llama-3 |

---

## 六、RLHF 的问题和前沿

### 已知问题

1. **Reward Hacking**：模型学会钻 RM 的空子（生成长但无意义的文本以获得高分）
2. **Sycophancy**：模型过于迎合用户（附和错误观点）
3. **Alignment Tax**：对齐后基准测试性能下降
4. **幻觉**：RLHF 不能完全消除幻觉

### 前沿方向

| 方法 | 核心思想 | 代表 |
|------|---------|------|
| Constitutional AI | AI 自己给 AI 做反馈（不用人工排序） | Claude |
| RLAIF | 用更强的 AI 当 Reward Model | Constitutional AI |
| DPO | 跳过 RM，直接从偏好训练 | Zephyr |
| KTO | 单样本偏好（不需要成对比较） | |
| GRPO | 组相对策略优化（DeepSeek 用） | DeepSeek-R1 |

---

## 七、和你的 tinyrl 的交叉

你的 `tinyrl/rlhf.py` 实现了：
- ✅ RewardModel（Bradley-Terry 训练）
- ✅ PPO 模拟器（clipped surrogate）
- ✅ RM + PPO 联合流程

**你理解了 ChatGPT 的对齐原理。**

---

## 八、一句话总结

> RLHF = SFT（学会遵循指令）+ RM（学会人类偏好）+ PPO（用偏好优化策略）。
>
> ChatGPT = GPT-3（预训练）+ RLHF（对齐）。没有 RLHF，GPT-3 只是一个补全机器；有了 RLHF，它变成了一个助手。
>
> **DPO 是 RLHF 的简化版——用数学等价变换跳过 RM，直接从偏好数据训练。**

---

*配套：[tinyrl/rlhf.py](../projects/tinyrl/rlhf.py) | [nanoGPT精读](nanoGPT-读懂最小GPT.md) | [transformer-attention-deep-精读](transformer-attention-deep-精读.md)*
