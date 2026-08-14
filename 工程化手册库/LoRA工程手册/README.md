# LoRA 工程手册

> **建立**：2026-08-13
> **是什么**：LoRA = Low-Rank Adaptation。冻结原权重，学一个低秩更新 ΔW = BA。
> **为什么重要**：训练参数少 100 倍 + 显存省 70% + 效果接近 full fine-tune → **大模型微调的工业标准**。

---

## 1. 是什么 + 为什么

### 是什么

**LoRA**（Edward Hu, Microsoft, 2021）：

```
原模型：Y = W · X         （W 是 d×d，冻结）
LoRA：  Y = (W + BA) · X   （B 是 d×r，A 是 r×d，r << d）
```

- **只训练 B 和 A**（2dr 参数，r 通常 4-64）
- **推理时合并**：W' = W + BA → 无额外延迟
- **多个 LoRA 可切换**：不同任务不同 LoRA，热切换

**演进**：
- **LoRA**（2021）：原始
- **QLoRA**（Tim Dettmers 2023）：4-bit 量化 + LoRA → 1 张卡微调 65B
- **DoRA**（2024）：分解权重为方向 + 幅度
- **PiSSA**（2024）：用 SVD 初始化 LoRA
- **LoRA+**（2024）：B 和 A 用不同学习率

### 为什么

| 维度 | Full Fine-tune | LoRA |
|------|---------------|------|
| 训练参数 | 7B | 10-100M（少 100x）|
| 显存 | 80GB+ | 20GB（省 70%）|
| 效果 | 基准 | 接近（差 0-2%）|
| 多任务 | 每任务一份权重 | 每任务一个 50MB LoRA |
| 推理延迟 | 基准 | 可合并 = 0 额外延迟 |
| 存储 | 每任务 14GB | 每任务 50MB |

---

## 2. 听说读写 4 能力

| 能力 | 含义 |
|------|------|
| **听** | 解析一个 LoRA 配置（rank / alpha / target modules / dropout）|
| **说** | 用 LoRA 圈行话（rank / alpha / target modules / QLoRA / adapter）|
| **读** | 读 LoRA 论文（Hu 2021）/ QLoRA（Dettmers 2023）/ DoRA（2024）|
| **写** | 用 LoRA 微调一个模型 + 部署 |

---

## 3. RADME 解析框架

```
R - Rank（秩）：r 值（4/8/16/64），决定表达能力
A - Alpha（缩放）：ΔW 实际 = α/r · BA，控制更新强度
D - Dropout：LoRA 层的 dropout（防过拟合）
M - Modules（目标模块）：哪些层加 LoRA（q_proj / v_proj / 全部）
E - Evaluation（评估）：下游任务 + perplexity
```

### R · Rank
- **r=4**：轻量（适合风格调整）
- **r=8-16**：通用（大多数任务甜点）
- **r=64+**：重任务（需要新知识）

**为什么 rank 有效**？**预训练权重已经低秩**——微调只需要在低维子空间内调整。

### A · Alpha
- 经验：alpha = 2 × rank（如 r=8, alpha=16）
- alpha 太大 → 过拟合；太小 → 学不到

### M · Modules
- **最小配置**：`q_proj, v_proj`（attention 的 Q 和 V）
- **推荐配置**：`q_proj, k_proj, v_proj, o_proj`（全 attention）
- **最强配置**：all-linear（attention + MLP）

### D · Dropout
- 通常 0.05-0.1
- 大 LoRA（r=64+）需要更多 dropout

### E · Evaluation
- 下游任务准确率
- Perplexity（语言建模）
- **vs Full FT 基准**

---

## 4. 6 维度评价

| 维度 | 指标 |
|------|------|
| **1. 准确性** | vs Full FT 差距（目标 < 2%）|
| **2. 效率** | 训练显存 / 时间 / 参数量 |
| **3. 可迁移性** | LoRA 在不同 base model 上 |
| **4. 可控性** | alpha / rank 调节效果可预测 |
| **5. 部署性** | 推理延迟 / 多 LoRA 切换 |
| **6. 安全性** | 不会"忘记"原能力（灾难性遗忘少）|

---

## 5. 工具栈（2026-08）

| 工具 | 特点 |
|------|------|
| **PEFT**（HuggingFace）| LoRA / QLoRA / DoRA 标准库 |
| **TRL**（HuggingFace）| SFT / DPO / PPO + LoRA |
| **Unsloth** | 2x 速度 + 省显存（CUDA 优化）|
| **Axolotl** | 配置驱动微调 |
| **LLaMA-Factory** | 中文友好 |
| **AutoLoRA** | 自动找 rank |
| **bitsandbytes** | QLoRA 的量化后端 |

---

## 6. 跨平台差异

| 场景 | 推荐 |
|------|------|
| **单卡 24GB** | QLoRA（4-bit + LoRA r=8）|
| **单卡 80GB** | LoRA（fp16，r=16）|
| **多卡** | 多 LoRA 并行训练 |
| **Mac** | MLX + LoRA |
| **CPU** | llama.cpp + LoRA |

---

## 7. 实战案例

### 案例：用 QLoRA 微调 Llama 3.1 8B（单卡 24GB）

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
import torch

# Step 1: 4-bit 量化加载
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=bnb_config,
    device_map="auto",
)
model = prepare_model_for_kbit_training(model)

# Step 2: LoRA 配置
lora_config = LoraConfig(
    r=16,                                    # rank
    lora_alpha=32,                           # alpha = 2 * r
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],  # all-linear
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 42M || all params: 8B || trainable%: 0.52%

# Step 3: 训练
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=SFTConfig(
        output_dir="./lora-output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
    ),
    formatting_func=format_instruction,  # 你的数据格式化函数
)

trainer.train()

# Step 4: 保存（只有 50MB）
model.save_pretrained("./lora-output")
# 只保存 LoRA 权重（B 和 A），不保存原模型

# Step 5: 推理（合并或热加载）
# 方式 A: 合并到 base model
merged = model.merge_and_unload()
merged.save_pretrained("./merged-model")

# 方式 B: 热加载（vLLM 多 LoRA）
# vllm serve meta-llama/Llama-3.1-8B --enable-lora --lora-modules my-lora=./lora-output
```

### 高级：多 LoRA 部署（vLLM）

```bash
# 一个 base model + N 个 LoRA
vllm serve meta-llama/Llama-3.1-8B \
    --enable-lora \
    --lora-modules \
        sql-lora=./loras/sql \
        code-lora=./loras/code \
        chat-lora=./loras/chat

# 请求时指定 LoRA
curl http://localhost:8000/v1/chat/completions \
    -d '{"model": "sql-lora", "messages": [...]}'
```

---

## 8. 反模式 10 条

1. **rank 太高**（r=256）→ 过拟合 + 显存浪费
2. **rank 太低**（r=1）→ 表达力不足
3. **只对 Q/V 加 LoRA**（漏了 MLP）→ 效果差
4. **alpha = rank**（应该是 2x）→ 更新太弱
5. **学习率太大**（>5e-4）→ 训练崩
6. **学习率太小**（<1e-5）→ 学不到
7. **不做量化就上大模型**（70B fp16 需要 140GB）
8. **评估只用 loss**（不看下游任务）→ 过拟合
9. **不保存 base model info**（不知道是哪个 base）→ 版本混乱
10. **推理时不合并**（额外延迟）→ 生产慢

---

## 9. 下一步

- 读 LoRA 论文（arXiv 2106.09685）
- 读 QLoRA 论文（arXiv 2305.14314）
- 用 PEFT + TRL 跑通 QLoRA 微调
- 试 Unsloth（2x 加速）
- 多 LoRA 部署（vLLM）

---

**版本**：v1.0（2026-08-13）
**核心理念**：**LoRA 让微调民主化。1 张卡 + 50MB = 定制大模型。**
