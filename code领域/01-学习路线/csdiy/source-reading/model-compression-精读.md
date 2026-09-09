# 模型压缩精读：量化 / 剪枝 / 蒸馏

> 参照：Han 2015 (Deep Compression) / Dettmers 2023 (QLoRA) / Hinton 2015 (Distillation)
>
> csdiy 对应：mixed-precision精读 + fine-tuning精读 + tinyquantize

---

## 一、为什么需要压缩

```
LLaMA-70B FP16: 140GB → 一张 A100 (80GB) 放不下
LLaMA-70B INT4:  35GB → 一张 A100 轻松部署

7B 模型:
  FP32: 28GB → 消费级 GPU 无法部署
  INT4:  3.5GB → 手机/树莓派可运行
```

三大方法：量化（降精度）+ 剪枝（删参数）+ 蒸馏（小模型学大模型）。

---

## 二、量化（Quantization）

### Post-Training Quantization (PTQ)

训练后直接量化，不需要重新训练。

```python
# 对称量化（参照 tinyquantize）
scale = max(abs(weights)) / 127
quantized = round(weights / scale)  # FP32 → INT8

# 反量化
dequantized = quantized * scale
```

### 量化方法对比

| 方法 | 精度 | 压缩比 | 需要校准数据 | 代表 |
|------|------|--------|------------|------|
| RTN (Round-to-Nearest) | 最简单 | 4x (INT8) | ❌ | GPTQ 基线 |
| GPTQ | 高 | 4-8x | ✅ 少量 | AutoGPTQ |
| AWQ | 高 | 4-8x | ✅ 少量 | Activation-aware |
| GGUF | 中 | 2-8x | ❌ | llama.cpp |
| BitsAndBytes | 中 | 4x | ❌ | QLoRA 用的 |
| SmoothQuant | 高 | 4x | ✅ | 解决激活值量化 |

### INT4 量化的效果

```
LLaMA-7B:
  FP16 (baseline): 准确率 100% (相对)
  INT8:            准确率 99.5%
  INT4 (AWQ):      准确率 98.5%
  INT4 (RTN):      准确率 92% (最差)
  INT3:            准确率 85% (可接受但不推荐)

→ INT4 是当前生产部署的甜点
```

### GGUF 格式（llama.cpp）

```
Q8_0:  8-bit 量化（质量最好，~7GB for 7B）
Q4_K_M: 4-bit 混合量化（推荐，~4GB）
Q3_K_S: 3-bit（最小，~3GB）
Q2_K:  2-bit（极小但质量差，~2.5GB）

→ M1 MacBook Air 可跑 LLaMA-7B（8GB 内存）
```

---

## 三、剪枝（Pruning）

### 非结构化剪枝（权重级别）

```
删除绝对值最小的权重（设为 0）：

# 稀疏度 50%
threshold = percentile(abs(weights), 50)
weights[abs(weights) < threshold] = 0

→ 50% 的权重为 0
→ 但稀疏矩阵在 GPU 上不加速（需要特殊硬件/软件支持）
```

### 结构化剪枝（通道/层级别）

```
删除整个通道/注意力头/层：

# 删除贡献最小的注意力头
head_importance = compute_head_importance(model)
prune_heads(model, least_important=20%)

→ 直接缩小模型 → 推理真的更快
→ 但需要重新训练恢复性能
```

### LLM 剪枝的挑战

```
LLM 参数太多（70B）→ 剪枝 + 重训练成本高
→ LLM 剪枝不如量化成熟
→ Wanda/SparseGPT 是当前最好的 LLM 剪枝方法（无重训练）
```

### Wanda（Sun 2023）

```
不需要重训练的 LLM 剪枝：
  按 |weight × activation| 排序 → 删除最小的
→ 50% 稀疏度，精度损失 <1%
→ 但需要稀疏矩阵支持（CUSPARSE）
```

---

## 四、知识蒸馏（Knowledge Distillation）

### 原理（参照 Hinton 2015）

```
Teacher（大模型）→ 生成 soft labels → Student（小模型）学习

Loss = α × CE(student, hard_labels)
     + (1-α) × T² × KL(student_soft || teacher_soft)

T = 温度（让 softmax 输出更"软"）
```

### 为什么 soft labels 有用

```
Hard labels (one-hot):  [1, 0, 0, 0]  ← 信息量: log(4) = 2 bits
Soft labels (T=5):      [0.7, 0.2, 0.08, 0.02]  ← 包含"类间关系"

例：分类"狗"时
  Hard: 只知道"这是狗"
  Soft: 知道"这更像狗，但和猫/狼也有点像"
→ Soft labels 包含"暗知识"（dark knowledge）
```

### LLM 蒸馏

```
方式 1: 序列级蒸馏
  Teacher 生成回复 → Student 作为训练数据

方式 2: Logit 蒸馏
  Student 直接学习 Teacher 的 logits 分布

方式 3: 特征蒸馏
  Student 学习 Teacher 的中间层 hidden states
```

### 代表成果

| Student | Teacher | 参数缩减 | 效果 |
|---------|---------|---------|------|
| DistilBERT | BERT | 110M→66M (40%) | 保留 97% |
| TinyBERT | BERT | 110M→66M | 保留 96% |
| Alpaca-7B | text-davinci-003 | 175B→7B | ~80% 能力 |
| Vicuna-7B | GPT-4 (序列级) | → 7B | ~90% 能力 |

---

## 五、三种方法组合

```
LLaMA-70B 部署优化：

① 量化: FP16 → INT4 (AWQ)
   140GB → 35GB

② 剪枝: 50% 稀疏度 (Wanda)
   35GB → ~18GB（如果支持稀疏）

③ 蒸馏: 70B → 7B (Vicuna 式)
   18GB → 3.5GB

→ 70B 能力压缩到树莓派可运行（但质量有损）
```

实际生产中通常只用**量化**（最成熟、精度损失最小）。

---

## 六、选择指南

```
你的部署场景？
├── 服务器 (A100/H100)
│   → FP16 或 BF16（不需要压缩）
├── 消费级 GPU (RTX 4090)
│   → INT4 (AWQ/GGUF Q4_K_M)
├── CPU/Mac
│   → GGUF Q4_K_M (llama.cpp)
├── 手机/嵌入式
│   → INT4 + 蒸馏 + 剪枝（激进压缩）
└── 边缘设备
    → 1-3B 蒸馏模型 + INT4
```

---

## 七、一句话总结

> 量化（INT4）= 最成熟的压缩方法 → 4x 压缩 + <2% 精度损失。
>
> 剪枝 = 删冗余参数 → 需要稀疏支持。
>
> 蒸馏 = 小模型学大模型 → DistilBERT 保留 97% 能力但小 40%。
>
> **生产首选：AWQ INT4 量化（质量/速度/兼容性最佳平衡）。**

---

*配套：[mixed-precision精读](mixed-precision-精读.md) | [fine-tuning-landscape精读](fine-tuning-landscape-精读.md) | [tinyquantize](../projects/tinyquantize/)*
