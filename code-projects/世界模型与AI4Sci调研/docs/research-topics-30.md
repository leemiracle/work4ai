# 30 个研究课题清单：从知识库到研究导航仪

> 产出：2026-07-23（v2.0.7）
> 目的：把项目 132 万字的"全景调研"提炼为 30 个**具体可执行的研究课题**，让"应用数学研究型工程师"有一张从"学"到"做研究"的导航地图
> 方法：扫描全项目已有的课题线索 + 结合 2025-2026 最新前沿（AlphaProof Nature / DeepSeekMath-V2 / AlphaProof Nexus / Sessa / Kimi K3）
> 分类：按用户画像的 5 个方向候选（ML 理论 / 概率随机过程 / 数值分析 / 优化 / 信息论），每方向 6 个课题

---

## §0. 为什么需要这份清单

项目有 166 个 md 文件 / 132 万字 / 1150 arXiv 引用——这是**知识库**。但从"学了"到"做出研究"之间有一个鸿沟：**哪个具体问题值得做？用什么数学工具？需要多大工作量？目标投哪个会议？**

这份清单回答这四个问题。30 个课题按"入门 → 进阶 → 前沿"三层排列，每个课题都标注了：
- **数学工具**：需要补哪些数学基础
- **前沿锚点**：2025-2026 的哪篇论文是这个课题的起点
- **工作量**：以"每周 10-20h"估算的月数
- **目标会议**：投哪里
- **章节连接**：项目里哪个模块是这个课题的知识基础

---

## §1. ML 理论方向（6 个课题）

### ML-1 · 形式化 Agent 的 Reward Hacking 分类学（入门）
- **问题**：LLM 在形式化环境（Lean/Z3）里的"作弊行为"如何系统分类？sorry 滥用 / 重复无意义 tactic / 利用 verifier bug / 利用 mathlib 错误
- **数学工具**：形式语言理论 + 反例生成 + 类型论基础
- **前沿锚点**：Lean Copilot [arXiv:2404.12534] 74.2% 自动化率背后的 sorry 风险
- **工作量**：6-12 月 · **目标**：NeurIPS Safety / ACL
- **章节连接**：模块 13 §13 §六 sorry 反例 + §八 课题 1

### ML-2 · Sessa power-law memory tail 的理论扩展（进阶）
- **问题**：Sessa 证明了 $O(\ell^{-\beta})$ 衰减，但 $\beta$ 的精确值如何依赖路由矩阵？能否设计出 $\beta \to 0$（distance-invariant retrieval）的显式构造？
- **数学工具**：随机矩阵理论 + 谱图论 + 动力系统稳定性
- **前沿锚点**：Sessa [arXiv:2604.18580]
- **工作量**：12-18 月 · **目标**：NeurIPS / COLT
- **章节连接**：模块 11 §07 §2.7 + docs/frontier-deep-dive/03

### ML-3 · DeepSeekMath-V2 的 Self-Verification 数学化（进阶）
- **问题**：DeepSeekMath-V2 让 LLM 自己验证证明——但"验证器"和"生成器"的 gap 如何数学化定义？gap 收敛到零时会发生什么？
- **数学工具**：PAC 学习理论 + Bayesian 推断 + 信息论
- **前沿锚点**：DeepSeekMath-V2 [arXiv:2511.22570] IMO 2025 金牌
- **工作量**：12-18 月 · **目标**：ICLR / NeurIPS
- **章节连接**：模块 13 §13 + docs/frontier-briefing-2026-07.md

### ML-4 · Grokking 现象的理论解释（前沿）
- **问题**：模型在训练很久后突然泛化（grokking）——这是权重 late phase 的什么相变？能否用统计力学描述？
- **数学工具**：统计力学 + 自由能景观 + 相变理论
- **前沿锚点**：Grokking [arXiv:2201.02177] + 2024-2026 理论进展
- **工作量**：18-24 月 · **目标**：NeurIPS / COLT
- **章节连接**：模块 14 §02 §统计力学

### ML-5 · Transformer 的 Expressive Power 与深度关系（前沿）
- **问题**：给定 $L$ 层 Transformer，它能表示什么函数类？深度 vs 宽度的 expressivity tradeoff？
- **数学工具**：计算复杂性 + 电路复杂度 + TC⁰ 理论
- **前沿锚点**：Merrill & Sabharwal 2023-2024 系列理论
- **工作量**：18-24 月 · **目标**：COLT / STOC / CCC
- **章节连接**：模块 14 §01 §三 计算复杂性

### ML-6 · AlphaProof 的 TTRL 收敛性分析（前沿）
- **问题**：AlphaProof 的 Test-Time RL 在推理时生成百万变体做问题专属适应——这个过程的收敛性如何保证？什么条件下会发散？
- **数学工具**：RL 理论 + MCTS 收敛分析 + 形式系统
- **前沿锚点**：AlphaProof [Nature, DOI:10.1038/s41586-025-09833-y]
- **工作量**：18-24 月 · **目标**：NeurIPS / Nature Machine Intelligence
- **章节连接**：模块 13 §13 §3.4 AlphaProof + 模块 14 §01

---

## §2. 概率随机过程方向（6 个课题）

### PR-1 · Diffusion 模型的 score matching 数学基础（入门）
- **问题**：为什么 $\nabla \log p(x)$ 可以从噪声样本估计？score matching 的方差如何随维度增长？
- **数学工具**：随机分析 + Stein 等价 + 测度论
- **前沿锚点**：Song [arXiv:1907.05600] score-SDE + DDPM [arXiv:2006.11239]
- **工作量**：6-12 月 · **目标**：NeurIPS / ICML
- **章节连接**：模块 14 §03 §score matching

### PR-2 · SDE 数值解的高阶方法（进阶）
- **问题**：现有 diffusion 采样用 Euler-Maruyama（1 阶）——能否设计 2-3 阶 SDE 求解器加速采样 5-10×？
- **数学工具**：随机数值分析 + Kloeden-Platen
- **前沿锚点**：DPM-Solver [arXiv:2206.00927] + 2024 高阶采样器
- **工作量**：12 月 · **目标**：NeurIPS / ICML
- **章节连接**：模块 14 §05 §八 ODE/SDE 数值解

### PR-3 · 长上下文 LLM 的遗忘过程建模（进阶）
- **问题**：LLM 在长上下文里"忘记"中间信息——能否用 Markov 链 / 随机过程建模这个遗忘？
- **数学工具**：Markov 链 + 遍历理论 + 信息衰减
- **前沿锚点**：StreamingLLM [arXiv:2309.17453] attention sink
- **工作量**：12 月 · **目标**：ICLR / EMNLP
- **章节连接**：模块 12 §05 §12.2 KV Cache + 模块 14 §03

### PR-4 · Mamba/SSM 的状态空间模型收敛性（前沿）
- **问题**：Mamba 的 selective SSM 在什么条件下保持长期记忆稳定？状态空间的 Lipschitz 常数如何控制？
- **数学工具**：控制论 + 动力系统稳定性 + 矩阵指数
- **前沿锚点**：Mamba [arXiv:2312.00752] + Sessa [arXiv:2604.18580]
- **工作量**：18 月 · **目标**：NeurIPS / ICML
- **章节连接**：模块 11 §07 §2.7 + 模块 14 §04

### PR-5 · 排队论分析 LLM Serving 系统（入门→进阶）
- **问题**：把 vLLM 副本建模为 M/G/1 排队系统，推导 P99 延迟的解析解；重尾分布（少数超长请求）如何影响稳定性？
- **数学工具**：排队论 + Pollaczek-Khinchine 公式 + 重尾分布
- **前沿锚点**：Mooncake [arXiv:2407.00079] KV-cache 排队
- **工作量**：6-12 月 · **目标**：SIGMETRICS / MLSys / EuroSys
- **章节连接**：模块 12 §05 §14.3

### PR-6 · 贝叶斯不确定性量化用于 AI4Science（进阶）
- **问题**：AlphaFold 的结构预测能给置信区间吗？如何用贝叶斯推断量化 GNoME 晶体稳定性预测的不确定性？
- **数学工具**：贝叶斯推断 + 变分推断 + 蒙特卡洛
- **前沿锚点**：AlphaFold pLDDT + 2024 ensemble 方法
- **工作量**：12 月 · **目标**：NeurIPS / Nature Machine Intelligence
- **章节连接**：模块 02 §4.2 实验噪声 + 模块 14 §01 §六

---

## §3. 数值分析方向（6 个课题）

### NA-1 · FP16 混合精度的误差传播分析（入门）
- **问题**：在飞腾 D3000（ARMv8.2-A）上，FP16 输入 + FP32 累加的误差如何随序列长度增长？能否给出显式误差上界？
- **数学工具**：浮点误差分析 + 条件数 + Higham 理论
- **前沿锚点**：飞腾 D3000 [项目模块 14 §05 §11] + FlashAttention 数值稳定
- **工作量**：6 月 · **目标**：arXiv preprint / workshop
- **章节连接**：模块 14 §05 §11.4 + §二 浮点

### NA-2 · 自动微分的形式化验证（进阶）
- **问题**：Certigrad4 用 Lean 证明了 MM/MV 的 gradient 正确——能否扩展到 attention 的反向传播（含 KV cache / masking / FlashAttention 的边界）？
- **数学工具**：Lean 4 + 数学归纳法 + 自动微分理论
- **前沿锚点**：Certigrad4 + Lean Copilot [arXiv:2404.12534]
- **工作量**：12-18 月 · **目标**：ICML / POPL
- **章节连接**：模块 12 §01 §10 + 模块 13 §13 §五

### NA-3 · Neural ODE 的 stiff 求解器设计（进阶）
- **问题**：Neural ODE 在学习多尺度动力学时会出现 stiff 系统——现有求解器（Dormand-Prince / adaptive Heun）如何优化？
- **数学工具**：ODE 数值解 + stiff 系统理论 + 隐式方法
- **前沿锚点**：Neural ODE [arXiv:1806.07366] + 2024 stiff 研究进展
- **工作量**：12 月 · **目标**：NeurIPS / ICML
- **章节连接**：模块 14 §05 §八 + §04 动力系统

### NA-4 · 国产 ARM CPU 的量化推理精度-速度 Pareto 前沿（入门→进阶）
- **问题**：在飞腾 D3000（INT8+SDOT / 无 BF16 / 无 SVE）上，量化推理的精度-速度 Pareto 前沿在哪？与 NVIDIA H100 的差距有多少是架构的、多少是工具链的？
- **数学工具**：Roofline 模型 + 数值精度分析 + 实验设计
- **前沿锚点**：MXFP4 QAT [docs/frontier-deep-dive/05] vs INT8 SDOT [模块 14 §05 §11]
- **工作量**：6-12 月 · **目标**：MLSys / EuroSys
- **章节连接**：模块 14 §05 §11 + 模块 12 §05 §13.6

### NA-5 · 大模型训练的 Loss Spike 数值分析（进阶）
- **问题**：DeepSeek-V3 做到"全程无 spike"——但 spike 的数值根源是什么？能否用浮点误差分析预测 spike？
- **数学工具**：浮点动力学 + 梯度统计 + 条件数监控
- **前沿锚点**：DeepSeek-V3 Technical Report [arXiv:2412.19437]
- **工作量**：12 月 · **目标**：ICLR / MLSys
- **章节连接**：模块 12 §01 §三 训练稳定性

### NA-6 · 谱方法用于 PDE 的神经网络加速（前沿）
- **问题**：用神经网络学习 PDE 的谱系数，能否比传统谱方法快 10-100×？误差如何控制？
- **数学工具**：谱方法 + 函数逼近论 + Galerkin 投影
- **前沿锚点**：Neural Operator [arXiv:1806.07366] + 2024-2026 Fourier Neural Operator
- **工作量**：18 月 · **目标**：NeurIPS / ICML / JCP
- **章节连接**：模块 14 §05 §九 谱方法 + 模块 02 §05 物理

---

## §4. 优化理论方向（6 个课题）

### OP-1 · Muon 优化器的收敛性证明（入门→进阶）
- **问题**：Kimi K3 用 Per-Head Muon 优化器——Muon（基于矩阵正交化）的收敛速率如何在非凸设定下证明？
- **数学工具**：凸优化 + 矩阵分析 + 随机逼近
- **前沿锚点**：Kimi K3 Per-Head Muon + Moonshot 技术报告
- **工作量**：6-12 月 · **目标**：NeurIPS / ICML
- **章节连接**：模块 14 §01 §九 优化理论

### OP-2 · RLHF/DPO/GRPO 的优化理论统一（进阶）
- **问题**：DPO 把 RLHF 简化为分类——能否用一个统一的优化框架解释 PPO/DPO/KTO/GRPO 的关系？
- **数学工具**：博弈论 + 变分推断 + KL 散度
- **前沿锚点**：DPO [arXiv:2305.18290] + GRPO [arXiv:2402.03300 DeepSeekMath]
- **工作量**：12 月 · **目标**：ICLR / NeurIPS
- **章节连接**：模块 12 §03 对齐训练

### OP-3 · AlphaProof Nexus 解决的优化问题深挖（前沿）
- **问题**：AlphaProof Nexus 解决了"Anchored GDA 的 O(1/t) 收敛率"开放问题——能否推广到更一般的 min-max 优化？
- **数学工具**：min-max 优化 + Lyapunov 函数 + ODE 连续时间分析
- **前沿锚点**：AlphaProof Nexus [arXiv:2605.22763]
- **工作量**：18 月 · **目标**：NeurIPS / Math Programming
- **章节连接**：模块 14 §01 §九 + 模块 13 §13

### OP-4 · MoE 路由的均衡理论（进阶）
- **问题**：Kimi K3 的 Quantile Balancing vs DeepSeek V3 的 aux-loss-free——哪种路由均衡策略在理论上更优？
- **数学工具**：博弈论（Nash 均衡）+ 排序统计 + 负载均衡
- **前沿锚点**：Kimi K3 Stable LatentMoE + DeepSeek V3
- **工作量**：12 月 · **目标**：ICML / NeurIPS
- **章节连接**：模块 11 §06 MoE + docs/frontier-deep-dive/01

### OP-5 · test-time compute 的最优分配（进阶→前沿）
- **问题**：o1/R1 风格的 test-time compute（推理时多算）——给定固定推理算力，如何在"想更多 step"vs"试更多 branch"之间最优分配？
- **数学工具**：最优停止理论 + 多臂老虎机 + 树搜索
- **前沿锚点**：DeepSeek-R1 [arXiv:2501.12948] + AlphaProof TTRL
- **工作量**：12-18 月 · **目标**：ICLR / NeurIPS
- **章节连接**：模块 13 §05 规划推理

### OP-6 · 灾难性抵消在梯度下降中的避免（入门→进阶）
- **问题**：$1 - \cos(x)$ 在 $x \to 0$ 时的灾难性抵消——在梯度下降的 loss landscape 中，类似的抵消如何影响收敛？Adam 的 momentum 如何缓解？
- **数学工具**：条件数 + 预条件 + Hessian 分析
- **前沿锚点**：模块 14 §05 §二 灾难性抵消 + Adam 理论
- **工作量**：6-12 月 · **目标**：arXiv / workshop → NeurIPS
- **章节连接**：模块 14 §05 §二 + §三 条件数

---

## §5. 信息论方向（6 个课题）

### IT-1 · LLM 的上下文窗口信息容量（入门→进阶）
- **问题**：一个 1M token 上下文的 LLM 实际能"记住"多少 bit？信息容量 vs 上下文长度的 scaling law？
- **数学工具**：Shannon 信息论 + 信道容量 + rate-distortion
- **前沿锚点**：Kimi K3 1M context + Inkling 1M + Needle-in-Haystack benchmark
- **工作量**：6-12 月 · **目标**：NeurIPS / EMNLP
- **章节连接**：模块 14 §01 §四 信息论

### IT-2 · KV Cache 的信息压缩极限（进阶）
- **问题**：KV cache 本质是历史信息的"压缩表示"——信息论下界是什么？现有 7 种 Cache 距离极限多远？
- **数学工具**：rate-distortion 理论 + 信息瓶颈
- **前沿锚点**：模块 12 §05 §12.2 七种 Cache + StreamingLLM [arXiv:2309.17453]
- **工作量**：12 月 · **目标**：ICLR / NeurIPS
- **章节连接**：模块 12 §05 §12.2

### IT-3 · 推测解码的 Accept Rate 信息论分析（入门→进阶）
- **问题**：speculative decoding 的 accept rate $\alpha$ 和 draft/target 模型的 KL 散度有什么关系？能否用信息论预测 $\alpha$？
- **数学工具**：KL 散度 + 互信息 + 假设检验
- **前沿锚点**：Leviathan [arXiv:2211.17192] + Medusa [arXiv:2401.10774]
- **工作量**：6-12 月 · **目标**：NeurIPS / ICML
- **章节连接**：模块 12 §05 §12.1

### IT-4 · 联邦学习的隐私-效用 tradeoff（进阶）
- **问题**：差分隐私（DP）在联邦学习中的隐私预算 $\epsilon$ 和模型效用 loss 的定量关系是什么？
- **数学工具**：差分隐私 + 信息论 + PAC-Bayes
- **前沿锚点**：DP-SGD + 2024-2026 FL 理论进展
- **工作量**：12 月 · **目标**：NeurIPS / ICML / CCS
- **章节连接**：模块 13 §08 安全 + 模块 14 §01 §四

### IT-5 · Agent 记忆系统的信息瓶颈（进阶→前沿）
- **问题**：Agent 的长期记忆（如 MemGPT）如何在有限存储下做信息检索？最优遗忘策略是什么？
- **数学工具**：信息瓶颈 + 缓存替换理论 + 记忆遗忘曲线
- **前沿锚点**：MemGPT + Generative Agents + 模块 13 §04
- **工作量**：12-18 月 · **目标**：NeurIPS / ICLR
- **章节连接**：模块 13 §04 记忆生态

### IT-6 · 量化模型的信息损失下界（前沿）
- **问题**：从 FP16 量化到 INT4 / MXFP4，信息论下界的损失是多少？现有方法（GPTQ/AWQ/QAT）距离下界多远？
- **数学工具**：rate-distortion 理论 + 量化误差分析 + 信息论不等式
- **前沿锚点**：MXFP4 QAT [Kimi K3] + GPTQ [arXiv:2210.17323] + AWQ [arXiv:2306.00978]
- **工作量**：18 月 · **目标**：NeurIPS / ICML / IEEE IT
- **章节连接**：模块 12 §05 §12.3 + docs/frontier-deep-dive/05

---

## §5.6 扩展方向（20 个课题，覆盖 CV/NLP/RL/Agent/AI4Science/安全）

前 30 个课题聚焦用户画像的 5 个数学方向。以下是 6 个应用/交叉方向的 20 个课题，适合在数学基础建立后探索。

### CV（计算机视觉）· 3 个

**CV-1 · Vision Transformer 的等变性理论**（进阶）
- **问题**：ViT 处理图像 patch 时，translation/rotation 等变性如何形式化？为什么数据增强不如架构等变有效？
- **数学工具**：群论 + 表示论 + 等变网络
- **前沿锚点**：DeiT [arXiv:2010.11929] + NequIP [Nature Comm 2022] 等变势函数的启示
- **工作量**：12 月 · **目标**：CVPR / NeurIPS
- **章节连接**：模块 11 §01 attention + 模块 02 §3.2 等变网络

**CV-2 · 扩散模型采样的随机分析优化**（进阶）
- **问题**：Stable Diffusion 的采样（DDIM/DPM-Solver）本质上是在解 reverse-time SDE——能否用随机分析设计更快的采样器？
- **数学工具**：SDE 数值解 + 随机插值
- **前沿锚点**：DPM-Solver [arXiv:2206.00927] + Flow Matching [arXiv:2305.10415]
- **工作量**：12 月 · **目标**：NeurIPS / ICML
- **章节连接**：模块 14 §05 §八 + 模块 14 §03

**CV-3 · 多模态对齐的信息论基础**（前沿）
- **问题**：CLIP 的 contrastive learning 本质是在做什么信息压缩？最优的 temperature 参数有理论最优值吗？
- **数学工具**：互信息 + rate-distortion + 对比损失理论
- **前沿锚点**：CLIP [arXiv:2103.00020] + InfoNCE 理论
- **工作量**：18 月 · **目标**：NeurIPS / CVPR
- **章节连接**：模块 11 §08 多模态

### NLP（自然语言处理）· 3 个

**NLP-1 · LLM 的 in-context learning 理论**（进阶→前沿）
- **问题**：为什么 GPT 能从 few-shot 示例中"学到"新任务，而不更新权重？这与梯度下降有什么等价关系？
- **数学工具**：线性回归 + 隐式梯度 + 双下降
- **前沿锚点**：Garg et al. 2022 "What can transformers learn in-context?" + Akyürek et al. 2022
- **工作量**：12-18 月 · **目标**：ICLR / NeurIPS
- **章节连接**：模块 11 §06 Transformer 变种

**NLP-2 · Tokenizer 的信息损失分析**（入门→进阶）
- **问题**：BPE/SentencePiece 在分词时丢失了多少信息？不同 tokenizer 对下游任务的影响能否量化？
- **数学工具**：信息论 + 压缩理论 + 编辑距离
- **前沿锚点**：SciReasoner [arXiv:2607.07708] 的 structure-aware tokenizer
- **工作量**：6-12 月 · **目标**：ACL / EMNLP
- **章节连接**：模块 11 §07 + docs/frontier-deep-dive/04

**NLP-3 · 长文本生成的全局一致性**（进阶）
- **问题**：LLM 在长文本生成中如何保持人物/情节/逻辑一致？能否用状态机/形式语法约束？
- **数学工具**：形式语法 + 有限状态自动机 + 图约束
- **前沿锚点**：OSWorld 2.0 长任务 [Agent S3] + DeepSeek-R1 长推理链
- **工作量**：12 月 · **目标**：ACL / NeurIPS
- **章节连接**：模块 13 §05 + §10

### RL（强化学习）· 4 个

**RL-1 · RLHF 中 reward hacking 的检测与缓解**（入门→进阶）
- **问题**：reward model 被"钻空子"（Goodhart's Law）——如何检测？KL 惩罚真的有效吗？
- **数学工具**：博弈论 + 对抗分析 + KL 散度
- **前沿锚点**：Constitutional AI [arXiv:2212.08073] + DeepSeek-R1 RLVR
- **工作量**：6-12 月 · **目标**：NeurIPS / ICLR
- **章节连接**：模块 12 §03 对齐 + 模块 13 §08 安全

**RL-2 · GRPO 的收敛性分析**（进阶）
- **问题**：DeepSeekMath 提出的 GRPO（Group Relative Policy Optimization）与标准 PPO 的收敛速率对比？
- **数学工具**：随机逼近 + 策略梯度理论 + 方差缩减
- **前沿锚点**：DeepSeekMath [arXiv:2402.03300] + PPO [arXiv:1707.06347]
- **工作量**：12 月 · **目标**：ICML / NeurIPS
- **章节连接**：模块 12 §03

**RL-3 · Agent 的 test-time compute 最优分配**（进阶→前沿）
- **问题**：给定固定推理算力，Agent 应该"多想几步"还是"多试几条路径"？ReAct vs ToT vs MCTS 的最优选择？
- **数学工具**：最优停止理论 + 多臂老虎机 + 树搜索
- **前沿锚点**：o1/R1 test-time scaling + AlphaProof TTRL
- **工作量**：12-18 月 · **目标**：ICLR / NeurIPS
- **章节连接**：模块 13 §05 规划推理

**RL-4 · 自博弈（Self-play）的纳什均衡收敛**（前沿）
- **问题**：AlphaGo/AlphaProof 用自博弈训练——自博弈在什么条件下收敛到 Nash 均衡？什么条件下循环不收敛？
- **数学工具**：博弈论 + 虚拟自我博弈理论 + 随机逼近
- **前沿锚点**：AlphaProof [Nature 2025] + AlphaGo Zero
- **工作量**：18 月 · **目标**：NeurIPS / COLT
- **章节连接**：模块 13 §13 §3.4

### Agent 系统· 4 个

**AG-1 · Agent 安全的形式化保证**（进阶→前沿）
- **问题**：如何用形式化方法（Lean/Z3）证明一个 Agent 不会执行某些危险操作（如删数据库）？
- **数学工具**：模型检查 + 时态逻辑 + LSM 策略验证
- **前沿锚点**：模块 13 §13 §四 Pattern B + ai-os-dd M8 Z3
- **工作量**：12-18 月 · **目标**：USENIX Sec / CCS / S&P
- **章节连接**：模块 13 §08 安全 + §13 形式化

**AG-2 · 多 Agent 博弈的机制设计**（进阶）
- **问题**：多个 LLM Agent 协作/竞争时，如何设计激励机制（mechanism design）让它们不欺骗？
- **数学工具**：机制设计 + 拍卖理论 + 博弈论
- **前沿锚点**：ChatDev / MetaGPT + AI 选举/辩论
- **工作量**：12 月 · **目标**：AAMAS / NeurIPS
- **章节连接**：模块 13 §06 多 Agent

**AG-3 · Agent 记忆的信息瓶颈**（进阶）
- **问题**：Agent 的长期记忆在有限存储下的最优遗忘策略？信息瓶颈方法如何应用？
- **数学工具**：信息瓶颈 + rate-distortion + 记忆模型
- **前沿锚点**：MemGPT + Generative Agents
- **工作量**：12 月 · **目标**：NeurIPS / ICLR
- **章节连接**：模块 13 §04 记忆

**AG-4 · Agent Benchmark 的统计有效性**（入门→进阶）
- **问题**：现有 Agent benchmark（OSWorld/SWE-bench/GAIA）的统计功效（statistical power）如何？多少样本才够？
- **数学工具**：假设检验 + 效应量 + 样本量计算
- **前沿锚点**：AgentBench [arXiv:2308.03688] + OSWorld 2.0
- **工作量**：6-12 月 · **目标**：NeurIPS D&B / EMNLP
- **章节连接**：模块 13 §07 评估

### AI4Science · 3 个

**SC-1 · 蛋白质 folding 的自由能景观理论**（进阶→前沿）
- **问题**：AlphaFold 学到的表征与物理自由能景观有什么关系？模型是否隐式学到了能量函数？
- **数学工具**：统计力学 + 自由能 + 能量景观
- **前沿锚点**：AlphaFold 2/3 [Nature 2021/2024] + ESM3
- **工作量**：12-18 月 · **目标**：Nature Machine Intelligence / NeurIPS
- **章节连接**：模块 02 §3 + §6

**SC-2 · AI 发现新材料的可证伪性**（进阶）
- **问题**：GNoME 发现了 220 万新晶体——如何系统验证它们的稳定性？分层验证协议如何设计？
- **数学工具**：统计检验 + DFT 交叉验证 + 实验设计
- **前沿锚点**：GNoME [Nature 624:80] + A-Lab 自主合成
- **工作量**：12 月 · **目标**：Nature Materials / NeurIPS
- **章节连接**：模块 02 §5 可复现性 + §8.1

**SC-3 · SciReasoner 跨域表征的信息论分析**（进阶）
- **问题**：SciReasoner 把蛋白质/分子/晶体统一编码——这个"统一表征空间"的几何结构是什么？
- **数学工具**：信息几何 + 表征学习 + 流形学习
- **前沿锚点**：SciReasoner [arXiv:2607.07708]
- **工作量**：12 月 · **目标**：NeurIPS / ICML
- **章节连接**：模块 02 §3.5 + docs/frontier-deep-dive/04

### 安全与对齐 · 3 个

**SA-1 · Prompt Injection 的形式化检测**（入门→进阶）
- **问题**：如何用形式化方法（正则 + 类型系统 + LLM classifier）检测 prompt injection？误报率和漏报率的 tradeoff？
- **数学工具**：形式语言 + 假设检验 + 分类理论
- **前沿锚点**：Lakera Guard + OWASP LLM Top 10
- **工作量**：6-12 月 · **目标**：USENIX Sec / ACL
- **章节连接**：模块 13 §08 §9.1

**SA-2 · RLHF 后校准（Calibration）的数学理论**（进阶）
- **问题**：RLHF 后的模型概率校准变差（overconfident）——为什么？如何数学化度量和修复？
- **数学工具**：概率校准 + Brier score + 期望校准误差（ECE）
- **前沿锚点**：OpenAI 的 calibration 研究 + Kadavath et al. 2022
- **工作量**：12 月 · **目标**：NeurIPS / ICLR
- **章节连接**：模块 12 §03 + 模块 13 §08

**SA-3 · Constitutional AI 的"宪法"设计理论**（前沿）
- **问题**：Constitutional AI 用一组规则（"宪法"）指导自我修正——如何数学化"宪法"的完备性？哪些规则组合是矛盾的？
- **数学工具**：deontic logic（道义逻辑）+ 一致性理论 + 社会选择理论
- **前沿锚点**：Constitutional AI [arXiv:2212.08073]
- **工作量**：18 月 · **目标**：NeurIPS / FAccT
- **章节连接**：模块 13 §08

---

## §6. 如何使用这份清单

### 6.1 选择课题的 3 个原则

1. **先选"入门"级**（标注"入门"或"入门→进阶"的）：ML-1 / PR-1 / PR-5 / NA-1 / NA-4 / OP-1 / OP-6 / IT-1 / IT-3——这些 6-12 月可出成果
2. **选与你的数学基础匹配的**：如果概率基础好，选 PR-1/PR-2/PR-3；如果优化好，选 OP-1/OP-2/OP-6
3. **锚定一个"前沿锚点"论文**：每个课题都有一篇 2025-2026 论文做起点——先精读这篇，再找 gap

### 6.2 6-8 年路径规划（基于用户画像）

```
Year 1-2（入门 → 进阶）：
  选 1 个"入门"课题（如 ML-1 / PR-5 / NA-1 / IT-3）
  补对应的数学基础
  产出：1-2 篇 workshop / arXiv preprint

Year 3-4（进阶 → 前沿）：
  选 1 个"进阶"课题（如 ML-2 / PR-2 / NA-2 / OP-2 / IT-2）
  开始建立学术声誉
  产出：1-2 篇顶会（NeurIPS/ICLR/ICML）

Year 5-6（前沿 → 研究者）：
  选 1 个"前沿"课题（如 ML-3 / ML-6 / NA-6 / OP-3 / IT-6）
  可能申请博士或大厂研究院
  产出：1 篇 Oral / Nature 子刊

Year 7-8（独立研究者）：
  在选定方向做系统性贡献
  目标：领域内被认可
```

### 6.3 每个课题的"第一步"

不管选哪个课题，**第一步都是**：
1. 精读"前沿锚点"论文（项目里标注的 arXiv）
2. 复现论文的核心实验（项目有 114 个 .py 实验脚本可参考）
3. 找一个"论文没回答的问题"——那就是你的课题

---

## §7. 这份清单与项目的关系

```
项目 132 万字（全景知识库）
    ↓ 提炼
30 个研究课题（研究导航仪）
    ↓ 锚定
前沿锚点论文（2025-2026 SOTA）
    ↓ 行动
6-8 年路径（从学到做研究）
```

这份清单把项目从"被动的知识库"升级为"主动的研究导航仪"——**读项目不是为了"学会 AI"，而是为了"找到值得做的问题"**。

---

## §8. 附录：2025-2026 AI4Math 三大旗舰（搜索新增）

这一轮搜索发现了 3 个**此前项目未覆盖**的 AI4Math 旗舰，应该补充到模块 03（AI4Math）：

1. **AlphaProof**（Nature 2025-11-12, DOI: 10.1038/s41586-025-09833-y）
   - AlphaZero-inspired RL on Lean · TTRL（推理时生成百万变体）
   - miniF2F-test 97.7%（12 TPU hours）→ 99.6%（500 TPU days TTRL）
   - IMO 2024 银牌（解 4/6 含最难 P6）
   - **已在模块 13 §13 引用，但 Nature DOI 是本轮新确认**

2. **DeepSeek-Prover-V2**（arXiv:2504.21801, 2025-04）
   - 开源 671B Lean 证明器 · subgoal decomposition
   - Mini-F2F test 88.9% pass@8192 · ProverBench 325 题（含 15 AIME）
   - **项目此前未引用**

3. **DeepSeekMath-V2**（arXiv:2511.22570, 2025-11）
   - **Self-Verifiable Mathematical Reasoning**——LLM 自己验证自己的证明
   - IMO 2025 金牌 + Putnam 2024 118/120（超人类最佳 90）
   - **项目此前未引用——这是 AI4Math 的范式转移**

4. **AlphaProof Nexus**（arXiv:2605.22763, 2026-06）
   - **首个大规模"AI 解决开放数学问题"**：9/353 Erdős 开放问题 + 44/492 OEIS 猜想
   - Agent 框架（LLM + Lean + AlphaProof as tool）+ 进化算法
   - **项目此前未引用——这是 AI 从"竞赛数学"走向"研究数学"的标志**

> 这 4 个论文 + 模块 13 §13 已有的 LeanDojo / Lean Copilot / Certigrad4，构成了 AI4Math 的 2025-2026 完整图景。建议后续（v2.0.8?）补到模块 03 AI4Math 的对应章节。

---

**清单元数据**：
- 产出：2026-07-23（v2.0.7）
- 课题来源：项目 14 模块的 §八/思考题/给建议 + 2025-2026 websearch 前沿
- 课题数量：30（5 方向 × 6 课题）
- 三层难度：入门 9 个 / 进阶 14 个 / 前沿 7 个
