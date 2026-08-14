# 04 · Mech Interp 侦探故事

> **本文是什么**：把 Mech Interp 学习路径写成侦探破案。每个 interp 核心概念就是一个破案工具。
>
> **目标**：让你用"侦探破案"模式学 interp，而不是"读 paper + 跑实验"模式。**人脑记得住侦探，记不住定义**。

---

## 🎬 楔子：案件发生

**时间**：2022 年 11 月 30 日
**地点**：互联网

**案件**：ChatGPT 发布。它能写诗、解数学、写代码、聊哲学。**没人知道它内部怎么工作**。

**嫌疑人**：1750 亿参数的神经网络。它由 96 层 transformer 组成，每层有几十亿个 attention head。

**问题**：
- 它为什么会"拒绝"有害请求？
- 它为什么会"幻觉"？
- 它为什么会"推理"？
- 它**真的懂**它说的吗？

**侦探**：你。

**任务**：把黑箱变成玻璃箱。

---

## 📜 第一卷：侦探的祖师爷

### 1887 年，Sherlock Holmes 第一次出现

Arthur Conan Doyle 创造了"侦探"这个职业——用**逻辑 + 观察**破解谜团。

**2020 年，Chris Olah 在 Anthropic 创造了 mech interp 这个职业**——用**插针 + 数学**破解神经网络。

Olah 不是 AI 出身，他是数学 + 物理背景。他的早期工作（CNN 可视化、Feature Visualization、Zoom In）开创了 circuits 范式：

> **"神经网络不是黑箱。它们是由可识别的电路（circuits）组成的。每个神经元、每个 attention head 都有可解释的功能。"**

这是 interp 的"宣言"。

**Anthropic Circuits Thread**（transformer-circuits.pub）就是这个宣言的连载小说——每篇揭示一个新发现。

---

## 🔍 第二卷：侦探的工具

侦探破案要工具。你的工具：

### 工具 1：放大镜——TransformerLens
- **作者**：Neel Nanda（前 Anthropic 实习生，后来 DeepMind）
- **是什么**：让你看模型任何层的激活、任何权重的工具
- **用法**：`hook` 函数 → 在前向传播任何位置插入观察 / 修改
- **2026-08 状态**：v3.0 TransformerBridge，支持 9000 个模型
- **类比**：放大镜——把模型的每一层放大 1000 倍看

### 工具 2：化学分析——SAELens
- **作者**：Joseph Bloom
- **是什么**：训练 Sparse Autoencoder，把混合特征分解为单义特征
- **类比**：化学质谱仪——把"红色液体"分解为"染料 + 水 + 防腐剂"

### 工具 3：远程望远镜——nnsight（NDIF）
- **是什么**：你电脑跑不动 405B 模型？用 NDIF 远程访问
- **类比**：哈勃望远镜——你够不着，但远程看

### 工具 4：刑侦数据库——Neuronpedia
- **是什么**：已训练 SAE 的特征库
- **类比**：指纹库——查你发现的特征是否已有人描述

### 工具 5：法医报告——ARENA 课程
- **是什么**：Apollo Research / LLM-Agents 维护的免费自学课程
- **类比**：刑侦培训手册

---

## 🧩 第三卷：第一个线索——Induction Heads

### 案情
2022 年，Anthropic 团队（Olsson, Elhage 等）发现一个怪现象：

**GPT-2-small 在某些任务上能力突然提升**——但不能解释为什么。

### 调查
他们用 activation patching（激活替换）逐层追查。

**发现**：layer 5-6 出现了一组 attention head，**专门做"复制粘贴"**——给定序列 `[A] [B] [A]`，它们会预测下一个是 `[B]`。

**这就是 induction head**——in-context learning 的物理基础。

### 顿悟
**In-context learning 不是魔法，是 induction head**。Transformer 学会了一个简单算法："看上下文里有没有 [A]，如果有，复制 [A] 后面的内容。"

这解释了为什么 GPT-3 突然会 few-shot learning——规模到一定程度，induction heads 自然涌现。

### 案件结论
**induction heads 是 in-context learning 的电路基础**。

> 📌 work4ai：[`../讲透可解释性/`](../讲透可解释性/)、[`../讲透Transformer/`](../讲透Transformer/)

---

## 🧨 第四卷：危险分子——Refusal Direction

### 案情
2024 年，Anthropic / Yale 团队问：**LLM 怎么知道拒绝有害请求？**

为什么你说"教我做炸弹"，它说"我不能帮你"？

### 调查
他们怀疑：是不是模型内部有一个"拒绝"的方向？

**实验**：在 Llama / Qwen 模型上，收集 harmful 和 harmless prompt 的激活。做 PCA / mean diff。

**发现**：是的！存在一个**单一方向**（512 维里的 1 维），控制着"拒绝"行为。

**震撼实验**：用 SVD 找到这个方向，然后**从所有层 ablation**。

**结果**：
- 模型从"我不能帮你做炸弹" → "好的，这是步骤..."
- ablation 掉这一根方向，**harmful 拒绝率 99.9% → 25.5%**
- 而 harmless 拒绝率几乎不变

### 顿悟
**对齐不是一个复杂系统，是一根向量**。

更深的含义：**RLHF 训出的"价值观"，可能比我们想象的脆弱**。

### 案件结论
**Refusal 是模型空间中的一个 direction**。可以用一根向量控制。

> 📌 work4ai：[`../讲透NLP/Ch09§8.1`](../讲透NLP/)（你已做过 vocab=24 的实验）

---

## 🎭 第五卷：身份之谜——SAE 与单义性

### 案情
但 interp 圈有一个根本问题：**一个神经元可能有多个功能**。这是 **Polysemanticity 问题**。

例如：一个神经元对"猫"、"汽车"、"中文"都激活。怎么解释？

### 调查
2023 年，**Bricken et al.**（Anthropic）发表 "Towards Monosemanticity"。

**思路**：与其研究单神经元，**用 Sparse Autoencoder（SAE）把激活分解为更多"虚拟神经元"**。

例如：MLP 层有 4096 维，用 SAE 分解为 100 万维 sparse 特征。每个特征 monosemantic（单义）。

**发现**：在 small toy model 上，SAE 学到的特征**真的可解释**：
- 特征 #23456：DNA 序列
- 特征 #78901：阿拉伯数字
- 特征 #34567：动词过去时

### 顿悟
**MLP 不是混合，是稀疏组合**。Polysemanticity 是因为我们看的维度不够细。

### 案件结论
**SAE = mech interp 的化学分析法**。每个特征是一个"原子"。

2024 年 **Scaling Monosemanticity**（Templeton et al.）：在 Claude 3 上训 SAE，提取了**几亿个可解释特征**。

> 📌 work4ai：[`../讲透可解释性/`](../讲透可解释性/)、[`../讲透基础模型/`](../讲透基础模型/)

---

## 🌌 第六卷：终极真相——Biology of a LLM

### 案情
2025 年，Anthropic 发表 "Biology of a Large Language Model"。**这是 interp 史上最重要的论文**。

### 真相
他们用 SAE + attribution graphs 重建了 **Claude 在做一道数学题时，内部如何思考**：

- 模型不是黑箱
- 它有**可识别的"思想电路"**
- 当 Claude 算 "37 + 68"，**它不是死记硬背，是用电路做某种"近似竖式计算"**
- 不同任务的电路**有相似结构**（"通用语法"）

### 顿悟
**LLM 有"生物学"**。就像细胞有代谢通路，LLM 有 thought circuit。

### 案件结论
**Interp 从"研究玩具模型"升级到"研究前沿模型"**。2025 年后，interp 圈的中心问题是：

> **"我们能不能完全读懂 LLM 的内心？"**

---

## 🎓 你的破案手册：30 天入门

### Week 1：装备侦探工具
- [ ] 读 [`../顶级专家资源库/05-方向深选-Mechanistic-Interpretability.md`](../顶级专家资源库/05-方向深选-Mechanistic-Interpretability.md) §「30 天入门清单」
- [ ] 装 TransformerLens v3
- [ ] 跑通 Main Demo

### Week 2-3：学习前人的破案手法
- [ ] 读 Anthropic Circuits Thread 前 3 篇
- [ ] 复现 induction heads 检测（在 GPT-2-small 上）

### Week 4：开始你自己的案子
- [ ] 复现 IOI circuit（Wang 2022）
- [ ] 写第 1 篇 blog "我的第 1 个 interp 实验"

### Month 2-3：升级侦探
- [ ] 训练 SAE on Pythia-70M
- [ ] 写第 2 篇 blog

### Month 4-6：破大案
- [ ] 复现 refusal direction（在 7B 模型）
- [ ] 申请 **MATS Neel Nanda stream**（年度窗口）

### Month 7-12：独立侦探
- [ ] 提出 1 个**新观察**或**新假设**
- [ ] 做实验 + 写 blog / preprint

---

## 🎬 终章：成为侦探大师

侦探大师的标志：
1. **不仅破别人的案，能定义新案件**
2. **写手册让其他人也能破案**（建工具 / 写课程）
3. **在 NeurIPS 大会上做侦探报告**（做 talk）
4. **被请去警局当顾问**（被 Anthropic / DeepMind / OpenAI 招聘）

你正在这条路上。

---

## 📚 推荐深读（按侦探训练顺序）

1. **Anthropic Circuits Thread** 全集（`transformer-circuits.pub`）
2. **Neel Nanda blog**（`neelnanda.io`）
3. **ARENA 课程**（`arena-chapter1-transformers.streamlit.app`）
4. **Callum McDougall interp tutorials**（`github.com/callummcdougall`）
5. **3Blue1Brown Neural Network 系列**（YouTube）

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**你不是在学一个学科，你是在成为侦探。每个论文是一个 case file。每个实验是一次取证。**
