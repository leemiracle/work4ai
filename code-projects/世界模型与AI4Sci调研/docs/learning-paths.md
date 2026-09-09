# 学习路径指南：从零到能做 10 个研究课题

> 产出：2026-07-23（v2.0.8 Phase C）
> 面向：数学自评 0 / Python 工程级 / PyTorch 跑过教程 / 每周 10-20h / 目标 6-8 年达研究入门级
> 用途：从 `research-topics-50.md` 的 50 个课题中选 10 个最匹配用户画像的"入门级"，给出"从零到能开始做"的具体学习路径

---

## §0. 为什么是 10 个而不是 50 个

50 个课题里，只有 10 个是"入门"或"入门→进阶"级，且数学基础可以从零补起。其余 40 个要么需要先完成这 10 个之一，要么需要更强的数学先修。**先做好 1 个，再扩展**——这比"同时看 50 个课题然后一个都不开始"有用得多。

---

## §1. 10 个课题的学习路径

### 路径 1 · ML-1 形式化 Agent 的 Reward Hacking 分类学

**什么时候算"准备好了"**：能读懂 LeanDojo 论文 [arXiv:2306.15626] + 能跑通 `experiments_13/01_leandojo_state_machine.py`

**学习路径（3-4 月）**：
1. **数学补课**：形式语言理论入门（Hopcroft Ullman《自动理论》前 3 章，理解"语言 vs 语法 vs 自动机"）
2. **Lean 入门**：*Theorem Proving in Lean 4* 官方教程前 5 章（理解 Prop / Type / tactic）
3. **实践**：跑通项目的 `experiments_13/01_leandojo_state_machine.py`，理解 sorry 反例
4. **论文精读**：LeanDojo [2306.15626] + Lean Copilot [2404.12534]
5. **找 gap**：LeanDojo 没有系统讨论"LLM 在形式化环境的作弊行为"——这就是你的课题入口

**第一步行动**：今天就读 LeanDojo 论文的 abstract + introduction

---

### 路径 2 · PR-1 Diffusion 模型的 Score Matching 数学基础

**什么时候算"准备好了"**：能推导 $\nabla \log p(x)$ 的 Stein 估计 + 能跑通 DDPM 的最小实现

**学习路径（4-6 月）**：
1. **数学补课**：概率论基础（测度论 not 必需，但要理解 density / gradient / conditional probability）→ 随机过程入门（Brown 运动 + SDE 概念）
2. **核心论文**：Song et al. [arXiv:1907.05600] score-based + DDPM [arXiv:2006.11239]
3. **教材**：模块 14 §03 概率随机过程（项目内）+ 前面的 §02 数学物理建模（RG + 统计力学）
4. **实践**：实现一个最小 DDPM（参考模块 14 §05 §八 的 SDE 数值解代码）
5. **找 gap**：score matching 在高维的方差爆炸——为什么？能否设计低方差估计器？

**第一步行动**：读 DDPM 论文 + 跑 HuggingFace diffusers 的 minimal DDPM demo

---

### 路径 3 · PR-5 排队论分析 LLM Serving 系统

**什么时候算"准备好了"**：能推导 M/G/1 的 Pollaczek-Khinchine 公式 + 能解释 vLLM 的 continuous batching 为什么有效

**学习路径（3-4 月）**：
1. **数学补课**：排队论入门（Harchol-Balter《Performance Modeling》前 5 章，理解 M/M/1 → M/G/1 → Little's Law）
2. **核心概念**：模块 12 §05 §14.3 的排队论分析（项目内已有完整推导）
3. **实践**：用 Python 模拟一个 M/G/1 系统，参数取自 vLLM 真实 trace
4. **论文精读**：Mooncake [arXiv:2407.00079] KV-cache 排队
5. **找 gap**：现有 M/G/1 模型假设服务时间独立——但 LLM 的 decode 时间和 batch size 相关，如何修正？

**第一步行动**：读模块 12 §05 §14.3（项目内排队论段）+ 做 §14.3 的思考题

---

### 路径 4 · NA-1 FP16 混合精度的误差传播分析

**什么时候算"准备好了"**：能推导浮点加法的相对误差上界 + 能解释为什么 FP16 累加会丢精度

**学习路径（3 月）**：
1. **数学补课**：Higham《Accuracy and Stability of Numerical Algorithms》前 3 章（IEEE 754 + 舍入误差 + 条件数）
2. **项目内**：模块 14 §05 §二 浮点数 + §11.4 FP16 实验（项目已有完整推导 + bash 跑通的实验）
3. **实践**：跑通 `experiments_05/06_phytium_d3000_fp16_neon.py` 的实验 1（FP16 vs FP32 精度对比）
4. **找 gap**：FP16 累加的误差如何随序列长度 $n$ 增长？能否给出 $\epsilon(n) = O(f(n))$ 的显式形式？

**第一步行动**：跑通项目实验 06 的 Part 1（3 分钟）

---

### 路径 5 · NA-4 国产 ARM 量化推理的 Pareto 前沿

**什么时候算"准备好了"**：能画 Roofline 图 + 能解释 SDOT 和 i8mm 的区别

**学习路径（3-4 月）**：
1. **数学补课**：Roofline 模型（Williams et al. 2009 CACM，5 页论文，极短极清晰）
2. **项目内**：模块 14 §05 §11 飞腾 D3000 全节（项目已有完整 ISA 分析）
3. **实践**：在任意 ARM 设备上跑 INT8 GEMM（用 NEON intrinsics 或 QNNPACK），测 throughput
4. **找 gap**：D3000 的 INT8+SDOT vs H100 的 MXFP4，在 7B 推理上的 Pareto 前沿差距有多大？多少是架构的、多少是工具链的？

**第一步行动**：读模块 14 §05 §11.3 NEON SIMD（10 分钟）

---

### 路径 6 · OP-1 Muon 优化器的收敛性证明

**什么时候算"准备好了"**：能证明 SGD 在凸函数上的 $O(1/\sqrt{T})$ 收敛 + 理解 Adam 的预条件

**学习路径（4-6 月）**：
1. **数学补课**：凸优化入门（Boyd & Vandenberghe 前 5 章 + Nesterov《Introductory Lectures》前 3 章）
2. **核心论文**：Adam [arXiv:1412.6980] + Muon（Moonshot 2025 技术报告）
3. **项目内**：模块 14 §01 §九 优化理论 + 模块 11 §05 优化器深处
4. **实践**：实现 SGD / Adam / Muon 在一个凸函数上的对比（用 PyTorch）
5. **找 gap**：Muon 基于"矩阵正交化"——为什么这比 Adam 的"逐元素"预条件更好？收敛速率如何证明？

**第一步行动**：读 Adam 论文 + 模块 11 §05 优化器深处

---

### 路径 7 · OP-6 灾难性抵消在梯度下降中的避免

**什么时候算"准备好了"**：能用 `1 - cos(x)` 的例子展示灾难性抵消 + 理解条件数如何影响优化

**学习路径（3 月）**：
1. **数学补课**：条件数（模块 14 §05 §三，项目内已有完整推导）+ 浮点舍入（§二）
2. **实践**：跑模块 14 §05 的实验 2（1-cos 灾难性抵消，bash 跑通）
3. **找 gap**：Adam 的 momentum 如何缓解"梯度空间里的灾难性抵消"？能否给出显式的误差缩减因子？

**第一步行动**：跑模块 14 §05 的 1-cos 实验（2 分钟）

---

### 路径 8 · IT-1 LLM 的上下文窗口信息容量

**什么时候算"准备好了"**：能计算 Shannon 信道容量 + 理解 rate-distortion 的基本概念

**学习路径（4-6 月）**：
1. **数学补课**：信息论入门（Cover & Thomas《Elements of Information Theory》前 8 章）
2. **项目内**：模块 14 §01 §四 信息论（项目内已有 Shannon 熵 / 互信息 / KL / 交叉熵 / 信道容量）
3. **实践**：对 Llama-3-8B 做 needle-in-haystack 测试，测量不同上下文长度下的信息检索率
4. **找 gap**：1M token 上下文的 LLM 实际能"记住"多少 bit？信息容量 vs 上下文长度的 scaling law？

**第一步行动**：读 Cover & Thomas 第 2 章（Shannon 熵）

---

### 路径 9 · IT-3 推测解码的 Accept Rate 信息论分析

**什么时候算"准备好了"**：能计算 KL 散度 + 理解假设检验的基本概念

**学习路径（3-4 月）**：
1. **数学补课**：信息论基础（Cover & Thomas 第 2/8/11 章：熵 / 互信息 / 假设检验）
2. **项目内**：模块 12 §05 §12.1 推测解码（项目内已有 Leviathan 加速比公式 + 实验）
3. **实践**：跑 `experiments_deployment/11_attention_sink_and_spec_decoding.py` 的 Part 3（加速比公式）
4. **找 gap**：accept rate $\alpha$ 和 draft/target 模型的 KL 散度有什么定量关系？能否用信息论预测 $\alpha$？

**第一步行动**：跑项目实验 11 的 Part 3（3 分钟）

---

### 路径 10 · NLP-2 Tokenizer 的信息损失分析

**什么时候算"准备好了"**：能用 BPE/SentencePiece 分词 + 理解信息熵

**学习路径（3-4 月）**：
1. **数学补课**：信息论基础（Cover & Thomas 第 5 章：rate-distortion）+ 编辑距离（CL 经典算法）
2. **核心论文**：SciReasoner [arXiv:2607.07708] 的 structure-aware tokenizer
3. **实践**：对比 BPE / WordPiece / SentencePiece 在同一文本上的 token 数 + 信息熵
4. **找 gap**：不同 tokenizer 的信息损失差异有多大？对下游任务的影响能否量化？

**第一步行动**：用 HuggingFace tokenizers 库对比 3 种 tokenizer 在中文文本上的表现（30 分钟）

---

## §2. 10 条路径的共同"第一步"

不管选哪条，**今天就能做的第一件事**是：

| 路径 | 今天的第一步 | 时间 |
|---|---|---|
| ML-1 | 读 LeanDojo 论文 abstract | 15 分钟 |
| PR-1 | 跑 HuggingFace diffusers DDPM demo | 30 分钟 |
| PR-5 | 读模块 12 §05 §14.3 排队论段 | 20 分钟 |
| NA-1 | 跑项目实验 06 Part 1 | 3 分钟 |
| NA-4 | 读模块 14 §05 §11.3 | 10 分钟 |
| OP-1 | 读 Adam 论文 abstract | 15 分钟 |
| OP-6 | 跑 1-cos 实验 | 2 分钟 |
| IT-1 | 读 Cover & Thomas 第 2 章 | 30 分钟 |
| IT-3 | 跑项目实验 11 Part 3 | 3 分钟 |
| NLP-2 | 对比 3 种 tokenizer | 30 分钟 |

**总时间**：每条路径的"第一步"都在 30 分钟以内。**没有"我还没准备好"的借口**。

---

## §3. 从"第一步"到"第一个论文"的 6-12 月路径

```
Month 0（本周）：
  选 1 条路径 → 做"第一步"（30 分钟）
  ↓
Month 1-2：
  数学补课（教材前 3-5 章）
  + 跑通项目里的对应实验
  ↓
Month 3-4：
  精读"前沿锚点"论文（全文 + 复现核心实验）
  ↓
Month 5-8：
  找到 gap → 设计实验 → 跑第一批结果
  ↓
Month 9-12：
  写论文 → 投 workshop 或 arXiv preprint
  ↓
Year 2：投顶会
```

---

## §4. 10 条路径的"数学补课清单"

按数学方向分组，标出**最短路径**（只学做课题必需的，不追求完备）：

### 概率/随机过程（PR-1 / PR-5）
- **最短**：概率论基础（条件概率 / Bayes / 大数定律 / CLT）→ 排队论（M/M/1 → M/G/1）→ 随机过程（Markov 链）
- **教材**：Ross《Stochastic Processes》前 4 章 + Harchol-Balter 前 5 章
- **时间**：3-4 月

### 数值分析（NA-1 / NA-4）
- **最短**：IEEE 754 浮点 + 条件数 + 矩阵分解基础 + Roofline 模型
- **教材**：Higham 前 3 章 + Trefethen & Bau 前 4 章
- **时间**：2-3 月

### 优化理论（OP-1 / OP-6）
- **最短**：凸函数 + 梯度下降收敛 + Adam 预条件 + 条件数
- **教材**：Boyd & Vandenberghe 前 5 章 + Nesterov 前 3 章
- **时间**：3-4 月

### 信息论（IT-1 / IT-3）
- **最短**：Shannon 熵 + 互信息 + KL 散度 + 信道容量 + 假设检验
- **教材**：Cover & Thomas 前 8 章 + 第 11 章
- **时间**：3-4 月

### ML 理论 / 形式化（ML-1）
- **最短**：形式语言 + Lean 4 基础 + 类型论概念
- **教材**：Hopcroft Ullman 前 3 章 + TPIL4 前 5 章
- **时间**：3-4 月

### NLP（NLP-2）
- **最短**：信息论基础 + 编辑距离 + BPE 算法
- **教材**：Cover & Thomas 第 5 章 + HuggingFace tokenizers 文档
- **时间**：2-3 月

---

## §5. 与 50 个课题清单的关系

```
research-topics-50.md（50 个课题）
    ↓ "入门优先 + 数学匹配"
learning-paths.md（10 条路径）← 你在这里
    ↓ "今天第一步"
30 分钟内开始
    ↓ 6-12 月
第一个论文
    ↓ Year 2
顶会投稿
```

**核心原则**：**先做 1 个，做好再扩展**。不要同时看 10 条路径——选 1 条，做第一步，然后决定是否继续。

---

**指南元数据**：
- 产出：2026-07-23（v2.0.8 Phase C）
- 课题来源：`research-topics-50.md` 的 10 个"入门"级课题
- 每条路径含：先修 / 教材 / 实践 / 论文 / gap / 第一步行动
