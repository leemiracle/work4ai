# 05 · 方向深选：Mechanistic Interpretability

> **铁律**：4 路并修 = 4 路都浅。**先深后广**——选 1 个方向钻到世界第一，然后扩展。本文件推荐方向 = **Mechanistic Interpretability（机制可解释性）**。

---

## 🎯 为什么选 Mech Interp

| 维度 | 评估 |
|---|---|
| **数学深度** | ★★★★★（SVD / 流形几何 / 稀疏编码 / 概率）— 契合你的数学专家终极目标 |
| **算力门槛** | ★★☆（7B 模型可在单张 H100 / A100 上分析；probing 在消费级 GPU 可做）|
| **开源生态** | ★★★★★（EleutherAI / Anthropic / OpenAI Superalignment 都是核心方向）|
| **社群开放度** | ★★★★★（EleutherAI / DLCT / interp Slack 都对新人极友好）|
| **理论 vs 工程平衡** | 偏理论，契合数学专家方向 |
| **变现路径** | Anthropic / OpenAI / DeepMind 持续高薪招 interp 研究员 |
| **未来 5 年** | ★★★★★（前沿模型可解释性是 AI safety 的核心 bottleneck）|

**反方观点**（你应该知道）：
- Interp 离产品远（不像 RAG / Agent 直接变现）
- 顶级岗位少（Anthropic interp team 全球 < 50 人）
- 进展非线性（很多月卡壳正常）

**结论**：如果你终极目标是数学专家 + AI 研究员，**这是当前最好的方向**。如果优先级是变现场景，选 RAG / Agent。

---

## 📚 必读资源（按顺序）

### 第 1 阶段：建直觉（月 1-2）

#### [必] 1. Anthropic Circuits Thread（必读全集）
- **URL**: `transformer-circuits.pub`
- **是什么**: Anthropic interp 团队的所有公开研究。从 2020 "In-context Learning and Induction Heads" 到 2024 "Scaling Monosemanticity"，是 interp 领域的「圣经」。
- **关键文章**（按时间读）:
  1. **"A Mathematical Framework for Transformer Circuits"**（2022）— 基础框架
  2. **"In-context Learning and Induction Heads"**（2022）— induction head 是核心概念
  3. **"Towards Monosemanticity"**（2023，Bricken et al.）— SAE 入门
  4. **"Scaling Monosemanticity"**（2024）— Claude 3 SAE
  5. **"Biology of a Large Language Model"**（2025）— Attribution Graphs 革命
- **每周 1 篇 + 实际跑代码验证**

#### [必] 2. Neel Nanda 的 Blog
- **URL**: `neelnanda.io`
- **是什么**: Neel Nanda 是 Google DeepMind interp 研究员 + MATS mentor。blog 通俗易懂。
- **必读**:
  - **"A Mechanistic Interpretability Agenda"** — 整个领域路线图
  - **"Actually, Othello-GPT has no emergent world model"** — 批判性思维示范
- **建议**: 把他所有 blog 都读

#### [必] 3. 3Blue1Brown + Jay Alammar
- **3Blue1Brown Neural Network 系列** — 直觉
- **Jay Alammar "Illustrated Transformer"** — `jalammar.github.io/illustrated-transformer` — 经典图解

#### [重] 4. Lilian Weng 长文
- **URL**: `lilianweng.github.io`
- **必读**: "Prompt Engineering"、"LLM Powered Autonomous Agents"、"Transformer Family"

### 第 2 阶段：动手（月 3-6）

#### [必] 5. ARENA 3.0（Alignment Research Engineer Accelerator）
- **URL**: `arena-chapter1-transformers.streamlit.app`（章节 1）/ 各章节独立 URL
- **是什么**: Apollo Research / LLM-Agents 维护的免费自学课程，5 章：
  - Chapter 1: Transformer from scratch（含 TransformerLens）
  - Chapter 2: Mech Interp 基础
  - Chapter 3: SAEs
  - Chapter 4: Advanced
  - Chapter 5: Capstone project
- **预期时间**: 100-150 小时
- **何时用**: 第 2 个月开始，每周 5-8h，**这是你最重要的实操入口**

#### [必] 6. Callum McDougall 的 interp tutorials
- **URL**: `github.com/callummcdougall`
- **是什么**: ARENA 主要作者，有大量 Jupyter notebook tutorial
- **关键**: **SAE-Vis 库**（可视化 SAE 特征）

### 第 3 阶段：前沿论文（月 7+）

按时间读 NeurIPS / ICLR interp workshop 经典论文：

#### [必] 经典论文清单
1. **Olah et al. (2020)** "Zoom In: An Introduction to Circuits" — circuits 起源
2. **Cammarata et al. (2020)** "Curve Circuits"
3. **Elhage et al. (2021)** "A Mathematical Framework for Transformer Circuits"
4. **Olsson et al. (2022)** "In-context Learning and Induction Heads"
5. **Bricken et al. (2023)** "Towards Monosemanticity"
6. **Templeton et al. (2024)** "Scaling Monosemanticity"（Claude 3 SAE）
7. **Cunningham et al. (2023)** SAE 原始论文
8. **Marks et al. (2024)** "Sparse Feature Circuits"
9. **Anthropic (2025)** "Biology of a Large Language Model" — Attribution Graphs
10. **Arditi et al. (2024)** "Refusal Direction" — 单根方向控制拒绝

---

## 🛠️ 工具栈（必学，按顺序）

### [必] 1. TransformerLens v3.0（Neel Nanda 原作，现 Jonah Larson 维护）
- **URL**: `github.com/TransformerLensOrg/TransformerLens`
- **是什么**: interp 研究标准库。Hook-based 干预、activation caching、weight 访问。
- **v3.0 (2026-04) 重大变化**:
  - 引入 **TransformerBridge** 系统
  - 从 ~200 模型扩展到 **9000 模型**（覆盖 48 架构）
  - 不再 reimplement 模型，直接 wrap HuggingFace
- **何时用**: 写 interp 实验、small-medium 模型（<9B 参数）
- **入门**: `transformerlensorg.github.io/TransformerLens/` → Main Demo

### [必] 2. SAELens v6（Joseph Bloom）
- **URL**: `github.com/decoderesearch/SAELens`
- **是什么**: 训练 / 分析 sparse autoencoders 的标准库。
- **特点**:
  - 与 TransformerLens 深度集成（`HookedSAETransformer`）
  - 也支持 HuggingFace / nnsight / 任何 PyTorch 模型
- **Slack**: `join.slack.com/t/opensourcemechanistic`（Open Source Mech Interp Slack）
- **何时用**: 学完 TransformerLens 后，进入 SAE 章节

### [必] 3. nnsight（NDIF 远程 interp）
- **URL**: `nnsight.net`
- **是什么**: interp on models too large to run locally。**通过 NDIF（National Deep Inference Facility）远程访问大模型**，包括 **Llama 3 405B**！
- **何时用**: 你想研究大模型但没算力时（完美契合你的预算约束）
- **入门**: `nnsight.net/notebooks/tutorials/get_started/start_remote_access/`

### [重] 4. nnterp（nnsight 的 TL 风格 wrapper）
- **URL**: `github.com/clmentbnn/nnterp`
- **是什么**: nnsight 之上加了 TransformerLens 风格的标准化接口，让你一份代码跑 GPT-2 / Llama / Gemma / Qwen / Phi。
- **特点**: 内置 logit lens / patchscope / activation steering

### [重] 5. Neuronpedia
- **URL**: `neuronpedia.org`
- **是什么**: 已训练 SAE 的特征库（web 界面探索）。包含 Gemma Scope 等预训练 SAE。

### [重] 6. Gemma Scope
- **是什么**: Google DeepMind 发布的 Gemma 2 每层预训练 SAE。直接拿来用，省训练成本。

### [选] 7. 其他 interp 工具
- **dictionary-learning**（`github.com/saprmarks/dictionary_learning`）— hackable SAE training
- **Sparsify**（`github.com/EleutherAI/sparsify`）— EleutherAI 的 TopK SAE
- **Overcomplete**（`github.com/KempnerInstitute/overcomplete`）— vision SAE
- **SAEBench**（`github.com/adamkarvonen/SAEBench`）— SAE benchmark suite

---

## 🧪 必复现项目（按难度）

每个复现都写成 blog，发出去。

### [必] 复现 1：Induction Heads（月 2-3）
- **源**: Olsson et al. 2022 / Anthropic Circuits Thread
- **做什么**: 用 TransformerLens 在 GPT-2-small 验证 induction head 存在 + 行为
- **预期发现**: layer 5-6 出现 prefix-matching 任务
- **难度**: ⭐⭐

### [必] 复现 2：IOI Circuit（月 3-4）
- **源**: Wang et al. 2022 "Interpretability in the Wild"
- **做什么**: GPT-2-small 处理 "John and Mary went to the store, John gave the bag to ___" 的电路
- **预期发现**: name mover heads + backup heads + S-inhibition heads
- **难度**: ⭐⭐⭐

### [必] 复现 3：Refusal Direction（月 4-5）
- **源**: Arditi et al. 2024（arXiv:2406.11717，你 work4ai 讲透NLP/Ch09 §8.1 已经做过！）
- **做什么**: 在 7B 模型上找到 refusal direction，ablation 让模型回答 harmful
- **难度**: ⭐⭐⭐

### [必] 复现 4：Sparse Autoencoder on Pythia（月 5-6）
- **源**: Bricken et al. 2023 / Cunningham et al. 2023
- **做什么**: 在 Pythia-70M / 160M 上训 SAE，可视化 monosemantic features
- **难度**: ⭐⭐⭐⭐

### [重] 复现 5：Attribution Graphs（月 7+）
- **源**: Anthropic 2025 "Biology of a Large Language Model"
- **做什么**: 在 Gemma Scope 已有 SAE 上构建 attribution graph
- **难度**: ⭐⭐⭐⭐⭐

---

## 🚀 30 天入门清单（**今天开始**）

### Week 1：建直觉
- [ ] Day 1-2: 读 Jay Alammar "Illustrated Transformer"
- [ ] Day 3-5: 读 Anthropic "A Mathematical Framework for Transformer Circuits"（即使只懂 50%）
- [ ] Day 6-7: 装 TransformerLens v3，跑通 Main Demo

### Week 2：第一个实验
- [ ] Day 8-10: 读 "In-context Learning and Induction Heads"
- [ ] Day 11-14: 复现 induction head detection（在 GPT-2-small 上）

### Week 3：进阶
- [ ] Day 15-17: 读 Wang 2022 IOI
- [ ] Day 18-21: 复现 IOI circuit

### Week 4：产出 + 社群
- [ ] Day 22-25: 写第 1 篇 blog "My first 3 weeks in mech interp"
- [ ] Day 26-28: 在 EleutherAI Discord 分享你的 blog，求 feedback
- [ ] Day 29-30: 评估是否冲 MATS Neel Nanda stream（9/4 截止！）

---

## 🧑‍🔬 必 follow 的研究员

| Twitter | GitHub | 谁 |
|---|---|---|
| `@NeelNanda` | `neelnanda` | DeepMind / TransformerLens 作者 / MATS mentor |
| `@donnay_ftw` | `donnay-l` | interp |
| `@StephenCFry` | `stevenpq` | interp 工具 |
| `@callummcdougall` | `callummcdougall` | ARENA 作者 / SAE-Vis |
| `@JosephBloom` | `jbloomOSS` | SAELens |
| `@chrmanning` | | Stanford NLP |
| `@AnthropicAI` | `anthropics` | Interp 论文 |
| `@redwoodresearch` | | Interp / safety |
| `@EleutherAI` | `EleutherAI` | 开源 interp |
| `@donnay_ftw` | | interp |
| `@tomlcbrown` | | interp |
| `@olshansky` | | interp |

**Web 入口**:
- **`alignmentforum.org` tag "Interpretability"** — 长文
- **`lesswrong.com` tag "Interpretability"`**

---

## 📌 备选方向（如果你不想做 interp）

如果 interp 不合你心意，下面是 3 个替代方向：

### 替代 1：Scaling Laws 理论
- 适合：纯数学倾向
- 资源：Hoffmann et al. 2022 Chinchilla / Kaplan 2020 / Besiroglu 等
- 缺点：需要大算力

### 替代 2：Sample-efficient RL / RLVR 理论
- 适合：你 work4ai 已有「讲透RL/04-07」基础
- 资源：DeepSeek R1 / GRPO / DAPO 论文
- 缺点：算法迭代快，理论相对不成熟

### 替代 3：Diffusion 理论
- 适合：SDE / score matching 数学深
- 资源：Yang Song 系列论文 / Karras 2022 EDM
- 缺点：偏离 LLM 主流

---

## 📌 本月必做（按你接受 interp 方向）

1. [ ] 读完 Anthropic Circuits Thread 前 3 篇
2. [ ] 装 TransformerLens v3 + 跑通 Main Demo
3. [ ] 复现 induction heads（在 GPT-2-small 上）
4. [ ] 写 1 篇 blog "我为什么选 interp 方向"
5. [ ] **决定是否冲 MATS Neel Nanda stream（9/4 截止）**
