# 学习路线图 · 从零到 AI 前沿研究员

> 为「应用数学研究型工程师」量身定制。
> 起点：Python 工程级 + 数学零基础 + ML/AI 零经验
> 终点：能在三大领域之一做出原创贡献
> 预算：每周 10-20 小时，3-5 年

---

## 0. 诊断：你的真实起点

**优势**：
- Python 工程级（能写类、测试、包管理）
- 逻辑思维强（工程实践锻炼）
- Git / 命令行 / Linux 日常

**短板**：
- 线代 / 概率统计 / 微积分 / 最优化 全部 0
- 没有任何 ML 项目 / 手写 / 论文经验
- 没有独立训过模型

**目标**：应用数学研究型工程师（研究 + 工程双栖）

---

## 1. 三阶段路线图（总览）

```
阶段 1（0-12 个月）：基础筑基
  ├─ Python ML 工具链熟练
  ├─ 数学补完（线代/概率/微积分/优化）
  └─ 经典 ML + 深度学习跑通

阶段 2（12-24 个月）：子领域深耕
  ├─ 选定一个子领域（建议从 AI4Math 或 AI4Science）
  ├─ 复现 3-5 篇 SOTA 论文
  └─ 写出第一个可发表的工作（小论文 / blog）

阶段 3（24-60 个月）：研究产出
  ├─ 在选定领域持续输出
  ├─ 寻找工业 / 学术合作
  └─ 形成个人研究主线
```

---

## 2. 阶段 1 详细（前 12 个月）

### 月 1-3：数学补完（残酷优先级）

**只补这三样，其他先放：**

1. **线性代数**（4 周）
   - 矩阵 / 向量 / 线性映射
   - 特征值 / SVD（最重要的分解）
   - 推荐：3Blue1Brown《线性代数的本质》+ Strang《Linear Algebra》前 8 章
   - **不做练习题不写代码就是浪费时间**

2. **概率统计**（4 周）
   - 概率分布 / 期望 / 方差
   - 贝叶斯 / 最大似然
   - 推荐：Ross《概率论基础》+ PyMC tutorial

3. **微积分 + 优化**（4 周）
   - 导数 / 偏导 / 梯度 / 链式法则（**反向传播的基础**）
   - 梯度下降 / 牛顿法 / 拉格朗日乘子
   - 推荐：Boyd《Convex Optimization》前 5 章

**不要补**：实分析、抽象代数、拓扑、测度论——这些等到阶段 3 真用得上时再补。

### 月 4-6：经典 ML + PyTorch

**目标**：能独立跑通 5 个经典 ML 项目。

1. **课程**：
   - 吴恩达《Machine Learning Specialization》（Coursera）
   - 李宏毅《机器学习》（YouTube 中文）

2. **手写**（每周一个）：
   - 线性回归 / 逻辑回归（NumPy 裸实现）
   - MLP（NumPy 反向传播）
   - 简单 CNN（PyTorch）
   - 简单 RNN / LSTM（PyTorch）
   - Transformer 单层实现（参考 Karpathy nanoGPT）

3. **资源**：
   - Karpathy [github.com/karpathy/nanoGPT](https://github.com/karpathy/nanoGPT) —— 最简洁的 GPT 实现
   - d2l.ai（《动手学深度学习》李沐）

### 月 7-9：现代深度学习

**目标**：理解 Transformer / Diffusion / GNN 三大架构。

1. **Transformer**（4 周）
   - 读「Attention Is All You Need」原论文（arXiv 1706.03762）
   - 跑 nanoGPT 训一个字符级 LM
   - 读 HuggingFace Transformers 源码（部分模块）

2. **Diffusion**（3 周）
   - 读 DDPM（arXiv 2006.11239）+ DDIM（arXiv 2010.02502）
   - 用 PyTorch 跑通 CIFAR-10 diffusion
   - 理解 Latent Diffusion（arXiv 2112.10752）

3. **GNN**（1 周，因为你可能不做材料）
   - PyG (PyTorch Geometric) 跑通 GCN / GAT
   - 理解 message passing

### 月 10-12：选定子领域 + 第一个项目

**这是最关键的决策点**。基于兴趣 + 前景，三选一：

#### 选项 A：AI4Math（推荐你优先考虑，与「数学专家」目标最契合）

- 学 Lean 4（[leanprover.github.io](https://leanprover.github.io)）
- 玩 The Natural Number Game
- 跑 DeepSeek-Prover V2 7B 在 miniF2F
- 读 AlphaProof / LeanDojo 论文
- **第一个项目**：用 Lean 形式化你熟悉的某个数学定理（如线性代数中的秩-零度定理）

#### 选项 B：AI4Science（最具工业落地前景）

- 跑 ColabFold 预测任意蛋白
- 跑 ESM-2 在 AFDB 上推理
- 学 RDKit（化学信息学）
- **第一个项目**：在 Kaggle 上跑一个分子性质预测比赛（如 Open Problems in Single-Cell Perturbation）

#### 选项 C：世界大模型（最热门、最卷）

- 跑 Open-Sora 1.2 或 Wan 2.1（家庭机器跑不了，找 Colab）
- 跑 LeRobot Diffusion Policy
- 读 Sora / Cosmos 论文
- **第一个项目**：复现 Dreamer v3 在 Atari（你的硬件能跑）

---

## 3. 阶段 2 详细（12-24 个月）

### 季度 5-6：深度复现

- 选 3-5 篇 SOTA 论文（参考本卷每章末尾的「📌 进一步阅读」）
- 不只是跑通——要理解每一处设计选择
- 写 blog 记录复现过程（中英文）

### 季度 7-8：找到研究问题

- 重读本卷 `04-synthesis/02-evaluation-open-problems.md`
- 选 1-2 个你感兴趣且可操作的问题
- 找导师 / 工业合作者（在你跑过 demo 后就有底气）

### 季度 9-10：第一个原创工作

- 不要追求"大"——一个清晰的 incremental 工作就够了
- 投 workshop / conference（如 NeurIPS Workshop、ICLR Workshop）
- 或者写成 arXiv preprint

### 季度 11-12：建立声誉

- 持续输出 blog / GitHub 项目
- 在 X / Twitter 上跟进领域动态
- 参加 1-2 次学术会议（即使线上）

---

## 4. 阶段 3 详细（24-60 个月）

这是最难规划的阶段，因为你已经从「学习者」变成「研究者」。原则：

1. **专注**：选一个细分方向深耕（如「Lean 自动定理证明的 premise selection」），不要东张西望
2. **合作**：找 2-3 个稳定合作者，每月产出
3. **风险**：敢于做 6 个月不出结果的高风险课题
4. **写作**：每 3 个月写一篇 blog，每年至少 1 篇 paper

---

## 5. 时间预算（每周 15 小时典型分配）

| 阶段 | 阅读论文 | 写代码 | 数学 | 写作输出 |
|---|---|---|---|---|
| 阶段 1（1-12 月） | 2h | 6h | 5h | 2h |
| 阶段 2（13-24 月） | 5h | 7h | 1h | 2h |
| 阶段 3（25+ 月） | 5h | 5h | 2h | 3h |

---

## 6. 资源大全

### 6.1 数学补完（免费）

- 3Blue1Brown [youtube.com/@3blue1brown](https://youtube.com/@3blue1brown)
- 李宏毅《机器学习》[youtube.com/@HungyiLeeNTU](https://youtube.com/@HungyiLeeNTU)
- 李沐《论文精读》[space.bilibili.com/21272036](https://space.bilibili.com/21272036)
- d2l.ai 中文版

### 6.2 工具链

- HuggingFace Transformers / Diffusers / Accelerate
- PyTorch Lightning
- Weights & Biases（实验追踪）
- uv / poetry（包管理）

### 6.3 论文跟踪

- [AK on X](https://x.com/_akhaliq)（每日 AI 论文）
- HuggingFace Daily Papers [huggingface.co/papers](https://huggingface.co/papers)
- arXiv sanitizer（订阅 cs.LG / cs.CL / stat.ML）
- 机器之心 / 量子位（中文媒体）

### 6.4 社区

- EleutherAI Discord（开源 AI 研究）
- LessWrong / Alignment Forum（理论深度）
- Lean Community [leanprover-community.github.io](https://leanprover-community.github.io)
- X / Twitter（最高信号密度）

---

## 7. 反模式（千万别做）

1. **「先把数学全补完再开始」**——错。永远补不完。学到 60% 就动手。
2. **「跟着吴恩达课一节不落」**——错。挑你需要的，剩下的用到时再补。
3. **「追求 PyTorch 源码」**——错。API 用熟即可，源码留到阶段 3。
4. **「同时学 3 个子领域」**——错。深度优先，一个突破点足够。
5. **「不写 blog」**——错。输出倒逼输入，没 blog 等于没学。
6. **「跳过复现直接做研究」**——错。没复现过的工作不算你懂。

---

## 8. 自检清单（每季度一次）

打勾越多，进度越好：

- [ ] 过去 3 个月读了 ≥ 5 篇本领域 SOTA 论文
- [ ] 过去 3 个月写了 ≥ 1 篇 blog 或 GitHub 项目
- [ ] 能用 30 秒向朋友解释我「最近在做什么」
- [ ] 能用 5 分钟向同行讲清我的子领域全貌
- [ ] 至少有 1 个「我自己想出来的」问题
- [ ] 至少有 1 个跑通的开源 demo
- [ ] 数学短板列表在缩短
- [ ] 有 1-2 个稳定的同行 / 合作者

---

## 📌 立即行动建议

如果你是 **0-3 个月新手**：本周做这件事——
1. 装 PyTorch + HuggingFace
2. 跑通 nanoGPT（Karpathy 的 200 行 GPT）
3. 写 1 篇 blog 记录踩坑

如果你是 **3-12 个月进阶**：本周做这件事——
1. 选定本卷三个领域之一（建议 AI4Math，跟你目标最契合）
2. 跑通对应章节的「复现指引」第一条
3. 写 1 篇 blog 总结你的复现

如果你是 **12 个月+**：本周做这件事——
1. 列出 3 个你认为本领域值得做的研究问题
2. 找一个导师 / 资深同行聊 30 分钟
3. 选 1 个问题开始 4 周冲刺

---

<!-- docs/roadmap.md, 2026-07-20 -->
