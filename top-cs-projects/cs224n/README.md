# Stanford CS224N (Winter 2026) · NLP with Deep Learning

> 对应 https://web.stanford.edu/class/cs224n/ **最新 2026 版**（Instructor: Diyi Yang + Yejin Choi）。
> 把 4 个作业 + GPT-2 默认期末项目的核心，做成可跑的教学简化版。

---

## ⚠️ 2026 版的重大变化（和旧版对比）

抓取官方 schedule 后发现的更新（这就是"不凭记忆、查最新"的价值）：

| 维度 | 旧版（2024 及以前） | **2026 版** |
|---|---|---|
| 作业数 | 5 个 | **4 个** |
| A4 内容 | NMT 机器翻译（Seq2Seq+Attention）| **LLM 评测**（全新）|
| 默认期末项目 | BERT | **GPT-2** |
| 新增主题 | — | Reasoning / PEFT / Agents+RAG / Post-training(RLHF/DPO) |
| Instructor | Manning | **Diyi Yang + Yejin Choi** |

---

## 📦 模块内容

| 文件 | 对应作业/项目 | 核心实现 | 占分 |
|---|---|---|---|
| [`cs224n_assignments.py`](cs224n_assignments.py) | A1-A4 四个作业 | 见下表 | 48% |
| [`gpt2_project.py`](gpt2_project.py) | Default Final Project | mini-GPT-2 前向推理 | 49% |

### 四个作业详解

| 作业 | 标题 | 本文件实现的核心 | CS224N 原版用什么 |
|---|---|---|---|
| **A1** | 词向量入门 | 共现矩阵 + SVD 降维 + cosine 相似度 + 词类比 | NumPy（同）|
| **A2** | 神经网络+依存分析 | 手写反传 + **梯度检验**(4e-11✅) + transition-based parsing | NumPy（同）|
| **A3** | Transformer | 手写 self-attention + 因果掩码 + multi-head | NumPy（原版 PyTorch）|
| **A4** | LLM 评测（2026新）| benchmark 模拟 + 准确率 + 错误分析 + 污染陷阱 | 纯标准库（原版调 API）|

---

## 🧩 GPT-2 默认项目（mini 实现）

`gpt2_project.py` 实现了 GPT-2 的完整前向推理（纯 NumPy，不训练）：

```
token_ids → TokenEmb + PosEmb → [TransformerBlock × 2] → LN → LM Head → logits
                                    ↓
                        Pre-LN: x + Attn(LN(x)) + FFN(LN(x))
```

| 组件 | 本实现 | 真实 GPT-2 (124M) |
|---|---|---|
| vocab | 100 | 50,257 |
| d_model | 64 | 768 |
| heads | 4 | 12 |
| layers | 2 | 12 |
| 参数量 | ~0.1M | 124M |

CS224N 原版项目要求：实现组件 + **训练** + 做 3 个下游任务（情感分类 / NER / NLI）。

---

## 🔴 三个必懂的"反直觉"点

1. **梯度检验是反传的"测谎仪"** — A2 的灵魂：手写梯度和数值梯度对比，相对误差 < 1e-6 才算对。本实现实测 4.31e-11 ✅
2. **因果掩码 = 自回归的本质** — GPT-2 的 attention 是下三角：位置 i 只能看 ≤i。这是"不能偷看未来"的数学实现。
3. **benchmark 污染陷阱** — A4（2026 新）的核心教训：训练时见过测试题 → 分数虚高 → 需要动态/私有 benchmark。

---

## 🚀 快速开始

```bash
cd cs224n

# 4 个作业
python3 cs224n_assignments.py    # 需要 numpy

# GPT-2 项目
python3 gpt2_project.py          # 需要 numpy
```

---

## 🔗 与 work4ai「讲透」系列的互补关系

| CS224N 作业/项目 | work4ai 对应深度讲解 | 关系 |
|---|---|---|
| A1 词向量 | — | 基础，讲透系列已超越 |
| A2 反传 | [`讲透PyTorch/`](../../讲透PyTorch/)（Autograd 数学本质 VJP）| 作业练手感，讲透钻原理 |
| A3 Transformer | [`讲透Transformer/`](../../讲透Transformer/) | 作业手写 attention，讲透深挖 MoE/推理优化 |
| A4 LLM 评测 | [`讲透基础模型/`](../../讲透基础模型/) | 作业学评测方法，讲透学 scaling law |
| GPT-2 项目 | [`讲透基础模型/`](../../讲透基础模型/) + [`讲透微调/`](../../讲透微调/) | 项目实现架构，讲透讲预训练→对齐→部署 |

> **CS224N = 动手实现**（练编程）；**讲透系列 = 深度原理**（练理解）。两者互补。

---

## 📅 2026 完整 Schedule（10 周）

| 周 | 主题 | 对应作业 |
|---|---|---|
| 1 | NLP 历史 + Word Vectors | A1 out |
| 2 | 反传/神经网络 + RNN/LM | A2 out, A1 due |
| 3 | Transformers + 项目介绍 | A3 out, A2 due |
| 4 | Pretraining + Post-training(RLHF/DPO) | 项目提案 out |
| 5 | PEFT + Agents/RAG | A4 out, A3 due |
| 6 | 评测 + Reasoning 1 | 提案 due |
| 7 | Reasoning 2 + Tokenization | A4 due |
| 8 | 可解释性 + 社会影响 | 里程碑 due |
| 9 | 多模态 + LoRA(Schulman) | |
| 10 | 开放问题 + Poster | 项目 due |

---

## 📚 核心资料

| 资料 | 链接 |
|---|---|
| 课程主页 | https://web.stanford.edu/class/cs224n/ |
| 2024 公开课视频 | [YouTube playlist](https://www.youtube.com/playlist?list=PLoROMvodv4rOaMFbaqxPDoLWjDaRAdP9D) |
| 真实作业代码 | `assignments_w26/*.zip`（官网下载，需 PyTorch）|
| GPT-2 项目 handout | `project_w25/CS_224n__Default_Final_Project__Build_GPT_2.pdf` |
| Jurafsky & Martin SLP3 | https://web.stanford.edu/~jurafsky/slp3/ |
