# CS329Z HW1 Part A: mini-Agent v0.1 — 从零实现 Agent

> **课程**: CS329Z Engineering AI Agents (Autumn 2025, Diyi Yang & John Yang)
> **作业**: HW1 Part A — 占总评 10%（其中 HW1 含 A/B 两部分）
> **对应模块**: W1 Foundations · W2 Building Blocks · W4 ReAct
> **代码位置**: `topic2-agents/cs329z-hw1a/`
> **完成度**: ★★★★★ (基础设施完整，mock 模式可完全跑通)
> **最后更新**: 2026-08-11

---

## 📚 作业定位

HW1 Part A 是 CS329Z 的**第一个动手作业**，要求学生**不依赖任何 Agent 框架**（不用 LangChain / DSPy / LlamaIndex），从零搭建一个能跑的 mini-Agent。

核心目标：理解 Compound AI System 的三大工程支柱——**RAG 检索、Tool use 工具调用、ReAct 推理-行动循环**。Part A 用手写 prompt 实现，Part B 再用 DSPy 重写（见 `HW1B.md`）。

**场景**：给一个论文仓库，做一个 agent 回答科学问题。

---

## 📅 核心模块

### 1. LLMClient — 统一 LLM 接口
- 基于 **litellm** 统一封装 OpenAI / Anthropic / Gemini / DeepSeek / Groq
- **Mock 兜底机制**：无 API key 时自动回退到基于规则的 mock 响应——保证代码始终能跑（教学场景关键设计）
- 支持成本统计与 verbose 调试输出
- **设计理由**：CS329Z W2 强调 model selection 与 cost/latency tradeoffs，litellm 让 tradeoff 可计算

### 2. SimpleRAG — 检索增强生成
- **Chunking**：固定 word count（chunk_size=30, overlap=10），简单稳定
- **Embedding**：教学用 hash embedding（无外部依赖）
- **Retrieval**：cosine similarity 向量检索
- 文档管理：`Document(id, content)` → 切分 → chunk 索引
- **反思**：固定长度会切断句子；生产系统应用 recursive chunking 或 semantic chunking

### 3. ToolRegistry — 工具注册与调用
内置 3 个工具：
| 工具 | 功能 | 选型理由 |
|------|------|---------|
| `calculator` | 数学计算 | Agent 必备的精确计算能力 |
| `search` | 信息检索 | 模拟网络搜索 |
| `read_file` | 本地知识读取 | 与 RAG 配合 |

### 4. ReActAgent — 推理-行动主循环
- **ReAct** (Yao et al. ICLR 2023)：交错 Thought / Action / Observation
- `max_iterations=3` 兜底防无限循环
- AgentTrace：记录完整执行轨迹（可观测性 + 调试）
- **终止条件**：LLM 输出 Final Answer 或达到最大步数

### 5. demo.py — 三类测试用例
1. **数学计算**（calculator 工具）
2. **知识检索**（RAG 向量召回）
3. **工具 + 检索混合**（多跳推理）

---

## 💻 项目代码

```
topic2-agents/cs329z-hw1a/
├── agent/
│   ├── llm.py            # LLMClient (litellm + Mock)
│   ├── rag.py            # SimpleRAG (chunking + embedding)
│   ├── tools.py          # ToolRegistry (calculator/search/read_file)
│   ├── react.py          # ReActAgent 主循环
│   └── hybrid_search.py  # BM25 + dense 混合检索（进阶）
├── demo.py               # 完整演示入口
├── tests/test_all.py     # smoke test
├── REFLECTION.md         # 设计决策反思文档
└── data/                 # 知识库文档
```

**运行**：
```bash
cd topic2-agents/cs329z-hw1a
python3 demo.py              # 跑通完整 mini-Agent
python3 -m pytest tests/ -v  # 跑测试
```

---

## 📊 关键论文

1. 🔴 **Yao et al. 2023** "ReAct: Synergizing Reasoning and Acting" ICLR — Agent 主循环的理论基础
2. 🔴 **Lewis et al. 2020** "RAG for Knowledge-Intensive NLP Tasks" NeurIPS — RAG 原始论文
3. 🟡 **Zaharia et al. 2024** "The Shift from Models to Compound AI Systems" BAIR — 思想锚点
4. 🟡 **Anthropic 2024** "Building Effective Agents" — workflow vs agent 的工程定义
5. 🟡 **Yang et al. 2024** "SWE-agent" — Agent-Computer Interface (ACI) 设计哲学

---

## 🎯 学习路径建议

1. **先跑 demo**：理解 RAG / Tool / ReAct 如何协同（无 API key 也能跑）
2. **读 REFLECTION.md**：模拟 CS329Z 口试的 10 个设计决策反思（为什么用 litellm？chunking 怎么选？ReAct 失败怎么办？）
3. **进阶升级**：配置真实 LLM API key → 添加 hybrid search → 扩展更多工具 → 接入 4-tuple Eval（见 `HW3.md`）

---

## 💡 设计决策反思（口试准备）

CS329Z 每次作业后有 **10 分钟 oral exam**。关键反思点：

- **litellm vs 原生 SDK**：统一 API、减少 vendor lock-in，代价是调试复杂度增加
- **hash embedding 的局限**：只捕获词频不懂语义，查 "GPU" 找不到 "graphics card"——教学可接受，生产必须用 sentence-transformers
- **ReAct vs CoT**：CoT 只在脑内推理，ReAct 把推理变行动（可查资料/算数/调 API）
- **多 agent vs 单 agent**：参考 Cemri 2025 批判——单 agent + 好工具往往够用

**完成度自评 ~40%**：基础功能齐全，但距离 A+ 还缺真实 LLM、hybrid search、自动评分、可观测性 trace JSON。
