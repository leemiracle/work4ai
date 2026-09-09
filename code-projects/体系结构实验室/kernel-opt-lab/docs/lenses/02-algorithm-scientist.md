# 视角 2：首席算法科学家（Chief Algorithm Scientist）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（keen-amber-fox），扮演 PhD、曾在 DeepMind/MSR/华为诺亚方舟、专长 LLM + numerical methods 的首席算法科学家
> **方法**：read-only 深度审查，grep 验证算法覆盖度

---

我已经完成了深入审查。证据确凿——`grep` 搜索结果显示，BF16 仅作为精度分析结论中的一行 `printf` 字符串被承认，但在任何地方都**从未实现**；此外，整个项目中对 GQA/causal/KV-cache/RoPE/RMSNorm/SwiGLU/INT4/GPTQ/AWQ **零提及**。以下是算法科学家的报告。

## 1. 视角定位

我以 LLM + 数值方法双背景审此项目：**算法选型正确性、数值稳定性、SOTA 覆盖度、量化的科学性**。结论先行——这是一个**体系结构调优做得极好（FP32 98.6% 峰值）、但算法维度严重偏科（CNN-centric）**的微内核实验室。它把"GEMM/Conv 微架构跑满"做到了天花板，却**几乎没碰 LLM 推理算子栈**。一句话：**离跑通 Llama-7B，本项目还差约 90% 的工作量。**

## 2. 八大盲区（算法科学家视角）

### 2.1 BF16 全程缺席——最致命缺口
`grep -i bf16` 全仓只在 `lens-precision.c` 的两行 `printf` 结论里出现"LLM 用 BF16"。**Llama/Mistral/Qwen/DeepSeek 全部 BF16 训练 + 推理**，FP16 在激活值分布下频繁溢出（你自己的 Adversarial 实验已证明）。必须验证 D3000 是否支持 armv8.6-a 的 `BFDOT`/`BFMMLA` 指令——若不支持则需用 FP32 simulate，这是 LLM 落地的前置条件。**这一项缺失，整个项目无法称"LLM 实验室"。**

### 2.2 Attention 是玩具版，缺全部 LLM 必备语义
现有 `attention_neon.c` 是**单头、dense、无 mask** 的教科书 attention。真实 decoder-only LLM 需要：**因果 mask（下三角）、KV-cache（每 token 追加 K/V 行）、GQA/MQA（Llama-2-70B/Llama-3 用分组共享 KV）、sliding-window（Mistral）**。当前实现跑不出任何一个真实模型的一层。

### 2.3 量化是 per-tensor INT8，远离 LLM 量化 SOTA
`lens-precision.c` 只做 per-matrix `scale = 127/absmax`。真实 LLM 量化栈：**GPTQ（Hessian 权重量化）、AWQ（激活感知）、SmoothQuant（离群点迁移到权重）、per-channel/per-group（group=128）、W4A16/W8A16 weight-only**。更关键——**缺 INT4**。INT4 是 LLM 部署的主流权重格式（显存减 4×），项目连数据类型都没有。

### 2.4 缺 dequant-on-the-fly GEMM（LLM 推理第一算子）
LLM 推理 90% 算力在 QKV/FFN 投影 GEMM，且主流是 **W4A16/W8A16**（权重 INT4/INT8，激活 BF16）。这需要"边反量化边乘加"的混合 GEMM，当前 `gemm_s8.c` 假设两端同 dtype，**完全不支持**。

### 2.5 KV-cache 量化与长上下文 attention 缺失
长上下文（32k-128k）的瓶颈是 KV-cache 显存。**INT8/INT4 KV-cache 量化 + Flash-Decoding（split-KV 跨核并行）** 是 SOTA，项目零覆盖。当前多核 Flash 在 N=128 时甚至 0.39× 倒挂（数据太少 OpenMP 开销主导），说明并行粒度策略不对。

### 2.6 Online softmax 无数值稳定性证明 + exp 用标量
Flash Attention 的 `expf(m_old - m_new)` rescale 在超长序列下有精度风险，且 `attention_neon.c` 用标量 `expf`（每次循环 1 次），**应改为 `exp2f` + `log2(e)` 常数折叠 + 多项式逼近**（FlashAttention 原版做法）。当前实现数值上"能用"但未经形式化分析。

### 2.7 FP16 GEMM 在 FP16 里累加——算法错误
`gemm_f16.c` 第 44 行 `float16x8_t c0 = vdupq_n_f16(0)` + `vfmaq_f16`，**累加器是 FP16**。K=1024 累加必然精度坍塌。ARM 正确做法是 FP16 输入、**FP32 累加**（`vfmlalq_low_f16` 系列或拆成 FP32 acc）。你的 `lens-precision` 观察到的"FP16 mean_rel 1%"部分根因即此。

### 2.8 缺 LLM 专属算子全集
**RMSNorm（非 LayerNorm，需 rsqrt）、RoPE（复数旋转，每层都做）、SwiGLU/SiLU FFN、token embedding gather、MoE routing + gather-scatter、speculative-decoding 验证算子**——零覆盖。这些才是 LLM 推理的"算子栈"。

## 3. 改造建议（P0/P1/P2）

### P0（不做无法称 LLM 实验室）
1. **实现 BF16 GEMM**：先查 D3000 的 `mrs` 寄存器 / 编译探测 `__ARM_BF16` 宏；若支持 armv8.6-a 用 `BFDOT`，否则 FP32 simulate 并标注 throughput 上限。BF16 理论吞吐应 ≈ FP32（同样 32-bit FMAC lane）或更高。
2. **因果 mask + KV-cache Flash Attention**：在 `attention_neon.c` 上加 `is_causal` 分支（j>i 直接置 -inf）和 KV-cache 增量模式（传入 past_kv，只算新 query 行）。这是 LLM 生成的最小可运行单元。
3. **FP16→FP32 累加修复**：把 `gemm_f16.c` 改为 FP16 输入 + FP32 累加器，重跑 precision lens，对比前后误差——这本身就是一个高价值实验。

### P1（接近 SOTA 推理栈）
1. **GQA support**：在 attention 里加 `n_kv_heads` 参数，query head 共享 KV head（reshape + broadcast），实测 GQA vs MHA 的加速比。
2. **W8A16 weight-only GEMM**：`gemm_w8a16.c`，B 为 INT8 + per-channel scale，内循环 `acc += (int8*B[k]) * scale[k] * A[k]`，对比纯 FP16 GEMM 的精度/速度。
3. **RoPE + RMSNorm 算子**：`rope.c`（复数旋转，NEON 可两 lane 并行实/虚部）、`rmsnorm.c`（NEON rsqrt 逼近），单测正确性 + GFLOPS。
4. **INT4 解包 + W4A16 GEMM**：`gemm_w4a16.c`，权重 4-bit 打包（两值一字节），反量化后 FP16 乘加。

### P2（前沿 + 工程化）
1. **SmoothQuant 风格的离群点迁移**：`smoothquant.c`，离线计算 per-channel scale，把激活离群点迁到权重，重测 INT8 误差。
2. **Pareto frontier 分析**：补 lens 画出 {INT4, INT8, BF16, FP16, FP32} × {GFLOPS, 误差} 的双轴 Pareto，回答"给定精度预算选哪条"。
3. **长上下文 split-KV Flash-Decoding**：跨核切分 KV 维度（而非 query 维度），解决当前 N 小时多核倒挂问题。

## 4. 五条关键洞察

1. **最大不足：算法维度严重偏科。** Winograd/im2col 是 CNN 时代的算法，LLM 一根卷积都不用。项目把 80% 精力投在了一个 LLM 不需要的算法族上，对真实 LLM 算子（GQA attention、W4A16 GEMM、RoPE）零覆盖。
2. **距离 Llama-7B 还有约 90%。** Llama-7B 单层需要：causal GQA attention（32 heads, d=128）+ RoPE + RMSNorm×2 + SwiGLU FFN（W4A16 GEMM×3）+ KV-cache。本项目目前只提供一个 dense 单头 attention 原型，缺约 12 个算子、缺 KV-cache、缺 BF16/INT4、缺反量化 GEMM。
3. **量化科学性不足。** per-tensor INT8 + 合成分布测试，无法回答"INT8 能否承载真实 LLM 激活分布"。真实 LLM 激活有 systematic outliers（Dettmers 2022），需 outlier-aware 量化。当前结论"INT8 在 WideRange 下 max_rel 6.21%"恰恰反证 per-tensor 不够。
4. **数值正确性有隐患。** FP16 在 FP16 累加（2.7 节）是算法错误，非误差容忍问题；Online softmax 的 rescale 稳定性未证明；exp 用标量拖慢 Flash。这些在跑真实模型时会放大成困惑度漂移。
5. **调优方法论是真正资产。** 4 FVU 校准、MR sweep、Roofline/PMU/Thermal lens 的体系结构分析方法论**极有价值且可迁移**——这套工具链套到 BF16/W4A16 上能立刻产出 D3000 上的最优参数表。**建议把方法论而非某个算子作为项目的可复用核心。**

## 5. 新增实验清单（.c 文件 + 设计）

| 文件 | 实验设计 | 关键产出 |
|---|---|---|
| `src/gemm_bf16.c` | 若 armv8.6-a：`BFDOT` 微内核 vs FP32-simulate 对照；MR sweep；对比 FP16 的精度+速度 | D3000 BF16 是否硬件支持 + 最优 MR + 跑满多少峰值 |
| `src/attention_llm.c` | causal mask + KV-cache + GQA(n_kv_heads 参数)，测 prefill(seq_len=2048) 与 decode(batch=1 单 token) 两阶段 | decode 阶段 KV-cache hit 的延迟 / prefill vs decode 性能断崖 |
| `src/gemm_w4a16.c` | INT4 权重(per-group=128 scale) + FP16 激活，对比纯 FP16 GEMM 的 GB/s 内存带宽节省与 GFLOPS | 权重反量化开销占比 + 是否 memory-bound |
| `src/rope.c` | RoPE NEON（实/虚部双 lane），正/反向，对 d=128 测 GFLOPS vs 标量 | RoPE 是否值得 NEON 化（通常访存 bound） |
| `src/rmsnorm.c` | RMSNorm NEON rsqrt（Newton 迭代 vs 硬件 frsqrte），LayerNorm 对照 | rsqrt 逼近精度/速度权衡 |
| `analysis/lens-pareto.c` | 跑全 dtype 的 GEMM + 误差，输出 {dtype, GFLOPS, max_rel} 三列，画 Pareto | 给出"精度预算→最优 dtype"决策表 |
| `src/flash_decoding.c` | 跨核切 KV 维度（split-kv）的长序列 attention，N=8192/32768 测多核扩展 | 修复当前 N 小时多核倒挂 + 长上下文吞吐 |
| `src/gemm_f32acc_f16.c` | 修复 FP16→FP32 累加，与现 FP16 累加版同输入对比误差 | 量化"错累加"导致的精度损失，科学闭环 |

**总评**：作为算子微架构实验室打 90 分，作为 LLM 算法实验室打 25 分。补齐 P0 三项（BF16 + causal/KV-cache attention + FP32 累加修复）即可跃升为"真实 LLM 单算子原型"，再补 P1 即可谈端到端。
