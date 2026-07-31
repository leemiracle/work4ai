# 讲透 RAG (检索增强生成, 透) · 完整版

> 用「直觉 → 数学 → 代码跑通 → 不足 → 应用」讲透 RAG。从"为什么 LLM 需要 RAG"到"chunk/rerank/混合检索"再到"GraphRAG/Agentic RAG 高级架构"。姊妹项目：`../讲透激活函数/`、`../讲透基础模型/`、`../讲透微调/`。

**5 篇全部完成**（00 原理 + 01 数学 + 02 工程 + 03 高级 + 04 评估）。

---

## 阅读顺序

```
00-为什么需要RAG (LLM知识问题+三选一)
   │
01-检索数学 (相似度/embedding/ANN)
   │
02-工程组件 (chunk/混合检索/rerank)  ← 工业流水线核心
   │
   ├── 03-高级架构 (GraphRAG/Agentic/Self-RAG/CRAG)  ← 朴素RAG不够时
   └── 04-评估 (RAGAS/faithfulness/relevance)
```

## 全部章节

| # | 文件 | 核心 | 实验关键数字 |
|---|---|---|---|
| 00 | `00-为什么需要RAG.md` | LLM知识三问题；参数化vs非参数化；三选一 | TF-IDF检索3个query精准命中(0.40/0.33/0.22) |
| | `experiments/00_why_rag.py` ✅ | 最小RAG检索 | |
| 01 | `01-检索数学.md` | 余弦相似度；TF-IDF词面vs神经语义；ANN | 余弦v1-v2=1但欧氏最大；TF-IDF抓不到同义词 |
| | `experiments/01_retrieval_math.py` ✅ | 相似度+ANN对比 | |
| 02 | `02-工程组件.md` | chunk切分；混合检索(RRF)；rerank | 117字切7块带overlap；词面+语义融合 |
| | `experiments/02_engineering.py` ✅ | chunk+混合检索 | |
| 03 | `03-高级架构.md` | GraphRAG/Agentic/Self-RAG/CRAG | (概念为主) |
| 04 | `04-评估.md` | RAGAS四指标；检索vs生成分别评 | 字符近似局限(诚实) |
| | `experiments/04_evaluation.py` ✅ | faithfulness/relevance近似 | |

## 怎么跑

```bash
cd /data/usershare/ai/work4ai/讲透RAG
for f in experiments/0*.py; do echo "=== $f ==="; python3 -u "$f"; done
```
纯 CPU + sklearn/numpy 可跑（无 GPU/HF 依赖）。

## 五大核心洞见

1. **参数化 vs 非参数化知识**：LLM 知识固化在权重里（幻觉/过时/私有），RAG 给它接外部可更新知识库。
2. **余弦相似度看方向**：语义相似=向量方向相近，不受文本长度干扰——这是 RAG 用余弦的原因。
3. **神经 embedding 克服词面局限**：TF-IDF 只懂词面（汽车↔轿车匹配不到），神经 embedding 懂语义。
4. **工业流水线 = chunk + 混合检索 + rerank**：切分小块、词面+语义融合召回、cross-encoder 精排，三步把检索质量拉满。
5. **检索与生成分开评估**：检索差（召回率低）和生成差（忠实度低）让答案错，但优化方向完全不同——先定位瓶颈。

## 决策铁律（与微调/prompt 的边界）
- 改**行为/风格/格式** → 微调（LoRA）
- 注**知识/事实/最新** → **RAG**
- 临时**适应/可溯源** → Prompt
- 常组合：LoRA 调行为 + RAG 注知识

## 环境备忘
本机无 GPU/无 sentence-transformers/faiss/ollama。RAG 实验用 **TF-IDF + sklearn** 演示检索原理（已跑通）；真实 RAG 用神经 embedding(bge/m3e) + LLM 生成 + 向量库(Milvus)，原理与本系列一致，只是组件换成生产级实现。
