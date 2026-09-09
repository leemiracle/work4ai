# AI应用开发实战指南

> 最后更新：2025-03 | 包含Prompt工程、RAG系统、模型部署、成本优化

---

## 📜 开发实战全景

```
AI应用开发流程
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 需求分析
   ↓
2. 模型选型
   ↓
3. Prompt工程 ← 持续优化
   ↓
4. 系统架构
   ├── RAG（检索增强）
   ├── Agent（工具调用）
   └── Fine-tuning（可选）
   ↓
5. 开发实现
   ↓
6. 测试评估
   ↓
7. 部署上线
   ↓
8. 监控优化
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 1. Prompt Engineering 高级技巧

### Prompt基础结构

**费曼解释**：Prompt = 指令 + 背景 + 示例 + 输入 + 约束

**模板**：
```
【角色】你是一个{角色描述}

【任务】{具体任务}

【背景】{上下文信息}

【示例】
输入: {示例输入}
输出: {示例输出}

【输入】
{实际输入}

【约束】
- {约束1}
- {约束2}

【输出格式】
{格式要求}
```

---

### 核心技巧

#### 1. 角色设定 (Role Prompting)

**费曼解释**：让AI扮演特定角色，激活相关知识。

**示例**：
```
❌ 差: 解释量子计算

✅ 好: 你是一位诺贝尔物理学奖得主，擅长用通俗易懂的比喻解释复杂概念。
请向一个高中生解释量子计算。
```

---

#### 2. Few-shot Learning

**费曼解释**：给几个示例，让模型"照猫画虎"。

**示例**：
```
提取产品名称和价格：

示例1:
输入: "我刚买了一台iPhone 15 Pro，花了999美元"
输出: {"product": "iPhone 15 Pro", "price": "$999"}

示例2:
输入: "这双Nike运动鞋只要120块"
输出: {"product": "Nike运动鞋", "price": "¥120"}

现在处理:
输入: "MacBook Pro M3售价1599美元"
输出:
```

**原则**：
- 2-5个示例最佳
- 示例要多样化
- 格式要一致

---

#### 3. Chain of Thought (CoT)

**费曼解释**：让模型"一步步思考"，展示推理过程。

**经典论文**：
- "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (Wei et al., 2022)

**零样本CoT**：
```
请一步步思考，然后回答：
{问题}
```

**Few-shot CoT**：
```
问题: 小明有5个苹果，给了小红2个，又买了3个，现在有几个？
思考: 
1. 开始有5个
2. 给了2个，剩下5-2=3个
3. 又买了3个，现在有3+3=6个
答案: 6个

问题: {新问题}
思考:
```

**效果**：
- 数学问题准确率提升40%+
- 复杂推理任务显著改善

---

#### 4. Self-Consistency

**费曼解释**：同一问题多次采样，选最一致的答案。

**论文**：
- "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (Wang et al., 2022)

**流程**：
```
1. 用温度>0生成N个答案（如5个）
2. 每个答案都有推理路径
3. 统计最频繁的答案
4. 作为最终结果
```

**适用**：
- 数学问题
- 逻辑推理
- 需要高准确率的场景

---

#### 5. Tree of Thoughts (ToT)

**费曼解释**：不只一条思路，探索多条可能的推理路径。

**论文**：
- "Tree of Thoughts: Deliberate Problem Solving with Large Language Models" (Yao et al., 2023)

**流程**：
```
        问题
       / | \
     思路1 思路2 思路3
      |    |    |
    评估  评估  评估
      |    |    |
    继续/放弃
      ↓
    最优路径
```

**适用**：
- 复杂决策
- 创意任务
- 需要探索的问题

---

#### 6. ReAct + CoT

**费曼解释**：结合推理和行动，边思考边使用工具。

**示例**：
```
问题: 马斯克现在的年龄是多少？

思考1: 我需要知道马斯克的出生日期
行动1: Search[Elon Musk birth date]
观察1: 1971年6月28日

思考2: 现在是2025年，计算年龄
行动2: Calculate[2025 - 1971]
观察2: 54

思考3: 我有足够信息回答
答案: 马斯克现在54岁
```

---

### Prompt优化技巧

#### 1. 明确性

```
❌ 模糊: 写一篇文章
✅ 明确: 写一篇800字的科普文章，主题是量子计算，目标读者是大学生，
       风格轻松幽默，包含至少3个比喻
```

---

#### 2. 分解复杂任务

```
❌ 一次性: 分析这份数据并生成报告

✅ 分步:
   步骤1: 先总结数据的主要特征
   步骤2: 识别异常值和趋势
   步骤3: 生成可视化建议
   步骤4: 撰写分析报告
```

---

#### 3. 输出格式控制

**JSON输出**：
```
请以JSON格式输出，schema如下：
{
  "name": "string",
  "age": "number",
  "skills": ["string"]
}

不要输出其他内容，只输出JSON。
```

**Markdown表格**：
```
请以Markdown表格格式输出，包含以下列：
| 产品名 | 价格 | 评分 |
```

---

#### 4. 负面约束

```
在回答时：
- 不要使用专业术语，除非必须
- 不要给出不确定的信息
- 不要超过100字
```

---

### Prompt模板库

#### 代码生成
```
【任务】根据需求生成{语言}代码

【需求】
{需求描述}

【要求】
- 代码清晰、有注释
- 遵循{语言}最佳实践
- 包含错误处理

【示例】（可选）
{示例代码}
```

---

#### 文本总结
```
【任务】总结以下文本

【文本】
{长文本}

【要求】
- 保留关键信息
- 字数控制在{N}字以内
- 使用要点形式

【输出格式】
## 核心观点
- 观点1
- 观点2

## 详细总结
{总结内容}
```

---

#### 信息提取
```
【任务】从文本中提取{信息类型}

【文本】
{文本}

【输出格式】（JSON）
{schema}

【注意】
- 如果信息不存在，填null
- 日期统一格式：YYYY-MM-DD
- 金额统一格式：数字+货币符号
```

---

### Prompt调试技巧

#### 1. A/B测试

```
版本A: "请解释{概念}"
版本B: "像给5岁孩子讲故事一样解释{概念}"

对比：
- 准确率
- 可读性
- 用户满意度
```

---

#### 2. 渐进式优化

```
1. 先用最简单的prompt
2. 测试失败案例
3. 针对性改进
4. 重复步骤2-3
```

---

#### 3. 错误分析

```
收集失败案例 → 分析原因 → 优化prompt

常见问题：
- 指令不够明确
- 示例不够
- 输出格式不匹配
- 缺少边界约束
```

---

## 2. RAG系统构建

### 什么是RAG？

**费曼解释**：RAG = Retrieval-Augmented Generation（检索增强生成）。让LLM先"查资料"再回答，而不是靠记忆。

**类比**：
- 纯LLM：闭卷考试，只能凭记忆
- RAG：开卷考试，可以查资料

---

### RAG架构

```
┌──────────────────────────────────────────┐
│                RAG 系统                   │
├──────────────────────────────────────────┤
│                                          │
│  查询流程:                                │
│  用户问题                                 │
│     ↓                                    │
│  Query处理 (改写、扩展)                   │
│     ↓                                    │
│  向量化 (Embedding)                       │
│     ↓                                    │
│  检索 (Vector Search)                     │
│     ↓                                    │
│  重排序 (Reranking) [可选]                │
│     ↓                                    │
│  上下文组装                               │
│     ↓                                    │
│  LLM生成答案                              │
│                                          │
│  索引流程:                                │
│  文档                                     │
│     ↓                                    │
│  切分 (Chunking)                          │
│     ↓                                    │
│  向量化 (Embedding)                       │
│     ↓                                    │
│  存储到向量数据库                          │
│                                          │
└──────────────────────────────────────────┘
```

---

### 核心组件

#### 1. 文档处理

**切分策略 (Chunking)**

**费曼解释**：把长文档切成小块，便于检索。

**切分方法**：

| 方法 | 描述 | 适用场景 |
|------|------|----------|
| **固定长度** | 按字符/token数切分 | 简单场景 |
| **句子切分** | 按句子边界切分 | 短文档 |
| **段落切分** | 按段落切分 | 文章、报告 |
| **语义切分** | 根据语义相似度切分 | 专业文档 |
| **递归切分** | 递归按不同粒度切分 | 通用场景 |

**推荐参数**：
- Chunk size: 500-1000 tokens
- Overlap: 50-100 tokens

**代码示例**（LangChain）：
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
)

chunks = text_splitter.split_text(document)
```

---

#### 2. Embedding模型

**费曼解释**：把文字变成向量，相似的内容在向量空间里距离近。

**主流模型**：

| 模型 | 维度 | 特点 | 价格 |
|------|------|------|------|
| **OpenAI text-embedding-3-small** | 1536 | 性价比高 | $0.02/1M tokens |
| **OpenAI text-embedding-3-large** | 3072 | 效果最好 | $0.13/1M tokens |
| **Cohere embed-v3** | 1024 | 多语言好 | $0.10/1M tokens |
| **BGE-large-zh** | 1024 | 中文开源 | 免费 |
| **E5-large-v2** | 1024 | 英文开源 | 免费 |

**选型建议**：
- 英文为主：OpenAI text-embedding-3-large
- 中文为主：BGE-large-zh 或 text-embedding-3-small
- 成本敏感：开源模型（BGE, E5）

---

#### 3. 向量数据库

**费曼解释**：专门存储和检索向量的数据库，能快速找到最相似的向量。

**主流选择**：

| 数据库 | 特点 | 适用场景 |
|--------|------|----------|
| **Pinecone** | 全托管，易用 | 生产环境 |
| **Weaviate** | 开源，功能全 | 自部署 |
| **Chroma** | 轻量，Python原生 | 开发测试 |
| **FAISS** | Facebook开源，高性能 | 大规模 |
| **Milvus** | 开源，可扩展 | 企业级 |
| **Qdrant** | Rust实现，高性能 | 高并发 |
| **pgvector** | PostgreSQL扩展 | 已有PG |

**代码示例**（Chroma）：
```python
import chromadb
from chromadb.utils import embedding_functions

# 初始化
client = chromadb.Client()
embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-api-key",
    model_name="text-embedding-3-small"
)

# 创建集合
collection = client.create_collection(
    name="documents",
    embedding_function=embedding_function
)

# 添加文档
collection.add(
    documents=["文档1内容", "文档2内容"],
    metadatas=[{"source": "file1.pdf"}, {"source": "file2.pdf"}],
    ids=["doc1", "doc2"]
)

# 查询
results = collection.query(
    query_texts=["查询文本"],
    n_results=5
)
```

---

#### 4. 检索策略

**a. 简单向量检索**

**费曼解释**：直接用问题检索最相似的文档。

```python
results = vector_store.similarity_search(query, k=5)
```

---

**b. 混合检索 (Hybrid Search)**

**费曼解释**：结合向量检索（语义）+ 关键词检索（精确）。

**论文**：
- "Dense Passage Retrieval" (Karpukhin et al., 2020)

```python
# 向量检索
vector_results = vector_store.similarity_search(query, k=10)

# 关键词检索（BM25）
keyword_results = bm25_search(query, k=10)

# 融合（RRF）
final_results = reciprocal_rank_fusion(
    vector_results, 
    keyword_results
)
```

**效果**：通常比单一检索好10-20%

---

**c. 重排序 (Reranking)**

**费曼解释**：检索出一批候选，用更强的模型重新排序。

**流程**：
```
1. 向量检索 → 返回Top 50
2. Reranker模型重排 → 返回Top 5
```

**Reranker模型**：
- Cohere Rerank
- BGE-reranker
- MonoT5

**代码示例**（Cohere）：
```python
import cohere

co = cohere.Client("api-key")

results = co.rerank(
    query=query,
    documents=documents,
    top_n=5,
    model="rerank-english-v2.0"
)
```

---

**d. 多查询 (Multi-Query)**

**费曼解释**：把一个问题拆成多个相关查询，分别检索，合并结果。

```python
# 原始问题
query = "如何提高机器学习模型的准确率"

# 生成多个相关查询
queries = [
    "提高机器学习模型准确率的方法",
    "机器学习模型优化技巧",
    "提升ML模型性能的策略"
]

# 分别检索
all_results = []
for q in queries:
    results = vector_store.search(q, k=5)
    all_results.extend(results)

# 去重、排序
final_results = deduplicate_and_rank(all_results)
```

---

#### 5. 上下文组装

**费曼解释**：把检索到的文档组织好，喂给LLM。

**Prompt模板**：
```
基于以下参考资料回答问题。如果参考资料中没有相关信息，
请说"根据提供的资料，我无法回答这个问题"。

参考资料：
{context}

问题：{query}

回答：
```

**技巧**：
- 按相关度排序
- 限制总token数
- 标注来源（可追溯）

---

### RAG优化技巧

#### 1. 查询改写

```python
# 原始查询可能表述不清
original = "怎么用那个东西"

# 改写为更清晰的查询
rewritten = "如何使用{产品名}的{功能}"
```

---

#### 2. 假设性文档 (HyDE)

**费曼解释**：先让LLM生成"假设的答案"，用假设答案去检索。

**论文**：
- "Precise Zero-Shot Dense Retrieval without Relevance Labels" (Gao et al., 2022)

**流程**：
```
1. 问题 → LLM生成假设答案
2. 假设答案 → Embedding
3. 用假设答案的embedding检索
```

---

#### 3. 父文档检索 (Parent Document Retriever)

**费曼解释**：检索小块文档，但返回大块上下文。

```python
# 索引时：切分成小块
# 检索时：返回小块所属的大块

chunks = split_small(documents)  # 200 tokens
parent_chunks = split_large(documents)  # 1000 tokens

# 检索小块
small_results = search(query)

# 返回对应的父文档
parent_results = get_parent(small_results)
```

---

### RAG评估指标

| 指标 | 描述 | 方法 |
|------|------|------|
| **Context Precision** | 检索内容的相关性 | 人工/LLM评估 |
| **Context Recall** | 需要的信息是否都检索到 | 对比ground truth |
| **Faithfulness** | 答案是否基于检索内容 | LLM评估 |
| **Answer Relevance** | 答案是否回答了问题 | LLM评估 |

**工具**：
- Ragas (开源评估框架)
- TruLens
- DeepEval

---

## 3. 模型部署

### 部署方式选择

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **API调用** | 简单、无需维护 | 成本高、数据外传 | 快速原型 |
| **云托管** | 可控、可扩展 | 需要配置 | 中小规模 |
| **自部署** | 完全控制、隐私 | 成本高、需运维 | 企业级 |

---

### API集成

**OpenAI API**：
```python
from openai import OpenAI

client = OpenAI(api_key="your-key")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

**Anthropic API**：
```python
from anthropic import Anthropic

client = Anthropic(api_key="your-key")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "你好"}
    ]
)

print(message.content[0].text)
```

---

### 本地部署

#### vLLM

**费曼解释**：高性能推理引擎，PagedAttention技术，吞吐量极高。

**安装**：
```bash
pip install vllm
```

**启动服务**：
```bash
vllm serve meta-llama/Llama-3.1-8B \
  --port 8000 \
  --dtype auto \
  --api-key token-abc123
```

**调用**：
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-abc123"
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B",
    messages=[{"role": "user", "content": "你好"}]
)
```

---

#### Ollama

**费曼解释**：最简单的本地运行方案，一行命令启动。

**安装**：
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh
```

**运行**：
```bash
# 下载并运行模型
ollama run llama3.1

# 或者作为服务
ollama serve
```

**API调用**：
```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.1",
        "prompt": "你好"
    }
)
```

---

#### llama.cpp

**费曼解释**：纯C++实现，支持CPU推理，资源消耗低。

**特点**：
- 可在CPU上运行
- 支持量化（GGUF格式）
- 内存占用低

**使用**：
```bash
# 下载模型
wget https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf

# 运行
./main -m llama-2-7b.Q4_K_M.gguf -p "你好"
```

---

### 云托管

#### Hugging Face Inference Endpoints

```python
# 创建endpoint后
from huggingface_hub import InferenceClient

client = InferenceClient(
    "your-endpoint-url",
    token="your-token"
)

response = client.text_generation("你好")
```

---

#### AWS Bedrock

```python
import boto3

client = boto3.client('bedrock-runtime')

response = client.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    body=json.dumps({
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 1000
    })
)
```

---

## 4. 成本优化

### 1. 模型选择

**分层策略**：
```
简单任务 → GPT-4o mini / Claude 3.5 Haiku
中等任务 → Claude 3.5 Sonnet / GPT-4o
复杂任务 → GPT-4 / Claude 3 Opus
```

**成本对比**（2024价格）：

| 模型 | Input ($/1M) | Output ($/1M) | 适用 |
|------|--------------|---------------|------|
| GPT-4o mini | 0.15 | 0.60 | 简单任务 |
| GPT-4o | 2.50 | 10.00 | 平衡 |
| GPT-4 Turbo | 10.00 | 30.00 | 复杂 |
| Claude 3.5 Haiku | 0.25 | 1.25 | 简单 |
| Claude 3.5 Sonnet | 3.00 | 15.00 | 平衡 |
| Claude 3 Opus | 15.00 | 75.00 | 最强 |

---

### 2. 缓存策略

**a. 语义缓存**

**费曼解释**：相似的问题返回缓存的答案，不用重新调用LLM。

```python
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())

# 相同或相似的问题会命中缓存
```

---

**b. 提示缓存（Prompt Caching）**

**费曼解释**：Claude和OpenAI支持缓存长system prompt，不重复计费。

**Claude示例**：
```python
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=[
        {
            "type": "text",
            "text": "很长的system prompt...",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": "问题"}]
)
```

**效果**：长prompt可节省90%的input成本

---

### 3. Token优化

**a. 压缩prompt**
```
❌ 冗长: "请你帮我分析一下这个数据，然后告诉我你的看法和建议"
✅ 精简: "分析数据，给出建议"
```

**b. 截断上下文**
- 限制历史对话长度
- 只保留相关内容

**c. 使用更短的输出**
```python
max_tokens=100  # 不需要长回答时限制
```

---

### 4. 批处理

**费曼解释**：一次处理多个请求，而不是逐个处理。

```python
# 批量embedding
texts = ["文本1", "文本2", "文本3", ...]
embeddings = openai.embeddings.create(
    input=texts,  # 一次传入多个
    model="text-embedding-3-small"
)
```

---

## 5. 监控与调试

### 监控指标

| 指标 | 描述 | 警戒值 |
|------|------|--------|
| **Latency** | 响应时间 | >5s |
| **Token Usage** | Token消耗 | 异常增长 |
| **Cost** | 成本 | 超预算 |
| **Error Rate** | 错误率 | >1% |
| **Quality** | 回答质量 | 用户反馈差 |

---

### 工具

**LangSmith**：
- LangChain官方监控
- 追踪每步执行
- 成本分析

**Weights & Biases**：
- 实验追踪
- Prompt版本管理

**Helicone**：
- OpenAI API监控
- 成本分析
- 缓存支持

---

### 调试技巧

#### 1. 日志记录

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Prompt: {prompt}")
logger.info(f"Response: {response}")
logger.info(f"Tokens: {response.usage}")
```

---

#### 2. 中间结果检查

```python
# RAG系统
retrieved_docs = retriever.get_relevant_documents(query)
print(f"检索到的文档: {retrieved_docs}")

context = format_docs(retrieved_docs)
print(f"组装的上下文: {context}")

response = llm.invoke(prompt)
print(f"LLM响应: {response}")
```

---

#### 3. A/B测试

```python
# 随机分配用户到不同版本
import random

version = random.choice(["A", "B"])

if version == "A":
    prompt = prompt_v1
else:
    prompt = prompt_v2

# 记录结果
log_experiment(version, prompt, response, user_feedback)
```

---

## 6. 安全与合规

### 1. 输入过滤

```python
def sanitize_input(user_input):
    # 移除潜在危险内容
    # 检测注入攻击
    # 限制长度
    return sanitized_input
```

---

### 2. 输出过滤

```python
def sanitize_output(llm_output):
    # 移除敏感信息
    # 检测有害内容
    # 格式化输出
    return sanitized_output
```

---

### 3. 访问控制

```python
# API密钥管理
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# 用户认证
def check_permission(user, action):
    if not user.can(action):
        raise PermissionError()
```

---

### 4. 数据隐私

- 敏感数据不发送到云端
- 本地处理或私有部署
- 数据脱敏
- 日志匿名化

---

## 7. 实战案例

### 案例1: 文档问答系统

**需求**: 构建企业内部文档问答系统

**架构**:
```
1. 文档上传 → 切分 → Embedding → 存入向量DB
2. 用户提问 → Embedding → 检索 → 组装Prompt → LLM回答
3. 返回答案 + 来源
```

**技术栈**:
- Embedding: OpenAI text-embedding-3-small
- Vector DB: Pinecone
- LLM: GPT-4o
- Framework: LangChain

**代码骨架**:
```python
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# 初始化
embeddings = OpenAIEmbeddings()
vectorstore = Pinecone.from_existing_index("index-name", embeddings)
llm = ChatOpenAI(model="gpt-4o")

# 构建问答链
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
)

# 查询
answer = qa.run("公司的休假政策是什么？")
```

---

### 案例2: 客服机器人

**需求**: 自动回复常见客服问题

**架构**:
```
1. 意图识别（分类）
2. 根据意图检索FAQ
3. LLM生成个性化回复
4. 人工接管复杂问题
```

**关键点**:
- FAQ库维护
- 多轮对话管理
- 情绪识别
- 无缝转人工

---

### 案例3: 代码助手

**需求**: 帮助开发者写代码、解释代码、debug

**架构**:
```
1. 代码理解 → 分析代码结构
2. 上下文检索 → 找相关代码
3. 代码生成 → LLM生成
4. 代码执行 → 验证（沙箱）
```

**关键点**:
- 代码解析
- AST分析
- 测试用例生成
- 安全执行

---

## 📚 推荐资源

### 框架文档
- LangChain: https://python.langchain.com
- LlamaIndex: https://docs.llamaindex.ai
- Haystack: https://docs.haystack.deepset.ai

### 教程
- DeepLearning.AI courses
- LangChain tutorials
- Hugging Face course

### 社区
- LangChain Discord
- r/LangChain
- AI Twitter/X

---

## 🔗 下一步

- [Lean4+AI专项](./LEAN4_AI_DICTIONARY.md) - 形式化证明与AI结合

---

*指南持续更新 | 最后更新：2025-03*
