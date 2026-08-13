# Embedding 工程手册

> **是什么**：把文字/图片/音频变成向量——让机器"理解"语义。
> **为什么重要**：Embedding 是 RAG / 搜索 / 推荐 / 聚类的基础。**没有好的 embedding = 没有 RAG**。

---

## 1. 是什么

**Embedding** = 把离散数据（文字）映射到连续向量空间。

```
"猫坐在垫子上" → [0.23, -0.45, 0.89, ..., 0.12]  （768-3072 维）
```

**核心假设**：**语义相近 → 向量相近**（cosine similarity 高）。

## 2. 模型选型（2026-08）

### 商业
| 模型 | 维度 | 特点 | 价格 |
|------|------|------|------|
| **OpenAI text-embedding-3-large** | 3072 | 英文最强 | $0.13/1M |
| **Voyage AI voyage-3** | 1024 | SOTA 质量 | 商业 |
| **Cohere Embed v3** | 1024 | 多语言 | 商业 |

### 开源
| 模型 | 维度 | 特点 |
|------|------|------|
| **BGE-M3**（智源）| 1024 | 多语言 + 开源最强 |
| **BGE-Large** | 1024 | 英文 |
| **E5-Mistral** | 4096 | 大模型当 embedder |
| **GTE-Large**（阿里）| 1024 | 中英 |
| **Nomic-Embed** | 768 | 可视化 |

### 中文
- **BGE-M3** / **GTE** / **M3E**（中文专门）

## 3. 评测

### Benchmark
| Benchmark | 测什么 |
|-----------|--------|
| **MTEB**（Massive Text Embedding Benchmark）| 58 任务综合 |
| **C-MTEB** | 中文版 |
| **BEIR** | 检索 |
| **LongEmbed** | 长文本 |

### 自己评测
```python
# 简单：找正例 + 负例
queries = ["how to cook pasta", "pasta recipe"]
positives = ["boil water, add pasta, cook 10 min"]
negatives = ["how to fix a car"]

# 好的 embedding: query-positive > query-negative
```

## 4. 多视角深层

### 📐 数学
- Embedding = 学习一个映射 f: text → R^d
- 训练目标：contrastive loss（正例拉近，负例推远）
- **关键**：对比学习（SimCSE / E5 / BGE 都用）

### 🧠 认知科学
- Embedding ≈ 人的**语义网络**（ Collins & Quillian）
- 人脑：概念按语义关系组织（猫 → 动物 → 生物）
- Embedding：概念按向量距离组织

### 💾 信息论
- Embedding = **有损压缩**（文字 → 固定维度向量）
- 好的 embedding 保留**语义信息**，丢弃**表面信息**
- 信息瓶颈理论

### 🌐 语言学
- **分布式假说**（Harris 1954）：一个词的意义由它的上下文决定
- Embedding 把这个假说**数学化**
- Word2Vec 是最早的实现

## 5. 微调 Embedding

```python
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader

model = SentenceTransformer('BAAI/bge-marge-en')

# 对比学习数据
train_examples = [
    InputExample(texts=['query', 'positive_doc'], label=1.0),
    InputExample(texts=['query', 'negative_doc'], label=0.0),
]

train_dataloader = DataLoader(train_examples, batch_size=16)
train_loss = losses.ContrastiveLoss(model)

model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=3)
```

## 6. 反模式 10 条

1. **用 GPT 当 embedder**（LLM 不是 embedding 模型）
2. **英文模型做中文**（跨语言性能差）
3. **不评就上线**（MTEB 分低的模型误事）
4. **维度太高**（3072 维存不起）→ 用 truncation
5. **不更新版本**（embedding 模型迭代快）
6. **混用不同模型**（向量空间不兼容）
7. **不分 batch**（大数据集 OOM）
8. **不 normalize**（cosine 需要归一化）
9. **忽略 max_seq_length**（长文本被截断）
10. **向量库 + embedding 不匹配**（维度不对）

---

**核心理念**：**Embedding 是 AI 理解世界的"坐标系"。好的 embedding = 好的 RAG/搜索/推荐。**
