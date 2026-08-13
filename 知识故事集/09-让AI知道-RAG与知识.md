# 09 · 让 AI 知道：RAG 与知识的故事（2020-2026）

> **时间**：2020-2026，6 年
> **核心冲突**：LLM 知识截止 2021。怎么让 AI 知道最新信息 + 不幻觉？
> **嵌入概念**：RAG、embedding、向量数据库、检索、幻觉

---

## 🎬 故事

### 2023 年 5 月 · 一个律师的灾难

Steven Schwartz，纽约律师。用 ChatGPT 查案例，准备官司。

ChatGPT 给了几个 citation：**Varghese v. China Southern Airlines**、**Shaboon v. United States** 等。

Schwartz 把这些写进法庭文件。

**问题**：这些案例**根本不存在**。ChatGPT 编造了名字 + 日期 + 内容。

2023 年 5 月，**法官 P. Kevin Castel 公开制裁 Schwartz**。全美头条。

**这是 LLM 幻觉（hallucination）问题的标志性事件**。

### LLM 为什么会幻觉？

LLM 训练目标 = **NTP**。它学到的是"互联网上接下来会出现的文字"。

如果你问"Gerald Ford 暗杀图谋"，LLM 知道 Gerald Ford 被暗杀过，**但具体几个图谋**？它不确定时，**会生成"看起来合理"的答案**。

LLM **没有"不知道"的概念**——它只会生成。

### 2020 · RAG 的诞生

**Patrick Lewis**（Facebook AI Research）2020 年发 **"Retrieval-Augmented Generation"**：

> "**Don't memorize. Retrieve.**"

**核心 idea**：
- 用户问问题
- 先**检索**相关文档（如 Wikipedia）
- 把检索到的文档 + 问题一起给 LLM
- LLM 基于文档生成答案

**关键**：知识不在模型权重里，**在外部文档库**。

### RAG 的工程实现

```
用户问题 "Gerald Ford 几次被暗杀？"
        ↓
[embedder] 把问题变成向量
        ↓
[向量数据库] 找最相似的文档（k-NN 检索）
        ↓
返回 Top-K 文档
        ↓
prompt = "基于以下文档回答：\n[文档]\n问题：Gerald Ford..."
        ↓
LLM 生成答案
```

### Embedding 是 RAG 的灵魂

**embedding** = 把文字变成向量（如 1536 维）。

语义相近的句子，向量也相近。

**例**：
- "猫坐在垫子上" → [0.3, -0.5, 1.2, ...]
- "猫咪躺在毯子上" → [0.31, -0.49, 1.18, ...]
- "汽车在公路上" → [-0.7, 0.4, -0.9, ...]

前两个向量相近，第三个远。

**embedding 模型**：
- OpenAI text-embedding-3-large
- BGE-M3（开源）
- Voyage AI
- Cohere Embed v3

### 向量数据库（Vector DB）

**用途**：存海量 embedding，快速 k-NN 检索。

**主流产品**：
- **Pinecone**（云服务）
- **Weaviate**（开源）
- **Milvus**（开源）
- **Chroma**（轻量）
- **Qdrant**（开源）
- **pgvector**（PostgreSQL 扩展）

**核心算法**：
- **HNSW**（Hierarchical Navigable Small World）：近似最近邻，O(log n)
- **IVF**（Inverted File）：聚类
- **PQ**（Product Quantization）：压缩

### 2023 · RAG 爆发

ChatGPT 发布后，所有公司想做"企业 AI 助手"——但要基于**企业内部文档**（不是互联网）。

**RAG 是唯一可行方案**。

2023 年起，RAG 成为 LLM 应用层最热方向。

### 高级 RAG（2024+）

简单 RAG 有问题：
1. **检索不准**——可能漏掉关键文档
2. **LLM 不看检索结果**——继续幻觉
3. **长上下文 token 成本**

**高级 RAG**：
- **HyDE**（Hypothetical Document Embedding）：先让 LLM 假设答案，用假设答案检索
- **RAG-Fusion**：多个 query 检索，融合结果
- **Self-RAG**：让 LLM 自己判断"是否需要检索"
- **GraphRAG**（Microsoft 2024）：用知识图谱 + 向量检索

### Long Context 是 RAG 的对手？

2024 后，**Gemini 1.5 / Claude 3.5** 支持 **100 万-200 万 token 上下文**。

**有人质疑**：把所有文档塞进 context 不就行？为什么还要 RAG？

**答案（2026 视角）**：
- **Long context + RAG 共存**
- Long context 适合**短期查询**（精度高，但贵）
- RAG 适合**大规模知识**（成本可控，但需要工程）

### RAG vs Fine-tuning

什么时候用 RAG，什么时候用 fine-tuning？

| 需求 | 选 |
|---|---|
| 让模型**知道新事实 / 最新信息** | **RAG**（微调学知识是反模式）|
| 让模型**固定格式 / 风格** | **Fine-tuning**（LoRA）|
| 临时适配 | Prompt |
| 复杂多步 | Agent |

---

## 🧠 核心概念

- **RAG**（Retrieval-Augmented Generation）：检索文档 + 生成答案。**外部知识库**。
- **Embedding**：把文字变向量。**语义相似度**。
- **向量数据库**：存海量 embedding，k-NN 检索。
- **HNSW**：近似最近邻算法。RAG 标配。
- **幻觉（Hallucination）**：LLM 编造看起来合理的内容。
- **HyDE / GraphRAG**：高级 RAG 技术。

## 🎨 类比

- **LLM 幻觉** = 一个健谈但分不清"知道"和"猜"的人：什么都能说，但编造内容
- **RAG** = 给这个人一本**百科全书** + **检索员**：每问问题先查百科，再答
- **Embedding** = 把每段文字放进一个**语义地图**：相近意思的位置相近
- **向量数据库** = 一个**会"按相似度找"的图书馆**：你说"找和这个意思相近的"，立刻返回
- **Long context** = 给这个人一本**百科全书 + 一个超强短期记忆**：能临时看完整本书，但贵
- **Fine-tuning** = 让这个人**学一门新专业**：贵，但学完后随时能用

## 💡 反直觉发现

1. **RAG 不是新概念**：2020 Lewis 论文就提出。**但 2023 ChatGPT 后才火**——LLM 普及 + 企业需求结合。

2. **检索精度比 LLM 还重要**：很多 RAG 系统效果差，**不是 LLM 差，是检索不到对的文档**。RAG 工程师 70% 时间花在检索优化。

3. **Embedding 模型不是 LLM**：很多人误以为 LLM 自带 embedding。实际**embedding 是独立训练的模型**（如 BGE / Voyage）。

4. **Long context 不会杀死 RAG**：100 万 token 看似够，但**成本高 + 检索精度问题**。RAG 仍是企业必需。

5. **微调不能学知识**：很多人想让模型"知道公司知识"，去 fine-tune。**这是反模式**——fine-tune 学风格，RAG 学知识。

6. **GraphRAG 是新方向**：2024 Microsoft 提出。**图 + 向量混合**，处理"实体关系"类问题比纯向量强。

## 🛠️ 我该深挖什么

### work4ai 系列
- [`../讲透RAG/`](../讲透RAG/)：检索数学 + 工程 + 高级架构 + 评估
- [`../讲透Prompt/`](../讲透Prompt/)：怎么 prompt RAG 模型

### 必读
- **Lewis et al. 2020 "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"**（RAG 起源）
- **Gao et al. 2024 "Retrieval-Augmented Generation for Large Language Models: A Survey"**（综述）

### 实验
```python
# 用 LangChain / LlamaIndex 搭一个最简 RAG：
# 1. 加载文档（如 PDF）
# 2. chunk 切片
# 3. embedding + 存 Chroma
# 4. 检索 + LLM 生成
# 5. 对比 RAG vs 不 RAG 的幻觉
```

---

## 🔗 下一篇

下一篇：[**10 · 让 AI 省钱：高效 AI 的故事**（2020-2026）](10-让AI省钱-高效AI.md)——KV Cache、量化、LoRA、vLLM。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**LLM 是健谈的健忘症患者。RAG 是给他一本百科全书 + 检索员。**
