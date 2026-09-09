# MXFP4 QAT 深度分析：量化从 PTQ 走向训练原生

> Kimi K3（2026-07-16）开创 · MXFP4 权重 + MXFP8 激活 · 从 SFT 阶段开始量化
> 代表量化从"推理优化"走向"训练原生"的转折点

## TL;DR

2026 年 7 月前，LLM 量化的主流是 **PTQ**（训练完再压）。Kimi K3 把 **MXFP4 QAT**（Quantization-Aware Training）推到万亿参数级——**从 SFT 阶段就开始量化**，模型在训练中学会补偿量化误差。这让 2.8T 模型的权重只需 ~1.4 TB（vs FP16 的 ~5.6 TB），自托管进入可行区间。这是量化范式的根本转变。

---

## 1. PTQ vs QAT 的根本区别

### 1.1 时间轴对比

```
PTQ（传统）：
  [FP16 预训练] → [FP16 SFT/RLHF] → [训练完成] → [量化压缩] → [int4 推理]
                                                    ↑
                                              量化误差是"事后补救"

QAT（Kimi K3）：
  [FP16/BF16 预训练] → [MXFP4 量化 SFT] → [MXFP4 RLHF] → [MXFP4 推理]
                         ↑                    ↑
                    模型学会在 4bit 下工作    量化误差在 RL 阶段也被优化
```

### 1.2 为什么 QAT 精度更好

PTQ 的量化误差是"事后"引入的——模型没见过量化后的数值分布，误差只能靠 GPTQ/AWQ 的数学技巧"补"。

QAT 的量化误差是"训练中"引入的——**模型在反向传播时见到量化后的梯度**，学会调整权重分布来"绕过"量化损失。这就像运动员在高原训练（低氧=量化误差）后回到平原（推理）会更强。

### 1.3 为什么 QAT 以前不流行

QAT 的代价是**训练成本翻倍**（每次 forward 都要模拟量化 + 反量化）。在 100B 规模下 QAT 已经很贵，万亿级别几乎不可行。Kimi K3 的工程突破是**把 QAT 的开销控制到可接受**（具体方法未完全公开，推测用了 straight-through estimator + selective quantization）。

---

## 2. MXFP4 = Microscaling FP4

### 2.1 什么是 MXFP4

**MXFP4**（Microscaling FP4）是 OCP（Open Compute Project）的 MX（Microscaling）格式标准：
- 每个权重 **4 bit 浮点**（不是整数！）：1 sign + 2 exponent + 1 mantissa
- 配 **per-block scaling factor**（通常 32 个权重共享一个 scale）
- NVIDIA Blackwell 原生支持 / AMD MI400 支持 / Intel 未来支持

### 2.2 为什么用浮点而非整数

| | INT4 | FP4 |
|---|---|---|
| 表示 | 均匀量化（等距格点）| 非均匀（指数格点，小值密集大值稀疏）|
| 适合分布 | 均匀分布 | **正态分布**（LLM 权重通常是）|
| 动态范围 | 小 | 大（指数部分提供）|

**LLM 权重分布是近似正态的**（大部分集中在 0 附近，少数 outlier）—— FP4 的非均匀格点天然匹配这个分布，比 INT4 更精确。

### 2.3 MXFP4 vs MXFP8 的分工

Kimi K3 用 **MXFP4 权重 + MXFP8 激活**：
- **权重用 4bit**：权重是静态的（训练完不变），可以更激进地压缩
- **激活用 8bit**：激活有大量 outlier（某些 channel 的激活值比平均大 100×），4bit 会崩，8bit 更安全

这个分工和现有 PTQ 量化的经验一致（weight-only 量化主流），但 K3 把它推到了 QAT 范式。

---

## 3. 对硬件生态的影响

### 3.1 硬件支持矩阵

| 硬件 | MXFP4 | MXFP8 | BF16 | INT8 SDOT |
|---|---|---|---|---|
| NVIDIA Blackwell (B200) | ✅ 原生 | ✅ | ✅ | ✅ |
| NVIDIA Hopper (H100) | ❌ | ✅ | ✅ | ✅ |
| AMD MI400 | ✅ | ✅ | ✅ | ✅ |
| **飞腾 D3000** | **❌** | **❌** | **❌** | ✅（SDOT）|

**关键洞察**：MXFP4 需要 Blackwell+ 级 GPU。飞腾 D3000（模块 14 §05 §11）走的是完全不同的路径——INT8 + SDOT，不依赖浮点格式。

### 3.2 国产硬件的"量化路径分叉"

| 路径 | 硬件 | 量化格式 | 优势 | 劣势 |
|---|---|---|---|---|
| **浮点路径** | NVIDIA / AMD | MXFP4 / FP8 | 精度好、生态成熟 | 硬件门槛高（Blackwell+）|
| **整数路径** | 飞腾 / 鲲鹏 | INT8 SDOT | 硬件门槛低、信创合规 | 精度略差、需要校准 |

这是信创 AI 的一个根本张力：**国产 CPU 走整数路径，国际 GPU 走浮点路径**——两者的量化策略和算子库不能直接互通。

---

## 4. 对项目各模块的影响

### 4.1 模块 12 §05 §12.3 量化矩阵

现有 §12.3 列了 25+ 量化后端，但都是 PTQ。MXFP4 QAT 是第一个**训练时量化**的大规模实践，应在 §12.3 补为"第四大范式"（vs GPTQ/AWQ/HQQ 的三大 PTQ 方法）。

### 4.2 模块 14 §05 §11 飞腾 D3000

D3000 的 INT8+SDOT 路径和 MXFP4 QAT 是**两条不兼容的量化路线**。模块 14 §05 §11.7「不支持的特性」已提到"无 BF16/无 i8mm"，MXFP4 是另一个 D3000 不支持的新格式。

### 4.3 模块 13 §13 形式化 Agent

QAT 的一个隐含优势：**量化后的模型更容易形式化验证**（因为数值空间小——4bit 只有 16 个值）。这与 Certigrad4 的"verified ML"思路有交叉——未来可能"QAT + 形式化验证"结合，让量化模型既有精度又有数学保证。

---

## 5. 预测：QAT 会成为标配吗？

**乐观**：
- Kimi K3 / DeepSeek V4 Pro 都用了 QAT
- Blackwell / MI400 原生支持 MXFP4
- 自托管万亿模型的需求驱动

**保守**：
- QAT 训练成本高（翻倍）
- PTQ 的精度已经很好（<1% loss），QAT 的边际收益递减
- 大多数团队没有万亿模型，PTQ 够用

**判断**：QAT 会在**万亿级开源模型**（Kimi/DeepSeek/GLM）中成为标配，但**百亿级闭源 API**（GPT/Claude）可能继续用 PTQ（因为 API 不暴露量化层，用户不关心）。

---

## 6. 来源

- [Kimi K3 技术概览](https://openlm.ai/kimi-k3/)（官方 QAT 配方）
- [HF Blog MXFP4 分析](https://huggingface.co/blog/ResterChed/kimi-k3-model-overview-mxfp4-quantization-open-wei)
- OCP MX Format Specification（Microscaling 格式标准）
- NVIDIA Blackwell 架构白皮书（MXFP4 硬件支持）
