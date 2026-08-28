# Fine-tuning 工程手册

> **是什么**：大模型微调全景——SFT → DPO → GRPO → LoRA，从"通用基座"到"听话专家"。
> **为什么重要**：预训练模型是"通才"，微调是**让它成为你的专家**。这是 LLM 应用层的核心工程。

---

## 1. 微调全景图

```
预训练（base model）
    ↓
SFT（Supervised Fine-Tuning）  — 学"怎么回答"
    ↓
Preference Alignment           — 学"什么是对的"
    ├─ RLHF（PPO + reward model）
    ├─ DPO（Direct Preference Optimization）
    └─ GRPO（Group Relative Policy Optimization）
    ↓
高效微调（Parameter-Efficient）
    ├─ LoRA / QLoRA / DoRA
    └─ Prefix Tuning / Adapter
```

## 2. 5 种微调方法对比

| 方法 | 原理 | 数据 | 成本 | 效果 | 适用 |
|------|------|------|------|------|------|
| **Full FT** | 更新所有权重 | 指令对 | 极高 | 最强 | 预算充足 |
| **SFT** | 监督学习"理想回答" | (prompt, ideal_response) | 中 | 强 | 格式/风格 |
| **RLHF** | reward model + PPO | 排序数据 | 高 | 强 | 对齐 |
| **DPO** | 直接用偏好数据 | (prompt, chosen, rejected) | 中 | 强 | 对齐（推荐）|
| **GRPO** | 规则驱动（verifiable reward） | 可验证任务 | 中 | 强 | 数学/代码 |

### SFT（Supervised Fine-Tuning）
- **数据**：(prompt, ideal_response) 对
- **方法**：标准交叉熵 loss
- **作用**：教模型"**怎么回答**"（格式/风格/指令遵循）
- **工具**：TRL SFTTrainer
- **深读**：[`讲透微调/SFT全景综合-2026-08`](../../讲透模型/讲透微调/SFT全景综合-2026-08.md)——数据工程/超参机械理由/LoRA 入侵维度/推理时代 SFT×RL 分工/Agent 轨迹 SFT 的工程级收口

### DPO（Direct Preference Optimization, 2023）
- **数据**：(prompt, chosen_response, rejected_response)
- **公式**：`L = -log σ(β · [log π(y_w)/π_ref(y_w) - log π(y_l)/π_ref(y_l)])`
- **关键**：**不需要 reward model，不需要 RL**
- **为什么有效**：Reward model 隐含在策略本身里（数学推导证明）
- **工具**：TRL DPOTrainer

### GRPO（Group Relative Policy Optimization, 2024 DeepSeek）
- **数据**：可验证任务（数学/代码/证明）
- **方法**：生成 N 个回答 → 用规则评分 → group 内相对优化
- **关键**：**不需要 reward model**，规则就是裁判
- **代表**：DeepSeek R1（数学接近 o1）

## 3. 听说读写

| 能力 | 含义 |
|------|------|
| **听** | 解析一个微调 pipeline（数据/方法/超参/评估）|
| **说** | SFT / DPO / GRPO / KL penalty / reward hacking |
| **读** | Hu 2021 (LoRA) / Rafailov 2023 (DPO) / Shao 2024 (GRPO) |
| **写** | 跑通一个完整的微调 pipeline |

## 4. 多视角深层

### 📐 数学
- SFT = 最大似然估计（MLE）
- DPO = 变分下界（隐含 reward = log π/π_ref）
- GRPO = group-normalized 策略梯度

### 🧠 认知科学
- SFT ≈ 模仿学习（小孩模仿大人）
- DPO ≈ 偏好学习（小孩从"对/错"反馈学）
- GRPO ≈ 规则学习（小孩从"规则"学，如数学对错）

### 💰 经济学
- Full FT = 大投入大回报
- LoRA = 小投入接近大回报（**ROI 最高**）
- DPO 比 RLHF 便宜 5-10x（不需要 reward model）

### 🏛️ 哲学
- SFT 学"**行为**"
- DPO/GRPO 学"**价值观**"
- **本质问题**：学的是"价值观"还是"讨好"？→ Sycophancy 问题

## 5. 工具栈

| 工具 | 用途 |
|------|------|
| **TRL**（HuggingFace）| SFT/DPO/PPO 标准库 |
| **PEFT** | LoRA/QLoRA |
| **Unsloth** | 2x 加速 |
| **Axolotl** | 配置驱动 |
| **LLaMA-Factory** | 中文友好 |
| **OpenRLHF** | 大规模 RLHF |

## 6. 实战：完整 pipeline

```python
from trl import SFTTrainer, DPOTrainer
from peft import LoraConfig

# Step 1: SFT
sft_trainer = SFTTrainer(
    model="meta-llama/Llama-3.1-8B",
    train_dataset=sft_data,  # (prompt, response)
    peft_config=LoraConfig(r=16, lora_alpha=32, ...),
    args=TrainingArguments(learning_rate=2e-4, ...),
)
sft_trainer.train()

# Step 2: DPO（基于 SFT 模型）
dpo_trainer = DPOTrainer(
    model=sft_trainer.model,
    train_dataset=dpo_data,  # (prompt, chosen, rejected)
    beta=0.1,
    peft_config=LoraConfig(r=16, ...),
)
dpo_trainer.train()
```

## 7. 反模式 10 条

1. **SFT 数据太少**（<100 条）→ 过拟合
2. **DPO beta 太大**（>0.5）→ 偏离参考模型太远
3. **DPO beta 太小**（<0.01）→ 学不到偏好
4. **不做 SFT 直接 DPO**（模型没"行为基础"）
5. **学习率太高**（>5e-4）→ 训练崩
6. **评估只用 loss**（必须看下游任务）
7. **reward hacking**（模型学会骗 reward model）
8. **灾难性遗忘**（微调后忘了预训练能力）
9. **数据不清洗**（低质量指令 → 低质量模型）
10. **不做 A/B 测试就上线**

---

**核心理念**：**SFT 教"怎么回答"，DPO/GRPO 教"什么是对的"。LoRA 让这一切便宜 100 倍。**
