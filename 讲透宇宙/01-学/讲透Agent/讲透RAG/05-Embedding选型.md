# 05 — Embedding 模型选型与评测

> 「讲透 RAG」第六篇。01 讲了检索数学（向量相似度）。本篇讲**选什么 embedding 模型**——这是 RAG 效果的第一决定因素。选错了，后面 chunk/rerank 再怎么调都白搭。

---

## 1. 灵魂：Embedding = 文本的"指纹"

$$
\boxed{\text{Embedding 模型} : \text{文本} \to \text{向量} \quad \text{选型决定 RAG 上限}}
$$

---

## 2. 主流模型对比（2026）

| 模型 | 维度 | 语言 | 许可 | MTEB 均分 | 特点 |
|---|:---:|---|---|:---:|---|
| **OpenAI text-embedding-3-large** | 3072 | 多语言 | 闭源 API | ~75 | 强但贵、不可私有部署 |
| **BGE-large-zh-v1.5**（智源）| 1024 | 中文强 | MIT | ~72 | ★ 中文开源首选 |
| **E5-mistral-7b** | 4096 | 多语言 | MIT | ~76 | 开源 SOTA 但重（7B）|
| **Cohere embed-v3** | 1024 | 多语言 | 商业 | ~74 | 商用稳定 |
| **GTE-large**（阿里）| 1024 | 中英 | Apache | ~73 | 性价比 |

### 选型维度

1. **语言**：中文为主 → BGE/GTE；英文 → E5/OpenAI
2. **部署**：要私有 → 开源（BGE/E5）；可接受 API → OpenAI/Cohere
3. **成本**：7B 模型效果好但推理慢；小模型（300M）够用就别上大的
4. **维度**：高维存储贵但表达强；可用 Matryoshka 降维

---

## 3. MTEB 评测（怎么判断好坏）

MTEB（Massive Text Embedding Benchmark）是 embedding 的"GLUE"：
- 8 类任务（分类/聚类/检索/STS/重排/...）
- 覆盖 100+ 语言

**但 MTEB ≠ 你的业务**。要建**自己的评测集**：
1. 收集 100 个真实 query
2. 人工标注相关文档
3. 算 Recall@k（前 k 个检索结果里有没有正确答案）

---

## 4. 实操建议

### 4.1 起步
- 中文：先用 **BGE-large-zh**（免费 + 强）
- 英文：先用 **OpenAI 3-small**（便宜 + 够用）

### 4.2 进阶
- 微调 embedding（用对比学习 + 你的领域数据）
- 但**先试通用模型**——很多场景够用，不必微调

### 4.3 陷阱
- **维度太高 → 向量库贵 + 慢**：1024 够用就别上 3072
- **模型升级要重算所有向量**：embedding 换了，整个索引作废
- **指令式 embedding**（如 Instructor）：不同任务加不同前缀，效果好但易用错

---

## 📌 下一步

[06-Chunking 与混合检索](06-Chunking与混合检索.md)——embedding 选好后，怎么切块、怎么混合 BM25 + 向量。

## ✍️ 练习

1. 用 BGE 和 OpenAI 分别 embedding 10 条中文 query，算它们余弦相似度的相关性。差异大吗？
2. 为什么 embedding 模型升级后必须重算所有向量？（提示：向量空间不同构。）
