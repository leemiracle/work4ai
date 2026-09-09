# Fine-tuning 全景精读：Full / LoRA / QLoRA / Adapter / Prompt Tuning

> 参照：Hu 2021 (LoRA) / Dettmers 2023 (QLoRA) / Houlsby 2019 (Adapter)
>
> csdiy 对应：tinylora(原) + nanoGPT精读 + mixed-precision精读

---

## 一、为什么需要 Fine-tuning

```
预训练模型（如 LLaMA-7B）:
  → 学了通用语言能力
  → 但不会特定任务（医疗问答/法律分析/代码生成）

Fine-tuning:
  → 在预训练权重上继续训练
  → 用少量任务数据 → 适应特定场景
```

---

## 二、Fine-tuning 方法分类

```
按可训练参数量排序：

Full Fine-tuning        → 100% 参数可训练（最贵）
Adapter Tuning          → 在每层插入小模块（5-10% 参数）
LoRA                    → 低秩适配器（0.5-2% 参数）
QLoRA                   → LoRA + 4-bit 量化（0.5% 参数 + 省显存）
Prompt Tuning           → 只训练 prompt 向量（0.01% 参数）
Prefix Tuning           → Prompt Tuning 变体（每层加 prefix）
```

---

## 三、Full Fine-tuning

```python
# 所有参数可训练
model = AutoModelForCausalLM.from_pretrained("llama-7b")
optimizer = AdamW(model.parameters(), lr=2e-5)
# → 7B × (2 bytes BF16 + 2 bytes grad + 12 bytes optimizer) = 112GB
```

**问题**：显存巨大（7B 需要 ~112GB）→ 消费级 GPU 不可能。

---

## 四、LoRA（Low-Rank Adaptation）

### 数学原理

```
原始: Y = X · W    (W 是 d×d 权重矩阵)

LoRA: Y = X · (W + ΔW)
          = X · (W + B · A)

  W: 冻结（不训练）
  A: d×r 矩阵（随机初始化，正态）
  B: r×d 矩阵（零初始化 → 初始 ΔW=0）
  r: 秩（通常 4-64，远小于 d）

可训练参数: r×d + d×r = 2rd（vs 全量 d²）
```

### 压缩比

```
d=4096, r=8:
  全量: 4096² = 16.7M 参数
  LoRA: 2 × 8 × 4096 = 65K 参数
  压缩: 256x

7B 模型全量微调: 112GB
7B 模型 LoRA: ~200MB 可训练参数 + 14GB 冻结权重 = 14.2GB
→ 一张 16GB GPU 就能微调 7B
```

### LoRA 的超参数

| 参数 | 典型值 | 影响 |
|------|--------|------|
| r (rank) | 8, 16, 32, 64 | 越大 → 表达力越强 → 更容易过拟合 |
| alpha | 2r 或 16 | LoRA 缩放因子（ΔW = α/r × BA）|
| target_modules | q_proj, v_proj | 哪些层加 LoRA（通常只加 Attention） |
| dropout | 0.05-0.1 | LoRA 层的 dropout |

### 哪些层加 LoRA

```
常见选择（按效果递减）：
  1. Q, K, V, O projection（Attention 的 4 个权重）→ 效果最好
  2. Gate, Up, Down projection（FFN 的 3 个权重）→ 增量效果
  3. Embedding + LM Head → 通常不加（太大了）

推荐：Q+V（最经典）或 Q+K+V+O+Gate+Up+Down（最大效果）
```

---

## 五、QLoRA（Quantized LoRA）

### 创新：4-bit 冻结权重 + LoRA

```python
# QLoRA 的三步创新：
# 1. NF4 量化（Normal Float 4-bit）
model = AutoModelForCausalLM.from_pretrained("llama-7b",
    load_in_4bit=True,           # ← 冻结权重量化到 4-bit
    bnb_4bit_quant_type="nf4",   # ← NF4 量化
    bnb_4bit_compute_dtype="bf16") # ← 计算时反量化到 BF16

# 2. LoRA 适配器（正常精度训练）
lora_config = LoraConfig(r=16, lora_alpha=32,
    target_modules=["q_proj","v_proj"])

# 3. Paged Optimizer（vLLM 同款的页式内存管理）
# → 防止显存碎片导致的 OOM
```

### 显存对比

```
7B 模型:
  Full FT (FP32):     112GB
  LoRA (BF16):         16GB
  QLoRA (4-bit):        6GB  ← 7B 模型在 RTX 4060 上微调！

70B 模型:
  Full FT:            1120GB
  QLoRA:               48GB  ← 一张 A100 就行
```

---

## 六、Adapter Tuning

### 原理

```
在每层 Transformer Block 中插入小模块：

原始 Block:
  x → Attention → FFN → output

Adapter Block:
  x → Attention → FFN → [Adapter] → output
                         ↓
                    Down → ReLU → Up
                    (d → r → d)

Adapter 参数: 2dr per layer（和 LoRA 类似）
但 Adapter 增加了推理延迟（LoRA 可以合并到权重中）
```

### vs LoRA

| 维度 | Adapter | LoRA |
|------|---------|------|
| 插入位置 | 层内新模块 | 权重旁路 |
| 推理延迟 | 增加（多一层计算） | **零**（可合并到 W） |
| 参数量 | 类似 | 类似 |
| 效果 | 类似 | 类似 |

**LoRA 更受欢迎**因为推理无额外延迟。

---

## 七、Prompt/Prefix Tuning

### Prompt Tuning

```
不修改模型权重，只训练一段"软 prompt"（连续向量）：

输入 = [soft_prompt (可训练)] + [actual_tokens (不训练)]
         ↑ 100-1000 个可训练向量

参数量: prompt_len × d_model ≈ 0.01% 模型参数
```

### Prefix Tuning

```
Prompt Tuning 的变体：每层都加 prefix

每层的前缀 = 可训练的 key-value 对
→ 在 Attention 的 KV Cache 前面插入可训练的前缀

效果比 Prompt Tuning 好（每层都有可调参数）
```

---

## 八、选择决策树

```
你的显存够大吗？
├── 够（≥4×模型大小）→ Full Fine-tuning（效果最好）
├── 不够但能放下模型
│   ├── 需要最快推理 → LoRA（可合并权重）
│   └── 需要最省显存 → QLoRA（4-bit 冻结）
└── 放不下模型
    └── Prompt/Prefix Tuning（只需 prompt 参数）
```

### 推荐配置

| 模型大小 | GPU | 推荐方法 | 可训练参数 |
|---------|-----|---------|-----------|
| 7B | RTX 4090 (24GB) | QLoRA r=16 | ~50MB |
| 7B | A100 (80GB) | LoRA r=32 | ~200MB |
| 13B | RTX 4090 | QLoRA r=8 | ~30MB |
| 70B | A100×4 | QLoRA r=16 | ~200MB |
| 7B | A100×8 | Full FT | 14GB |

---

## 九、一句话总结

> LoRA = 冻结大权重 + 训练低秩 ΔW = BA → 0.5% 参数微调。
>
> QLoRA = LoRA + 4-bit 量化 → 7B 模型只需 6GB 显存。
>
> **LoRA 是当前 LLM 微调的事实标准（HuggingFace PEFT / Axolotl / Unsloth 全支持）。**

---

*配套：[mixed-precision精读](mixed-precision-精读.md) | [nanoGPT精读](nanoGPT-读懂最小GPT.md) | [tinytorch/optim.py](../projects/tinytorch/optim.py)*
