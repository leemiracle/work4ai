# 02 · 交互与知识层 Topics：Prompt（L1）/ Context（L2）/ RAG（L5）

> 各 topic 含：**使用背景**（谁在打/何时检索）+ 实测规模 + 代表仓（star 为 2026-08-19 API 实测）+ 批判视角。姊妹篇：[`01-链路总纲与实测仲裁.md`](01-链路总纲与实测仲裁.md)。

---

## L1 Prompt 层——"人怎么说话给模型听"

### topic:prompt-engineering（16,098 仓）

- **使用背景**：应用开发者与 AI 产品团队给 prompt 模板库/指南/评测工具打的总标签。2023 年 ChatGPT 引爆后成为应用层第一 topic；检索它 = 找"提示词写法与管理的成熟方案"。**2025 后重心迁移**：从"怎么写 prompt"转向"怎么管理/版本化/评测 prompt"（prompt 从手艺变成工程资产——与本项目 prompt 工程手册的立场一致）。
- **代表仓**：dair-ai/Prompt-Engineering-Guide（77,566★，指南类事实标准）；f/awesome-chatgpt-prompts（量级 ~100k★，8-19 API 限速未实测，待核）；stanfordnlp/dspy（37,401★，**把 prompt 当可优化参数**自动搜索，"prompt 之后的范式"）。
- **批判**：16k 仓里大量是 2023-2024 的教程/合集（AI-slop 重灾区）；真正活跃的是工具链（dspy/promptfoo）。教程看指南一篇就够，重点看评测与编译型框架。

### topic:system-prompts（246）/ prompt-tuning（340）/ chain-of-thought（514）/ structured-output（660）

- **使用背景**：
  - `system-prompts`：**逆向工程社区**——泄露/收集各家产品的系统提示词（GPT/Claude/Gemini 的 system prompt 复盘），产品经理与 prompt 工程师用来学习大厂怎么写系统提示。小而精，信噪比高。
  - `prompt-tuning`：**学术界**——软提示（soft prompt）微调方向，与 PEFT 的 prefix-tuning 交界（见 04 篇）。注意与"prompt optimization"（dspy 方向）是两回事：前者改 embedding，后者改文本。
  - `chain-of-thought`：推理研究圈（CoT 论文复现/自洽性/CoT 安全），rasbt/reasoning-from-scratch（5,010★）是从零实现推理的经典教材仓。
  - `structured-output`：工程界——JSON schema 约束解码（vLLM xgrammar/guidance 生态的用户侧标签），与 L9 的 grammar-constrained-decoding 交界。
- **检索建议**：找系统提示词范例 → `system-prompts`；找 CoT 实现 → `chain-of-thought`；找结构化输出 → `structured-output` + `function-calling`。

## L2 Context 层——"一次对话内给模型看什么"

### topic:context-engineering（2,702 仓）

- **使用背景**：2025 年 Karpathy 定义"Context Engineering = 在正确的时间把正确的信息放进上下文窗口的艺术"后，从 prompt-engineering 分裂出的**新范式标签**。打这个标签的是 agent 框架/上下文压缩/记忆管理工具作者。检索它 = 找"上下文窗口工程化管理"（压缩、分层、持久化）的最新方案。对照：prompt-engineering 关注**单条指令质量**，context-engineering 关注**整个窗口的预算分配**——这是从"写作"到"内存管理"的范式升级。
- **代表仓**：infiniflow/ragflow（88,785★，RAG 引擎也抢这个标签——上下文工程与 RAG 融合的证据）；letta-ai/letta（24,298★，MemGPT 后身，把上下文当 OS 内存分页管理）。
- **批判**：2.7k 仓但概念定义仍松散，很多仓只是蹭新词；判断标准——真做 context 工程的仓必有"token 预算/分层加载/压缩比"这类量化指标。

### topic:long-context（361）/ memory-management（3,395）

- **使用背景**：`long-context` 是模型侧研究（长上下文注意力优化/评测基准，Kimi/Qwen-Long 适配），用户少但专业；`memory-management` 是双栖 topic——传统内存管理项目（历史存量）与 agent 记忆项目（新增长）并存，检索 agent 记忆时优先用 L4 的 `agent-memory`（2,849，纯度高）。
- **关联**：本项目 `../../Agent记忆系统案例/`（mem0 深读）是该层活案例。

## L5 RAG 层——"模型怎么查资料"（41,086 主 topic）

### topic:rag（41,086）/ retrieval-augmented-generation（6,722）

- **使用背景**：企业知识库/文档问答/客服系统的标配架构，2024-2026 应用落地第一大场景。`rag` 是通俗短名（41k），`retrieval-augmented-generation` 是论文名（6.7k）——**前者工程后者学术**，检索时按需选。打标签的是：RAG 框架（ragflow）、向量库外围工具、行业方案（法律/医疗知识库）。
- **代表仓**：infiniflow/ragflow（88,785★）；run-llama/llama_index（51,740★，数据框架双料）。
- **批判**：41k 仓是"万仓级噪声池"，大量 demo 级项目；找生产级方案看 `agentic-rag`（785）或框架仓的 production 标签。

### topic:embeddings（8,210）/ vector-database（7,273）/ reranking（646）/ agentic-rag（785）/ multimodal-rag（123）

- **使用背景**：
  - `embeddings`：向量模型与 embedding 工具（BGE/E5 生态外围）；`vector-database`：qdrant/chroma/weaviate 及其集成生态——两者是 RAG 的存储底座。
  - `reranking`：重排序器（cross-encoder），RAG 精度提升的关键配件，检索质量调优时用。
  - `agentic-rag`：**2025 起的增长明星**——把检索决策交给 agent（何时检索/检索什么/几轮）。785 仓但增速快，是 RAG 2.0 的标签。
  - `multimodal-rag`：图文混合检索（123 仓，概念热 topic 冷的典型）。
- **链路直觉**：embeddings(编码) → vector-database(存取) → reranking(精排) → rag(组装) → agentic-rag(自治)——五标签正好是 RAG 技术栈的五层，检索时按你要做的那一层选标签。

## 本层 5W2H 速览（详解见 06 篇）

- **Who**：应用开发者（L1/L5）、agent 框架作者（L2）、企业 IT（L5 RAG 落地）
- **Why 存在**：模型权重固定后，行为差异全靠"进窗口的东西"——L1/L2/L5 是不改权重改输入的三种粒度（指令/窗口管理/外部知识）
- **How much**：rag 41k > prompt-engineering 16k > context-engineering 2.7k——越新的概念 topic 越小，但增速越快

## refs
- GitHub Search API 实测 2026-08-19（/tmp/opencode/topics-audit/counts.json）
- 代表仓 star：repos API 2026-08-19（dair-ai 77,566 / ragflow 88,785 / llama_index 51,740 / letta 24,298 / dspy 37,401 / reasoning-from-scratch 5,010）；f/awesome-chatgpt-prompts 因 API 限速未实测（量级待核）
- Karpathy context engineering 论（2025，用户框架2 引）

*updated: 2026-08-19*
