# 工程化手册库 · 总入口

> **建立**：2026-08-13
> **参照**：prompt 工程手册（11 文件）+ skills 工程手册（6 文件）的方法论
> **本文是什么**：7 份新手册的总索引，每份精简为 3 合 1 文件（解析+评价+实战）

---

## 📚 7 份手册

| # | 手册 | 目录 | 用途 |
|---|---|---|---|
| 1 | **RAG** | [`RAG工程手册/`](RAG工程手册/) | 检索增强生成：chunk / 向量库 / 检索质量 |
| 2 | **MCP** | [`MCP工程手册/`](MCP工程手册/) | Model Context Protocol：给 LLM 写工具 |
| 3 | **Agents** | [`Agents工程手册/`](Agents工程手册/) | 智能体：工具调用 / 规划 / 记忆 |
| 4 | **Inference** | [`Inference工程手册/`](Inference工程手册/) | 推理服务：vLLM / SGLang / 部署 |
| 5 | **Context Engineering** | [`ContextEngineering手册/`](ContextEngineering手册/) | 上下文工程：长 context / KV cache |
| 6 | **Quantization** | [`Quantization工程手册/`](Quantization工程手册/) | 量化：int8 / int4 / NVFP4 |
| 7 | **知识图谱** | [`知识图谱工程手册/`](知识图谱工程手册/) | Knowledge Graph：Obsidian / Zettelkasten |
| 8 | **Embedding** | [`Embedding工程手册/`](Embedding工程手册/) | 嵌入：编码器选型 / 微调 / 评测 |
| 9 | **FineTuning** | [`FineTuning工程手册/`](FineTuning工程手册/) | 微调：SFT / 全参 vs PEFT / 数据配比 |
| 10 | **LoRA** | [`LoRA工程手册/`](LoRA工程手册/) | LoRA：秩选择 / 目标模块 / [多视角深层分析](LoRA工程手册/02-多视角深层分析.md) |
| 11 | **SafetyAlignment** | [`SafetyAlignment手册/`](SafetyAlignment手册/) | 安全对齐：红队 / 护栏 / 拒答策略 |
| 12 | **Tokenization** | [`Tokenization工程手册/`](Tokenization工程手册/) | 分词：BPE / 词表设计 / 多语言 |
| 13 | **VectorDB** | [`VectorDB工程手册/`](VectorDB工程手册/) | 向量库：索引（HNSW/IVF）/ 混合检索 / 选型 |

---

## 📐 每份手册的统一结构（3 合 1）

参照 prompt/skills 的方法论，每份手册 1 个文件，含：

```
1. 是什么 + 为什么
2. 听说读写（4 能力）
3. N 要素解析框架（类似 ROIF-CSE）
4. 6 维度评价
5. 工具栈（2026-08 核实）
6. 跨平台/跨场景差异
7. 实战案例
8. 反模式 10 条
9. 下一步
```

---

## 🎯 与已有手册的关系

```
已有（完整版 11+6 文件）：
├── prompt工程手册/
└── skills工程手册/

新建（精简版 1 文件/份）：
└── 工程化手册库/
    ├── RAG工程手册/
    ├── MCP工程手册/
    ├── Agents工程手册/
    ├── Inference工程手册/
    ├── ContextEngineering手册/
    ├── Quantization工程手册/
    └── 知识图谱工程手册/
```

---

## 📌 使用建议

- **需要时查**：遇到具体问题查对应手册
- **不求全读**：7 份 × 300 行 = 2100 行，按需读
- **迭代改进**：用过 1 次后，把实战经验补进去

---

**版本**：v1.0（2026-08-13）
