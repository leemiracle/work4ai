# 10 · 让 AI 省钱：高效 AI 的故事（2020-2026）

> **时间**：2020-2026，6 年
> **核心冲突**：大模型太贵 / 太慢 / 太大。怎么让普通人能用？
> **嵌入概念**：KV Cache、量化、LoRA、蒸馏、vLLM、FlashAttention

---

## 🎬 故事

### 2020 · GPT-3 推理成本

GPT-3 175B 推理成本：
- 1 张 V100 80GB 装不下
- 需要 5 张 V100（80GB × 5 = 400GB 显存）
- 推理 1 个 token 需要 ~50ms

**OpenAI 卖 API 一年亏几亿美元**——这是为什么 GPT-3 API 起初那么贵。

**问题**：怎么让推理便宜 / 快？

### 2021 · FlashAttention 革命

**Tri Dao**（Stanford PhD）2022 年发 **FlashAttention**（实际工作从 2021 开始）。

**问题**：标准 attention 在 GPU 上很慢——需要 O(N²) 内存读写。

**FlashAttention 的洞察**：attention 计算可以**重排**，让中间矩阵不离开 GPU SRAM。

**结果**：**attention 快 2-3 倍，显存省 5-10 倍**。

2023 **FlashAttention 2**：进一步优化。
2024 **FlashAttention 3**：H100 GPU 特化。

**所有主流 LLM 都用 FlashAttention**——一个内核优化改变了行业。

### 2022 · vLLM 横空出世

2023 年 6 月，**SkyPilot / Berkeley** 团队发 **vLLM**：

**核心创新**：**PagedAttention**——把 KV cache 当虚拟内存管理。

**之前**：每个请求预留连续显存。浪费 60-80%。
**vLLM**：KV cache 按块分配（像 OS 页表）。**吞吐量提升 2-24 倍**。

vLLM 一夜成为 LLM 推理标准。**所有云厂商都用 vLLM**。

2026-08 vLLM **v0.27.0**：561 commits / 242 contributors。

### 2021 · LoRA 让微调便宜

**Edward Hu**（Microsoft）2021 发 **LoRA**（Low-Rank Adaptation）：

**核心 idea**：不更新原始权重 W，**学一个低秩更新 ΔW = BA**（B 是 d×r，A 是 r×d，r << d）。

**结果**：
- 训练参数从 7B → **10-100M**（少 100 倍）
- 训练显存从 80GB → **20GB**
- **效果几乎不输 full fine-tune**

LoRA 一发，**所有 fine-tune 都用它**。

2023 **QLoRA**（Tim Dettmers）：4-bit 量化 + LoRA。**在 1 张 48GB 卡上微调 65B 模型**。

### 2023 · 量化时代

**量化（Quantization）** = 把 fp32 / bf16 权重转成 int8 / int4。

- **fp32**：4 字节 / 参数
- **bf16**：2 字节
- **int8**：1 字节（小 4 倍）
- **int4**：0.5 字节（小 8 倍）

**70B 模型 fp16 = 140GB**（要 2 张 A100 80GB）
**70B 模型 int4 = 35GB**（1 张 A100 即可）

主流量化方法：
- **GPTQ**（2022）
- **AWQ**（MIT Han Lab 2023）
- **bitsandbytes NF4**（QLoRA 配套）
- **GGUF**（llama.cpp 格式，CPU 友好）

### 2023 · llama.cpp 让 CPU 也能跑

**Georgi Gerganov**（保加利亚独立开发者）2023 年把 LLaMA 用纯 C++ 重写：

- **CPU / Mac M 系列**也能跑
- **GGUF 量化格式**：4-bit / 5-bit / 8-bit
- 13B 模型在 MacBook Air 上跑

**llama.cpp 让"本地 LLM"成为可能**——所有爱好者都用。

### 2024 · 端侧 AI 兴起

Apple Intelligence（2024 WWDC）：
- iPhone / Mac 内置 3B 模型
- 用户隐私数据不出设备
- 推理用 Neural Engine

**端侧 AI**：模型必须 < 10B + 量化 + 优化。

### 高效 AI 的 6 大方向（2025+）

1. **稀疏 attention**：Mamba / Linear Attention / Hybrid
2. **PD 分离**（Prefill/Decode）：解耦推理阶段
3. **KV 压缩**：减少 KV cache 内存
4. **推理加速**：vLLM / SGLang / TensorRT-LLM
5. **量化**：int4 / fp8 / NVFP4
6. **MoE**（Mixture of Experts）：参数多但激活少

---

## 🧠 核心概念

- **KV Cache**：自回归生成时缓存已计算的 K/V，避免重复计算。**LLM 推理核心优化**。
- **PagedAttention**：vLLM 把 KV cache 当虚拟内存管理。
- **FlashAttention**：重排 attention 计算，减少 HBM 读写。2-3x 速度。
- **LoRA**：低秩微调。参数少 100 倍，效果接近。
- **QLoRA**：4-bit + LoRA。1 张卡微调 65B。
- **量化**：fp16 → int4。显存小 8 倍。
- **蒸馏**：大模型"教"小模型。
- **MoE**（Mixture of Experts）：参数多但每次激活少。DeepSeek V3 / Mixtral 用。

## 🎨 类比

- **KV Cache** = 厨师做完每道菜**保留半成品**：下次再做同样菜时，从半成品开始，不用从头
- **PagedAttention** = 把厨房储物柜**按需分配**（不是每道菜预留一大堆储物柜）
- **FlashAttention** = 厨师**重新安排做菜顺序**，让中间半成品不离开操作台（少走动 = 快）
- **LoRA** = 不改原版书（大权重），**写一本薄薄的"修订笔记"**（低秩矩阵）
- **量化** = 把高清图片**压缩成 jpeg**：丢失一点质量，文件小 8 倍
- **蒸馏** = 大师（teacher）**手把手教徒弟（student）**：徒弟小，但学到精髓
- **MoE** = 一个公司**100 个部门**，但每个项目只用 5 个部门——参数多但实际工作量小

## 💡 反直觉发现

1. **算法优化比硬件更重要**：FlashAttention（2022 算法创新）让 attention 快 2-3 倍——**相当于免费换了一代 GPU**。

2. **vLLM 是工程突破不是算法突破**：vLLM 没发明新算法，**只是把 OS 虚拟内存思想搬到 KV cache**。**工程 = 算法的产物**。

3. **LoRA 效果"几乎不输"full fine-tune**：2021 大家不信。**2024 所有 fine-tune 都用 LoRA**。低秩假设真的成立。

4. **量化到 int4 几乎无损**：4-bit 量化看起来丢 8 倍精度。但实验表明 **70B-int4 ≈ 70B-fp16**。**大模型对量化极不敏感**。

5. **CPU 也能跑 LLM**：llama.cpp 让 MacBook 跑 70B 模型。**Apple Silicon 的统一内存是关键**（CPU 和 GPU 共享内存）。

6. **MoE 让参数"虚高"**：DeepSeek V3 671B 但只激活 37B。**真实计算量 = 37B 模型**。这就是为什么便宜。

## 🛠️ 我该深挖什么

### work4ai 系列
- [`../讲透KV Cache/`](../讲透KV Cache/)：KV cache 完整原理 + 优化
- [`../讲透GPU与系统级/`](../讲透GPU与系统级/)：FlashAttention + vLLM + 量化 + CUDA
- [`../讲透复用权重/`](../讲透复用权重/)：迁移学习 + PEFT + LoRA + QLoRA + 蒸馏 + 持续学习
- [`../讲透微调/`](../讲透微调/)：LoRA / PEFT / QLoRA 实战
- [`../讲透分布式AI系统/`](../讲透分布式AI系统/)：DDP / FSDP / ZeRO / TP

### 必读
- **Dao et al. 2022 "FlashAttention: Fast and Memory-Efficient Exact Attention"**
- **Kwon et al. 2023 "Efficient Memory Management for LLM Serving with PagedAttention"**（vLLM）
- **Hu et al. 2021 "LoRA: Low-Rank Adaptation"**
- **Dettmers et al. 2023 "QLoRA"**

### 实验
```python
# 1. 用 transformers 量化 Llama 3.1 8B 到 int4
# 2. 用 vLLM 部署 + benchmark TPS
# 3. 用 PEFT + LoRA 微调一个小模型
```

---

## 🔗 下一篇

下一篇：[**11 · 让 AI 思考：推理模型与 AlphaProof**（2024-2026）](11-让AI思考-推理与AlphaProof.md)——o1 / R1 / 形式化数学。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**6 年时间，LLM 推理从 5 张 V100 → 1 张手机芯片。算法 + 工程 + 量化让 AI 民主化。**
