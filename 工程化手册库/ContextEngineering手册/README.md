# Context Engineering 工程手册

> **建立**：2026-08-13
> **是什么**：管理 LLM 的上下文窗口（context window）——决定给模型看什么、看多少、怎么排。
> **为什么重要**：100K-2M token 时代，"塞满 context"≠好效果。**怎么选、怎么压缩、怎么缓存**是工程核心。

---

## 1. 是什么 + 为什么

Context Engineering = **决定 LLM 在每次推理时看到什么内容**的工程。

2024+ 所有前沿模型都支持 100K-2M token（Claude / Gemini / GPT-4o）。但**长 context 不是免费**：
- **成本**：100K token 输入 ≈ $0.15-1.50（按模型）
- **延迟**：prefill 100K token 需要 1-10 秒
- **lost in the middle**：中段注意力衰减
- **精度下降**：超长 context 时指令遵循率降低

**核心问题**：不是"塞多少"，是"**选什么 + 怎么排 + 怎么压缩**"。

---

## 2. 听说读写 4 能力

| 能力 | 含义 |
|------|------|
| **听** | 解析一个 prompt 的 context 结构（系统/历史/检索/任务）|
| **说** | 用 context 圈的行话（token budget / prefix caching / lost-in-middle）|
| **读** | 读长 context 论文（LongBench / RULER / NIAH）|
| **写** | 设计 context 管理方案（RAG / 压缩 / 选择 / 缓存）|

---

## 3. SPACC 解析框架

任何 context 管理方案可拆为 5 要素：

```
S - Selection（选择）：从海量内容选哪些进 context
P - Arrangement（排列）：选出的内容怎么排序（前/中/后）
A - Compression（压缩）：怎么压缩冗余（摘要/去重/量化）
C - Caching（缓存）：怎么复用已计算（prefix caching / KV cache）
C - Cost control（成本控制）：token 预算 + 延迟优化
```

### 各要素详解

#### S · Selection（选择）
| 策略 | 何时用 |
|------|--------|
| 全塞（full context）| < 32K token，简单任务 |
| RAG 检索 top-K | 知识库场景 |
| 滑动窗口 | 对话历史 |
| 摘要 + 详情 | 长文档 |
| LLM 选择（"select relevant"）| 复杂决策 |

#### P · Arrangement（排列）
- **Anthropic 建议**：长数据在前 + 指令在后（改进 30%）
- **重要内容放前/后**（避免 lost-in-middle）
- **结构化标记**（XML tag / Markdown header）

#### A · Compression（压缩）
- **摘要**：用小模型先摘要
- **去重**：cosine similarity 过滤
- **截断**：按 token 预算硬切
- **量化**：数值精度降低（极端）

#### C · Caching
- **Prefix caching**：固定前缀（系统 prompt）缓存
- **KV cache reuse**：重复前缀复用 KV
- **Prompt caching API**：Anthropic / OpenAI 都支持

#### C · Cost
- 输入 token 价格 vs 输出 token 价格
- 延迟：prefill 比 decode 慢
- p50 vs p99 延迟

---

## 4. 6 维度评价

| 维度 | 指标 |
|------|------|
| **1. 准确性** | Needle-in-Haystack (NIAH) 准确率 |
| **2. 稳健性** | 同样内容不同位置，结果一致吗 |
| **3. 可迁移性** | 跨模型（Claude 200K vs Gemini 2M）|
| **4. 效率** | token 消耗 + 延迟 + 成本 |
| **5. 可控性** | 改 context 结构，结果可预测 |
| **6. 安全性** | 信息泄漏 / prompt injection via context |

---

## 5. 工具栈（2026-08）

| 工具 | 用途 |
|------|------|
| **Anthropic Prompt Caching** | Claude 前缀缓存，省钱 90% |
| **OpenAI Prompt Caching** | GPT 自动缓存（128 token+）|
| **LLMLingua** | Microsoft 压缩 prompt（5-10x）|
| **RAGAS** | RAG context 质量评估 |
| **LongBench** | 长 context benchmark |
| **NIAH (Needle in Haystack)** | 检索精度测试 |
| **LangChain StuffDocumentChain** | 文档管理 |

---

## 6. 跨平台差异

| 模型 | Context 长度 | 特点 |
|------|-------------|------|
| **Claude Opus 4 / Sonnet 4** | 200K-1M | XML 结构 + 数据在前 |
| **GPT-4o / GPT-5** | 128K-256K | Bookend（指令前+后）|
| **Gemini 2.5 Pro** | 2M | 多模态长 context |
| **Llama 3.3 / Qwen 2.5** | 128K | 开源，需自部署 |

---

## 7. 实战案例：搭一个 100K context 的代码分析系统

```python
# 目标：分析一个 100K 行的代码库
# 不能直接塞（200K token 不够 + lost in middle）

# Step 1: Selection（用 RAG 选相关文件）
relevant_files = rag_search("authentication bug", top_k=20)

# Step 2: Compression（每个文件只取关键函数）
compressed = [extract_functions(f) for f in relevant_files]

# Step 3: Arrangement（XML 结构 + 数据在前）
prompt = f"""
<codebase>
{format_as_xml(compressed)}
</codebase>

<task>
Find the authentication bug in the code above.
</task>
"""

# Step 4: Caching（固定系统 prompt 缓存）
# Anthropic API 自动缓存系统 prompt 前缀

# Step 5: Cost control（限制总 token < 100K）
total_tokens = count_tokens(prompt)
assert total_tokens < 100_000
```

---

## 8. 反模式 10 条

1. **全塞**：把所有内容塞进 context（成本爆炸 + lost in middle）
2. **指令在前**：长数据场景应数据在前
3. **无结构**：纯文本拼接（模型分不清段落）
4. **无缓存**：每次重新算 prefix（浪费 90% 成本）
5. **忽略 lost in middle**：重要内容放中段
6. **超长摘要**：用 LLM 摘要但摘要本身很长
7. **不评估**：没跑 NIAH / LongBench 就上线
8. **忽略延迟**：100K prefill 可能 10 秒
9. **无 token budget**：不限制总 token
10. **跨模型直接复制**：Claude 200K 策略 ≠ Gemini 2M 策略

---

## 9. 下一步

- 读 Anthropic "Prompt Caching" 文档
- 读 LongBench / RULER benchmark 论文
- 用 LLMLingua 压缩你的 prompt
- 跑一次 NIAH 测试你的系统

---

## 10. 案例：S（Selection）的工业化实现

本手册 SPACC 的 **S（Selection）** 在"给 agent 喂代码库"场景已形成完整产业，见 [`Agent上下文案例/`](../../Agent上下文案例/)：

- **领域全景**：六条技术路线（预构建图谱 / LSP 实时 / 嵌入向量 / 图排序地图…）+ 全项目速查表
- **深剖案例**：[`codegraph代码知识图谱/`](../../Agent上下文案例/codegraph代码知识图谱/)——一次 MCP 调用替代 28–43 次 grep/Read（tool calls -88%，tokens -62%），以及它主动披露的代价（驻留上下文 +80%——正是 P/A/C 三要素的问题）

---

**版本**：v1.0（2026-08-13；2026-08-14 增 §10 案例）
**核心理念**：**Context 不是越多越好。选 + 排 + 压 + 缓存 = 工程。**
