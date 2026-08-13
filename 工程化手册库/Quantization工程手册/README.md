# Quantization（量化）工程手册

> **建立**：2026-08-13
> **是什么**：把模型权重从 fp16/bf16 压缩到 int8/int4/int2，降低显存 + 加速推理。
> **为什么重要**：70B fp16 = 140GB（2 张 A100）；70B int4 = 35GB（1 张 A100）。**量化让大模型平民化**。

---

## 1. 是什么 + 为什么

**量化** = 降低数值精度（fp32 → fp16 → bf16 → int8 → int4 → int2）。

**核心 tradeoff**：
- 精度 ↓ → 显存 ↓ + 速度 ↑ + 质量 ↓
- **但**：大模型对量化极不敏感（70B int4 ≈ 70B fp16）

**2026 主流**：
- 训练：bf16（默认）/ fp8（H100）
- 推理：int4（端侧）/ int8（服务器）/ fp8（H100）

---

## 2. 听说读写 4 能力

| 能力 | 含义 |
|------|------|
| **听** | 解析一个量化方案（GPTQ/AWQ/NF4/...）|
| **说** | 用量化圈行话（per-channel/group-size/activation quant）|
| **读** | 读量化论文（GPTQ 2022 / AWQ 2023 / QLoRA 2023 / SpinQuant 2024）|
| **写** | 实现量化 pipeline |

---

## 3. PMMEA 解析框架

```
P - Precision（精度）：目标精度（int4/int8/fp8）
M - Method（方法）：量化算法（RTN/GPTQ/AWQ/NF4/SpinQuant）
M - Mapping（映射）：per-tensor / per-channel / per-group
E - Evaluation（评估）：PPL / 下游任务 / 人类评估
A - Acceleration（加速）：硬件支持（CUDA/Triton/Metal）
```

---

## 4. 6 维度评价

| 维度 | 指标 |
|------|------|
| **1. 准确性** | PPL（困惑度）/ 下游任务准确率 / vs fp16 差距 |
| **2. 稳健性** | 不同模型 / 不同层量化敏感度 |
| **3. 可迁移性** | 跨硬件（NVIDIA/AMD/CPU/Mac）|
| **4. 效率** | 显存节省 / 速度提升 / 能耗 |
| **5. 可控性** | 量化误差可控 + 可调试 |
| **6. 安全性** | 量化引入 bias / 后门 |

---

## 5. 工具栈（2026-08）

| 工具 | 方法 | 用途 |
|------|------|------|
| **bitsandbytes** | NF4 / int8 | QLoRA 配套 |
| **AutoGPTQ** | GPTQ | 后训练量化 |
| **AutoAWQ** | AWQ | MIT Han Lab |
| **llama.cpp GGUF** | k-quants | CPU/Mac 推理 |
| **compressed-tensors** | 通用 | vLLM 标准 |
| **TensorRT-LLM** | FP8 / INT4 | NVIDIA 最优 |
| **Apple MLX** | int4 | Mac 优化 |
| **NVIDIA ModelOpt** | NVFP4 | Blackwell |

---

## 6. 量化方法对比

| 方法 | 精度 | 校准数据 | 速度 | 质量 | 适用 |
|------|------|---------|------|------|------|
| **RTN**（Round-to-Nearest）| 任意 | 无 | 最快 | 差 | 玩具 |
| **GPTQ**（2022）| int4/int8 | 需要 | 中 | 好 | 通用 |
| **AWQ**（2023）| int4 | 需要 | 快 | 很好 | vLLM |
| **NF4**（QLoRA, 2023）| 4-bit | 无 | 快 | 好 | 微调 |
| **SpinQuant**（2024）| int4 | 需要 | 快 | 最好 | Meta 最新 |
| **FP8**（H100）| 8-bit float | 训练时 | 最快 | 极好 | H100/H200 |
| **NVFP4**（Blackwell）| 4-bit float | 训练时 | 极快 | 极好 | B100/B200 |

---

## 7. 实战案例

### 案例 1：用 bitsandbytes 量化 Llama 3.1 8B 到 NF4

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=bnb_config,
)
# 8B fp16 = 16GB → NF4 = 5GB（省 70%）
```

### 案例 2：用 AutoAWQ 量化（vLLM 部署用）

```python
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_pretrained("meta-llama/Llama-3.1-70B")
model.quantize("meta-llama/Llama-3.1-70B", quant_config={
    "zero_point": True,
    "q_group_size": 128,
})
model.save_quantized("./llama-70b-awq")
# 70B fp16 = 140GB → AWQ int4 = 35GB
```

### 案例 3：用 llama.cpp 转 GGUF（CPU/Mac 推理）

```bash
# 下载原模型 → 转 GGUF → 量化
python convert_llama_to_gguf.py --model Llama-3.1-8B
./llama-quantize Llama-3.1-8B.gguf Llama-3.1-8B-Q4_K_M.gguf Q4_K_M
# 8B fp16 = 16GB → Q4_K_M = 4.5GB（MacBook Air 可跑）
```

---

## 8. 反模式 10 条

1. **量化小模型**：1B 模型量化后质量崩（大模型才耐量化）
2. **per-tensor 量化**：精度差（用 per-channel / per-group）
3. **忽略 group_size**：128 是甜点（太小慢，太大精度差）
4. **不评估就上线**：必须跑 PPL + 下游任务
5. **量化 KV cache 不评估**：KV 量化对长 context 影响大
6. **混合精度不记录**：哪些层量化哪些不量，要文档化
7. **硬件不匹配**：GGUF 在 NVIDIA 上不如 GPTQ
8. **忽略 activation 量化**：只量化权重不够（W8A8 比 W8A16 快）
9. **过度量化**：int2 在大多数任务上崩
10. **不校准**：GPTQ/AWQ 需要校准数据（128-512 样本）

---

## 9. 下一步

- 读 QLoRA 论文（arXiv 2305.14314）
- 读 AWQ 论文（arXiv 2306.00978）
- 用 bitsandbytes 跑 NF4 量化
- 用 vLLM 部署 AWQ 模型

---

**版本**：v1.0（2026-08-13）
**核心理念**：**量化让大模型平民化。70B int4 在单卡 A100 跑 = 生产力革命。**
