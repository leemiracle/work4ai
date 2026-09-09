# 2026 年 7 月 AI 前沿简报

> 产出：2026-07-23
> 范围：2026 年 6-7 月发布的重大 AI 突破（项目 v2.0.4 之后的"活"内容）
> 方法：websearch 多方向并行检索，筛选 5 个最具架构创新价值的前沿
> 用途：让项目保持"活"的状态——这些内容应逐步吸收到模块 11/12/13 的对应章节

---

## §0. TL;DR · 5 个最值得关注的前沿

| 排名 | 事件 | 日期 | 核心创新 | 对项目的影响 |
|---|---|---|---|---|
| 🥇 1 | **Kimi K3**（Moonshot）| 2026-07-16 | 2.8T 参数 + KDA + AttnRes + Stable LatentMoE + MXFP4 QAT | 模块 11 §06/§07 + 模块 12 §05 |
| 🥈 2 | **Inkling**（Thinking Machines / Murati）| 2026-07-15 | 975B MoE + 相对位置偏置（不用 RoPE）+ 短卷积 + 5:1 SWA:Global | 模块 11 §03/§07 |
| 🥉 3 | **Sessa**（arXiv:2604.18580）| 2026-04 | attention 嵌入 recurrent feedback path（理论：power-law memory tail）| 模块 11 §07（attention 变种）|
| 4 | **SciReasoner**（arXiv:2607.07708）| 2026-07 | 跨域科学基础模型（蛋白质/小分子/晶体统一）| 模块 02 AI4Science |
| 5 | **Gemini 3.6 Flash + Macaron-V1** | 2026-07-21 | 工程优化 + Mixture-of-LoRA（4 专家路由）| 模块 12 §05 部署 + 模块 13 §13 |

---

## §1. 🥇 Kimi K3：开源 3T 时代的开启（2026-07-16）

**Moonshot AI** 发布 **Kimi K3**——**首个开源 3 万亿参数级模型**（2.8T），超越 DeepSeek V4 Pro 近 1.75 倍。权重 7 月 27 日开源。

### 架构创新（4 大新组件）

| 组件 | 全称 | 作用 |
|---|---|---|
| **KDA** | Kimi Delta Attention | 混合线性 attention，1M 上下文高效扩展（部分层用线性 attention 减二次开销）|
| **AttnRes** | Attention Residuals | 跨深度选择性检索（每层可"回看"任意早层表示，而非均匀累加）|
| **Stable LatentMoE** | 稳定潜变量 MoE | 896 专家 / 16 激活 + Quantile Balancing 路由 + soft dropping |
| **MXFP4 QAT** | 量化感知训练 | 权重 MXFP4 + 激活 MXFP8，**从 SFT 阶段就开始量化**（非 PTQ）|

### 配套优化
- **Per-Head Muon 优化器**：每个 attention head 独立学习率
- **SiTU（Sigmoid Tanh Unit）**：替代 GeLU/SwiGLU 的激活函数
- **Gated MLA**：门控 Multi-head Latent Attention（DeepSeek MLA 的进化）
- **完全平衡专家并行训练**：静态 shape + 无 host 同步

### 对项目的影响
- **模块 11 §07 attention 变种**：KDA + AttnRes 是 2026 年最新的 attention 创新，应在 §2.6「新兴方向」补一段
- **模块 12 §05 §12.3 量化矩阵**：MXFP4 QAT 是新的量化路径（vs 现有的 PTQ 主流）—— D3000 不支持 MXFP4 但 NVIDIA Blackwell 原生支持
- **模块 11 §06 Transformer 变种**：Stable LatentMoE + Gated MLA 是 MoE 的新进化

> 来源：[openlm.ai/kimi-k3](https://openlm.ai/kimi-k3/) / [PoYo 架构解析](https://poyo.ai/hub/kimi-k3-architecture) / [HF Blog](https://huggingface.co/blog/ResterChed/kimi-k3-model-overview-mxfp4-quantization-open-wei)

---

## §2. 🥈 Inkling：Mira Murati 新实验室首个从零训练模型（2026-07-15）

**Thinking Machines Lab**（前 OpenAI CTO Mira Murati 创立）发布 **Inkling**——975B 参数 MoE（41B 激活），Apache 2.0 开源。

### 反主流的架构选择（5 个"不追求 leaderboard"的设计）

| 主流做法 | Inkling 的反主流选择 | 理由 |
|---|---|---|
| RoPE 位置编码 | **学习式相对位置偏置** | 微调基底应避免位置编码偏置 |
| 标准 attention block | **每 block 加短卷积**（在 K/V 投影后）| 局部模式捕获 |
| 全局或固定 SWA | **5:1 local-to-global attention 交替** | 兼顾长程 + 局部 |
| SwiGLU 激活 | （未公开，可能用新的）| — |
| 推理时 speculative decoding | **训练时就嵌入 MTP 层** | MTP drafter 训练时一起学，推理时零额外成本 |

### 关键数字
- 975B 总 / 41B 激活（4.2% 激活率）
- 66 层 / 256 专家 / 6 激活 + 2 共享专家
- 1M 上下文 / 原生文本+图像+音频
- BF16 = 2TB VRAM / NVFP4 = 600GB VRAM
- 配套 Inkling-Small：276B（12B 激活），某些 benchmark 超过 975B 版本

### "不追求 leaderboard"的哲学
Inkling 在多数 benchmark 上**不是最强**，但作者明确说：**这是为微调设计的基底**，不是 trophy。其优势在 token 效率 / 多模态广度 / 安全 refusal 行为 / 可微调性。

### 对项目的影响
- **模块 11 §03 位置编码**：相对位置偏置 vs RoPE 的对比应更新（Inkling 是 2026 年最大规模的相对位置偏置实验）
- **模块 11 §07 attention 变种**：5:1 SWA:Global 交替是 sliding window 的新工程化
- **模块 12 §02 微调**：Inkling 的"为微调设计"哲学应作为案例

> 来源：[HF Blog: thinkingmachines-inkling](https://huggingface.co/blog/thinkingmachines-inkling)

---

## §3. 🥉 Sessa：attention 嵌入 recurrent feedback（理论突破）

**Sessa: Selective State Space Attention**（arXiv:2604.18580, LibratioAI）—— 一个**理论性很强**的新架构。

### 核心创新：拓扑而非比例

主流 hybrid（Jamba / Zamba）是 **interleave**（Transformer 层和 Mamba 层并排）。Sessa 不同——**把 attention 嵌入 recurrent feedback path**：

```
标准 hybrid（Jamba）:        Sessa:
  [Attention] → [Mamba]        [Mamba + Attention-in-feedback]
       ↓                            ↑↓（反馈环）
  [Mamba] → [Attention]        一次前向里 attention 在反馈环里多次激活
```

### 理论保证（power-law memory tail）

在显式假设下，Sessa 证明了：
- 记忆影响衰减为 $O(\ell^{-\beta})$，其中 $0 < \beta < 1$
- **比 Transformer 的 $O(1/\ell)$ 慢**（β<1 时 ℓ^-β 衰减比 ℓ^-1 慢）
- **比 Mamba 的指数衰减慢得多**
- 唯一能实现"distance-invariant retrieval"（影响不随距离衰减）的架构类

### 局限
- 只在 125M / 350M 参数 + 合成任务上验证
- 未在十亿级参数 / 标准 benchmark 上验证
- 理论假设较强

### 对项目的影响
- **模块 11 §07 §2.7**「线性 attention 与 SSM/Mamba 的统一」：Sessa 是这条线的最新理论进展，应在 §2.7 补一段
- **模块 14 §04 动力系统**：Sessa 的 power-law memory tail 分析用到了动力系统的概念（BIBO 稳定 + 多路径反馈）

> 来源：[arXiv:2604.18580](https://arxiv.org/abs/2604.18580) / [GitHub: LibratioAI/sessa](https://github.com/LibratioAI/sessa) / [Groundy 解析](https://groundy.com/articles/sessa-breaks-the-mamba-or-transformer-binary-distance-invariant-retrieval/)

---

## §4. SciReasoner：跨域科学基础模型（arXiv:2607.07708）

**SciReasoner**（2026-07）—— 首个**统一处理蛋白质/小分子/无机晶体**的科学基础模型。

### 核心创新：structure-aware vocabulary

不同领域的结构数据（蛋白质 3D / 分子图 / 晶格）被**离散化为统一的"结构感知词汇表"**：
- 蛋白质：Foldseek 编码
- 小分子：ConfSeq 编码
- 晶体：SLICES 编码

这些结构 token 作为"可寻址的证据单元"嵌入 autoregressive reasoning trajectory。

### 性能（86 benchmark / 67 SOTA）
- 蛋白质：Cellular Component annotation Fmax 0.42 → 0.55（低同源/orphan-like）
- 化学：单步 retrosynthesis accuracy 0.63 → 0.72
- 材料：分离元素/化合物相 + 解析高/低带隙
- 双盲专家评估：98% 的案例中 reasoning trace 被评为"优于或等同于前沿 LLM"

### 对项目的影响
- **模块 02 AI4Science**：SciReasoner 是 2026 年 AI4Science 的旗舰基础模型，应在模块 02 对应章节补一段
- **模块 13 §13 形式化 Agent**：SciReasoner 的"structure as evidence"思想和形式化验证的"proof as evidence"有哲学共鸣

> 来源：[arXiv:2607.07708](https://arxiv.org/abs/2607.07708)

---

## §5. 工程优化与后训练创新（Gemini 3.6 / Macaron-V1）

### Gemini 3.6 Flash（Google, 2026-07-21）
- 比 3.5 Flash 减少 17% output token（同质量）
- DeepSWE benchmark 提升 65%
- **Gemini 4 已开始预训练**（"最雄心勃勃的预训练 run"）

### Gemini 3.5 Flash-Lite
- 350 tokens/s（最快）
- $0.3/1M input + $2.5/1M output
- SWE-Bench Pro 54.2%（vs 3 Flash 的 49.6%）—— **小模型超越大模型**

### Gemini 3.5 Flash Cyber
- 网络安全专用 + CodeMender agent
- **政府限定向发布**（双用途技术谨慎部署）

### Macaron-V1（Mind Lab, 2026-07-21）
- **首个基于 GLM-5.2 后训练**的模型
- **Mixture-of-LoRA (MoL)** 架构：4 个 LoRA 专家
  - L0 Chat（对话主干）
  - L1 Agent（工具使用）
  - L2 Coding（代码/SWE）
  - L3 GenUI（UI 渲染）
- **748B 旗舰**（744B base + 4×1B LoRA）/ 50B Tall（35B base + 4×3.7B LoRA）
- LongStraw：2M token 上下文训练

### 对项目的影响
- **模块 12 §05 部署**：3.5 Flash-Lite 350 tokens/s + Macaron MoL 是新的部署形态
- **模块 13 §13**：Macaron MoL 的"base frozen + LoRA 专家"是 continual learning 的工程化（呼应 Certigrad4 的"verified ML"思想——base 不变，只加 LoRA，更易形式化验证）

> 来源：[Google Blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/) / [Macaron-V1 发布](https://macaron.im/mindlab/research/introducing-macaron-v1)

---

## §6. AI4Science 突破（2 个 Nature 旗舰）

### NISE（Nature 2026-06-24）
**Zero-shot design of drug-binding proteins** —— 用两个神经网络迭代（LASErMPNN 设计序列 + Boltz-2 预测结构）：
- exatecan binder：100% 成功率（4/4 设计实验验证结合）
- apixaban binder：83% 成功率 + **80 pM 亲和力**（比之前最佳好 **10000 倍**）
- 神经证明阅读（neural proofreading）：LASErMPNN 再建议 2 个氨基酸替换 → 亲和力再提升 100×

### AI-redesigned protein evolution（Nature 2026-07-22）
用 ProteinMPNN 重新设计蛋白酶作为进化的**起点**：
- 3 个不同 BoNT 蛋白酶，AI-redesigned 起点进化出的活性**全部高于**野生型起点
- 对 ataxin-2（神经退行性疾病相关）：**79 倍特异性提升**
- 核心 insight：**AI redesign 提升 mutational robustness**，解锁野生型无法到达的高功能序列空间

### 对项目的影响
- **模块 02 AI4Science**：这两个 Nature 旗舰是 2026 年 AI4Science 的代表性突破

> 来源：[Nature: s41586-026-10670-w](https://www.nature.com/articles/s41586-026-10670-w) / [Nature: s41586-026-10820-0](https://www.nature.com/articles/s41586-026-10820-0)

---

## §7. 这一轮前沿对项目的"反向启示"

1. **MXFP4 QAT 是新量化范式**（Kimi K3）—— 模块 12 §05 §12.3 现有的"25+ 量化后端"以 PTQ 为主，应补 MXFP4 QAT（训练时就量化）
2. **attention 嵌入 feedback 是新拓扑**（Sessa）—— 模块 11 §07 现有的"interleave hybrid"思路被挑战
3. **相对位置偏置在大规模重生**（Inkling）—— 模块 11 §03 位置编码章节应更新"RoPE 不是唯一答案"
4. **跨域科学基础模型出现**（SciReasoner）—— 模块 02 AI4Science 有了一个"统一基础模型"的新范式
5. **Mixture-of-LoRA 作为 continual learning**（Macaron）—— 模块 13 §13 §五 Certigrad4 的"verified ML"思路可以扩展到"verified LoRA"（base 不变，只验证 LoRA delta）

---

## §8. 立即可做的 5 个吸收动作（按价值排序）

| # | 动作 | 目标章节 | 工作量 |
|---|---|---|---|
| 1 | 加 MXFP4 QAT 到模块 12 §05 §12.3 | 量化矩阵补一行 | 0.5h |
| 2 | 加 Sessa 到模块 11 §07 §2.7 | attention-SSM 统一补一段 | 1h |
| 3 | 加 Kimi K3 KDA+AttnRes 到模块 11 §07 §2.6 | 新兴方向 | 1h |
| 4 | 加 Inkling 5:1 SWA 到模块 11 §07 | sliding window 工程化 | 0.5h |
| 5 | 加 SciReasoner 到模块 02 | AI4Science 新范式 | 1h |

如果用户后续要做"前沿吸收"轮，这 5 个动作总共 4 小时，把项目更新到 2026-07 最前沿。

---

**简报元数据**：
- 产出时间：2026-07-23
- 检索方法：websearch 3 个方向并行（breakthrough / architecture / AI4Science）
- 引用：2 个 arXiv（2604.18580 Sessa / 2607.07708 SciReasoner）+ 5 个博客/技术报告 URL（无新 arXiv 凭记忆风险）
- 这份简报本身**不引入新 arXiv 到项目正文**，只作为"前沿跟踪"参考——后续吸收到正文时再单独核实
