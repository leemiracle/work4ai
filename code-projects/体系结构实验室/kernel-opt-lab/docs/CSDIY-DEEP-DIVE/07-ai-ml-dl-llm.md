# AI / ML / DL / LLM 深度展开（25+ 门）

> **来源**：csdiy.wiki + librarian delegate（gentle-emerald-otter）实际 webfetch 验证
> **判定基准**：飞腾 D3000 NEON 算子优化 + Flash Attention + LLM 系统项目

---

## 一、机器学习系统（5 门）⭐ 项目核心分类

### 1. CMU 10-414/714: Deep Learning Systems ⭐⭐⭐
- **讲师**：Zico Kolter, **Tianqi Chen（陈天奇）**（TVM/MXNet/XGBoost 作者）
- **难度**：🌟🌟🌟 ｜ **学时**：100h
- **官网**：https://dlsyscourse.org
- **视频**：https://www.youtube.com/watch?v=qbJqOFMyIwg
- **GitHub**：[PKUFlyingPig/CMU10-714](https://github.com/PKUFlyingPig/CMU10-714)
- **作业（5 个 Assignment 从零实现 DL 库 Needle）**：
  - HW0：环境配置 + Python/NumPy 基础
  - **HW1**：实现自动微分（computational graph 前向/反向）
  - HW2：优化算法（SGD/Adam）+ 数据加载 + 损失函数 + 基础分类
  - **HW3**：**GPU CUDA backend** + CNN（卷积、池化）
  - **HW4**：RNN/LSTM/**Transformer** + 真实任务训练
- **核心价值**：理解 PyTorch `aten::mm` 内部实现 → 明白为什么要手写 NEON GEMM

### 2. ⭐⭐⭐ UCSD CSE234: Data Systems for ML（最高优先）
- **讲师**：Hao AI Lab（UCSD）
- **难度**：🌟🌟🌟 ｜ **学时**：120h
- **官网**：https://hao-ai-lab.github.io/cse234-w25/
- **教材**：https://hao-ai-lab.github.io/cse234-w25/resources/
- **语言**：Python + **Triton**
- **课程结构（3 Part）**：
  - **Part 1**：Modern DL / 计算图 / Autodiff / **Tensor format, MatMul 与硬件加速器**
  - **Part 2**：**GPUs & CUDA / GPU MatMul 与算子编译 / Triton 编程** / 图优化 / Memory / Quantization
  - **Part 3 LLM 系统**：并行策略 / LLM 基础（Transformer/Attention/MoE）/ **FlashAttention / Continuous Batching / PagedAttention** / Disaggregated Prefill/Decoding / Scaling Law
- **核心价值**：**csdiy 全站唯一明确讲授 FlashAttention + PagedAttention + continuous batching 的系统课**。Triton block-level 编程与 NEON tiling 同源。推荐配合 nanoGPT、nano-vllm 学习

### 3. MIT 6.5940: TinyML and Efficient DL Computing ⭐⭐⭐
- **讲师**：**Song Han（韩松）**（Deep Compression、Once-for-All 作者）
- **难度**：🌟🌟🌟🌟 ｜ **学时**：50h
- **官网**：[2024fall](https://hanlab.mit.edu/courses/2024-fall-65940)
- **视频**：[2024 YouTube](https://www.youtube.com/playlist?list=PL80kAHvQbh-qGtNc54A6KW4i4bkTPjiRF)
- **GitHub**：[PKUFlyingPig/MIT6.5940_TinyML](https://github.com/PKUFlyingPig/MIT6.5940_TinyML)
- **5 个 Lab**：①量化 ②剪枝 ③NAS ④LLM 压缩 ⑤LLM 部署
- **课程 3 部分**：
  - Part 1：剪枝/量化/蒸馏/NAS
  - Part 2：LLM 推理/长上下文/多模态/GAN/扩散
  - Part 3：分布式并行/梯度压缩/边缘训练
- **核心价值**：对应学术界 lens（17）P0 — 2:4 sparse / INT4 / FP8 / W4A16 全覆盖

### 4. Machine Learning Compilation (MLC) ⭐⭐⭐
- **讲师**：**Tianqi Chen（陈天奇）**（TVM 创始人之一）
- **难度**：🌟🌟🌟 ｜ **学时**：30h
- **官网**：https://mlc.ai/summer22-zh/
- **视频**：[Bilibili](https://www.bilibili.com/video/BV15v4y1g7EU)
- **笔记**：https://mlc.ai/zh/index.html
- **作业**：[GitHub notebooks](https://github.com/mlc-ai/notebooks/blob/main/assignment)
- **核心价值**：以 Apache TVM 为例，**TensorIR 的 loop tiling/vectorization/unrolling 就是手写 NEON GEMM 的自动化版本**。学习后可用 TVM `tensorize` 把 NEON 指令注入计算图

### 5. 智能计算系统 AICS（陈云霁）⭐⭐
- **讲师**：**陈云霁**（寒武纪创始人，中科院）
- **难度**：🌟🌟🌟 ｜ **学时**：100h+
- **官网**：https://novel.ict.ac.cn/aics/
- **视频**：[Bilibili](https://space.bilibili.com/494117284)
- **GitHub**：[Yuichi1001/2024-AICS-EXP](https://github.com/Yuichi1001/2024-AICS-EXP)
- **教材**：《智能计算系统》（陈云霁）
- **作业（旧版 6 个实验）**：编写卷积算子 → 为 TensorFlow 添加算子 → **BCL 语言编写算子**（类 CUDA）→ 硬件 MLU 设计。2024 新版全面 PyTorch + 大模型
- **核心价值**：国内唯一"从框架到硬件"全链路课程，BCL 算子编程与 NEON intrinsics 思路一致

---

## 二、深度学习（10 门）

### 6. Coursera Deep Learning（吴恩达）⭐⭐
- **难度**：🌟🌟🌟🌟 ｜ **学时**：80h
- **官网**：https://www.coursera.org/specializations/deep-learning
- 圣经级 DL 入门，从 NN 基础→CNN→RNN→Transformer

### 7. 国立台湾大学：李宏毅机器学习 ⭐⭐⭐
- **讲师**：李宏毅
- **难度**：🌟🌟🌟🌟 ｜ **学时**：80h
- **官网**：[2023](https://speech.ee.ntu.edu.tw/~hylee/ml/2023-spring.php) / [2025](https://speech.ee.ntu.edu.tw/~hylee/ml/2025-spring.php)
- **15 个 Lab**：Regression/Classification/CNN/Self-Attention/Transformer/GAN/BERT/Anomaly/Explainable/Attack/Adaptation/RL/Compression/LLL/Meta。2025 版侧重 RAG/Agent/LLM
- **价值**：覆盖 DL 几乎所有领域，风趣幽默，助教示例代码齐全

### 8. CMU 11-785: Introduction to Deep Learning ⭐⭐⭐⭐
- **难度**：🌟🌟🌟🌟🌟 ｜ **学时**：120h
- **官网**：https://deeplearning.cs.cmu.edu/S26/index.html
- "硬核" DL 核心，从 NN→CNN→RNN→Attention/Transformer→优化与泛化

### 9. MIT 6.7960: Deep Learning ⭐⭐⭐⭐
- **难度**：🌟🌟🌟🌟 ｜ MIT DL 教学团队

### 10. NYU DLSP21（Yann LeCun）⭐⭐
- **讲师**：**Yann LeCun**（深度学习三巨头之一）
- **难度**：🌟🌟🌟🌟
- **官网**：https://atcold.github.io/NYU-DLSP21/
- **视频**：[YouTube](https://www.youtube.com/playlist?list=PLLHTzKZzVU9e6xrdgUq8og5XjT8sSaeIw)

### 11. UMich EECS 498-007（Justin Johnson）⭐⭐⭐
- **讲师**：**Justin Johnson**（Stanford CS231n 主讲）
- **难度**：🌟🌟🌟🌟
- **官网**：https://web.eecs.umich.edu/~justincj/teaching/eecs498/FA2020/
- **视频**：[YouTube](https://www.youtube.com/playlist?list=PL5-TkQAfAZFbzxXZqoG4HxcttcVzw6VrP)
- **价值**：CV DL 顶级课程，覆盖 CNN/Transformer 最新架构

### 12. Stanford CS231n: CNN for Visual Recognition ⭐⭐⭐
- **讲师**：**Justin Johnson / Fei-Fei Li**
- **官网**：http://cs231n.stanford.edu/
- **视频**：[2017 Bilibili](https://www.bilibili.com/video/BV1nJ411z7fe)
- **价值**：**CNN 经典 → 卷积算子原理**（Winograd 算法背景）

### 13. Stanford CS224n: NLP ⭐⭐⭐
- **官网**：https://web.stanford.edu/class/cs224n/
- **价值**：**NLP/Transformer → Attention 算子背景**，与 FlashAttention 直接相关

### 14. Stanford CS224w: ML with Graphs ⭐
- **官网**：https://web.stanford.edu/class/cs224w/
- GNN，与算子优化关系较弱

### 15. UCB CS285: Deep RL ⭐
- **官网**：http://rail.eecs.berkeley.edu/deeprlcourse/
- 强化学习，与算子无关

---

## 三、深度生成模型（2 门 + 路线图）

### 16. 生成模型路线图
- **URL**：https://csdiy.wiki/深度生成模型/roadmap/
- 推荐学习顺序：MIT 6.S184 → MIT 6.S978（何恺明）→ UCB CS294-158 → CMU 10423
- **LLM 方向专项**：Stanford CS336 / **CMU 15-779**（ML Systems LLM Edition）/ CMU 11-868 / CMU 11-667 + 11-711

### 17. MIT 6.S184: GenAI with SDE ⭐⭐
- **讲师**：Peter Holderrieth & Ezra Erives
- **难度**：🌟🌟🌟🌟 ｜ **学时**：20h
- **官网**：https://diffusion.csail.mit.edu/
- **教材**：[Flow Matching and Diffusion Models (arXiv:2506.02070)](https://arxiv.org/abs/2506.02070)
- 从微分方程视角讲 Flow Matching 和 Diffusion Model

---

## 四、大语言模型（3 门 + 路线图隐藏 5 门）

### 18. ⭐⭐⭐ CMU 11-868: LLM Systems（核心）
- **难度**：🌟🌟🌟🌟 ｜ **学时**：120h
- **官网**：https://llmsystem.github.io/llmsystem2025spring/
- **作业平台**：https://llmsystem.github.io/llmsystem2025springhw/
- **教材**：精选论文 + 《Programming Massively Parallel Processors, 4th Ed》
- **5 个 Assignment + 期末项目**：
  - A1：自动微分框架 + **CUDA 手写算子** + 基础 NN
  - A2：GPT2 模型构建
  - A3：**手写 CUDA 的 Softmax 和 LayerNorm 算子优化**
  - A4：分布式模型训练
  - A5 + 期末项目
- **4 大核心内容**：①GPU 编程与自动微分 ②模型训练（ZeRO/FlashAttention/DDP/Megatron）③模型压缩（GPTQ/MoE/JAX/Triton/vLLM）④前沿（RAG/多模态/RLHF）
- **核心价值**：**直接对应项目算法 lens P0** — causal/KV-cache/GQA + 手写算子优化

### 19. CMU 11-667: LLM Methods and Applications ⭐⭐
- **难度**：🌟🌟🌟🌟 ｜ **官网**：https://cmu-llms.org/
- 偏 LLM 算法与应用（语言模型架构、对齐、跨模态、伦理）

### 20. CMU 11-711: Advanced NLP（Graham Neubig）⭐⭐
- **官网**：https://www.phontron.com/class/anlp-fall2024/
- NLP 方法论基础，含 Transformer/Attention

### 21-25. ⭐ 路线图隐藏课程（csdiy 详情页外，但路线图强烈推荐）

| 课程 | 讲师 | 核心价值 |
|---|---|---|
| **CMU 15-779 ML Systems LLM Edition** ⭐⭐⭐ | Zhihao Jia | **比 11-868 更核心**：FlashAttention IO-aware + Triton + PagedAttention + 推测解码 + Mirage + Alpa。[cs.cmu.edu/~zhihaoj2/15-779](https://www.cs.cmu.edu/~zhihaoj2/15-779/) |
| **Stanford CS336 LM from Scratch** ⭐⭐⭐ | Tatsu+Percy | 从零构建 LLM（Tokenizer/架构/**算子**/后训练）|
| MIT 6.S978 ⭐⭐ | 何恺明 | 深度生成模型全貌 |
| UCB CS294-158 ⭐ | Pieter Abbeel | 深度无监督学习 |
| CMU 10423 ⭐ | — | GenAI（偏 LLM）|

---

## 项目相关性总览

| 等级 | 课程 | 核心理由 |
|---|---|---|
| 🔴 **核心** | CSE234, CMU 11-868, CMU 15-779, CMU 10-414, MIT 6.5940, MLC | 直接覆盖 FlashAttention/CUDA 算子/Triton/量化/编译 |
| 🟡 **中等** | Karpathy NN:Z2H, CS231n, CS224n, 李宏毅, CMU 11-785, EECS 498 | DL 算法背景，理解算子优化的"为什么" |
| 🟢 **弱** | CS224w, CS285, NYU DLSP21, Coursera DL | 应用层，与算子优化无直接交集 |

**最高优先级**：若聚焦 NEON 算子 + FlashAttention + LLM 系统，**CSE234 + CMU 11-868 + CMU 15-779** 是必学三件套。
