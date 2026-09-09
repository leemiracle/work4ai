# DeepSeek LLM 精读：Scaling Open-Source Language Models with Longtermism

> arXiv:2401.02954（2024-01-05，DeepSeek-AI，86 位作者按姓氏字母序）
> 本地仓：`~/ai/explore/deepseek-ai/DeepSeek-LLM`

## 0. 论文 ID 勘误（重要）

任务原给定两个 ID：2311.07911 与 2401.02954。经 arXiv 页面核实：

- **2311.07911 ≠ DeepSeek 论文**。它是 Google 的 *Instruction-Following Evaluation for Large Language Models*（即 IFEval 基准）。混淆来源：DeepSeek-LLM README 的 "Instruction Following Evaluation" 一节明确引用 `arxiv.org/pdf/2311.07911.pdf` 作为**评测工具**（用其 500 条可验证指令 prompt 评测 Chat 模型的指令遵循能力），属"引用关系"而非"姊妹论文"。
- **2401.02954 才是 DeepSeek LLM 正主**，且该单篇已完整覆盖用户所述"预训练 + 对话 SFT + DPO"全流程（论文 §2 预训练、§4 Alignment 含 SFT 与 DPO）。因此本合并篇以 2401.02954 为唯一主体，IFEval 作为评测环节在 §4 实验部分交代。

## 1. 一句话定位

DeepSeek 首代基座模型的技术宣言：以一套**自己重新拟合的 scaling law** 为导航，从零训练 7B/67B 开源模型（2T tokens、中英双语），67B 在代码/数学/推理上全面超越 LLaMA-2 70B，Chat 版对齐后中文开放域超越 GPT-3.5。它确立了 DeepSeek "长期主义 + 完全开源 + 论文级透明" 的路线，是后续 V2（MLA/MoE）、V3、R1 的起点。

## 2. 动机与痛点

1. **Scaling law 结论互相矛盾**：Kaplan 2020（算力大头给模型）与 Chinchilla 2022（大头给数据）的最优分配结论不一致，且都缺少超参数是否最优的完整交代——"给 scaling 蒙上乌云"。开源社区只顾刷固定尺寸（7B/13B/70B），没人重做 scaling 基础研究。
2. **超参随算力规模怎么变没有可操作公式**：batch size、learning rate 与 compute 的关系只有零散经验观察，小模型上得到的结论在大模型上不适用。
3. **开源模型在数学/代码上与闭源差距大**，中文能力尤其稀缺——需要双语从零预训练而非英文模型续训。

## 3. 核心方法

### 3.1 数据：三阶段流水线（dedup → filter → remix）

- **激进去重**：跨 dump 全库去重（MinhashLSH，文档级+字符串级）。关键数据：用 91 个 Common Crawl dump 联合去重，删除率 **89.8%**，是单 dump 去重（22.2%）的 4 倍。
- **过滤**：语言学+语义双视角文档质量评估，删低质网页但保护低资源语言知识。
- **重混**：补偿欠代表领域，提高多样性。
- **Tokenizer**：BBPE（基于 tokenizers 库），GPT-2 式 pre-tokenizer 防止跨类符合并，数字逐位切分；常规词表 100,000 + 15 special = 100,015，训练时配 102,400 留余量；在 24GB 多语料上训练。

### 3.2 架构：LLaMA 微设计 + 深度加宽的宏设计

微设计完全沿用 LLaMA：Pre-Norm + RMSNorm、SwiGLU（FFN 中间维 8/3·d）、RoPE。宏设计的关键选择：

| | 层数 | d_model | heads | KV heads | ctx | batch | lr | tokens |
|---|---|---|---|---|---|---|---|---|
| 7B | 30 | 4096 | 32（MHA） | 32 | 4096 | 2304 | 4.2e-4 | 2T |
| 67B | 95 | 8192 | 64（GQA） | 8 | 4096 | 4608 | 3.2e-4 | 2T |

67B 用 GQA 省推理成本，且**加深而非加宽 FFN**（95 层异常深），既对齐社区参数规格又利于流水线切分。初始化 std=0.006，AdamW（β1=0.9, β2=0.95, wd=0.1），梯度裁剪 1.0。

### 3.3 Multi-step 学习率调度器（为"继续训练"设计）

替代 cosine：2000 步 warmup 到峰值 → 80% tokens 处降到 **31.6%** → 90% 处降到 **10%**。1.6B 模型 100B tokens 实验证明最终性能与 cosine 基本一致，但**换训练规模时可复用第一段训练**——这是"长期主义"在工程上的直接体现（后来 V3 系列的持续迭代正受益于此设计哲学）。

### 3.4 超参数的 scaling law

在 1e17~2e19 FLOPs 上做 batch/lr 网格搜索（复用 multi-step 第一段省算力），以"泛化误差不超过最优 0.25%"定义近优参数带，拟合幂律：

$$\eta_{opt} = 0.3118 \cdot C^{-0.1250}, \qquad B_{opt} = 0.2920 \cdot C^{0.3271}$$

规律：算力越大最优 batch 越大、最优 lr 越小；最优区是一条宽带（选参容错高）。在 1e20 FLOPs 上验证拟合公式给出的参数正落在最优区中心。

### 3.5 用 M（non-embedding FLOPs/token）替代 N（参数量）拟合 IsoFLOP

论点：6N₁（非嵌入参数）忽略 attention 开销，6N₂（全参数）又计入对容量贡献小的词表计算，小模型上误差可达 50%。新尺度：

$$M = 72\,n_{layer}\,d_{model}^2 + 12\,n_{layer}\,d_{model}\,l_{seq}, \qquad C = MD$$

用 Chinchilla 的 IsoFLOP profile（8 个算力档 × 每档约 10 种模型/数据分配）拟合：

$$M_{opt} = 0.1715 \cdot C^{0.5243}, \qquad D_{opt} = 5.8316 \cdot C^{0.4757}$$

a≈0.52/b≈0.48 接近均衡分配。scaling 曲线成功外推预测了 1000× 算力外 7B/67B 的验证 loss（图 5 蓝星落在拟合线上）。

### 3.6 数据质量改变最优分配（最有洞见的发现）

同一套实验流程换三种数据（自家早期/自家当前/OpenWebText2）重跑：

| 数据 | a（模型指数） | b（数据指数） |
|---|---|---|
| OpenAI（OpenWebText2） | 0.73 | 0.27 |
| Chinchilla（MassiveText） | 0.49 | 0.51 |
| 自家早期数据 | 0.450 | 0.550 |
| 自家当前数据 | 0.524 | 0.476 |
| 自家流程跑 OpenWebText2 | 0.578 | 0.422 |

**数据质量越高，算力越应该分给模型而不是数据**——这既解释了 Kaplan vs Chinchilla 的矛盾（数据分布不同），也提供了一个"用 scaling 分配指数反推数据质量"的间接度量。

### 3.7 对齐：SFT + DPO

- **SFT 数据**：150 万条中英实例 = 120 万 helpful（31.2% 通用 + 46.6% 数学 + 22.2% 代码）+ 30 万 safety。7B 训 4 epochs（lr 1e-5），67B 仅 2 epochs（lr 5e-6）——67B 很快过拟合顶到 benchmark 上界。
- **重复率问题**：用 3868 条中英 prompt 度量"无尽重复"比例，发现 math SFT 数据越多重复率越高（数学推理模式相似、弱模型学不会就复读）。两阶段 SFT 与 DPO 都能在保住 benchmark 的同时显著压低重复。
- **DPO**：偏好对由自家的 DeepSeek Chat 模型生成候选响应构造（多语言 prompt，覆盖创意写作/问答/指令遵循；harmlessness 同法）。训练 1 epoch、lr 5e-6、batch 512、warmup+cosine。结论：DPO 显著提升开放域生成，标准 benchmark 基本不动。

### 3.8 基础设施

HAI-LLM 框架（幻方）：Megatron 式 4D 并行 + ZeRO-1 + flash attention + 计算通信重叠 + 算子融合；bf16 训练、fp32 梯度累积；**in-place cross-entropy**（CE CUDA kernel 内即时 bf16→fp32 转换并用梯度覆写 logits，省 HBM）；每 5 分钟异步存 checkpoint（最多丢 5 分钟进度）；支持换 3D 并行配置续训。评测用 vLLM 做生成任务。

## 4. 实验与结果

**Base 模型（67B vs LLaMA-2 70B）**：

| | MMLU | GSM8K | HumanEval | BBH | C-Eval | CMMLU |
|---|---|---|---|---|---|---|
| LLaMA-2 70B | 69.0 | 58.4 | 28.7 | 62.9 | 51.4 | 53.1 |
| DeepSeek 67B | **71.3** | **63.4** | **42.7** | **68.7** | **66.1** | **70.8** |

代码 +14、中文 +15~19 的差距是最大亮点。7B 同样小胜 LLaMA-2 7B（HumanEval 26.2 vs 14.6）。

**Chat 模型**：HumanEval 73.78 / GSM8K 84.1 / MATH 32.6 / 匈牙利高考 65 分（人工评分，对齐 Grok-1 的评测协议，且公开了勘误：剔除 16-18 题最低分并修正图）。**AlignBench**（683 题中文开放域）上 67B Chat 超越 ChatGPT，仅次于两版 GPT-4；DPO 版几乎全维度再涨。英语开放域（MT-Bench/AlpacaEval）同样领先开源。**IFEval**（即 2311.07911 的基准）用 prompt-level loose 指标评测指令遵循，验证对齐质量。

**防刷分的诚实实验**：加 2000 万条中文选择题（+MC）可把 7B Chat 的 MMLU 49.4→60.9、C-Eval 47.0→71.3，但非选择题形式的知识能力不涨——**明确拒绝把 MC 数据加入训练**，并公开该对照表警示社区。这在 2024 年初的 benchmark 污染氛围里是罕见的透明。

## 5. 局限与后续

论文自认：训练数据偏差传导、幻觉、重复生成三类固有缺陷。隐含局限：4096 上下文已落后于同期长文本竞争、纯 dense 架构成本高。

后续演进（同一条代码血脉）：DeepSeekMoE（2401.06066）→ **V2**（MLA + 细粒度 MoE，2405.04434）→ **V3**（671B MoE + MTP，2412.19437）→ **R1**（RL 推理，2501.12948）。本篇的 multi-step LR、scaling 方法论、HAI-LLM 基建、SFT+DPO 配方全部被继承；"长期主义"（论文标题关键词）指：为继续训练预留接口、开源中间 checkpoint、用 scaling law 而非刷分导航。

## 6. 与代码的对照

本地仓是模型发布仓（模型代码托管在 HuggingFace `deepseek-ai/deepseek-llm-*` 的 `trust_remote_code` 中），本地核心资产是评测与复现材料：

| 论文概念 | 位置 |
|---|---|
| 匈牙利高考评测（§5.3 held-out） | `evaluation/hungarian_national_hs_solutions/`（含人工评分方案与勘误说明） |
| IFEval 指令遵循评测 | `evaluation/IFEval/` |
| more_results（附录 A.3/A.5 完整表） | `evaluation/more_results.md`、`evaluation/deepseek-67b-1206-no-sp.jsonl` |
| 数据流水线三阶段（§2.1） | README §4 "cc_cleaner" 分布式批处理系统描述（代码未开源） |
| multi-step LR / 超参表（§2.3） | README §4 Pre-Training（数字一致） |
| 训练框架（§2.4 HAI-LLM） | 对应幻方开源的 hf-megatron（今 DeepSeek 开源训练基建前身） |
| 架构超参（95 层/GQA/8192） | HF 仓 `config.json`（`num_hidden_layers=95, num_key_value_heads=8`），README FAQ 给出 GGUF/GPTQ 量化指引 |
| tokenizer BBPE 100015 | HF 仓 `tokenizer.json`（README FAQ 解释为何无法转 SentencePiece，及给 llama.cpp 提的 PR#4070） |

## 7. 学习路径

1. **前置**：Transformer 基础（RoPE/SwiGLU/RMSNorm/GQA 各自解决什么）、Kaplan 2020 与 Chinchilla 2022 两篇 scaling 原文（本文全部对话对象）。
2. **精读顺序**：§3.1 超参 scaling → §3.2 M 表示与 IsoFLOP 拟合 → §3.3 数据质量实验（全文最独特贡献）→ §2 预训练细节 → §4 对齐 → §5 评测。第一遍跳过基础设施节。
3. **复现建议**：
   - 小规模重演超参 scaling：用 1e17~1e18 FLOPs（单卡数十 GPU 时）+ multi-step LR 首段复用，验证 η/B 幂律公式；
   - 用开源中间 checkpoint（AWS S3，`--request-payer`）做训练动态分析：loss 曲线与 benchmark 轨迹的对应关系；
   - 对齐侧复现 DPO：偏好对全由自模型生成（无人工标注），单卡 7B 可跑 TRL 的 DPOTrainer，重点观察重复率变化；
   - 读后续 V2 论文的 MLA 节前，先回看本篇 GQA 的动机（KV cache 成本），可以看出 MLA 是 GQA 思路的彻底化。

（完）
