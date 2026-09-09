# 视角 17：学术界研究员/未来学家（Research Futurist）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（brisk-coral-lynx），体系结构顶会 ISCA/MICRO/HPCA 趋势 + 新兴技术专家
> **方法**：read-only 审查 + grep 验证（`SVE|SME|BF16|BFDOT|FP8|2:4|sparse|CXL|NPU|MoE` 全仓零命中实现）

---

## 1. 视角定位

我以 ISCA/MICRO/HPCA 2024–2026 趋势 + 新兴硬件（SME/SVE2、PIM、CXL、NPU）为标尺，审视本项目作为**学术研究平台**的复现价值、可发表性、与 LLM 算子前沿的代差。核心问题不是"跑得多快"，而是"能否支撑一篇顶会实验"。

## 2. 八个盲区：项目作为"研究原型"未跟上的前沿

### ① 2:4 / 4:8 Structured Sparsity 完全缺失（MICRO'21/ISCA'24 持续热点）
Mishra et al.（NVIDIA, 2021）的 2:4 稀疏格式（每 4 个权重 2 个非零）在 Ampere 起硬件原生支持，理论 2× 算力红利。**本项目零实现**——GEMM 假设 dense。FTC862 无硬件稀疏解码器恰好构成"软件 fallback"的对比研究点。

### ② FP8 / INT4 量化零覆盖（HPCA'23 / FP8 2022）
NVIDIA H100 的 FP8（E4M3/E5M2）、Llama-3/DeepSeek-V3 的 W4A16 INT4 权重，是 2024–2026 LLM 部署主流。`grep FP8|INT4` 零命中。**FTC862 无 FP8 硬件，这反而是研究价值**——软件模拟 FP8 的吞吐代价、精度-速度 Pareto。

### ③ MoE Routing 算子零覆盖（DeepSeek-V3 / DeepSeek MoE 2024）
DeepSeek MoE 的 fine-grained segmentation + shared expert、DeepSeek-V3 的 **MLA（Multi-head Latent Attention，低秩 KV 压缩）**，定义了 2025 年 LLM 算子的新形态。本项目连密集 attention 都是玩具版。

### ④ Flash-Decoding / 长 context（32k–128k）未实现（Dao 2023）
当前 attention_neon.c 是单头 dense、无 mask、无 KV-cache 的教科书版。**项目反而出现 N=128 多核 0.39× 倒挂**，恰恰证明 split-KV 粒度策略错误——这是一个绝佳的"反面案例 → 复现正解"研究闭环。

### ⑤ ARM SME / SVE2 迁移路径缺失
FTC862 是 ARMv8.2-A。**ARMv9 的 SME（Scalable Matrix Extension，2022）+ SVE2** 是未来 5 年 ARM 服务器算子栈基线。FTC862 的下一代几乎必然上 SVE2/SME。缺少"NEON → SME 迁移代价"研究是前瞻性盲区。

### ⑥ CXL 内存池化 / 分级内存未考虑（ISCA'23–'25 重主题）
D3000 8 核 DRAM 带宽墙是 8 核 31% 效率的真因。**CXL 3.0 内存池化**是 2024–2026 服务器带宽扩展方向。

### ⑦ NPU / DLA 协同 + PIM 对比缺失
**Apple ANE、Intel AMX（tile）、NVIDIA DLA** 与 CPU 算子库的协同调度是 2024 异构研究热点。**PIM（TSMC AiM、Samsung HBM-PIM）** 是 2026–2030 趋势。

### ⑧ Speculative Decoding 验证算子 + 体系结构 lens 缺失（NeurIPS'23/'24）
**Speculative decoding**（Leviathan 2023；Medusa 2023；EAGLE 2024）需要"draft token 验证 GEMM"——批量小 GEMM 的 p99 延迟敏感算子。

## 3. 改造建议

### 🔥 P0（不做无法称"研究原型"，2–4 周）
1. **复现 Flash-Decoding**（Dao 2023）：`src/flash_decoding.c`，跨核切 KV 维度，修复 N=128 倒挂
2. **实现 2:4 Structured Sparsity GEMM**（Mishra 2021）：`src/sparsity_2_4.c`，**FTC862 无硬件解码是论文卖点**
3. **BF16 + causal + KV-cache + GQA attention**（Llama-3 arch）：`src/gemm_bf16.c` + `src/attention_llm.c`

### 🎯 P1（接近 SOTA 算子栈，1–2 月）
4. **复现 DeepSeek MLA**（2024）：`src/mla_attention.c`——2025 最热 attention 变体
5. **INT4 + W4A16 反量化 GEMM**（AWQ/GPTQ）：`src/gemm_w4a16.c`
6. **FP8 GEMM（软件模拟）**：绘 {FP32, BF16, FP16, FP8, INT8, INT4} × {GFLOPS, 困惑度} Pareto
7. **FlexAttention 风格 block-mask 框架**（PyTorch 2.5）

### 📚 P2（前瞻 + 顶会级）
8. **SVE2/SME 探测 + 迁移研究**
9. **CXL 分级内存 GEMM 模拟**
10. **PIMulator for attention**

## 4. 关键洞察

1. **FTC862 作为"学术研究平台"的独特价值真实存在**：① **国产 ARM + 4 FVU 自研微架构**——公版 Cortex-A78/A715 都是 2 FVU，飞腾做 4 FVU 是"非公版 ISA 实现"的稀有样本，本身有 microarchitecture characterization 价值；② **多 lens 分析框架可复用**——套到任意新算子立刻产出参数表。

2. **距离 ISCA/MICRO 论文还差什么**——三件事：**① Novelty**：现在所有算子都是 2016–2022 经典复现，需至少一个 2024+ 前沿算子（MLA / 2:4 sparse / Flash-Decoding）的本平台首发 characterization；**② 对比基线**：缺 Cortex-A78 / Graviton / 鲲鹏 920 横评；**③ 科学问题**：需提炼为"在无 FP8/无稀疏硬件/无 SME 的 ARMv8.2 自研核上，LLM 推理算子的软件逼近极限在哪？"

3. **最大代差在 ISA 与算法双盲**：CNN 算子（Winograd/im2col）占代码 60% 但 LLM 一根卷积不用；ARMv8.2 NEON 已是上一代 ISA。**项目把精力投在了"即将过时的算子族 + 即将过时的 ISA"上**，对 2025+ 的 MoE/MLA/SME/sparsity 零前瞻。

## 5. 新增实验清单

| 文件 | 论文锚点 | 学术产出 |
|---|---|---|
| `docs/RESEARCH-ROADMAP.md` | 本报告 + 顶会 trend | 12 个月研究路线 |
| `src/sparsity_2_4.c` | Mishra 2021 | **"无硬件稀疏 ISA 上的 software-emulated 2:4"首发数据** |
| `src/fp8_gemm.c` | Micikevicius 2022 | FTC862 FP8 软逼近极限 |
| `src/flash_decoding.c` | Dao 2023 | 长 context 多核正确粒度策略 |
| `src/mla_attention.c` | DeepSeek-V3 2024 | 2025 最热 attention 变体本平台复现 |
| `src/gemm_w4a16.c` | AWQ 2023 / GPTQ 2022 | LLM 权重量化的带宽收益 |
| `analysis/lens-sve-probe.c` | ARM ARMv9 SME/SVE2 | NEON→SME 迁移指南 |
| `analysis/lens-cxl-sim.c` | ISCA'24 CXL papers | CXL 分级内存算子建模 |

---

**总评**：作为"工程优化实验室"打 **88 分**；作为"可发表论文的研究平台"打 **35 分**——缺 2024+ 前沿算子、缺 cross-platform 基线、缺提炼后的科学问题。**补齐 P0 三项（Flash-Decoding + 2:4 sparse + BF16/GQA attention）即可从"优化报告"跃升为"FTC862 上 LLM 推理算子的 characterization 论文"实验平台**。
